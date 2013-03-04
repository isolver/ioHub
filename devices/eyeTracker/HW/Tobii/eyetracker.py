"""
ioHub
pyEyeTracker Interface
.. file: ioHub/devices/eyeTracker/HW/Tobii/eyetracker.py

Copyright (C) 2012-2013 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: ??
.. fileauthor:: ??
"""

import numpy as np 
import ioHub
import ioHub.devices
from ioHub.constants import EventConstants, DeviceConstants, EyeTrackerConstants

from ioHub.devices import Computer
from ioHub.devices.eyeTracker import EyeTrackerDevice

try:
    from tobiiclasses  import *
    from tobiiCalibrationGraphics import TobiiPsychopyCalibrationGraphics
except:
    pass

class EyeTracker(EyeTrackerDevice):
    """EyeTracker class is the main class for the pyEyeTrackerInterface module,
    containing the majority of the eye tracker functionality commonly needed
    for a range of experiments.

    With the integration of the pyEyeTrackerInterface into the ioHub module, the EyeTracker
    device is a device along with the other currently supported ioHub devices; Keyboard, Mouse,
    and GamepPad, etc..

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

    #. Eye Tracker Initialization / State Setting
    #. Ability to Define the Graphics Layer for the Eye Tracker to Use During Calibration / System Setup
    #. Starting and Stopping of Data Recording
    #. Sending Synchronization messages to the Eye Tracker
    #. Accessing the Eye Tracker Timebase
    #. Accessing Eye Tracker Data During Recording
    #. Synchronizing the Local Experiment timebase with the Eye Tracker Timebase, so Eye Tracker events
       can be provided with local time stamps when that is appropriate.
    #. Experiment Flow Generics
    """

    # >>> Constants:

    # >>> Custom class attributes
    _tobii=None
    # <<<

    # >>> Overwritten class attributes
    DEVICE_TIMEBASE_TO_SEC=0.00001
    _COMMAND_TO_FUNCTION={}
    _INSTANCE=None #: Holds the reference to the current instance of the EyeTracker object in use and ensures only one is created.
    _latestSample=None # latest eye sample from tracker
    _latestGazePosition=0,0 # latest gaze position from eye sample. If binocular, average valid eye positions
    _displaySettings=None
    
    ALL_EVENT_CLASSES=[]

    DEVICE_TYPE_ID=DeviceConstants.EYE_TRACKER
    DEVICE_TYPE_STRING=DeviceConstants.getName(DeviceConstants.EYE_TRACKER)
    __slots__=[]
    # <<<

    def __init__(self, dconfig, *args,**kwargs):
        """
        EyeTracker class. This class is to be extended by each eye tracker specific implemetation
        of the pyEyeTrackerInterface.
        """
        
        if EyeTracker._INSTANCE is not None:
            raise ioHub.devices.ioDeviceError(EyeTracker._INSTANCE,'EyeTracker object has already been created;'
                                                                   ' only one instance can exist.\n Delete existing'
                                                                   ' instance before recreating EyeTracker object.')

        from .... import BinocularEyeSample

        EyeTracker.ALL_EVENT_CLASSES=[BinocularEyeSample,]

        self.monitor_event_types=EyeTracker.ALL_EVENT_CLASSES

        EyeTracker._ioServer=dconfig['_ioServer']

        # create Device level class setting dictionary and pass it Device constructor
        deviceSettings={
            'type_id':self.DEVICE_TYPE_ID,
            'device_class':EyeTracker.__name__,
            'name':dconfig.get('name','tracker'),
            'monitor_event_types':dconfig.get('monitor_event_types',EyeTracker.ALL_EVENT_CLASSES),
            'os_device_code':'OS_DEV_CODE_NOT_SET',
            'max_event_buffer_length':dconfig.get('event_buffer_length',1024)
            }
        EyeTrackerDevice.__init__(self,*args,**deviceSettings)

                            
        self._startupConfiguration=dconfig

        # set this instance as 'THE' instance of the eye tracker.
        EyeTracker._INSTANCE=self

        # >>>> Display / Calibration related information to use for config if possible
        EyeTracker._displaySettings = self._startupConfiguration['display_settings']
        # <<<<
        
        sampling_rate=None
        runtime_settings=self._startupConfiguration.get('runtime_settings',None)
        if runtime_settings:
            sampling_rate=runtime_settings.get('sampling_rate',None)
            
        tobii_model=self._startupConfiguration.get('model',None)
        serial_number=self._startupConfiguration.get('serialNumber',None)
        ioHub.print2err('Using model {0} and product id {1} when searching for Tobii systems.'.format(tobii_model,serial_number))
        
        
        EyeTracker._tobii=None
        try:
            EyeTracker._tobii=TobiiTracker(product_id=serial_number,model=tobii_model)
        except:
            pass
        
        if self._tobii and sampling_rate and sampling_rate in self._tobii.getAvailableSamplingRates():
            ioHub.print2err('Settings Tobii sampling rate to %f.'%sampling_rate)
            self._tobii.setSamplingRate(sampling_rate)
    
    def experimentStartDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the start of an experiment.
        """
        
        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
 
    def blockStartDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the start of an experiment block.
        """

        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED

    def trialStartDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the start of an experiment trial.
        """
    
        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
         
    def trialEndDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the end of an experiment trial.
        """

        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
         
    def blockEndDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the end of an experiment block.
        """

        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED

    def experimentEndDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the end of an experiment session.
        """

        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
        
    def trackerTime(self):
        """
        Current eye tracker time in native time base. The Tobii system uses a 
        usec timebase.
        """
        if self._tobii:
            return self._tobii.getCurrentEyeTrackerTime()
        return -1.0
        
    def trackerSec(self):
        """
        Current eye tracker time, normalized to sec.msec.
        """
        if self._tobii:
            return self._tobii.getCurrentEyeTrackerTime()*self.DEVICE_TIMEBASE_TO_SEC
        return -1.0

    def setConnectionState(self,*args,**kwargs):
        """
        setConnectionState is a no-op when using the Tobii system, as the 
        connection is established when the Tobii EyeTracker class is created, and remains
        active until the program ends, or a error occurs resulting in the loss
        of the tracker connection.
        """
        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
            
    def isConnected(self):
        """
        isConnected returns whether the Tobii is connected to the experiment PC
        and if the tracker state is valid. Returns True if the tracker can be 
        put into Record mode, etc and False if there is an error with the tracker
        or tracker connection with the experiment PC.
        """
        if self._tobii:
            return self._tobii.getTrackerDetails().get('status',False)=='OK'
        return False
            
    def sendCommand(self, *args, **kwargs):
        """
        The Tobii has several custom commands that can be sent to set or get
        information about the eye tracker that is specific to Tobii
        systems. Valid command tokens and associated possible valid command values
        are as follows:
        
        TO DO: complete based on these tracker object methods
            - getTrackerDetails
            - getName
            - setName
            - getHeadBox
            - setXSeriesPhysicalPlacement (no-op if tracker is not an X series system)
            - getEyeTrackerPhysicalPlacement
            - getAvailableExtensions
            - getEnabledExtensions
            - enableExtension
            - ....
            
        Commands always return their result at the end of the command call, if
        there is any result to return. Otherwise EyeTrackerConstants.EYETRACKER_OK
        is returned.
        """

        command=None

        if len(args)>0:
            command=args[0]
            args=args[1:]

        if 'waitForResponse' in kwargs:
            del kwargs['waitForResponse']

        if command in EyeTracker._COMMAND_TO_FUNCTION:
            EyeTracker._COMMAND_TO_FUNCTION[command](*args)
        else:
            ioHub.print2err('ERROR: Tobii command {0} not supported'.format(command))

    def sendMessage(self,*args,**kwargs):
        """
        Sending sync messages to the Tobii Eye Tracker is not supported. If 
        the ioDataStore functionality is enabled, you can send Message events
        from the experiment program and they will be saved with the online
        eye data that is collected. The accuracy of the time stamp for
        Experiment Message Events and Tobii eye data is < 1.0 msec, and the
        resolution of the ioHub time base is 1 usec on Windows.
        """
        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
        
    def runSetupProcedure(self, *args ,**kwargs):
        """
        runSetupProcedure passes the graphics environment over to the eye tracker interface so that it can perform such things
        as camera setup, calibration, etc. This is a blocking call that will not return until the setup procedure is done; at which time
        the graphics environment can be taken back over by psychopy.  See the EyeTrackerSetupGraphics class for more information.

        The graphicsContext argument should likely be the psychopy full screen window instance that has been created
        for the experiment.
        """
        try:
            # Optional kwargs that can be passed in to control built in calibration graphics and sound
            targetForegroundColor=kwargs.get('targetForegroundColor',None) # [r,g,b] of outer circle of targets
            targetBackgroundColor=kwargs.get('targetBackgroundColor',None) # [r,g,b] of inner circle of targets
            screenColor=kwargs.get('screenColor',None)                     # [r,g,b] of screen
            targetOuterDiameter=kwargs.get('targetOuterDiameter',None)     # diameter of outer target circle (in px)
            targetInnerDiameter=kwargs.get('targetInnerDiameter',None)     # diameter of inner target circle (in px)

            genv=TobiiPsychopyCalibrationGraphics(self)

            genv.runCalibration()
            genv.window.close()
            
            genv._unregisterEventMonitors() 
            genv.clearAllEventBuffers()
            
        except:
            ioHub.print2err("Error during runSetupProcedure")
            ioHub.printExceptionDetailsToStdErr()
        return True

    def enableEventReporting(self,enabled=True):
        EyeTrackerInterface.enableEventReporting(self,enabled)
        self.setRecordingState(enabled)

    def setRecordingState(self,*args,**kwargs):
        """
        setRecordingState is used to start or stop the recording of data from 
        the eye tracking device.
        
        args:
           recording (bool): if True, the eye tracker will start recordng available
              eye data and sending it to the experiment program if data streaming
              was enabled for the device. If recording == False, then the eye
              tracker stops recording eye data and streaming it to the experiment.
              
        If the eye tracker is already recording, and setRecordingState(True) is
        called, the eye tracker will simple continue recording and the method call
        is a no-op. Likewise if the system has already stopped recording and 
        setRecordingState(False) is called again.
        """
        if len(args)==0:
            return ('EYETRACKER_ERROR','EyeTracker.setRecordingState','recording(bool) must be provided as a args[0]')
        enable=args[0]
        
        if self._tobii and enable is True and not self.isRecordingEnabled():
            return self._tobii.startTracking(self._handleNativeEvent)
        
        elif self._tobii and enable is False and self.isRecordingEnabled():
            return self._tobii.stopTracking()
            
        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
    def isRecordingEnabled(self,*args,**kwargs):
        """
        isRecordingEnabled returns the recording state from the eye tracking device.
        True == the device is recording data
        False == Recording is not occurring
        """
        if self._tobii:      
            return self._tobii._isRecording
        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED

    def getEyesToTrack(self,*args,**kwargs):
        """
        Tobii eye trackers always record in binocular mode. If the eyes are blinking,
        or one or both are out of the devices tracking range, then missing
        data is returned for the missing eyes. (Fields are set to MISSING DATA)
        """
        return EyeTrackerConstants.BINOCULAR

    def setEyesToTrack(self,*args,**kwargs):
        """
        Tobii eye trackers always record in binocular mode, so this is a no-op
        method for the Tobii implementation.
        """
        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED

    def getSamplingRate(self,*args,**kwargs):
        """
        Returns the currently set sampling rate for the connected Tobii system.
        
        To determine what sampling rates are supported by your model of Tobii,
        use the sendCommand method of this class as follows:
            
            samplig_rate_list=tobii_tracker.sendCommand('valid_sampling_rate_options')
            
        samplig_rate_list will be a list of valid sample rate frequencies for
        the connected eye tracker.
        """
        if self._tobii:      
            return self._tobii.getSamplingRate()
        return 0.0
        
    def setSamplingRate(self,*args,**kwargs):
        """
        Sets the sampling rate to use during recording. The value passed to
        this method must be one of the values supported by your eye tracker model.
        
        To determine what sampling rates are supported by your model of Tobii,
        use the sendCommand method of this class as follows:
            
            samplig_rate_list=tobii_tracker.sendCommand('valid_sampling_rate_options')
            
        samplig_rate_list will be a list of valid sample rate frequencies for
        the connected eye tracker.
        """
        if self._tobii:      
            srate=-1
            if len(args):
                srate=args[0]
            elif kwargs.get('sampling_rate',False):
                srate= kwargs.get('sampling_rate',False)
            
            if srate in self._tobii.getAvailableSamplingRates():
                return self._tobii.setSamplingRate(srate)
                
        return EyeTrackerConstants.EYETRACKER_ERROR



    def getDataFilterLevel(self,*args,**kwargs):
        """
        Retrieving information about the eye data filtering level being used
        by the Tobii system is not possible via the API. This is a no-op method for
        the Tobii implementation.
        """
        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED

    def setDataFilterLevel(self,*args,**kwargs):
        """
        Setting the eye data filtering level being used
        by the Tobii system is not possible via the API. This is a no-op method for
        the Tobii implementation.
        """
        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
        
    def getLatestSample(self, *args, **kwargs):
        """
        Returns the latest sample retrieved from the Tobii device. The Tobii
        system always using the BinocularSample Evenet type. The following fields
        of this ioHub event type are supported:
            
            TO DO: give list of fields used in binoc. sample event and a meaning
            for each field that is relevent for the Tobii system.
        """
        return self._latestSample

    def getLatestGazePosition(self, *args, **kwargs):
        """
        Returns the latest 2D eye gaze position retrieved from the Tobii device.
        This represents where on the calibrated surface the eye tracker is 
        reporting each eyes gaze vector is intersecting.
        
        In general, the y or vertical component of each eyes gaze position should
        be the same value, since in typical user populations the two eyes are
        yoked vertically when they move. Therefore any difference between the 
        two eyes in the y dimention is likely due to eye tracker error.
        
        Differences between the x, or horizontal component of the gaze position,
        indicate that the participant is being reported as looking behind or
        in front of the calibrated plane. When a user is looking at the 
        calibration surface , the x component of the two eyes gaze position should be the same.
        Differences between the x value for each eye either indicates that the
        user is not focussing at the calibrated depth, or that there is error in the eye data.
        
        The above remarks are true for any eye tracker in general.
        
        """
        return self._latestGazePosition

    def drawToHostApplicationWindow(self,*args,**kwargs):
        """
        The Tobii system does not provide a real-time feedback application 
        for the operator of the system, therefore this method is not supported
        and is a no-op.
        """
        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
        
    def getDigitalPortState(self, *args, **kwargs):
        """
        This method is not supported by the Tobii implementation of the common
        eye tracker interface.
        """
        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
         
    def setDigitalPortState(self, *args, **kwargs):
        """
        This method is not supported by the Tobii implementation of the common
        eye tracker interface.
        """
        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
    
    def _poll(self):
        """
        The Tobii system uses a callback approach to providing new eye data as 
        it becomes available, so polling (and therefore this method) are not used.
        """
        pass
    
    def _handleNativeEvent(self,*args,**kwargs):
        """
        This method is called every time there is new eye data available from
        the Tobii system, which will be roughly equal to the sampling rate eye 
        data is being recorded at. The callback needs to return as quickly as 
        possible so there is no chance of overlapping calls being made to the
        callback. Therefore this method simply puts the event data received from 
        the eye tracker device, and the local ioHub time the callback was
        called, into a buffer for processing by the ioHub event system.
        """
        eye_data_event=args[1]
        
        logged_time_iohub_usec=Computer.getTime()*1000000.0
        logged_time_tobii_local_usec=self._tobii._getTobiiClockTime()        
        data_time_in_tobii_local_time=self._tobii._sync_manager.convert_from_remote_to_local(eye_data_event.Timestamp)
        
        #local_tobii_iohub_time_delta=logged_time_tobii_local_usec-logged_time_iohub_usec        
        data_delay=logged_time_tobii_local_usec-data_time_in_tobii_local_time
        
        logged_time=logged_time_iohub_usec/1000000.0
        device_event_time=data_time_in_tobii_local_time/1000000.0
        iohub_event_time=(logged_time_iohub_usec-data_delay)/1000000.0 # in sec.msec_usec
        data_delay=data_delay/1000000.0
        
        #ioHub.print2err("Received Tobii Data: ",logged_time,device_event_time,iohub_event_time,data_delay)
        self._addNativeEventToBuffer((logged_time,device_event_time,iohub_event_time,data_delay,eye_data_event))
        #ioHub.print2err("Data Added")

    
   
    def _getIOHubEventObject(self,*args,**kwargs):
        """
        _getIOHubEventObject is used to convert a device's events from their 'native' format
        to the ioHub DeviceEvent object for the relevent event type.

        If an event driven callback method is used, then this method should be employed to do
        the conversion between object types, so a minimum of work is done in the callback itself.

        The method expects a tuple of two arguements:
            (logged_time,event)=args[0] (when the callback is used to register device events)
        """        
        #ioHub.print2err("_getIOHubEventObject got: ",args,kwargs)
        logged_time,device_event_time,iohub_event_time,data_delay,eye_data_event=args[0]
        
        # TO DO: Convert the middle layer representation of a Tobii data event to 
        # the array format needed by ioHub for the appropriete data type.        
        # TO DO: integrate data into ioHub event handling
        
