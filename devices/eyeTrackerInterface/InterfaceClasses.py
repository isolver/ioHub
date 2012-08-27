"""
ioHub Python Module

Copyright (C) 2012 Sol Simpson 
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version). 

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""

import sys,gc
import numpy as N
import ioHub
#from ..... import Device,Computer
#from ....eye_events import *

#from .... import RTN_CODES,EYE_CODES,PUPIL_SIZE_MEASURES,DATA_TYPES,\
#              ET_MODES,CALIBRATION_TYPES,CALIBRATION_MODES,DATA_STREAMS,\
#              DATA_FILTER,USER_SETUP_STATES

class EyeTracker(Device):
    '''EyeTracker class is the main class for the pyEyeTrackerInterface module, 
    containing the majority of the eye tracker functionality commonly needed
    for a range of experiments.
    
    With the integration of the pyEyeTrackerInterface into the ioHub module, the EyeTracker
    device is a device along with the other currently supported ioHub devices; Keyboard, Mouse,
    and Parallel Port.
    
    For implementers of pyEyeTracker interfaces, this means that the interface itself is running
    in the ioHub process, and communication between the computer and the eyetracker is done via
    the ioHub.

    For users of the pyEyeTrackerInterface for an eye tracker and psychopy, there is a second,
    experiment side ( psychopy side ) interface that has a parallel public API that 'talks'
    to the ioHub server. The good news for users is that this is transparent and you should not
    even realize this is happening in use. The good news for interface developers is that the 
    client side interface is dynamically generated at the start-up of the experiment based on the
    server side interface, so you do not need to maintain 2 seperate interfaces or worry about
    keeping them in sync.    
           
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
    '''   
    
    #: Used by pyEyeTrackerInterface implentations to store relationships between an eye 
    #: trackers command names supported for pyEyeTrackerInterface sendCommand method and  
    #: a private python function to call for that command. This allows an implemetation 
    #: of the interface to expose functions that are not in the core pyEyeTrackerInterface spec 
    #: without have to use the EXT extension class.
    _COMMAND_TO_FUNCTION={}     
    
    _INSTANCE=None #: Holds the reference to the current instance of the EyeTracker object in use and ensures only one is created.

    EXT=None  # IF Vendor specific extensioin of API must be done, create an extension of EyeTrackerVendorExtension class and add an instance of it here. 

    _setupGraphics=None # instance of EyeTrackerSetupGraphics class, if supported

    _latestSample=None
    
    eyeTrackerConfig=None # holds the configuration / settings dict for the device
    displaySettings=None
    
    #  >>>> Class attributes used by parent Device class
    DEVICE_START_TIME = 0.0 # Time to subtract from future device time reads. 
                             # Init in Device init before any calls to getTime() 
    
    DEVICE_TIMEBASE_TO_USEC=1.0 # the multiplier needed to convert dive times to usec times.
    
    dataType = Device.dataType+[]
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames
    # <<<<<
    
    lastPollTime=0.0    
    lastCallbackTime=0.0
    
    # used for simple lookup of device type and category number from strings
    categoryTypeString='EYE_TRACKER'
    deviceTypeString='EYE_TRACKER_DEVICE'
    
    # >>> implementation specific private class attributes


    # <<<
    def __init__(self,*args,**kwargs):
        '''
        EyeTracker class. This class is to be extended by each eye tracker specific implemetation
        of the pyEyeTrackerInterface.
        
        Please review the documentation page for the specific eye tracker model that you are using the 
        pyEyeTrackerInterface with to get the appropriate module path for that eye tracker; for example,
        if you are using an interface that supports eye trackers developed by EyeTrackingCompanyET, you
        may initialize the eye tracker object for that manufacturer something similar too :
       
           eyeTracker = hub.eyetrackers.EyeTrackingCompanyET.EyeTracker(**kwargs)
        
        where hub is the instance of the ioHubClient class that has been created for your experiment.
        
        **kwargs are an optional set of named parameters.
        
        **If an instance of EyeTracker has already been created, trying to create a second will raise an exception. Either destroy the first instance and then create the new instance, or use the class method EyeTracker.getInstance() to access the existing instance of the eye tracker object.**
        '''
        if EyeTracker._INSTANCE is not None:
            raise "EyeTracker object has already been created; only one instance can exist.\n \
            Delete existing instance before recreating EyeTracker object."
            sys.exit(1)  
        
        # >>>> eye tracker config
        EyeTracker.eyeTrackerConfig=kwargs['dconfig']
        #print " #### EyeTracker Configuration #### "
        #print self.eyeTrackerConfig
        #print ''
        # <<<<
        
        # create Device level class setting dictionary and pass it Device constructor
        deviceSettings={'instance_code':self.eyeTrackerConfig['instance_code'],
            'category_id':ioHub.DEVICE_CATERGORY_ID_LABEL[EyeTracker.categoryTypeString],
            'type_id':ioHub.DEVICE_TYPE_LABEL[EyeTracker.deviceTypeString],
            'device_class':self.eyeTrackerConfig['device_class'],
            'user_label':self.eyeTrackerConfig['name'],
            'os_device_code':'OS_DEV_CODE_NOT_SET',
            'max_event_buffer_length':self.eyeTrackerConfig['event_buffer_size']
            }
        Device.__init__(self,**deviceSettings)
        
        # set this instance as 'THE' instance of the eye tracker.
        EyeTracker._INSTANCE=self

        EyeTracker.DEVICE_START_TIME=0.0
        
        # >>>> eye tracker setting to config (if possible)
        #
        # Current settings, example from possible values.
        #
        # 'sampling_rate': 60.0, 
        # 'vog_settings': {
        #                  'pupil_illumination': 'dark', 
        #                  'pupil_center_algorithm': 'centroid', 
        #                  'tracking_mode': 'pupil-cr'
        #                 } 
        # 'default_calibration': '9P'
        # 'track_eyes': 'BINOC'
        # 'runtime_filtering': {
        #                       'ANY': 0
        #                      }
        runtimeSettings=self.eyeTrackerConfig['runtime_settings']
        #print ''
        #print " #### EyeTracker Runtime Settings #### "
        #print runtimeSettings
        #print ''
        # <<<<
        
        # >>>> Display / Calibration related information to use for config if possible
        #
        # Current settings, example from possible values.
        #
        # 'device_class': 'Display'
        # 'enable': True 
        # 'name': 'calibrationPlane'
        # 'instance_code': 'display_serial_number'
        # 'head_stationary': True 
        # 'IPD': 30.0 
        # 'physical_calibration_surface_dimensions': {
        #                        'width': 900
        #                        'height': 600
        #                        }
        # 'default_eye_physical_calibration_surface_distance': {
        #                               'bottom_center': 660
        #                               'top_center': 600
        #                               }
        # 'orthoganal_eye_to_physical_calibration_surface_location': {
        #                   'horizontal': 450
        #                   'vertical': 300
        #                   }
        # 'physical_calibration_surface_unit_type' : 'mm'
        # 'calibration_surface_bounds': {
        #                    'left': 0
        #                    'top': 0 
        #                    'right': 1920
        #                    'bottom': 1080
        #                    }
        # 'calibration_surface_bounds_unit_type': 'pixels'
        # 'psychopy_config_file': 'unknown'
        EyeTracker.displaySettings = self.eyeTrackerConfig['display_settings']
        #print ''
        #print " #### EyeTracker Display Settings #### "
        #print self.displaySettings
        #print ''        
        # <<<<

    def _getRPCInterface(self):
        '''
        This method is what builds the list of ioHub 'client side' methods that are visible
        for this device. This list == the list of callable methods a user can make to the device
        from the experiment process via something like:
        
           iohubClient.devices.eyetracker.experimentStartDefaultLogic()
            
        or to make it look shorter:
        
           eyetracker = iohubClient.devices.eyetracker
           
        then all calls to eyetracker methods are just:

           r=eyetracker.isRecordingEnabled()
           if r is False:
               eyetracker.setRecordingState(True)
           etc...           
        '''
        rpcList=[]
        dlist = dir(self)
        for d in dlist:
            if d[0] is not '_' and not d.startswith('I_'):
                if callable(getattr(self,d)):
                    rpcList.append(d)
        return rpcList
        
    def experimentStartDefaultLogic(self,*args,**kwargs):
        '''
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the start of an experiment.  
        '''
        recording_filename=None
        if 'filename' in kwargs:
            recording_filename=kwargs['filename']
        else:
            recording_filename=(self.eyeTrackerConfig['runtime_settings']['default_native_data_file_name'])+'.edf'
            
        return RTN_CODES.ET_NOT_IMPLEMENTED
 
    def blockStartDefaultLogic(self,*args,**kwargs):
        '''
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the start of an experiment block.  
        '''
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def trialStartDefaultLogic(self,*args,**kwargs):
        '''
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the start of an experiment trial.  
        '''
        return RTN_CODES.ET_NOT_IMPLEMENTED
         
    def trialEndDefaultLogic(self,*args,**kwargs):
        '''
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the end of an experiment trial.  
        '''
        return RTN_CODES.ET_NOT_IMPLEMENTED
         
    def blockEndDefaultLogic(self,*args,**kwargs):
        '''
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the end of an experiment block.  
        '''
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def experimentEndDefaultLogic(self,*args,**kwargs):
        '''
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the end of an experiment session.  
        '''       
        return RTN_CODES.ET_NOT_IMPLEMENTED
        
    def trackerTime(self):
        '''
        Current eye tracker time (timebase is eye tracker dependent)
        '''
        return RTN_CODES.ET_NOT_IMPLEMENTED
   
    def trackerUsecTimeSinceDeviceInit(self):
        '''
        Current eye tracker time, normalized. (in usec for since ioHub initialized Device)
        '''
        return RTN_CODES.ET_NOT_IMPLEMENTED
        
   
    def setConnectionState(self,*args,**kwargs):
        '''
        setConnectionState is used to connect ( setConnectionState(True) ) or disable ( setConnectionState(False) )
        the connection of the pyEyeTrackerInterface to the eyetracker.
        
        args:
            enabled (bool): True = enable the connection, False = disable the connection.
        kwargs (dict): any eye tracker specific parameters that should be passed.
        '''
        enabled=None
        if len(args)>0:
            enabled=args[0]
        if enabled is True or enabled is False:
            return RTN_CODES.ET_NOT_IMPLEMENTED
        else:
            return ['EYETRACKER_ERROR','Invalid arguement type','setConnectionState','enabled',enabled,args]
            
    def isConnected(self):
        '''
        isConnected returns whether the pyEyeTrackerInterface is connected to the eye tracker (returns True) or not (returns False)
        '''
        return return RTN_CODES.ET_NOT_IMPLEMENTED
            
    def sendCommand(self, *args, **kwargs):
        '''
        sendCommand sends a text command and text command value to the eye tracker. Depending on the command and on the eye trackers
        implementation, when a command is send, the eye tracker may or n=may not response indicating the status of the command. If the
        command is not going to return a response from the eye tracker, the method will return RTN_CODES.ET_RESULT_UNKNOWN.
        Please see the specific eye tracker implementation you are working with for a list of supported command's and value's.
        
        Args:
        
           command (str): string command to send to the eye tracker. See the specific eye tracker documentation for pyEyeTracker for a list of valid commands.
           value (str): the string form of the value of the command to send.
        
        kwargs:        
           wait (bool or callable) *NOT CURRENTLY SUPPORTED; FUNCTIONS AS ALWAYS == TRUE*: if bool, True = do not return from function until result of command if known (if it can be known); False = return immediately after sending the command, ignoring any possible return value. If wait is a callable, then wait fould be a reference to the callback function you want called when the return value is available. If no return value is possible for the command, wait is ignorded and RTN_CODES.ET_RESULT_UNKNOWN is returned immediately..           
        
        Return: the result of the command call, or one of the ReturnCodes Constants ( ReturnCodes.ET_OK, ReturnCodes.ET_RESULT_UNKNOWN, ReturnCodes.ET_NOT_IMPLEMENTED ) 
        '''
        if len(args)>=2:
            command=args[0]
            value=args[1]
        else:
            return ('EYETRACKER_ERROR','EyeTracker.sendCommand','requires args of length >=2, command==args[0],value==args[1]')
        wait=False
        if wait in kwargs:
            wait=kwargs['wait']
        
        return RTN_CODES.ET_NOT_IMPLEMENTED
        
    def sendMessage(self,*args,**kwargs):
        '''
        sendMessage sends a text message to the eye tracker. Depending on the eye trackers implementation, when a message is send,
        the eye tracker may or may not response indicating the message was received. If the
        message is not going to receive a response from the eye tracker, the method will return RTN_CODES.ET_RESULT_UNKNOWN.
        Messages are generally used to send general text information you want saved with the eye data file  but more importantly
        are often used to syncronize stimulus changes in the experiment with the eye data stream. This means that the sendMessage 
        implementation needs to perform in real-time, with a delay of <1 msec from when a message is sent to when it is logged in
        the eye tracker data file, for it to be accurate in this regard. If this standard can not be met, the expected delay and
        message precision (variability) should be provided in the eye tracker's implementation notes for the pyEyeTRacker interface.  
        
        Args:        
           message (str): string command to send to the eye tracker. The default maximum length of a message string is 128 characters.
        
        kwargs:
           time_offset (int): number of int msec that the time stamp of the message should be offset by. This can be used so that a message can be sent for a display change **BEFORE** or **AFTER** the aftual flip occurred (usually before), by sending the message, say 4 msec prior to when you know the next trace will occur, entering -4 into the offset field of the message, and then send it and calling flip() 4 msec before the retrace to ensure that the message time stampe and flip are both sent and schuled in advance. (4 msec is quite large buffer even on windows these days with morern hardware BTW)
        '''
        message=args[0]
        
        time_offset=0
        if time_offset in kwargs:
            time_offset=kwargs['time_offset']
            
        return RTN_CODES.ET_NOT_IMPLEMENTED
        
    def createRecordingFile(self, *args,**kwargs):
        '''
        createRecordingFile instructs the eye tracker to open a new file on the eye tracker computer to save data collected to
        during the recording. If recording is started and stopped multiple times while a single recording file is open, each 
        start/stop recording pair will be represented within the single file. A recording file is closed by calling
        closeRecordingFile(). Normally you would open a rtecoring file at the start of an experimental session and close it
        at the end of the experiment; starting and stopping recording of eye data between trials of the experiment.
        
        kwargs:
           fileName (str): Name of the recording file to save on the eye tracker. This does *not* include the path to the file. Some eye trackers have limitations to the length of their file name, so please refer to the specific implemtations documenation for any caviates.
           path (str): This optional parameter can be used to specify the path to the recording file that should be saved. The path must already exist. If this paramemter is not specified, then the defualt file location is used. 
        '''
        fileName=None
        if fileName in kwargs:
            fileName= kwargs['fileName']
        else:
            return ('EYETRACKER_ERROR','EyeTracker.createRecordingFile','fileName must be provided as a kwarg')
        
        return RTN_CODES.ET_NOT_IMPLEMENTED
        
    def closeRecordingFile(self,*args,**kwargs):
        '''
        closeRecordingFile is used to close the currently open file that is being used to save data from the eye track to the eye tracker computer. 
        Once a file has been closed, getFile(localFileName,fileToTransfer) can be used to transfer the file from the eye tracker computer to the 
        experiment computer at the end of the experiment session.

        kwargs:
           fileName (str): Name of the recording file to save on the eye tracker. This does *not* include the path to the file. Some eye trackers have limitations to the length of their file name, so please refer to the specific implemtations documenation for any caviates.
           path (str): This optional parameter can be used to specify the path to the recording file that should be saved. The path must already exist. If this paramemter is not specified, then the defualt file location is used. 
        '''
        return RTN_CODES.ET_NOT_IMPLEMENTED

    
    def getFile(self,*args,**kwargs):
        '''
        getFile is used to transfer the file from the eye tracker computer to the experiment computer at the end of the experiment session.

        kwargs:
           localFileName (str): Name of the recording file to experiment computer.
           fileToTransfer (str): Name of the recording file to transfer from the eye tracker.
        '''
        
        fileToTransfer=None
        if fileToTransfer in kwargs:
            fileToTransfer=kwargs['fileToTransfer']
        
        localFileName=None
        if localFileName in kwargs:
            localFileName=kwargs['localFileName']
        
        return RTN_CODES.ET_NOT_IMPLEMENTED 

    
    def runSetupProcedure(self, *args ,**kwargs):
        '''
        runSetupProcedure passes the graphics environment over to the eye tracker interface so that it can perform such things
        as camera setup, calibration, etc. This is a blocking call that will not return until the setup procedure is done; at which time
        the graphics environment can be taken back over by psychopy.  See the EyeTrackerSetupGraphics class for more information.
        
        The graphicsContext arguement should likely be the psychopy full screen window instance that has been created 
        for the experiment.
        '''
        graphicsContext=None
        if len(args)>0:
            graphicsContext=args[0]
        else:
            return ['EYETRACKER_ERROR','runSetupProcedure requires graphicsContext==args[0]']
            
        if self._setupGraphics is None:
            self._setupGraphics=EyeTrackerSetupGraphics(graphicsContext=graphicsContext,**kwargs)
        r=self._setupGraphics.run()
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def stopSetupProcedure(self):
        '''
        stopSetupProcedure allows a user to cancel the ongoing eye tracker setup procedure. Given runSetupProcedure is a blocking
        call, the only way this will happen is if the user has another thread that makes the call, perhaps a watch dog type thread.
        So in practice, calling this method is not very likely I do not think.
        '''
        result=None
        if self._setupGraphics is not None:
            result = self._setupGraphics.stop()
        return RTN_CODES.ET_NOT_IMPLEMENTED
                
    def setRecordingState(self,*args,**kwargs):
        '''
        setRecordingState is used to start or stop the recording of data from the eye tracking device. Use sendCommand() set the necessary information 
        for your eye tracker to enable what data you would like saved, send over to the experiment computer during recording, etc.
        
        args:
           recording (bool): if True, the eye tracker should start recordng data.; false = stop recording data.
        '''
        if len(args)==0:
            return ('EYETRACKER_ERROR','EyeTracker.setRecordingState','recording(bool) must be provided as a args[0]')
        enable=args[0]
        
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def isRecordingEnabled(self,*args,**kwargs):
       '''
       isRecordingEnabled returns the recording state from the eye tracking device.
       True == the device is recording data
       False == Recording is not occurring
       '''
       return RTN_CODES.ET_NOT_IMPLEMENTED 
     
    def getDataFilterLevel(self,*args,**kwargs):
        '''
        getDataFilterLevel returns the numerical code the current device side filter level 
        set for the specific data_stream. 
        
        Currently, filter levels 0 (meaning no filter) through 
        5 (highest filter level) can be specified via the pyEyeTrackerInterface.
        They are defined in ET_FILTERS.
        
        data_streams specifies what output the filter is being applied to by the device. The
        currently defined output streams are defined in DATA_STREAMS and are
        ALL,FILE,NET,SERIAL,ANALOG. ALL indicates that the filter level for all available output streams should be
        provided, in which case a dictionary of stream keys, filter level values should be returned.
        
        If an ET device supports setting one filter level for all available output streams, it can simply return
        (ALL, filter_level).
        
        If a stream type that is not supported by the device for individual filtering is specified, 
        an error should be generated.
        '''
        data_stream=DATA_STREAMS.ALL
        if 'data_stream' in kwargs:
            data_stream=kwargs['data_stream']
        elif len(args)>0:
            data_stream=args[0]
        
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def setDataFilterLevel(self,*args,**kwargs):
        '''
        setDataFilteringLevel sets the code for current ET device side filter level 
        for the specific data_stream. 
        
        Currently, filter levels OFF (meaning no filter) through 
        LEVEL_5 (highest filter level) can be specified via the pyEyeTrackerInterface.
        They are defined in DATA_FILTER Enum.
        
        data_streams specifies what output the filter is being applied to by the device. The
        currently defined output streams are defined in DATA_STREAMS, and are
        ALL,FILE,NET,SERIAL,ANALOG. ALL indicates that the filter level should be applied to all 
        available output streams,
        
        If an ET device supports setting one filter level for all available output streams, 
        then setting using filter_level only should be done.
        
        If a stream type that is not supported by the device for individual filtering is specified, 
        an error should be generated.
        '''
        if len(args)==0:
            return ['EYETRACKER_ERROR',"EyeTracker.setDataFilterLevel", "level = args[0], but no args provided")
        level=args[0]
        
        # example code below......
        supportedLevels=(DATA_FILTER.OFF,DATA_FILTER.LEVEL_1,DATA_FILTER.LEVEL_2)
        if level not in supportedLevels:
            return ['EYETRACKER_ERROR',"EyeTracker.setDataFilterLevel", "Invalid level value provided; must be one of (DATA_FILTER.OFF,DATA_FILTER.LEVEL_1,DATA_FILTER.LEVEL_2)")
        
        data_stream=DATA_FILTER.ALL
        if data_stream in kwargs:
            data_stream=kwargs['data_stream']
        supportedFilterStreams=(DATA_STREAMS.ALL,DATA_STREAMS.NET,DATA_STREAMS.ANALOG)
        if data_stream not in supportedFilterStreams:
            return ['EYETRACKER_ERROR',"EyeTracker.setDataFilterLevel", "Invalid data_stream value provided; must be one of (DATA_STREAMS.ALL,DATA_STREAMS.NET,DATA_STREAMS.ANALOG)")
        
        lindex = supportedLevels.index(level)
        
        return RTN_CODES.ET_NOT_IMPLEMENTED
        
    def getLatestSample(self, *args, **kwargs):
        '''
        Returns the latest sample retieved from the eye tracker device.
        '''
        return RTN_CODES.ET_NOT_IMPLEMENTED #return self._latestSample
    
    def drawToGazeOverlayScreen(self,*args,**kwargs):
        '''
        drawToGazeOverlayScreen provides a generic interface for ET devices that support
        having graphics drawn to the Host / Control computer gaze overlay area, or other similar
        graphics area functionality.
        
        The method should return the appropriate return code if successful or if the command failed,
        or if it is unsupported.
        
        There is no set list of values for any of the arguements for this command, so please refer to the
        ET imlpementation notes for your device for details. Hypothetical examples may be:
        '''
        drawingcommand=None
        if len(args)==0:
            return ('EYETRACKER_ERROR','drawToGazeOverlayScreen','args must have length > 0: drawingcommand = args[0]')
        else:
            drawingcommand=args[0]
            
        return RTN_CODES.ET_NOT_IMPLEMENTED    

    def getDigitalPortState(self, *args, **kwargs):
        '''
        getDigitalPortState returns the current value of the specified digital port on the ET computer. 
        This can be used to read the parallel port or idigial lines on the ET host PC if the ET has such functionality.
        
        args:
            port = the address to read from on the host PC. Consult your ET device documentation for appropriate values.
        '''
        if len(args)==0:
            return ('EYETRACKER_ERROR','getDigitalPortState','port=args[0] is required.')
        port = int(args[0])    
        return RTN_CODES.ET_NOT_IMPLEMENTED
         
    def setDigitalPortState(self, *args, **kwargs):
        '''
        setDigitalPortState sets the value of the specified digital port on the ET computer. 
        This can be used to write to the parallel port or idigial lines on the ET Host / Operator PC if the ET
        has such functionality.
        
        args:
            port = the address to write to on the host PC. Consult your ET device documentation for appropriate values.
            value = value to assign to port
        '''
        if len(args)<2:
            return ('EYETRACKER_ERROR','setDigitalPortState','port=args[0] and value=args[1] are required.')        
        port = int(args[0])    
        value = int(args[1])
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _poll(self):
        '''
        For use in systems where a polling model is used to check for new events and samples.
        If your eye tracker supports an event based call-back approach, use _handleEvent(...) instead 
        of _poll and remove the periodic timer from the ioHub_config.yaml file settings.
        '''
        currentTime=int(Computer.currentUsec())
        currentHostTime = self.trackerTime()
        ioHub_time_offset= currentTime-currentHostTime
         
        #get native events queued up
        while 1:    
            # get each native device event (this will be eye tracker specific)
            #
            # ....
            
            # determine the event type and map it to one of the ioHub eye tracker event types
            # found in ioHub.devices.eyeTrackerInterface.eye_events.py
            #
            # ......
            
            # put the ioHub eye tracker Device event in devices buffer for pickup by the ioHub.
            self.I_eventBuffer.append(ioHubEvent)

        EyeTracker.lastPollTime=currentTime
    
    def _handleEvent(self,*args,**kwargs):
        '''
        _handleEvent is used by devices that signal new events by using an event driven
        callback approach. 
        One args is required, the device event to be handled, "event"
        '''
        if len(args) > 0:
            event=args[0]
            
        currentTime=int(Computer.currentUsec())
        confidenceInterval=currentTime-self.lastCallbackTime
        
        # do any manipulation to the native event object here before putting it in the devices
        # circular buffer. Remember to keep work done in the callback to a minimum. For example,
        # the conversion to a native ioHub event is done in the getIOHubEventObject(event,device_instance_code)
        # method, so does not need to be done here.
        #
        # ......
        #
        
        EyeTracker.lastCallbackTime=currentTime
        
        # append the native event to the deque as a tuple of (current_time, event)
        # This can be unpacked in the getIOHubEventObject and the current_time 
        # used as the logged_time field of the ioHub DeviceEvent object.
        #
        self.I_eventBuffer.append((currentTime,event))
        pass
    
    @staticmethod    
    def getIOHubEventObject(*args,**kwargs):
        '''
        getIOHubEventObject is used to convert a devices events from their 'native' format
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
        
        # CASE 1: Polling is being used to get events:
        #
        if len(args)==2:
            event=args[0]
            device_instance_code=args[1]
            
        return event # already an EyeTracker Event    
        
        #
        # CASE 2: Callback is used to register events
        # if len(args)==2:
        #    logged_time,event=args[0]
        #    device_instance_code=args[1]
        #
        # Convert the native event type to the appropriate DeviceEvenet type for an EyeTracker.
        # See iohub.devices.eyeTrackerInterface.eye_events.py for the list of intended eye tracker 
        # event types (includes Samples).
        #
        # ......
        #
        #
        # return event # Return the ioHub EyeTracker event class instance.    
        
        

    def _eyeTrackerToDisplayCoords(self,*args,**kwargs):
        '''
        For eye tracker that have a static or fixed type internal mapping, 
        this method is used to convert from eye tracker units to display units.
        Default implementation is to just pass the data through untouched.
        '''
        if len(args<2):
            return ['EYETRACKER_ERROR','_eyeTrackerToDisplayCoords requires two args gaze_x=args[0], gaze_y=args[1]']
        gaze_x=args[0]
        gaze_y=args[1]
        
        # do mapping if necessary
        # default is no mapping 
        display_x=gaze_x
        display_y=gaze_y
        
        return display_x,display_y
        
        
    
    def _displayToEyeTrackerCoords(self,*args,**kwargs):
        '''
        For eye tracker that have a static or fixed type internal mapping, 
        this method is used to convert from display units to eye tracker units.
        Default implementation is to just pass the data through untouched.
        '''
        if len(args<2):
            return ['EYETRACKER_ERROR','_displayToEyeTrackerCoords requires two args display_x=args[0], display_y=args[1]']
        display_x=args[0]
        display_y=args[1]
        
        # do mapping if necessary
        # default is no mapping 
        gaze_x=display_x
        gaze_y=display_y
        
        return gaze_x,gaze_y
    
    def __del__(self):
        """
        Do any final cleanup of the eye tracker before the object is destroyed. Users should not call or change this method. It is for implemetaion by interface creators and is autoatically called when an object is destroyed by the interpreter.
        """
        EyeTracker._INSTANCE=None
        
 
class EyeTrackerSetupGraphics(object):
    '''
    EyeTrackerUserSetupGraphics provides a minimalistic standard 'public' interface
    that can be used for taking control of the experiment runtime graphics environment
    and keyboard / mouse by the eye tracker interface during 'black box' modes such as
    camera setup, calibration, validation, etc. 

    Developers of eye tracker interfaces for CETI can extend this class and implement 
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
    def __init__(self,graphicsContext,**kwargs):
        '''
        The EyeTrackerSetupGraphics instance is created the first time eyetracker.runSetupProcedure(graphicsContext)
        is called. The class instance is then reused in future calls. 
        graphicsContext object type is dependent on the graphics environment being used.
        Since psychopy normalizes everything in this regard to psychopy.visual.Window (regardless of
        whether pyglet or pygame backend is being used), then likely graphicsContext should be the instance of
        Window that has been created for your psychopy experiment. For an eye tracking experiment
        this would normally be a single 'full screen' window.
        '''
        self.graphicsContext=graphicsContext
        
    def run(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics.run is not implemented."
        return _handleDefaultState(*args,**kwargs)   

    def _handleDefaultState(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleDefaultState is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def _handleCameraSetupState(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleCameraSetupState is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def _handleParticipantSetupState(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleParticipantSetupState is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCalibrateState(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleCalibrateState is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleValidateState(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleValidateState is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleDCState(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleDCState is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCM_A_State(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleCM_A_State is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCM_B_State(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleCM_B_State is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCM_C_State(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleCM_C_State is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCM_D_State(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleCM_D_State is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCM_E_State(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleCM_E_State is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCM_F_State(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleCM_F_State is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def stop(self, returnMessage):
        print "EyeTrackerSetupGraphics.stop is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def getKeyboardMouseEvents(self):
        print "EyeTrackerSetupGraphics.getKeyboardMouseEvents is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
class EyeTrackerVendorExtension(object):
    '''
    EyeTrackerVendorExtension is the base class used to add custom functionality to the pyEyeTracker
    module when the standard pyEyeTracker functionality set can not be used to meet the requirements
    of the specific eye trackers needs. This should be used AS A LAST RESORT to add the necessary 
    functionality for any eye tracker. If you believe that certain functionality can not be met with 
    the current pyEyeTracker core API, please first contact the pyEyeTracker development team and discuss
    your requirements and needs. It may a) be possible to achieve what you need already, or b) be the
    case that your requirement is agreed to be a use case that should be added to the core pyEyeTracker 
    fucntionality instead of being added via an EyeTrackerVendorExtension. If either of these two situations
    are the case, the development team will put your requirements on the roadmap for the pyEyeTracker development
    and you or someone else are welcome to submit a patch for review containing the added functionality to the
    base pyEyeTracker code.
    '''
    
    def __init__(self):
        pass
