"""
ioHub
.. file: ioHub/devices/eyeTrackerInterface/InterfaceClasses.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

import numpy as N
import ioHub
from ioHub.devices import Device, Computer, EventConstants
from ioHub.devices.eyeTrackerInterface import RTN_CODES,DATA_TYPES,\
                                          ET_MODES,CALIBRATION_TYPES,CALIBRATION_MODES,DATA_STREAMS,\
                                          DATA_FILTER,USER_SETUP_STATES

#noinspection PyUnusedLocal,PyTypeChecker
class EyeTrackerInterface(Device):
    """
    The EyeTrackerInterface class is the main class for the pyEyeTrackerInterface module,
    containing the majority of the eye tracker functionality commonly needed
    for a range of experiments. With the integration of the pyEyeTrackerInterface into the ioHub module,
    the EyeTrackerInterface is the API for the ioHub's Eye Tracker device, making it consistant with the other
    supported ioHub Device Types.

    The EyeTrackerInterface class is extended by a particular Eye Tracking system's implementation by creating
    a subclass of the EyeTrackerInterface within a directory in the
    ioHub/devices/eyeTrackerInterface/HW module path. It is these sub classes of the EyeTrackerInterface
    that are used to define which version of the EyeTrackerInterface is to be used for a given experiment,
    based on which eye tracker you plan on using the EyeTrackerInterface with.

    For a list of current and in development Eye Tracker Implementations, please see the Eye Tracker
    Implementations section of this page.

    For users of the pyEyeTrackerInterface, the eye tracker device is no different than any other
    device in the ioHub, other than the device API is larger, reflecting the fact that eye trackers are in
    general somewhat more complicated than a keyboard or mouse for example.

    For implementers of pyEyeTrackerInterface, this means that the pyEyeTrackerInterface implementation
    you write is running in the ioHub Process, and communication between the PsychoPy Experiment Process and the
    Eye Tracker Implementation is handled via the ioHub.

    Not every eye tracker implementation of the pyEyeTrackerInterface will support all of the specifications
    functionality. This is to be expected and pyEyeTrackerInterface was designed with this in mind.
    When a specific implementation does not support a given method, if that method is called,
    a default *not supported* behaviour is built into the base implementation.

    On the other hand, some eye trackers offer very specialized functionality that
    is not as common across the eye tracking field, or functionality that is just currently missing from the
    pyEyeTrackerInterface, so is not part of the pyEyeTrackerInterface core yet. ;) In these cases,
    the specific eye tracker implementation can expose the non core pyEyeTrackerInterface
    functionality for their device by adding extra command types to the
    sendCommand method of the API, or as a last resort, via the *EyeTracker.EXT* attribute of the class.

    ### Note:

    > Only **one** instance of EyeTracker can be created within an experiment. Attempting to create > 1
    instance will raise an exception. To get the current instance of the EyeTracker you can call the
    class method EyeTracker.getInstance(); this is useful as it saves needing to pass an eyeTracker
    instance variable around your code.

    Methods are broken down into several categories within the EyeTracker class:

    * Eye Tracker Initialization / State Setting
    * Ability to Define the Graphics Layer for the Eye Tracker to Use During Calibration / System Setup
    * Starting and Stopping of Data Recording
    * Sending Synchronization messages to the Eye Tracker
    * Accessing the Eye Tracker Timebase
    * Accessing Eye Tracker Data During Recording
    * Synchronizing the ioHub time base with the Eye Tracker time base, so Eye Tracker events
    can be provided with local time stamps when that is appropriate.
    * Experiment Flow Generics
    """
    
    #: Used by pyEyeTrackerInterface implentations to store relationships between an eye 
    #: trackers command names supported for pyEyeTrackerInterface sendCommand method and  
    #: a private python function to call for that command. This allows an implemetation 
    #: of the interface to expose functions that are not in the core pyEyeTrackerInterface spec 
    #: without have to use the EXT extension class.
    _COMMAND_TO_FUNCTION={}

    #: Holds the reference to the current instance of the EyeTracker object
    #: in use and ensures only one is created.
    _INSTANCE=None

    # IF Vendor specific extensioin of API must be done,
    # create an extension of EyeTrackerVendorExtension class and add an instance of it here.
    EXT=None

    # hold last received ioHub eye sample (in ordered array format) from tracker.
    _latestSample=RTN_CODES.ET_NOT_IMPLEMENTED

    # holds the last gaze position read from the eye tracker. If binocular recording is
    # being performed, this is an average of the left and right gaze position x,y fields.
    _latestGazePosition=0,0

    # stores the eye tracker device related configuration settings from the iohub .yaml config file
    _eyeTrackerConfig=None

    # stores the calibration display device related configuration settings from the iohub .yaml config file
    _displaySettings=None
    
    #  >>>> Class attributes used by parent Device class

    # Time to subtract from future device time reads.
    # Should be set in Device init before any calls to getTime()
    DEVICE_START_TIME = 0.0

    # the multiplier needed to convert device times to sec.msec times.
    DEVICE_TIMEBASE_TO_SEC=1.0

    CATEGORY_LABEL = 'EYE_TRACKER'
    DEVICE_LABEL = 'EYE_TRACKER_DEVICE'

    # last sec.msec time the poll method was called (if in use)
    _lastPollTime=0.0

    # last sec.msec time the event callback method was called (if in use)
    lastCallbackTime=0.0
    

    __slots__=[]
    def __init__(self,*args,**kwargs):
        """
        EyeTracker class. This class is to be extended by each eye tracker specific implementation
        of the pyEyeTrackerInterface.

        Please review the pyEyeTrackerInterface documentation page for the specific eye tracker model that you
        are using to get the appropriate class path for that eye tracker; for example,
        if you are using an interface that supports eye trackers developed by EyeTrackingCompanyET, you
        would set the eye tracking class in the eye tracker device settings of the experiments iohub_config.yaml to:

           class: eyeTrackerInterface.HW.EyeTrackingCompanyET.EyeTracker

        where hub is the instance of the ioHubConnection class that has been created for your experiment.
        """
        if self.__class__._INSTANCE is not None:
            raise ioHub.devices.ioDeviceError(self.__class__.__name__,"EyeTracker object has already been created; "
                                                                      "only one instance can exist. Delete existing "
                                                                      "instance before recreating EyeTracker object.")

        if 'os_device_code' not in kwargs:
            kwargs['name']='eyetracker'
        if 'os_device_code' not in kwargs:
            kwargs['os_device_code']='OS_DEV_CODE_NOT_SET'
        if 'category_id' not in kwargs:
            kwargs['category_id']=EventConstants.DEVICE_CATERGORIES['EYE_TRACKER']
        if 'type_id' not in kwargs:
            kwargs['type_id']=EventConstants.DEVICE_TYPES['EYE_TRACKER_DEVICE'],
        if 'device_class' not in kwargs:
            kwargs['device_class']=self.__class__.__name__
        if 'max_event_buffer_length' not in kwargs:
            kwargs['max_event_buffer_length']=1024
        if 'auto_report_events' not in kwargs:
            kwargs['auto_report_events']=True

        Device.__init__(self,*args,**kwargs)
        
        self.__class__._INSTANCE=self

        self.__class__.DEVICE_START_TIME=0.0
        
        #runtimeSettings=self._eyeTrackerConfig['runtime_settings']
        #self.__class__._displaySettings = self._eyeTrackerConfig['display_settings']



    def experimentStartDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that is used to perform a set of
        eye tracker default code associated with the start of an experiment.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
 
    def blockStartDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the start of an experiment block.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def trialStartDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the start of an experiment trial.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
         
    def trialEndDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the end of an experiment trial.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
         
    def blockEndDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the end of an experiment block.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def experimentEndDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the end of an experiment session.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
        
    def trackerTime(self):
        """
        Current eye tracker time (timebase is eye tracker dependent)
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
   
    def trackerSec(self):
        """
        Current eye tracker time, normalized to sec.msec.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
        
   
    def setConnectionState(self,*args,**kwargs):
        """
        setConnectionState is used to connect ( setConnectionState(True) ) or disable ( setConnectionState(False) )
        the connection of the pyEyeTrackerInterface to the eyetracker.

        args:
            enabled (bool): True = enable the connection, False = disable the connection.
        kwargs (dict): any eye tracker specific parameters that should be passed.
        """
        enabled=None
        if len(args)>0:
            enabled=args[0]
        if enabled is True or enabled is False:
            return RTN_CODES.ET_NOT_IMPLEMENTED
        else:
            return ['EYETRACKER_ERROR','Invalid arguement type','setConnectionState','enabled',enabled,args]
            
    def isConnected(self):
        """
        isConnected returns whether the pyEyeTrackerInterface is connected to the
        eye tracker (returns True) or not (returns False)
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
            
    def sendCommand(self, *args, **kwargs):
        """
        sendCommand sends a text command and text command value to the eye tracker.
        Depending on the command and on the eye trackers implementation, when a command is send,
        the eye tracker may or may not response indicating the status of the command. If the
        command is not going to return a response from the eye tracker, the method will return
        RTN_CODES.ET_RESULT_UNKNOWN. Please see the specific eye tracker implementation you are
        working with for a list of supported command's and value's.

        Args:

            command (str): string command to send to the eye tracker. See the specific eye tracker
            documentation for pyEyeTrackerInterface for a list of valid commands.
            value (str): the string form of the value of the command to send.

        kwargs:
            wait (bool or callable) *NOT CURRENTLY SUPPORTED; FUNCTIONS AS ALWAYS == FALSE*: if bool, True = do
                not return from function until result of command if known (if it can be known);
                False = return immediately after sending the command, ignoring any possible return value.
                If wait is a callable, then wait should be a reference to the callback function you want
                called when the return value is available. If no return value is possible for the command,
                wait is ignored and RTN_CODES.ET_RESULT_UNKNOWN is returned immediately..

        Return: the result of the command call, or one of the ReturnCodes Constants
                ( ReturnCodes.ET_OK, ReturnCodes.ET_RESULT_UNKNOWN, ReturnCodes.ET_NOT_IMPLEMENTED )
        """
        command=None
        value=None

        if len(args)==1:
            command=args[0]
        elif len(args)==2:
            command=args[0]
            value=args[1]
        else:
            return 'EYETRACKER_ERROR','EyeTracker.sendCommand','requires args of length >0, command==args[0],value==args[1], \
                    optional kwarg of wait=True | False'

        wait=False
        if wait in kwargs:
            wait=kwargs['wait']
        
        return RTN_CODES.ET_NOT_IMPLEMENTED
        
    def sendMessage(self,*args,**kwargs):
        """
        sendMessage sends a text message to the eye tracker. Depending on the eye trackers implementation,
        when a message is send,
        the eye tracker may or may not response indicating the message was received. If the
        message is not going to receive a response from the eye tracker,
        the method will return RTN_CODES.ET_RESULT_UNKNOWN.
        Messages are generally used to send general text information you want saved with the eye data file
        but more importantly are often used to synchronize stimulus changes in the experiment with the eye
        data stream. This means that the sendMessage implementation needs to perform in real-time,
        with a delay of <1 msec from when a message is sent to when it is time stamped by the eye tracker,
        for it to be accurate in this regard.

        If this standard can not be met, the expected delay and message precision (variability) should be
        provided in the eye tracker's implementation notes for the pyEyeTrackerInterface.

        Args:
           message (str): string command to send to the eye tracker.
                          The default maximum length of a message string is 128 characters.

        kwargs:
           time_offset (int): number of int msec that the time stamp of the message should be offset by.
                              This can be used so that a message can be sent for a display change **BEFORE** or
                              **AFTER** the actual flip occurred (usually before), by sending the message,
                              say 4 msec prior to when you know the next trace will occur,
                              entering -4 into the offset field of the message,
                              and then send it and calling flip() 4 msec before the retrace to ensure
                              that the message time stamp and flip are both sent and scheduled in advance.
                               (4 msec is quite large buffer even on windows these days with modern hardware BTW)
        """
        message=args[0]
        
        time_offset=0
        if time_offset in kwargs:
            time_offset=kwargs['time_offset']
            
        return RTN_CODES.ET_NOT_IMPLEMENTED
        
    def createRecordingFile(self, *args,**kwargs):
        """
        createRecordingFile instructs the eye tracker to open a new file on the eye tracker computer to save data collected to
        during the recording. If recording is started and stopped multiple times while a single recording file is open, each
        start/stop recording pair will be represented within the single file. A recording file is closed by calling
        closeRecordingFile(). Normally you would open a rtecoring file at the start of an experimental session and close it
        at the end of the experiment; starting and stopping recording of eye data between trials of the experiment.

        kwargs:
           fileName (str): Name of the recording file to save on the eye tracker. This does *not* include the path
                           to the file. Some eye trackers have limitations to the length of their file name,
                           so please refer to the specific implemtations documenation for any caviates.
           path (str): This optional parameter can be used to specify the path to the recording file that
                       should be saved. The path must already exist. If this paramemter is not specified,
                       then the defualt file location is used.
        """
        fileName=None
        if fileName in kwargs:
            fileName= kwargs['fileName']
        else:
            return 'EYETRACKER_ERROR','EyeTracker.createRecordingFile','fileName must be provided as a kwarg'
        
        return RTN_CODES.ET_NOT_IMPLEMENTED
        
    def closeRecordingFile(self,*args,**kwargs):
        """
        closeRecordingFile is used to close the currently open file that is being used to save data from the eye track to the eye tracker computer.
        Once a file has been closed, getFile(localFileName,fileToTransfer) can be used to transfer the file from the eye tracker computer to the
        experiment computer at the end of the experiment session.

        kwargs:
           fileName (str): Name of the recording file to save on the eye tracker.
                           This does *not* include the path to the file. Some eye trackers have limitations
                           to the length of their file name, so please refer to the specific implemtations
                           documenation for any caviates.
           path (str): This optional parameter can be used to specify the path to the recording
                       file that should be saved. The path must already exist. If this paramemter
                       is not specified, then the defualt file location is used.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED

    
    def getFile(self,*args,**kwargs):
        """
        getFile is used to transfer the file from the eye tracker computer to the experiment
        computer at the end of the experiment session.

        kwargs:
           localFileName (str): Name of the recording file to experiment computer.
           fileToTransfer (str): Name of the recording file to transfer from the eye tracker.
        """
        
        fileToTransfer=None
        if fileToTransfer in kwargs:
            fileToTransfer=kwargs['fileToTransfer']
        
        localFileName=None
        if localFileName in kwargs:
            localFileName=kwargs['localFileName']
        
        return RTN_CODES.ET_NOT_IMPLEMENTED 

    
    def runSetupProcedure(self, *args ,**kwargs):
        """
        runSetupProcedure allows the eye tracker interface to perform such things as camera setup,
        calibration, etc. This is a blocking call that will not return until the setup procedure is done; at which time
        the graphics environment is given back to PsychoPy.

        Implementation details are 100% eye tracker specific.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED

                
    def setRecordingState(self,*args,**kwargs):
        """
        setRecordingState is used to start or stop the recording of data from the eye tracking device.
        Use sendCommand() set the necessary information for your eye tracker to enable what data you would like saved,
        sent over to the experiment computer during recording (if in a two computer setup), etc.

        args:
           recording (bool): if True, the eye tracker should start recordng data.; false = stop recording data.
        """
        if len(args)==0:
            return 'EYETRACKER_ERROR','EyeTracker.setRecordingState','recording(bool) must be provided as a args[0]'
        enable=args[0]
        
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def isRecordingEnabled(self,*args,**kwargs):
       """
       isRecordingEnabled returns the recording state from the eye tracking device.
       True == the device is recording data
       False == Recording is not occurring
       """
       return RTN_CODES.ET_NOT_IMPLEMENTED 
     
    def getDataFilterLevel(self,*args,**kwargs):
        """
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
        """
        data_stream=DATA_STREAMS.ALL
        if 'data_stream' in kwargs:
            data_stream=kwargs['data_stream']
        elif len(args)>0:
            data_stream=args[0]
        
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def setDataFilterLevel(self,*args,**kwargs):
        """
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
        """
        if len(args)==0:
            return ['EYETRACKER_ERROR',"EyeTracker.setDataFilterLevel", "level = args[0], but no args provided"]
        else:
            level=args[0]

            data_stream=DATA_FILTER.ALL
            if 'data_stream' in kwargs:
                data_stream=kwargs['data_stream']

            # example code below......
            supportedLevels=(DATA_FILTER.OFF,DATA_FILTER.LEVEL_1,DATA_FILTER.LEVEL_2)
            supportedFilterStreams=(DATA_STREAMS.ALL,DATA_STREAMS.NET,DATA_STREAMS.ANALOG)

            if level not in supportedLevels:
                return ['EYETRACKER_ERROR',"EyeTracker.setDataFilterLevel", "Invalid level value provided; must be one of (DATA_FILTER.OFF,DATA_FILTER.LEVEL_1,DATA_FILTER.LEVEL_2)"]

            if data_stream not in supportedFilterStreams:
                return ['EYETRACKER_ERROR',"EyeTracker.setDataFilterLevel", "Invalid data_stream value provided; must be one of (DATA_STREAMS.ALL,DATA_STREAMS.NET,DATA_STREAMS.ANALOG)"]

            lindex = supportedLevels.index(level)

            # handle based on filter level and filter type
            # ......

            return RTN_CODES.ET_NOT_IMPLEMENTED

    def getEyesToTrack(self,*args,**kwargs):
        """
        getEyesToTrack returns the eye(s) that the tracker is set to record.

        return:
           (int constant): EventConstants.LEFT | EventConstants.RIGHT | EventConstants.BOTH | EventConstants.NONE
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def setEyesToTrack(self,*args,**kwargs):
        """
        setEyesToTrack sets the eye(s) that the tracker is set to record.

        args:
             arg[0] = EventConstants.LEFT | EventConstants.RIGHT | EventConstants.BOTH
        return:
             (boolean) status of method success
        """
        if len(args)==0:
            return RTN_CODES.ET_ERROR
        eyes=args[0]
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def getSamplingRate(self,*args,**kwargs):
        """
        getSamplingRate returns the sampling rate (in Hz) that the tracker is set to record at.
                        For example, 30.0 or 60.0 or 250.0 or 1000.0 may be valid values assuming your
                        eye tracking hardware supports that sampling rate.

        return:
           (float): The sampling rate in Hz the eye tracker is set to record at.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def setSamplingRate(self,*args,**kwargs):
        """
        setSamplingRate sets the requested sampling rate (in Hz) that the tracker should sample at.
                        For example, 30.0 or 60.0 or 250.0 or 1000.0 may be valid values assuming your
                        eye tracking hardware supports that sampling rate.

        args:
            arg[0] (float): The sample rate you want to set the eye tracker to.
        return:
           (float): The sampling rate the eye tracker is actually now set to record at. This may not equal what you
                    requested.
        """
        if len(args)==0:
            return RTN_CODES.ET_ERROR
        srate=args[0]
        return RTN_CODES.ET_NOT_IMPLEMENTED


    def getLatestSample(self, *args, **kwargs):
        """
        Returns the latest sample retieved from the eye tracker device.

        Args: None

        Returns:
            EyeSample | BinocularEyeSample
        """
        return self._latestSample

    def getLatestGazePosition(self, *args, **kwargs):
        """
        Returns the latest eye gaze position retieved from the eye tracker device. This is retrieved
        from the last sample recieved from the device, reading the gaze_x, gaze_y fields. If binocular
        recording is being performed, the average position of both eyes is returned. If no samples have been
        received from the eye tracker, 0, 0 is returned.

        Args: None

        Returns:
            (tuple): (gaze_x,gaze_y)
        """
        return self._latestGazePosition

    def drawToHostApplicationWindow(self,*args,**kwargs):
        """
        drawToHostApplicationWindow provides a generic interface for ET devices that support
        having graphics drawn to the Host / Control Computer / Application gaze overlay area,
        or other similar graphics area functionality.

        The method should return the appropriate return code if successful or if the command failed,
        or if it is unsupported.

        There is no set list of values for any of the arguments for this command, so please refer to the
        ET pyEyeTrackerInterface implementation notes for your device for details.
        """
        drawingcommand=None
        if len(args)==0:
            return 'EYETRACKER_ERROR','drawToGazeOverlayScreen','args must have length > 0: drawingcommand = args[0]'
        else:
            drawingcommand=args[0]
            
        return RTN_CODES.ET_NOT_IMPLEMENTED    

    def getDigitalPortState(self, *args, **kwargs):
        """
        getDigitalPortState returns the current value of the specified digital port on the ET computer.
        This can be used to read the parallel port or idigial lines on the ET host PC if the ET has
        such functionality.

        args:
            port = the address to read from on the host PC. Consult your ET device documentation for
                   appropriate values.
        """
        if len(args)==0:
            return 'EYETRACKER_ERROR','getDigitalPortState','port=args[0] is required.'
        port = int(args[0])    
        return RTN_CODES.ET_NOT_IMPLEMENTED
         
    def setDigitalPortState(self, *args, **kwargs):
        """
        setDigitalPortState sets the value of the specified digital port on the ET computer.
        This can be used to write to the parallel port or other digial lines on the ET Host / Operator PC if the ET
        has such functionality.

        args:
            port = the address to write to on the host PC. Consult your ET device documentation for appropriate values.
            value = value to assign to port
        """
        if len(args)<2:
            return 'EYETRACKER_ERROR','setDigitalPortState','port=args[0] and value=args[1] are required.'
        port = int(args[0])    
        value = int(args[1])
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _poll(self):
        """
        For use in systems where a polling model is used to check for new events and samples.
        If your eye tracker supports an event based call-back approach,  _handleNativeEvent(...) is used instead
        of _poll.

        If using _poll, be sure to specify the periodic timer interval in the ioHub_config.yaml
        file settings for the eye tracker.

        Users of the ioHub never need to call _poll, it is handled automaitically.
        """
        loggedTime=Computer.currentSec()
        currentHostTime = self.trackerTime()
        ioHub_time_offset= loggedTime-currentHostTime

        #get native events queued up
        noMoreDeviceEvents=True
        while 1:    
            # get each native device event (this will be eye tracker specific)
            #
            # ....
            
            # determine the event type and map it to one of the ioHub eye tracker event types
            # found in ioHub.devices.eyeTrackerInterface.eye_events.py
            #
            # ......

            # put the ioHub eye tracker event IN ORDERED LIST FORM in devices buffer for pickup by the ioHub.
            ioHubEvent = list()
            self._addNativeEventToBuffer(ioHubEvent)

            if noMoreDeviceEvents:
                break

        self.__class__._lastPollTime=loggedTime
        if 1:
            return 'EYETRACKER_ERROR','_poll','Default Poll Logic being Used. This must be implemented on a per eye tracker basis.'

    def _handleNativeEvent(self,*args,**kwargs):
        """
        _handleEvent is used by devices that signal new events by using an event driven
        callback approach.

        One args is required, the native device event to be handled, "event"

        If using _handleNativeEvent, be sure to remove the periodic timer interval in the ioHub_config.yaml
        file settings for the eye tracker.

        Users of the ioHub never need to call _poll, it is handled automatically.
        """
        loggedTime=Computer.currentSec()

        event=None
        if len(args) > 0:
            event=args[0]
        
        # do any manipulation to the native event object here before putting it in the devices
        # circular buffer. Remember to keep work done in the callback to a minimum. For example,
        # the conversion to a native ioHub event is done in the _getIOHubEventObject(event)
        # method, so does not need to be done here.
        #
        # ......
        #

        if 1:
            return 'EYETRACKER_ERROR','_handleNativeEvent','Default _handleNativeEvent callback Logic being Used. This must be implemented on a per eye tracker basis.'

        self.__class__.lastCallbackTime=loggedTime
        
        # append the native event to the deque as a tuple of (loggedTime, event)
        # This can be unpacked in the _getIOHubEventObject and the current_time 
        # used as the logged_time field of the ioHub DeviceEvent object.
        #
        self._addNativeEventToBuffer((loggedTime,event))
    
    @staticmethod    
    def _getIOHubEventObject(*args,**kwargs):
        """
        _getIOHubEventObject is used to convert a devices event from their 'native' format
        to the ioHub DeviceEvent object representation for the relevent event type.

        *If a polling model is used to retrieve events, this conversion is actually done in
        the polling method itself, so the passed in event here would just be returned back without change.

        *If an event driven callback method is used, then this method should be employed to do
        the conversion between object types, so a minimum of work is done in the callback itself.

        This method is not used by end users.

        The method expects args:
            (logged_time,event)=args[0] (when the callback is used to register device events)
            event = args[0] (when polling is used to get device events)
        """
        
        # CASE 1: Polling is being used to get events:
        #
        #event=None
        #if len(args)==1:
        #    event=args[0]
        #return event

        # OR

        #
        # CASE 2: Callback is used to register events
        # if len(args)==2:
        #    logged_time,event=args[0]
        #
        # Convert the native event type to the appropriate DeviceEvent type for an EyeTracker,
        # IN ORDERED LIST FORM.
        #
        # See iohub.devices.eyeTrackerInterface.eye_events.py for the list of intended eye tracker 
        # event types (includes Samples).
        #
        # ......
        #
        #
        # return eventAsOrderedList # Return the ioHub EyeTracker event as ordered list.

        return 'EYETRACKER_ERROR','_getIOHubEventObject','Default _getIOHubEventObject callback Logic being Used. This must be implemented on a per eye tracker basis.'


    def _eyeTrackerToDisplayCoords(self,*args,**kwargs):
        """
        For eye tracker that have a static or fixed type internal mapping,
        this method is used to convert from eye tracker units to display units.
        Default implementation is to just pass the data through untouched.

        This method is not used by end users.
        """
        if len(args) < 2 :
            return ['EYETRACKER_ERROR','_eyeTrackerToDisplayCoords requires two args gaze_x=args[0], gaze_y=args[1]']
        gaze_x=args[0]
        gaze_y=args[1]
        
        # do mapping if necessary
        # default is no mapping 
        display_x=gaze_x
        display_y=gaze_y

        return display_x, display_y

        
    
    def _displayToEyeTrackerCoords(self,*args,**kwargs):
        """
        For eye tracker that have a static or fixed type internal mapping,
        this method is used to convert from display units to eye tracker units.
        Default implementation is to just pass the data through untouched.

        This method is not used by end users.

        """
        if len(args) < 2:
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
        Do any final cleanup of the eye tracker before the object is destroyed.
        Users should not call or change this method. It is for implementation by interface creators
        and is automatically called when an object is destroyed by the interpreter.
        """
        self.__class__._INSTANCE=None


class EyeTrackerVendorExtension(object):
    """
    EyeTrackerVendorExtension is the base class used to add custom functionality to the pyEyeTrackerInterface
    module when the standard pyEyeTrackerInterface functionality set can not be used to meet the requirements
    of the specific eye trackers needs. This should be used AS A LAST RESORT to add the necessary
    functionality for any eye tracker. If you believe that certain functionality can not be met with
    the current pyEyeTrackerInterface core API, please first contact the pyEyeTrackerInterface development
    team and discuss your requirements and needs. It may a) be possible to achieve what you need already, or b) be the
    case that your requirement is agreed to be a use case that should be added to the core pyEyeTracker
    fucntionality instead of being added via an EyeTrackerVendorExtension. If either of these two situations
    are the case, the development team will put your requirements on the roadmap for the pyEyeTrackerInterface
    development and you or someone else are welcome to submit a patch for review containing the added
    functionality to the base pyEyeTrackerInterface code.
    """
    
    def __init__(self):
        pass