#        eyes[LEFT]['gaze_mm'][0]=eye_data_event.LeftGazePoint3D.x
#        eyes[LEFT]['gaze_mm'][1]=eye_data_event.LeftGazePoint3D.y
#        eyes[LEFT]['gaze_mm'][2]=eye_data_event.LeftGazePoint3D.z
#        eyes[LEFT]['eye_location_norm'][0]=eye_data_event.LeftEyePosition3DRelative.x
#        eyes[LEFT]['eye_location_norm'][1]=eye_data_event.LeftEyePosition3DRelative.y
#        eyes[LEFT]['eye_location_norm'][2]=eye_data_event.LeftEyePosition3DRelative.z
#        eyes[RIGHT]['gaze_mm'][0]=eye_data_event.RightGazePoint3D.x
#        eyes[RIGHT]['gaze_mm'][1]=eye_data_event.RightGazePoint3D.y
#        eyes[RIGHT]['gaze_mm'][2]=eye_data_event.RightGazePoint3D.z
#        eyes[RIGHT]['eye_location_norm'][0]=eye_data_event.RightEyePosition3DRelative.x
#        eyes[RIGHT]['eye_location_norm'][1]=eye_data_event.RightEyePosition3DRelative.y
#        eyes[RIGHT]['eye_location_norm'][2]=eye_data_event.RightEyePosition3DRelative.z

        event_type=EventConstants.BINOC_EYE_SAMPLE

        left_gaze_x=eye_data_event.LeftGazePoint2D.x
        left_gaze_y=eye_data_event.LeftGazePoint2D.y
        right_gaze_x=eye_data_event.RightGazePoint2D.x
        right_gaze_y=eye_data_event.RightGazePoint2D.y

        if left_gaze_x != -1 and left_gaze_y != -1:
            left_gaze_x,left_gaze_y=self._eyeTrackerToDisplayCoords(left_gaze_x,left_gaze_y)
        if right_gaze_x != -1 and right_gaze_y != -1:
            right_gaze_x,right_gaze_y=self._eyeTrackerToDisplayCoords(right_gaze_x,right_gaze_y)
        # TO DO: Set CI to be equal to current time error stated in Tobii Sync manager
        confidenceInterval=0.0 
        binocSample=[
                     0,
                     0,
                     Computer._getNextEventID(),
                     event_type,
                     device_event_time,
                     logged_time,
                     iohub_event_time,
                     confidenceInterval,
                     data_delay,
                     0, # filtered id (always 0 right now)
                     left_gaze_x,
                     left_gaze_y,
                     EyeTrackerConstants.UNDEFINED, # Left Eye Angle z
                     eye_data_event.LeftEyePosition3D.x,
                     eye_data_event.LeftEyePosition3D.y,
                     eye_data_event.LeftEyePosition3D.z,
                     EyeTrackerConstants.UNDEFINED, # Left Eye Angle x
                     EyeTrackerConstants.UNDEFINED, # Left Eye Angle y
                     EyeTrackerConstants.UNDEFINED, # Left Camera Sensor position x
                     EyeTrackerConstants.UNDEFINED, # Left Camera Sensor position y
                     eye_data_event.LeftPupil,
                     EyeTrackerConstants.PUPIL_DIAMETER,
                     EyeTrackerConstants.UNDEFINED, # Left pupil size measure 2
                     EyeTrackerConstants.UNDEFINED, # Left pupil size measure 2 type
                     EyeTrackerConstants.UNDEFINED, # Left PPD x
                     EyeTrackerConstants.UNDEFINED, # Left PPD y
                     EyeTrackerConstants.UNDEFINED, # Left velocity x
                     EyeTrackerConstants.UNDEFINED, # Left velocity y
                     EyeTrackerConstants.UNDEFINED, # Left velocity xy
                     right_gaze_x,
                     right_gaze_y,
                     EyeTrackerConstants.UNDEFINED, # Right Eye Angle z 
                     eye_data_event.RightEyePosition3D.x,
                     eye_data_event.RightEyePosition3D.y,
                     eye_data_event.RightEyePosition3D.z,
                     EyeTrackerConstants.UNDEFINED, # Right Eye Angle x
                     EyeTrackerConstants.UNDEFINED, # Right Eye Angle y
                     EyeTrackerConstants.UNDEFINED, #Right Camera Sensor position x
                     EyeTrackerConstants.UNDEFINED, #Right Camera Sensor position y
                     eye_data_event.RightPupil,
                     EyeTrackerConstants.PUPIL_DIAMETER,
                     EyeTrackerConstants.UNDEFINED, # Right pupil size measure 2
                     EyeTrackerConstants.UNDEFINED, # Right pupil size measure 2 type
                     EyeTrackerConstants.UNDEFINED, # Right PPD x
                     EyeTrackerConstants.UNDEFINED, # Right PPD y
                     EyeTrackerConstants.UNDEFINED, # right velocity x
                     EyeTrackerConstants.UNDEFINED, # right velocity y
                     EyeTrackerConstants.UNDEFINED, # right velocity xy
                     int(str(eye_data_event.LeftValidity)+str(eye_data_event.RightValidity))
                     ]

        EyeTracker._latestSample=binocSample
        
        if eye_data_event.LeftValidity>=2 and eye_data_event.RightValidity >=2:
            EyeTracker._latestGazePosition=None#EyeTracker._latestGazePosition=[EventConstants.UNDEFINED,EventConstants.UNDEFINED]
        elif eye_data_event.LeftValidity<2 and eye_data_event.RightValidity<2:
            EyeTracker._latestGazePosition=[(right_gaze_x+left_gaze_x)/2.0,
                                            (right_gaze_y+left_gaze_y)/2.0]
        elif eye_data_event.LeftValidity<2:
            EyeTracker._latestGazePosition=[left_gaze_x,left_gaze_y]
        elif eye_data_event.RightValidity<2:
            EyeTracker._latestGazePosition=[right_gaze_x,right_gaze_y]

        EyeTracker._lastCallbackTime=logged_time
        
        #ioHub.print2err('eye data extracted: ',binocSample)  
        return binocSample
        
    def _eyeTrackerToDisplayCoords(self,*args,**kwargs):
        """
        For eye tracker that have a static or fixed type internal mapping,
        this method is used to convert from eye tracker units to display units.
        Default implementation is to just pass the data through untouched.
        """
        if len(args)<2:
            return ['EYETRACKER_ERROR','_eyeTrackerToDisplayCoords requires two args gaze_x=args[0], gaze_y=args[1]']
        gaze_x=args[0]
        gaze_y=args[1]
        dw,dh=ioHub.devices.Display.getStimulusScreenResolution()
        ox,oy=ioHub.devices.Display.getStimulusScreenOrigin()
        # For the Tobii, the data used for screen gaze position is represented
        # as a normalized value between 0.0 and 1.0. Therefore, this method
        # needs to convert that to screen pixel coordinates based on the
        # current screen resolution and settings in the Display device. 
        display_x=gaze_x*dw-ox
        display_y=(1.0-gaze_y)*dh-oy
        
        return display_x,display_y
        
    def _displayToEyeTrackerCoords(self,*args,**kwargs):
        """
        For eye tracker that have a static or fixed type internal mapping,
        this method is used to convert from display units to eye tracker units.
        Default implementation is to just pass the data through untouched.

        For the Tobii system, this means converting from the screen coordinate
        space to a normalized value between 0.0 and 1.0. 0.0 is top-left of
        screen, 1.0 is bottom-right.
        """
        if len(args)<2:
            return ['EYETRACKER_ERROR','_displayToEyeTrackerCoords requires two args display_x=args[0], display_y=args[1]']
        display_x=args[0]
        display_y=args[1]
        
        dw,dh=ioHub.devices.Display.getStimulusScreenResolution()
        ox,oy=ioHub.devices.Display.getStimulusScreenOrigin()
        gaze_x=dw/(display_x+ox*dw)
        gaze_y=dh/(display_y+oy*dh)
        
        return gaze_x,gaze_y

    def _close(self):
        if self._tobii:
            self._tobii.disconnect()
        EyeTrackerInterface._close(self)