"""
pyEyeTrackerInterface: common Python interface for multiple eye tracking devices.

Part of the pyEyeTracker library 
Copyright (C) 2012  Florian Niefind (SMI GmbH), Sol Simpson 
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version). 

.. moduleauthor::  Florian Niefind < Florian.Niefind@smi.de> + contributors, please see credits section of documentation.
"""

from collections import deque


import sys
import ioHub
from ..... import Device, Computer
from ....eye_events import *

from .... import RTN_CODES, DATA_TYPES, \
              ET_MODES, CALIBRATION_TYPES, CALIBRATION_MODES, DATA_STREAMS, \
              DATA_FILTER, USER_SETUP_STATES,EyeTrackerInterface

from ctypes import *
from iViewXAPI import  *            #iViewX library


class EyeTracker(EyeTrackerInterface):
    """EyeTracker class is the main class for the pyEyeTrackerInterface module, 
    containing the majority of the eye tracker functionality commonly needed
    for a range of experiments.
       
    Not every eye tracker implemenation of the pyEyeTrackerInterface specification will
    support all of the specifications functionality. This is to be expected and
    pyEyeTrackerInterface has been designed to handle this case. When a specific
    implementation does not support a given method, if that method is called, 
    a default *not supported* behaviour is built into the base implemetation.
       
    On the other hand, some eye trackers offer very specialized functionality that
    is as common across the eye tracking field so is not part of the pyEyeTrackerInterface core, 
    or functionality that is just currently missing from the pyEyeTrackerInterface. ;) 
    
    In these cases, the specific eye tracker implemetation can expose the non core pyEyeTrackerInterace 
    functionality for their device by adding extra command types to the
    sendCommand method, or as a last resort, via the *EyeTracker.EXT* attribute of the class.

    .. note:: 
    
        Only **one** instance of EyeTracker can be created within an experiment. Attempting to create > 1 instance will raise an exception. To get the current instance of the EyeTracker you can call the class method EyeTracker.getInstance(); this is useful as it saves needing to pass an eyeTracker instance variable around your code. 
        
    Methods are broken down into several categories within the EyeTracker class:
    
    #. Eye Tracker Initalization / State Setting    
    #. Ability to Define the Graphics Layer for the Eye Tracker to Use During Calibration / System Setup
    #. Starting and Stopping of Data Recording
    #. Sending Syncronization messages to the Eye Tracker
    #. Accessing the Eye Tracker Timebase
    #. Accessing Eye Tracker Data During Recording
    #. Syncronizing the Local Experiment timebase with the Eye Tracker Timebase, so Eye Tracker events can be provided with local time stamps when that is appropriate.
    #. Experiment Flow Generics 
    """
    # >>> Custom class attributes

    _iViewXAPI = None
    connected = False #connected to the tracker?
    recording = False #recording?
    saved_data = False #has data already been stored?
    recording_file = None
    sample_rate = 0
    _eyes = 'BINOCULAR'
    EVENT_HANDLER = None
    SAMPLE_HANDLER = None
    handle_event = None
    handle_sample = None
    _eventArrayLengths = {}
    # <<<

    # >>> Overwritten class attributes
    DEVICE_TIMEBASE_TO_USEC=1.0 # the multiplier needed to convert dive times to usec times.
    __slots__=[]
    # <<<
    def __init__(self, *args, **kwargs):
        """EyeTracker class. This class is to be extended by each eye tracker specific implemetation of the pyEyeTrackerInterface.
        
        Please review the documentation page for the specific eye tracker model that you are using the pyEyeTrackerInterface with to get
        the appropriate class name for that eye tracker; for example, if you are using an interface that supports eye trackers developed by
        EyeTrackingCompanyET, you may initialize the eye tracker object for that manufacturer something similar too :
       
           eyeTracker = hub.eyetrackers.EyeTrackingCompanyET.EyeTracker(**kwargs)
        
        where hub is the instance of the ioHubConnection class that has been created for your experiment.
        
        **kwargs are an optional set of named parameters.
        
        **If an instance of EyeTracker has already been created, trying to create a second will raise an exception. Either destroy the first instance and then create the new instance, or use the class method EyeTracker.getInstance() to access the existing instance of the eye tracker object.**
        """
        
        
        if EyeTracker._INSTANCE is not None:
            raise "EyeTracker object has already been created; only one instance can exist.\n \
            Delete existing instance before recreating EyeTracker object."
            sys.exit(1)  
        
        # >>>> eye tracker config
        EyeTracker.eyeTrackerConfig = kwargs['dconfig']
        
        # create Device level class setting dictionary and pass it Device constructor
        deviceSettings = {'instance_code':self.eyeTrackerConfig['instance_code'],
            'category_id':ioHub.devices.EventConstants.DEVICE_CATERGORIES[EyeTracker.CATEGORY_LABEL],
            'type_id':ioHub.devices.EventConstants.DEVICE_TYPES[EyeTracker.DEVICE_LABEL],
            'device_class':self.eyeTrackerConfig['device_class'],
            'name':self.eyeTrackerConfig['name'],
            'os_device_code':'OS_DEV_CODE_NOT_SET',
            'max_event_buffer_length':self.eyeTrackerConfig['event_buffer_length'],
            }
        EyeTrackerInterface.__init__(self, **deviceSettings)
        
        # set this instance as 'THE' instance of the eye tracker.
        EyeTracker._INSTANCE = self
        
        runtimeSettings = self.eyeTrackerConfig['runtime_settings']
        EyeTracker.sample_rate = runtimeSettings['sampling_rate']
        
        
        EyeTracker.displaySettings = self.eyeTrackerConfig['display_settings']

        # implementation specific SMI attributes
        EyeTracker._iViewXAPI = windll.LoadLibrary("iViewXAPI.dll")
                                 
        #specific commands       
        EyeTracker._COMMAND_TO_FUNCTION = {'Calibrate':EyeTracker._iViewXAPI.iV_Calibrate, 'Validate':EyeTracker._iViewXAPI.iV_Validate}
        
        #initialize callbacks for new events and samples
        
        #define output and input to the function
        EyeTracker.EVENT_HANDLER = CFUNCTYPE(c_int, CEvent)
        #convert the python function to a c-callback function
        EyeTracker.handle_event = EyeTracker.EVENT_HANDLER(self._handleNativeEvent)
        #and pass it over to the iViewX event callback function
        EyeTracker._iViewXAPI.iV_SetEventCallback(EyeTracker.handle_event)
        #and the same for samples
        EyeTracker.SAMPLE_HANDLER = CFUNCTYPE(c_int, CSample)
        EyeTracker.handle_sample = EyeTracker.SAMPLE_HANDLER(self._handleNativeEvent)        
        EyeTracker._iViewXAPI.iV_SetSampleCallback(EyeTracker.handle_sample)
        

    def _EyeTrackerToDisplayCoords(self, *args, **kwargs):
        
        if len(args) < 2:
            return ['EYETRACKER_ERROR', '_eyeTrackerToDisplayCoords requires two args gaze_x=args[0], gaze_y=args[1]']
        gaze_x = args[0]
        gaze_y = args[1]
        
        width, height = ioHub.devices.display.Display.getScreenResolution()
        
        # do mapping if necessary
        # default is no mapping 
        display_x = gaze_x - (width / 2)
        display_y = -(gaze_y - (height / 2))
        
        return display_x, display_y
    
    def _DisplayToEyeTrackerCoords(self, *args, **kwargs):
        
        if len(args) < 2:
            return ['EYETRACKER_ERROR', '_displayToEyeTrackerCoords requires two args display_x=args[0], display_y=args[1]']
        display_x = args[0]
        display_y = args[1]
        
        width, height = ioHub.devices.display.Display.getScreenResolution()
        
        # do mapping if necessary
        # default is no mapping 
        gaze_x = display_x + (width / 2)
        gaze_y = -display_y + (height / 2)
        
        return gaze_x, gaze_y
    
    def experimentStartDefaultLogic(self, *args, **kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the start of an experiment.  
        
        SMI: 
        Connects the tracker assuming you record on the local machine,
        Starts recording
        
        If you intend to record and run the experiment from different computers do not use this function.
        Establish the functionality with setConnectionState and the appropriate network settings 
        """
        res = self.setConnectionState(True)
        res = self.setRecordingState(True)
        
        return RTN_CODES.ET_OK
 
    def blockStartDefaultLogic(self, *args, **kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the start of an experiment block.  
        
        arguments (optional): Calibrate = True, set to False if you want to skip the Calibration
        """
        calibrate = kwargs.get('calibrate', True)
        if calibrate:
            res = self._iViewXAPI.iV_Calibrate()
            res = self.setRecordingState(True)
                
        return RTN_CODES.ET_OK

    def trialStartDefaultLogic(self, *args, **kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the start of an experiment trial.  
        
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
         
    def trialEndDefaultLogic(self, *args, **kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the end of an experiment trial.  
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
         
    def blockEndDefaultLogic(self, *args, **kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the end of an experiment block.  
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def experimentEndDefaultLogic(self, *args, **kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the end of an experiment sessio.  
        
        SMI: Stops recording, disconnects and stores the data if it has not been stored before
        """       
        if self._iViewXAPI != None:
            # File transfer and cleanup!
            
            self.setRecordingState(False)
            
            if not EyeTracker.saved_data:
                self.getFile()
            
            self.setConnectionState(False);
            
            return RTN_CODES.ET_OK
        return ('EYETRACKER_ERROR', 'EyeLink EyeTracker is not initialized.')
        
    def trackerTime(self):
        """
        Current eye tracker time ( in USEC since device interface was initialized)
        """
        time = c_ulonglong(1) #allocate memory
        EyeTracker._iViewXAPI.iV_GetCurrentTimestamp(byref(time))
        return (time.value - self.DEVICE_START_TIME) * self.DEVICE_TIMEBASE_TO_USEC
   
    def setConnectionState(self, *args, **kwargs):
        """
        setConnectionState is used to connect ( setConnectionState(True) ) or disable ( setConnectionState(False) )
        the connection of the pyEyeTrackerInterface to the eyetracker.
        
        Args:
        
            enabled (bool): True = enable the connection, False = disable the connection.
            
        SMI optional:
            SendIPAddress (string): IP address of iView X computer: default 127.0.0.1
            SendPort (int): port being used by iView X SDK for sending data to iViewX default 4444
            RecvIPAdress (string): IP address of local computer default 127.0.0.1
            ReceivePort (int): port being used by iView X SDK for receiving data from iViewX default 5555
        """
        enabled = args[0]
        
        if enabled is True:
            SendIPAddress = kwargs.pop('SendIPAdress', "127.0.0.1")
            SendPort = kwargs.pop('SendPort', 4444)
            RecvIPAddress = kwargs.pop('RecvIPAdress', "127.0.0.1")
            ReceivePort = kwargs.pop('ReceivePort', 5555)       
            res = EyeTracker._iViewXAPI.iV_Connect(c_char_p(SendIPAddress), c_int(SendPort), c_char_p(RecvIPAddress), c_int(ReceivePort))
            
            if res != 1: #if something did not work out
                return ['EYETRACKER_ERROR', 'Return Code is ' + str(res) + '. Refer to the iView X SDK Manual for its meaning.']
            
            
            if EyeTracker.DEVICE_START_TIME == 0.0:
                EyeTracker.DEVICE_START_TIME = self.trackerTime()
            
            #Get Samplerate
            #system_data is a system info data structure defined in the iViewXAPI
            system_data = CSystem(0, 0, 0, 0, 0, 0, 0, 0)
            res = EyeTracker._iViewXAPI.iV_GetSystemInfo(byref(system_data))
            if EyeTracker.sample_rate != system_data.samplerate:
                ioHub.print2err('Warning: Sample rate mismatch. User requested sample rate of %iHz, system now recording at %iHz.' % (EyeTracker.sample_rate, system_data.samplerate))
                EyeTracker.sample_rate = system_data.samplerate
                
            EyeTracker.connected = True                   
            return True 
                                  
        elif enabled is False:
            res = EyeTracker._iViewXAPI.iV_Disconnect()        
            EyeTracker.connected = False   
            return False  
                                 
        else:
            return ['EYETRACKER_ERROR', 'Invalid argument type', 'setConnectionState', 'enabled', enabled, kwargs]
            
    def isConnected(self):
        """
        isConnected returns whether the pyEyeTrackerInterface is connected to the eye tracker (returns True) or not (returns False)
        """
        return EyeTracker.connected
            
    def sendCommand(self, *args, **kwargs):
        """
        sendCommand sends a text command and text command value to the eye tracker. Depending on the command and on the eye trackers
        implementation, when a command is sent, the eye tracker may or may not respond indicating the status of the command. If the
        command is not going to return a response from the eye tracker, the method will return RTN_CODES.ET_RESULT_UNKNOWN.
        Please see the specific eye tracker implementation you are working with for a list of supported command's and value's.
        
        Args:
        
           command (str): string command to send to the eye tracker. See the specific eye tracker documentation for pyEyeTracker for a list of valid _iViewXAPI.
           value (str): the string form of the value of the command to send. SMI: can contain multiple parameters split by spaces
           wait (bool or callable) *NOT CURRENTLY SUPPORTED; FUNCTIONS AS ALWAYS == TRUE*: if bool, True = do not return from function until result of command if known (if it can be known); False = return immediately after sending the command, ignoring any possible return value. If wait is a callable, then wait fould be a reference to the callback function you want called when the return value is available. If no return value is possible for the command, wait is ignorded and RTN_CODES.ET_RESULT_UNKNOWN is returned immediately..           
        
        Return: the result of the command call, or one of the ReturnCodes Constants ( ReturnCodes.ET_OK, ReturnCodes.ET_RESULT_UNKNOWN, ReturnCodes.ET_NOT_IMPLEMENTED ) 
        """
        
        if len(args) >= 2:
            command = args[0]
            value = args[1]
        else:
            command = args[0]
            value = None
        wait = kwargs.pop('wait', False)
        if wait:
            ioHub.print2err("Warning: iViewX_EyeTracker.sendCommand wait param not implemented")
        
        if command in EyeTracker._COMMAND_TO_FUNCTION:
            if value:
                res = EyeTracker._COMMAND_TO_FUNCTION[command](value)
            else:
                res = EyeTracker._COMMAND_TO_FUNCTION[command]()
            return RTN_CODES.ET_RESULT_UNKNOWN    
        else:
            if value:
                res = EyeTracker._iViewXAPI.iV_SendCommand(c_char_p(command + " " + value))
            else:
                res = EyeTracker._iViewXAPI.iV_SendCommand(c_char_p(command))
        
        if res != 1: #if something did not work out
            return ['EYETRACKER_ERROR', 'Return Code is ' + str(res) + '. Refer to the iView X SDK Manual for its meaning.']
        return RTN_CODES.ET_OK
        
    def sendMessage(self, *args, **kwargs):
        """
        sendMessage sends a text message to the eye tracker. Depending on the eye trackers implementation, when a message is sent,
        the eye tracker may or may not response indicating the message was received. If the
        message is not going to receive a response from the eye tracker, the method will return RTN_CODES.ET_RESULT_UNKNOWN.
        Messages are generally used to send general text information you want saved with the eye data file  but more importantly
        are often used to syncronize stimulus changes in the experiment with the eye data stream. This means that the sendMessage 
        implementation needs to perform in real-time, with a delay of <1 msec from when a message is sent to when it is logged in
        the eye tracker data file, for it to be accurate in this regard. If this standard can not be met, the expected delay and
        message precision (variability) should be provided in the eye tracker's implementation notes for the pyEyeTRacker interface.  
        
        Args:
        
           message (str): string command to send to the eye tracker. The default maximum length of a message string is 128 characters.
           time_offset (int): number of int msec that the time stamp of the message should be offset by. This can be used so that a message 
               can be sent for a display change **BEFORE** or **AFTER** the actual flip occurred (usually before), by sending the message, say 4 
               msec prior to when you know the next trace will occur, entering -4 into the offset field of the message, and then send it and 
               calling flip() 4 msec before the retrace to ensure that the message time stamp and flip are both sent and scheduled in advance. 
               (4 msec is quite large buffer even on windows these days with modern hardware BTW)
        
        SMI: offsetting the timestamp is not possible with our system. This would need to be done offline
        """
        message = args[0]
        time_offset = kwargs.pop('time_offset', 0)
        
        res = EyeTracker._iViewXAPI.iV_SendImageMessage(c_char_p(message))
        if time_offset != 0:
            ioHub.print2err('Warning: Time-offset option is not available in iViewX. The original message timestamp was not modified!\n')
        if res != 1:
            return ['EYETRACKER_ERROR', 'Return Code is ' + str(res) + '. Refer to the iView X SDK Manual for its meaning.']
        return RTN_CODES.ET_OK 

        
    def createRecordingFile(self, *args, **kwargs):
        """
        createRecordingFile instructs the eye tracker to open a new file on the eye tracker computer to save data collected to
        during the recording. If recording is started and stopped multiple times while a single recording file is open, each 
        start/stop recording pair will be represented within the single file. A recording file is closed by calling
        closeRecordingFile(). Normally you would open a recording file at the start of an experimental session and close it
        at the end of the experiment; starting and stopping recording of eye data between trials of the experiment.
        
        Args:
           fileName (str): Name of the recording file to save on the eye tracker. This does *not* include the path to the file. Some eye trackers have limitations to the length of their file name, so please refer to the specific implemtations documenation for any caviates.
           path (str): This optional parameter can be used to specify the path to the recording file that should be saved. The path must already exist. If this paramemter is not specified, then the defualt file location is used. 
        """
        from os import getcwd as getcwd
        
        fileName = kwargs.pop('fileName', False)
        path = kwargs.pop('path', getcwd())
        
        if path and fileName:
            EyeTracker.recording_file = path + fileName
        else:
            return ('EYETRACKER_ERROR', 'EyeTracker.createRecordingFile', 'fileName must be provided as a kwarg')
        
    def closeRecordingFile(self, **kwargs):
        """
        closeRecordingFile is used to close the currently open file that is being used to save data from the eye track to the eye tracker computer. 
        Once a file has been closed, getFile(localFileName,fileToTransfer) can be used to transfer the file from the eye tracker computer to the 
        experiment computer at the end of the experiment session.
        
        SMI: Not necessary with the SMI system.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def getFile(self, *args, **kwargs):
        """
        getFile is used to transfer the file from the eye tracker computer to the experiment computer at the end of the experiment session.

        Args:
        
           localFileName (str): Name of the recording file to experiment computer.
           fileToTransfer (str): Name of the recording file to transfer from the eye tracker.
           
           SMI: local filename must be a full path (absolute or relative)
               fileToTransfer is not needed, as no files are stored on the tracker PC
        
        """
        
        localFileName = kwargs.pop('localFileName', EyeTracker.recording_file)
        description = kwargs.pop('description', '')
        user = kwargs.pop('user', '')
        overwrite = kwargs.pop('overwrite', 1)
        
        if not localFileName: #no local filename has been given or previously set
            return ('EYETRACKER_ERROR', 'EyeTracker.getFile', 'fileName must be provided as a kwarg or set with method: createRecordingFile')
        
        if "\\" not in localFileName:
            from os import getcwd
            localFileName = getcwd() + localFileName
            
        res = EyeTracker._iViewXAPI.iV_SaveData(c_char_p(localFileName), c_char_p(description), c_char_p(user), overwrite)
        if res != 1:
            return ['EYETRACKER_ERROR', 'Return Code is ' + str(res) + '. Refer to the iView X SDK Manual for its meaning.']
        EyeTracker.saved_data = True
        return RTN_CODES.ET_OK 
    
    def runSetupProcedure(self, graphicsContext=None , **kwargs):
        
        self.setConnectionState(True)
        
        runTimeSettings = self.eyeTrackerConfig['runtime_settings']

        cal_pts = int(runTimeSettings['default_calibration'][0])
        calibrationData = CCalibration(cal_pts, 1, 0, 0, 1, 20, 239, 1, 15, b"")
        EyeTracker._iViewXAPI.iV_SetupCalibration(byref(calibrationData))
        res = EyeTracker._iViewXAPI.iV_Calibrate()

        EyeTracker._iViewXAPI.iV_Validate()
        res = EyeTracker._iViewXAPI.iV_GetAccuracy(byref(accuracyData), 1)

        ioHub.print2err("deviationXLeft ", str(accuracyData.deviationXLeft), " deviationYLeft ", str(accuracyData.deviationYLeft))
        ioHub.print2err("deviationXRight ", str(accuracyData.deviationXRight), " deviationYRight ", str(accuracyData.deviationYRight))
           
        res = EyeTracker._iViewXAPI.iV_ShowTrackingMonitor()
        
        #if self._setupGraphics is None:
        #    self._setupGraphics=EyeTrackerSetupGraphics(graphicsContext=graphicsContext,**kwargs)
        #return self._setupGraphics.run()

    def stopSetupProcedure(self):
        result = None
        if self._setupGraphics is not None:
            result = self._setupGraphics.stop()
        return result
                
    def setRecordingState(self, recording=False, **kwargs):
        """
        setRecordingState is used to start or stop the recording of data from the eye tracking device. Use sendCommand() set the necessary information 
        for your eye tracker to enable what data you would like saved, send over to the experiment computer during recording, etc.
        
        Args:
           recording (bool): if True, the eye tracker should start recording data.; False = stop recording data.
        """
        
        if recording is True:
            res = EyeTracker._iViewXAPI.iV_StartRecording()
            if res not in [1, 192]: #192 means it is already recording...
                return ['EYETRACKER_ERROR', 'Return Code is ' + str(res) + '. Refer to the iView X SDK Manual for its meaning.']
            EyeTracker.recording = True                   
            return True                              
        elif recording is False:
            res = EyeTracker._iViewXAPI.iV_StopRecording()        
            if res != 1:
                return ['EYETRACKER_ERROR', 'Return Code is ' + str(res) + '. Refer to the iView X SDK Manual for its meaning.']
            EyeTracker.recording = False
            return False                              
        else:
            return ['EYETRACKER_ERROR', 'Invalid argument type', 'setConnectionState', 'enabled', recording, kwargs]
            

    def isRecordingEnabled(self, **args):
        """
        isRecordingEnabled returns the recording state from the eye tracking device.
        True == the device is recording data
        False == Recording is not occurring
        """
        return EyeTracker.recording
     
    def getDataFilterLevel(self, data_stream='ET_DATA_STREAMS.ALL', **args):
        """
        getDataFilteringLevel returns the numerical code the current device side filter level 
        set for the specific data_stream. 
        
        Currently, filter levels 0 (meaning no filter) through 
        5 (highest filter level) can be specified via the pyEyeTrackerInterface.
        They are defined in ET_FILTERS.
        
        data_streams specifies what output the filter is being applied to by the device. The
        currently defined output streams are defined in ET_DATA_STREAMS and are
        ALL,FILE,NET,SERIAL,ANALOG. ALL indicates that the filter level for all available output streams should be
        provided, in which case a dictionary of stream keys, filter level values should be returned.
        
        If an ET device supports setting one filter level for all available output streams, it can simply return
        (ALL, filter_level).
        
        If a stream type that is not supported by the device for individual filtering is specified, 
        an error should be generated.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def setDataFilterLevel(self, level, data_stream='ET_DATA_STREAMS.ALL', **args):
        """
        setDataFilteringLevel sets the numerical code for current ET device side filter level 
        for the specific data_stream. 
        
        Currently, filter levels 0 (meaning no filter) through 
        5 (highest filter level) can be specified via the pyEyeTrackerInterface.
        They are defined in ET_FILTERS.
        
        data_streams specifies what output the filter is being applied to by the device. The
        currently defined output streams are defined in ET_DATA_STREAMS, and are
        ALL,FILE,NET,SERIAL,ANALOG. ALL indicates that the filter level should be applied to all 
        available output streams,
        
        If an ET device supports setting one filter level for all available output streams, 
        then setting using filter_level only should be done.
        
        If a stream type that is not supported by the device for individual filtering is specified, 
        an error should be generated.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def drawToGazeOverlayScreen(self, drawingcommand='UNIMPLEMENTED', position=None, value=None, **args):
        """
        drawToGazeOverlayScreen provides a generic interface for ET devices that support
        having graphics drawn to the Host / Control computer gaze overlay area, or other similar
        graphics area functionality.
        
        The method should return the appropriate return code if successful or if the command failed,
        or if it is unsupported.
        
        There is no set list of values for any of the arguements for this command, so please refer to the
        ET imlpementation notes for your device for details. Hypothetical examples may be:
        
        # clear the overlay area to black
        eyetracker.drawToGazeOverlayScreen(drawingcommand='CLEAR',  value="BLACK")

        # draw some white text centered on the overlay area
        eyetracker.drawToGazeOverlayScreen(drawingcommand='TEXT', position=('CENTER',512,387),  value="This is my Text To Show", color='WHITE')

        # draw an image on the overlay area
        eyetracker.drawToGazeOverlayScreen(drawingcommand='IMAGE',  value="picture.png", position=('CENTER',512,387))
        
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def getDigitalPortState(self, port, **args):
        """
        getDigitalPortState returns the current value of the specified digital port on the ET computer. 
        This can be used to read the parallel port or digital lines on the ET host PC if the ET has such functionality.

        port = the address to read from on the host PC. Consult your ET device documentation for appropriate values.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
 
    def setDigitalPortState(self, port, value, **args):
        """
        setDigitalPortState sets the value of the specified digital port on the ET computer. 
        This can be used to write to the parallel port or digital lines on the ET Host / Operator PC if the ET
        has such functionality.

        port = the address to write to on the host PC. Consult your ET device documentation for appropriate values.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleNativeEvent(self, *args, **kwargs):
        """
        _handleNativeEvent is used by devices that signal new events by using an event driven
        callback approach.
        One args is required, the device event to be handled, "event"
        """
        if len(args) > 0:
            event = args[0]
        currentTime = int(Computer.currentUsec())
        EyeTracker.lastCallbackTime = currentTime

        # append the native event to the deque as a tuple of (current_time, event)
        # This can be unpacked in the _getIOHubEventObject and the current_time 
        # used as the logged_time field of the ioHub DeviceEvent object.

        self._nativeEventBuffer.append((currentTime, event))

        # Debugging .......
        #if isinstance(event, CEvent):
            
            #===================================================================
            # printout for debug
            #===================================================================

            #ioHub.print2err('BEFORE: ')
            #for field in event._fields_:
            #   ioHub.print2err(field[0],' ')
            #   ioHub.print2err((str(event.__getattribute__(field[0])),' ')
            #   ioHub.print2err('')
            
            
        #elif isinstance(event, CSample):
            
            #===================================================================
            # printout for debug
            #===================================================================

            #for field in event._fields_:
            #   ioHub.print2err(field[0],' ')
            #   if field[0] == 'leftEye' or field[0] == 'rightEye':
            #       eye = event.__getattribute__(field[0])
            #       for eyefield in eye._fields_[0:3]:
            #           ioHub.print2err(eyefield[0], ' ')
            #           ioHub.print2err(str(eye.__getattribute__(eyefield[0])),'  ')
            #   else:
            #       ioHub.print2err(str(event.__getattribute__(field[0])) + ' ')
            #       ioHub.print2err('')
        return 1
        
        
    def _getIOHubEventObject(self, *args, **kwargs):
        '''
        _getIOHubEventObject is used to convert a devices events from their 'native' format
        to the ioHub DeviceEvent obejct for the relevent event type. 
        
        If a polling model is used to retrieve events, this conversion is actually done in
        the polling method itself.
        
        If an event driven callback method is used, then this method should be employed to do
        the conversion between object types, so a minimum of work is done in the callback itself.
        
        The method expects two args:
            (logged_time,event)=args[0] (when the callback is used to register device events)
            event = args[0] (when polling is used to get device events)
            device_instance_code=args[1]
        '''
        try:
            currentTime = int(Computer.currentUsec())
    
            if len(args) == 2:
                logged_time, event = args[0]
                device_instance_code = args[1]
    
            # (1sec in usec/samplerate) / 2 -> half the sampling rate is the confidence interval
            confidenceInterval = (1000000.0 / EyeTracker.sample_rate) / 2.0 
            
            if isinstance(event, CSample):
                
                
                event_timestamp = (event.timestamp - self.DEVICE_START_TIME) * self.DEVICE_TIMEBASE_TO_USEC
                TT = self.trackerTime()
                event_delay = TT - event_timestamp
                hub_timestamp = currentTime - event_delay
    
                # for monocular samples, the non-recorded eye is a dummy data_struct filled with 0-values
                # that is the same as a binocular sample where 1 eye went missing: TODO implement a test
                # that can distinguish these two cases
                
                #case monocular sample
                if EyeTracker._eyes != 'BINOCULAR':
                    
                    event_type = EventConstants.EVENT_TYPES['EYE_SAMPLE']
                    
                    if event.rightEye.gazeX == 0:
                        myeye = EventConstants.LEFT
                        eye = event.leftEye
                    else:
                        myeye = EventConstants.RIGHT
                        eye = event.rightEye
                            
                    pupilDiameter = eye.diam
                    gazeX, gazeY = self._EyeTrackerToDisplayCoords(eye.gazeX, eye.gazeY)
                    eyePosX = eye.eyePositionX
                    eyePosY = eye.eyePositionY
                    eyePosZ = eye.eyePositionZ
                    
                    #monoSample = MonocularEyeSample(experiment_id=0, session_id=0, event_id=Computer.getNextEventID(),
                    #                    event_type=event_type, device_instance_code=device_instance_code,
                    #                    device_time=event_timestamp, logged_time=currentTime, hub_time=hub_timestamp,
                    #                    confidence_interval=confidenceInterval, delay=event_delay,
                    #                    eye=myeye, gaze_x=gazeX, gaze_y=gazeY, gaze_z= -1.0,
                    #                    eye_cam_x=eyePosX, eye_cam_y=eyePosY, eye_cam_z=eyePosZ,
                    #                    angle_x= -1.0, angle_y= -1.0, raw_x= -1.0, raw_y= -1.0,
                    #                    pupil_measure1=pupilDiameter, pupil_measure2= -1, ppd_x= -1, ppd_y= -1,
                    #                    velocity_x= -1.0, velocity_y= -1.0, velocity_xy= -1.0, status=0)
    
                    monoSample = [0, 0, Computer.getNextEventID(), event_type, device_instance_code,
                        event_timestamp, logged_time, hub_timestamp,
                        confidenceInterval, event_delay,
                        myeye, gazeX, gazeY, -1.0,
                        eyePosX, eyePosY, eyePosZ,
                        - 1.0, -1.0, -1.0, -1.0,
                        pupilDiameter, -1, -1, -1,
                        - 1.0, -1.0, -1.0, 0]
                    
                    EyeTracker._latestSample = monoSample    
    
                    EyeTracker._latestGazePosition = gazeX, gazeY
                    #ioHub.print2err( monoSample
                    EyeTracker._eventArrayLengths['EYE_SAMPLE'] = len(monoSample)
                    return monoSample
                
                else: #case: Binocular Eye Sample
                    
                    event_type = ioHub.devices.EventConstants.EVENT_TYPES['BINOC_EYE_SAMPLE']
                    
                    leftEye = event.leftEye
                    leftPupilDiameter = leftEye.diam
                    leftGazeX, leftGazeY = self._EyeTrackerToDisplayCoords(leftEye.gazeX, leftEye.gazeY)
                    leftEyePosX = leftEye.eyePositionX
                    leftEyePosY = leftEye.eyePositionY
                    leftEyePosZ = leftEye.eyePositionZ
                    
                    rightEye = event.rightEye
                    rightPupilDiameter = rightEye.diam
                    rightGazeX, rightGazeY = self._EyeTrackerToDisplayCoords(rightEye.gazeX, rightEye.gazeY)
                    rightEyePosX = rightEye.eyePositionX
                    rightEyePosY = rightEye.eyePositionY
                    rightEyePosZ = rightEye.eyePositionZ
    
                    #binocSample = BinocularEyeSample(experiment_id=0, session_id=0, event_id=Computer.getNextEventID(),
                    #    event_type=event_type, device_instance_code=device_instance_code,
                    #    device_time=event_timestamp, logged_time=logged_time, hub_time=hub_timestamp,
                    #    confidence_interval=confidenceInterval, delay=event_delay,
                    #    eye=myeye, left_gaze_x=leftGazeX, left_gaze_y=leftGazeY, left_gaze_z= -1.0,
                    #    left_eye_cam_x=leftEyePosX, left_eye_cam_y=leftEyePosY, left_eye_cam_z=leftEyePosZ,
                    #    left_angle_x= -1.0, left_angle_y= -1.0, left_raw_x= -1.0, left_raw_y= -1.0,
                    #    left_pupil_measure1=leftPupilDiameter, left_pupil_measure2= -1, left_ppd_x= -1, left_ppd_y= -1,
                    #    left_velocity_x= -1.0, left_velocity_y= -1.0, left_velocity_xy= -1.0,
                    #    right_gaze_x=rightGazeX, right_gaze_y=rightGazeY, right_gaze_z= -1.0,
                    #    right_eye_cam_x=rightEyePosX, right_eye_cam_y=rightEyePosY, right_eye_cam_z=rightEyePosZ,
                    #    right_angle_x= -1.0, right_angle_y= -1.0, right_raw_x= -1.0, right_raw_y= -1.0,
                    #    right_pupil_measure1=rightPupilDiameter, right_pupil_measure2= -1, right_ppd_x= -1, right_ppd_y= -1,
                    #    right_velocity_x= -1.0, right_velocity_y= -1.0, right_velocity_xy= -1.0, status=0)
    
                    binocSample = [0, 0, Computer.getNextEventID(),
                        event_type, device_instance_code,
                        event_timestamp, logged_time, hub_timestamp,
                        confidenceInterval, event_delay,
                        leftGazeX, leftGazeY, -1.0,
                        leftEyePosX, leftEyePosY, leftEyePosZ,
                         - 1.0, -1.0, -1.0, -1.0,
                         leftPupilDiameter, -1, -1, -1,
                          - 1.0, -1.0, -1.0,
                         rightGazeX, rightGazeY, -1.0,
                         rightEyePosX, rightEyePosY, rightEyePosZ,
                          - 1.0, -1.0, -1.0, -1.0,
                         rightPupilDiameter, -1, -1, -1,
                          - 1.0, -1.0, -1.0, 0]
    
                    EyeTracker._latestSample = binocSample
                    EyeTracker._latestGazePosition = (leftGazeX + rightGazeX) / 2.0, (leftGazeY + rightGazeY) / 2.0                
                    EyeTracker._eventArrayLengths['BINOC_EYE_SAMPLE'] = len(binocSample)
                    return binocSample    
                
                
            elif isinstance(event, CEvent):
                #fixations are the only event supported by iViewX
                #generates a start and end event from the single SMI native event
    
                event_status = 0
                
                which_eye = event.eye
                if which_eye == 'r':
                    which_eye = EventConstants.RIGHT
                else:
                    which_eye = EventConstants.LEFT
                
                
                start_event_time = (event.startTime - self.DEVICE_START_TIME) * self.DEVICE_TIMEBASE_TO_USEC
                end_event_time = (event.endTime - self.DEVICE_START_TIME) * self.DEVICE_TIMEBASE_TO_USEC
                event_duration = event.duration
                
                a_gazeX, a_gazeY = self._EyeTrackerToDisplayCoords(event.positionX, event.positionY)
                
                if event.endTime == 0: #start event
                    
                    event_timestamp = start_event_time
                    event_delay = self.trackerTime() - event_timestamp
                    hub_timestamp = currentTime - event_delay
                
                    event_type = ioHub.devices.EventConstants.EVENT_TYPES['FIXATION_START']
    
                    #fse = FixationStartEvent(experiment_id=0, session_id=0, event_id=Computer.getNextEventID(),
                    #    event_type=event_type, device_instance_code=device_instance_code,
                    #    device_time=event_timestamp, logged_time=currentTime, hub_time=hub_timestamp,
                    #    confidence_interval=confidenceInterval, delay=event_delay, eye=which_eye,
                    #    gaze_x=a_gazeX, gaze_y=a_gazeY, gaze_z= -1,
                    #    angle_x= -1.0, angle_y= -1.0, raw_x= -1.0, raw_y= -1.0,
                    #    pupil_measure1= -1.0, pupil_measure2= -1.0,
                    #    ppd_x= -1.0, ppd_y= -1.0, velocity_x= -1.0, velocity_y= -1.0, velocity_xy= -1.0, status=event_status)
    
                    fse = [0, 0, Computer.getNextEventID(),
                        event_type, device_instance_code, event_timestamp, currentTime, hub_timestamp,
                        confidenceInterval, event_delay, which_eye,
                        a_gazeX, a_gazeY, -1,
                        - 1.0, -1.0, -1.0, -1.0,
                        - 1.0, -1.0,
                        - 1.0, -1.0, -1.0, -1.0, -1.0, event_status]
                    
                    EyeTracker._eventArrayLengths['FIXATION_START'] = len(fse)
                    return fse
                
                elif end_event_time > 0: #fixation end
                    
                    event_timestamp = end_event_time
                    event_delay = self.trackerTime() - event_timestamp
                    hub_timestamp = currentTime - event_delay
                        
                    event_type = ioHub.devices.EventConstants.EVENT_TYPES['FIXATION_END']
    
                    #fee = FixationEndEvent(experiment_id=0, session_id=0, event_id=Computer.getNextEventID(),
                    #    event_type=event_type, device_instance_code=device_instance_code,
                    #    device_time=event_timestamp, logged_time=currentTime, hub_time=hub_timestamp,
                    #    confidence_interval=confidenceInterval, delay=event_delay, eye=which_eye,
                    #    duration=event_duration, start_gaze_x= -1.0, start_gaze_y= -1.0, start_gaze_z= -1.0,
                    #    start_angle_x= -1.0, start_angle_y= -1.0, start_raw_x= -1.0, start_raw_y= -1.0,
                    #    start_pupil_measure1= -1.0, start_pupil_measure2= -1.0, start_ppd_x= -1.0, start_ppd_y= -1.0,
                    #    start_velocity_x= -1.0, start_velocity_y= -1.0, start_velocity_xy= -1.0,
                    #    end_gaze_x=a_gazeX, end_gaze_y=a_gazeY, end_gaze_z= -1.0,
                    #    end_angle_x= -1.0, end_angle_y= -1.0, end_raw_x= -1.0, end_raw_y= -1.0,
                    #    end_pupil_measure1= -1.0, end_pupil_measure2= -1.0, end_ppd_x= -1.0, end_ppd_y= -1.0,
                    #    end_velocity_x= -1.0, end_velocity_y= -1.0, end_velocity_xy= -1.0,
                    #    average_gaze_x= -1.0, average_gaze_y= -1.0, average_gaze_z= -1.0,
                    #    average_angle_x= -1.0, average_angle_y= -1.0, average_raw_x= -1.0, average_raw_y= -1.0,
                    #    average_pupil_measure1= -1.0, average_pupil_measure2= -1.0, average_ppd_x= -1.0, average_ppd_y= -1.0,
                    #    average_velocity_x= -1.0, average_velocity_y= -1.0, average_velocity_xy= -1.0,
                    #    peak_velocity_x= -1.0, peak_velocity_y= -1.0, peak_velocity_xy= -1.0, status=event_status)
    
                    fee = [0, 0, Computer.getNextEventID(),
                        event_type, device_instance_code,
                        event_timestamp, currentTime, hub_timestamp,
                        confidenceInterval, event_delay, which_eye,
                        event_duration, -1.0, -1.0, -1.0,
                        - 1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0,
                        - 1.0, -1.0, -1.0,
                        a_gazeX, a_gazeY, -1.0,
                        - 1.0, -1.0, -1.0, -1.0,
                        - 1.0, -1.0, -1.0, -1.0,
                        - 1.0, -1.0, -1.0,
                        - 1.0, -1.0, -1.0,
                        - 1.0, -1.0, -1.0, -1.0,
                        - 1.0, -1.0, -1.0, -1.0,
                        - 1.0, -1.0, -1.0,
                        - 1.0, -1.0, -1.0, event_status]
                    
                    EyeTracker._eventArrayLengths['FIXATION_END'] = len(fee)
                    return fee
                else:
                    ioHub.print2err('Error: Something went wrong with the timestamping. Got negative timestamp.')
                    ioHub.print2err(event.endTime)
    
                    return RTN_CODES.ET_ERROR
            else:
                ioHub.print2err("EyeTracker._getIOHubEventObject: Unknown input format.")
                return RTN_CODES.ET_ERROR
        except Exception, e:
            ioHub.printExceptionDetailsToStdErr()
   
    def getLatestSample(self, *args, **kwargs):
        """
        Returns the latest sample retieved from the eye tracker device.
        """
        return self._latestSample
    
    def getLatestGazePosition(self, *args, **kwargs):
        """
        Returns the latest eye Gaze Position retieved from the eye tracker device.
        """
        return self._latestGazePosition 
    
    def getEyesToTrack(self, *args, **kwargs):
        '''
        Returns the eyes being tracked
        '''
        return self._eyes
    
    
    def setEyesToTrack(self, *args, **kwargs):
        '''
        Set the eyes to be tracked: LEFT, RIGHT, BINOCULAR
        
        SMI: Setting the eyes to track is not currently supported, but planned
        in the very near future. Currently the recording will always be 
        binocular.
        '''
        if len(args) == 0:
            return RTN_CODES.ET_ERROR
        #EyeTracker._eyes = args[0]
#        if EyeTracker._eyes == 'BINOCULAR':
#            EyeTracker._iViewXAPI.iV_SetTrackingParameter(c_char_p(''), c_char_p('BOTH'), c_int(0))
#            return RTN_CODES.OK
#        elif EyeTracker._eyes == 'LEFT':
#            EyeTracker._iViewXAPI.iV_SetTrackingParameter(c_char_p(''), c_char_p('LEFT'), c_int(0))
#            return RTN_CODES.OK
#        elif EyeTracker._eyes == 'RIGHT':
#            EyeTracker._iViewXAPI.iV_SetTrackingParameter(c_char_p(''), c_char_p('RIGHT'), c_int(0))
#            return RTN_CODES.OK
#        else:
#            return RTN_CODES.ET_NOT_IMPLEMENTED    
        return RTN_CODES.ET_NOT_IMPLEMENTED


    def getSamplingRate(self, *args, **kwargs):
        '''
        Returns the sample rate that was last recorded with or that the user set
        in the config file if no recording has taken place yet.
        '''
        return EyeTracker.sample_rate
    
    
    def setSamplingRate(self, *args, **kwargs):
        '''
        SMI: Setting the sample rate is currently not supported. The system will 
        automatically return a warning upon connecting to the tracker, if the 
        requested sample rate is not supported by the tracker. The sampling rate 
        will then be set by the tracker.
        '''
        if len(args) == 0:
            return RTN_CODES.ET_ERROR
        EyeTracker.sample_rate = args[0]
        return RTN_CODES.ET_NOT_IMPLEMENTED    
            
    def getEventArrayLengths(self, *args, **kwargs):
        return (EyeTracker._eventArrayLengths,)
     
    def __del__(self):
        """
        Do any final cleanup of the eye tracker before the object is destroyed. Users should not call or change this method. It is for implemetaion by interface creators and is autoatically called when an object is destroyed by the interpreter.
        """
        EyeTracker._INSTANCE = None

        
class EyeTrackerSetupGraphics(object):
    '''
    EyeTrackerUserSetupGraphics provides a minimalistic standard 'public' interface
    that can be used for taking control of the experiment runtime graphics environment
    and keyboard / mouse by the eye tracker interface during 'black box' modes such as
    camera setup, calibration, validation, etc. 

    Developers of eye tracker interfaces for pyETI can extend this class and implement 
    the specifics necessary to have the eye tracker perform whatever functionality is 
    supported by the eye tracker in terms of user facing graphics for these types of tasks.
    
    * Users 'enter' the graphics mode provided by the EyeTrackerUserCalibrationGraphics class by 
      calling a method of the eyetracker object from their experiment script:

      runSetupProcedure(*args,**kwargs):

      which in turn calls the run(....) method the this class.
      
    * This call blocks the user script, handing over control of the graphics state to the eye tracker interface. 
      The user script will remain blocked until you call the objects returnToUserSpace() method, or the user
      manages to call the eyetracker.stopSetupProcedure() method.
      
    * Devlopers can access keyboard and mouse events occurring on the experiment computer by calling:
    
      events = getKeyboardMouseEvents() # returns all keyboard and mouse events since 
                                        # the last call or since the last time 
                                        # clearKeyboardAndMouseEvents() was called.
    '''
    def __init__(self, graphicsContext, **kwargs):
        '''
        The EyeTrackerSetupGraphics instance is created the first time eyetracker.runSetupProcedure(graphicsContext)
        is called. The class instance is then reused in future calls. 
        graphicsContext object type is dependent on the graphics environment being used.
        Since psychopy normalizes everything in this regard to psychopy.visual.Window (regardless of
        whether pyglet or pygame backend is being used), then likely graphicsContext should be the instance of
        Window that has been created for your psychopy experiment. For an eye tracking experiment
        this would normally be a single 'full screen' window.
        '''
        self.graphicsContext = graphicsContext
        
    def run(self, *args, **kwargs):
        ioHub.print2err("EyeTrackerSetupGraphics.run is not implemented.")
        return 'dummy'#_handleDefaultState(*args,**kwargs)   

    def _handleDefaultState(self, *args, **kwargs):
        ioHub.print2err("EyeTrackerSetupGraphics._handleDefaultState is not implemented.")
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def _handleCameraSetupState(self, *args, **kwargs):
        ioHub.print2err("EyeTrackerSetupGraphics._handleCameraSetupState is not implemented.")
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def _handleParticipantSetupState(self, *args, **kwargs):
        ioHub.print2err("EyeTrackerSetupGraphics._handleParticipantSetupState is not implemented.")
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCalibrateState(self, *args, **kwargs):
        ioHub.print2err("EyeTrackerSetupGraphics._handleCalibrateState is not implemented.")
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleValidateState(self, *args, **kwargs):
        ioHub.print2err("EyeTrackerSetupGraphics._handleValidateState is not implemented.")
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleDCState(self, *args, **kwargs):
        ioHub.print2err("EyeTrackerSetupGraphics._handleDCState is not implemented.")
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCM_A_State(self, *args, **kwargs):
        ioHub.print2err("EyeTrackerSetupGraphics._handleCM_A_State is not implemented.")
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCM_B_State(self, *args, **kwargs):
        ioHub.print2err("EyeTrackerSetupGraphics._handleCM_B_State is not implemented.")
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCM_C_State(self, *args, **kwargs):
        ioHub.print2err("EyeTrackerSetupGraphics._handleCM_C_State is not implemented.")
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCM_D_State(self, *args, **kwargs):
        ioHub.print2err("EyeTrackerSetupGraphics._handleCM_D_State is not implemented.")
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCM_E_State(self, *args, **kwargs):
        ioHub.print2err("EyeTrackerSetupGraphics._handleCM_E_State is not implemented.")
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCM_F_State(self, *args, **kwargs):
        ioHub.print2err("EyeTrackerSetupGraphics._handleCM_F_State is not implemented.")
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def stop(self, returnMessage):
        ioHub.print2err("EyeTrackerSetupGraphics.stop is not implemented.")
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def getKeyboardMouseEvents(self):
        ioHub.print2err("EyeTrackerSetupGraphics.getKeyboardMouseEvents is not implemented.")
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
class EyeTrackerVendorExtension(object):
    '''
    EyeTrackerVendorExtension is the base class used to add custom functionality to the pyEyeTrackerInterface
    module when the standard pyEyeTrackerInterface functionality set can not be used to meet the requirements
    of the specific eye trackers needs. This should be used AS A LAST RESORT to add the necessary 
    functionality for any eye tracker. If you believe that certain functionality can not be met with 
    the current pyEyeTrackerInterface core API, please first contact the pyEyeTrackerInterface development team and discuss
    your requirements and needs. It may a) be possible to achieve what you need already, or b) be the
    case that your requirement is agreed to be a use case that should be added to the core pyEyeTrackerInterface 
    fucntionality instead of being added via an EyeTrackerVendorExtension. If either of these two situations
    are the case, the development team will put your requirements on the roadmap for the pyEyeTrackerInterface development
    and you or someone else are welcome to submit a patch for review containing the added functionality to the
    base pyEyeTrackerInterface code.
    '''
    
    def __init__(self):
        pass
