"""
ioHub
pyEyeTracker Interface
.. file: ioHub/devices/eyetracker/__init__.py

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""
import numpy as N
import ioHub
from ioHub.devices import Device
from ioHub.constants import DeviceConstants,EyeTrackerConstants
import hw

#noinspection PyUnusedLocal,PyTypeChecker
class EyeTrackerDevice(Device):
    """
    The EyeTrackerDevice class is the main class for the common eye tracker 
    interface API built into ioHub.

    The common eye tracker interface class is implemented for different
    eye tracker models by creating a subclass of the EyeTrackerDevice class
    and implementing the common eye tracker API components that can be supported
    by the given eye tracking hardware. It is these sub classes of the
    EyeTrackerDevice that are used to define which implementation of the 
    common eye tracker interface is to be used during an experiment,
    based on which eye tracker hardware you plan on using.

    Not every eye tracker implementation of the common eye tracker interface
    will support all of the interfaces functionality, however a core set of minimum
    functionality is expected to be supported by all implementation. 
    This is not surprising given the deversity of eye tracking devices in use today,
    and the common eye tracker interface was designed with this in mind.
    When a specific implementation does not support a given method, if that method
    is called, a default *not supported* behaviour is built into the base 
    implementation (currently the default behaviour is to simply do nothing and treat
    non supported functionality as no-op calls within the API). This will likely
    improve over time to provide some form of developer feedback when non supported
    functionality is being used by a particular eye tracker implementation.

    On the other hand, some eye trackers offer very specialized functionality that
    is not as common across the eye tracking field, or functionality that currently 
    maybe just missing from the common eye tracker interface. In these cases, 
    the devlopers of the specific eye tracker implementation can expose non standard 
    eye tracker interface functionality for their device by adding extra command types
    that are accessed by the sendCommand method of the eye tracker device API. 
    This practice is discurraged and should be used as a last resort however, as doing so breaks 
    the idea of having eye tracking experiment scripts that can
    be run on different eye tracking hardware simply by changing the eye tracker
    class being used in the iohub_config.yaml
    
    Methods in the EyeTrackerDevice class are broken down into several categories
    within the EyeTracker class:

    #. Eye Tracker Initialization / State Setting.
    #. Ability to Define the Graphics Layer for the Eye Tracker to Use During Calibration / System Setup.
    #. Starting and Stopping of Data Recording.
    #. Sending Synchronization messages or codes to the Eye Tracker.
    #. Accessing Eye Tracker Data During Recording.
    #. Accessing the Eye Tracker Timebase.
    #. Synchronizing the ioHub time base with the Eye Tracker time base, so Eye Tracker events can be provided with local time stamps when that is appropriate.

    .. note:: 

        Only **one** instance of EyeTracker can be created within an experiment. Attempting to create > 1
        instance will raise an exception. To get the current instance of the EyeTracker you can call the
        class method EyeTracker.getInstance(); this is useful as it saves needing to pass an eyeTracker
        instance variable around your code.
    """

    # Used to hold the EyeTracker subclass instance to ensure only one instance of
    # a given eye tracker type is created. This is a current ioHub limitation, not the limitation of
    # all eye tracking hardware.
    _INSTANCE=None
    
    # the multiplier needed to convert device times to sec.msec times.
    DEVICE_TIMEBASE_TO_SEC=1.0

    # Used by pyEyeTrackerDevice implementations to store relationships between an eye
    # trackers command names supported for EyeTrackerDevice sendCommand method and
    # a private python function to call for that command. This allows an implementation
    # of the interface to expose functions that are not in the core EyeTrackerDevice spec
    # without have to use the EXT extension class.
    _COMMAND_TO_FUNCTION = {}

    DEVICE_TYPE_ID=DeviceConstants.EYETRACKER
    DEVICE_TYPE_STRING='EYETRACKER'
    __slots__=['_latest_sample','_latest_gaze_position', '_runtime_settings']

    def __init__(self,*args,**kwargs):
        """
        The EyeTrackerDevice class is extended by each eye tracker hardware
        specific implementation of the common eye tracker interface. The hardware
        specific extensions of the EyeTrackerDevice class are named EyeTracker.

        Please review the EyeTracker device documentation page for the specific 
        eye tracker hardware that is being used at experiment runtime to get the
        appropriate class path for that eye tracker implementation; this class
        path is what is used to indicate what implementation of the common eye
        tracker interface will be loaded when the experiment starts.
        For example, if the experiment will be run using the interface 
        that supports eye trackers developed by EyeTrackingCompanyET (hypothetically),
        then set the eye tracker device class that starts the eye tracker device 
        settings section of the iohub_config.yaml for the experiment to:

        eyetracker.HW.EyeTrackingCompanyET.EyeTracker
        """
        if self.__class__._INSTANCE is not None:
            raise ioHub.devices.ioDeviceError(self,"EyeTracker object has already been created; "
                                                    "only one instance can exist. Delete existing "
                                                    "instance before recreating EyeTracker object.")
        else:
            self.__class__._INSTANCE=self
                
        Device.__init__(self,*args,**kwargs['dconfig'])

        # hold last received ioHub eye sample (in ordered array format) from tracker.
        self._latest_sample=EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
    
        # holds the last gaze position read from the eye tracker as an x,y tuple. If binocular recording is
        # being performed, this is an average of the left and right gaze position x,y fields.
        self._latest_gaze_position=EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED                                        

        # stores the eye tracker runtime related configuration settings from the ioHub .yaml config file
        self._runtime_settings=kwargs['dconfig']['runtime_settings']                                          
    
        #TODO: Add support for message ID to Message text lookup table in ioDataStore
        # data table that can be used by ET systems that support sending int codes,
        # but not text to tracker at runtime for syncing.
        
    def trackerTime(self):
        """
        trackerTime returns the current time reported by the eye tracker device.
        The time base is implementation dependent. 
        
        Args:
            None
        
        Return:
            float: The eye tracker hardware's reported current time.
        """
        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
   
    def trackerSec(self):
        """
        trackerSec takes the time received by the EyeTracker.trackerTime() method
        and returns the time in sec.usec-msec format.
        
        Args:
            None
        
        Return:
            float: The eye tracker hardware's reported current time in sec.msec-usec format.        
        """
        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
        
   
    def setConnectionState(self,enable):
        """
        setConnectionState is used to connect ( setConnectionState(True) ) 
        or disable ( setConnectionState(False) ) the connection of the ioHub 
        to the eyetracker hardware.
        
        Note that a connection to the eye tracking hardware is automatically
        openned when the ioHub Server process is started. So there is no need to
        call this method at the start of your experiment. Doing so will have no
        effect on the connection state.

        Args:
            enable (bool): True = enable the connection, False = disable the connection.

        Return:
            bool: indicates the current connection state to the eye tracking hardware.
            
        """
        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
            
    def isConnected(self):
        """
        isConnected returns whether the EyeTrackerDevice is connected to the
        eye tracker hardware or not.
        
        Args:
            None
            
        Return:
            bool:  True = the eye tracking hardware is connected. False otherwise.
        """
        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
            
    def sendCommand(self, key, value=None):
        """
        The sendCommand method allows arbitrary *commands* or *requests* to be
        issued to the eye tracker device. Valid values for the arguements of this 
        method are completely implementation specific, so please refer to the 
        eye tracker implentation page for the eye tracker being used for a list of 
        valid key and value combinations (if any). 
        
        In general, eye tracker implementations should **not** need to support 
        this method unless there is critical eye tracker functionality that is 
        not accessable using the other methods in the EyeTrackerDevice class.
        
        Args:
            key (str): the command or function name that should be run.
            value (object): the (optional) value associated with the key. 


        Return:
            object: the result of the command call
            int: EyeTrackerConstants.EYETRACKER_OK
            int: EyeTrackerConstants.EYETRACKER_ERROR
            int: EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
        """

        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
        
    def sendMessage(self,message_contents,time_offset=None):
        """
        The sendMessage method sends a text or int message to the eye tracker. 
        
        Messages are generally used to send information you want 
        saved with the native eye data file and are often used to 
        synchronize stimulus changes in the experiment with the eye
        data stream being saved to the native eye tracker data file (if any).
        
        This means that the sendMessage implementation needs to 
        perform in real-time, with a delay of <1 msec from when a message is 
        sent to when it is time stamped by the eye tracker, for it to be 
        accurate in this regard.

        If this standard can not be met, the expected delay and message 
        timing precision (variability) should be provided in the eye tracker's 
        implementation notes.

        Args:
           message_contents (str or int): 
               If message_contents is a string, check with the implementations documentation if there are any string length limits.

        Kwargs:
           time_offset (float): sec.msec_usec time offset that the time stamp of
                              the message should be offset in the eye tracker data file.
                              time_offset can be used so that a message can be sent
                              for a display change **BEFORE** or **AFTER** the actual
                              flip occurred, using the following formula:
                                  
                              time_offset = sendMessage_call_time - event_time_message_represent
                              
                              Both times should be based on the ioHub.Computer.getTime() time base.
                              
                              If time_offset is not supported by the eye tracker implementation being used, a warning message will be printed to stdout.
        
        Return:
            (int): EyeTrackerConstants.EYETRACKER_OK, EyeTrackerConstants.EYETRACKER_ERROR, or EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED                      
        """
            
        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
    
    def runSetupProcedure(self, starting_state=EyeTrackerConstants.DEFAULT_SETUP_PROCEDURE):
        """
        The runSetupProcedure allows the eye tracker interface to perform 
        such things as participant placement validation, camera setup, calibration,
        and validation type activities. The details of what this method does exactly
        is implementation specific. This is a blocking call for the experiment process
        and will not return until the necessary steps have been done so that the
        eye tracker is ready to start collecting eye data when the method returns.
        
        Args: 
            None
            
        Kwargs: 
            starting_state (int): The state that the eye tracker should start with or
                perform when the runSetupProcedure method is called. Valid options are:
                    EyeTrackerConstants.DEFAULT_SETUP_PROCEDURE (the default) indicates that the standard setup and calibration procedure should be performed.
                    EyeTrackerConstants.CALIBRATION_START_STATE indicates the eye tracker should immediately start the calibration procedure when the method is called.
                    EyeTrackerConstants.VALIDATION_START_STATE indicates the eye tracker should immediately start the validation procedure when the method is called.
                    EyeTrackerConstants.DRIFT_CORRECTION_START_STATE indicates the eye tracker should immediately start the validation procedure when the method is called.
                An eye tracker implementation is only required to support the EyeTrackerConstants.DEFAULT_SETUP_PROCEDURE setting.
                
        Return:
            int: EyeTrackerConstants.EYETRACKER_OK if this method and starting_state is supported and the runSetupProcedure ran successfully. If the starting state specified was anything other than EyeTrackerConstants.VALIDATION_START_STATE, the performed calibration routine must have also passed (been sucessful). 
                 EyeTrackerConstants.EYETRACKER_CALIBRATION_ERROR if this method and starting_state is supported but either calibration or drift correction (depending on the state argument provided) failed. In this case; the method can be called again to attempt a sucessful calibration and or drift correction.                
                 EyeTrackerConstants.EYETRACKER_ERROR if this method is supported and starting_state is, but an error occurred during the method (other than a failed calibration or drift correct result).
                 EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED if the eye tracker implementation does not support this method or the specified starting_state.
        """
        
        # Implementation Note: Change this list to only include the states your eye tracker can support.
        IMPLEMENTATION_SUPPORTED_STATES=[EyeTrackerConstants.DEFAULT_SETUP_PROCEDURE,
                                         EyeTrackerConstants.CALIBRATION_START_STATE,
                                         EyeTrackerConstants.VALIDATION_START_STATE,
                                         EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED]
        
        if starting_state in [EyeTrackerConstants.DEFAULT_SETUP_PROCEDURE,
                              EyeTrackerConstants.CALIBRATION_START_STATE,
                              EyeTrackerConstants.VALIDATION_START_STATE,
                              EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED]:

            if starting_state in IMPLEMENTATION_SUPPORTED_STATES:
                # Implementation Note: Run your custom implementation logic for the method here
                ioHub.print2err("EyeTracker should handle runSetupProcedure method with starting_state of {0} now.".format(starting_state))
                
                # Implementation Note: result should be changed to return one of
                #       EyeTrackerConstants.EYETRACKER_OK 
                #       EyeTrackerConstants.EYETRACKER_CALIBRATION_ERROR 
                #       EyeTrackerConstants.EYETRACKER_ERROR 
                result = EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
                return result
            else:
                return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
        else:
            return ioHub.server.createErrorResult("INVALID_METHOD_ARGUMENT_VALUE",error_message="The starting_state arguement value provided is not recognized",method="EyeTracker.runSetupProcedure",arguement='starting_state', value=starting_state)            

                
    def setRecordingState(self,recording):
        """
        The setRecordingState method is used to start or stop the recording 
        and transmition of eye data from the eye tracking device.
        
        Args:
            recording (bool): if True, the eye tracker will start recordng data.; false = stop recording data.
           
        Return:
            bool: the current recording state of the eye tracking device
        """
        
        if not isinstance(recording,bool):
            return ioHub.server.createErrorResult("INVALID_METHOD_ARGUMENT_VALUE",error_message="The recording arguement value provided is not a boolean.",method="EyeTracker.setRecordingState",arguement='recording', value=recording)
        
        # Implementation Note: Perform your implementation specific logic for this method here
        ioHub.print2err("EyeTracker should handle setRecordingState method with recording value of {0} now.".format(recording))
        
        # Implementation Note: change current_recording_state to be True or False, based on whether the eye tracker is now recording or not.
        current_recording_state=EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
        return current_recording_state

    def isRecordingEnabled(self):
        """
        The isRecordingEnabled method indicates if the eye tracker device is currently
        recording data or not. 
   
        Args:
           None
  
        Return:
            bool: True == the device is recording data; False == Recording is not occurring
        """
        
        # Implementation Note: Perform your implementation specific logic for this method here
        ioHub.print2err("EyeTracker should handle isRecordingEnabled method now.")

        # Implementation Note: change is_recording to be True or False, based on whether the eye tracker is recording or not.
        is_recording=EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
        
        return is_recording
        
    def getLastSample(self):
        """
        The getLastSample method returns the latest ioHub sample event available.
        The eye tracker must be recording data for a sample event to be returned, otherwise None is returned.

        Args: 
            None

        Returns:
            int: If this method is not supported by the eye tracker interface, EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED is returned.

            None: If the eye tracker is not currently recording data.

            EyeSample: If the eye tracker is recording in a monocular tracking mode, the latest sample event of this event type is returned.

            BinocularEyeSample:  If the eye tracker is recording in a binocular tracking mode, the latest sample event of this event type is returned.
        """
        
        return self._latest_sample

    def getLastGazePosition(self):
        """
        The getLastGazePosition method returns the latest eye gaze position retieved from the eye tracker device.
        This is the position on the calibrated 2D surface that the eye tracker is reporting as the current eye position.
        The units are in the units in use by the Display device. 
        
        If binocular recording is being performed, the average position of both eyes is returned. 
        
        If no samples have been received from the eye tracker, or the eye tracker is not currently recording data, None is returned.

        Args: 
            None

        Returns:
            int: If this method is not supported by the eye tracker interface, EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED is returned.

            None: If the eye tracker is not currently recording data or no eye samples have been received.

            tuple: Latest (gaze_x,gaze_y) position of the eye(s)
        """
        return self._latest_gaze_position


    def _eyeTrackerToDisplayCoords(self,eyetracker_point):
        """
        The _eyeTrackerToDisplayCoords method must be used by an eye trackers implementation
        of the common eye tracker interface to convert monitor screen based x,y coordinates
        from the eye trackers coordinate space to the ioHub.devices.Display coordinate
        space being used. Any screen based coordinates that exist in the data
        provided to the ioHub by the device implementation must use this method to
        convert the x,y screen position to the correct coordinate space.
        
        Default implementation is to just pass the x,y screen position through as (x,y) tuple.

        Args:
            eyetracker_point (object): eye tracker implementation specific data type representing an x, y position on the calibrated 2D plane (typically a computer display screen).

        Returns:
            (x,y): The x,y eye position on the calibrated surface in the current ioHub.devices.Display coordinate type and space.
        """
        gaze_x=eyetracker_point[0]
        gaze_y=eyetracker_point[1]
        
        # do mapping if necessary
        # default is no mapping 
        display_x=gaze_x
        display_y=gaze_y

        return display_x, display_y
   
    def _displayToEyeTrackerCoords(self,display_x,display_y):
        """
        The _displayToEyeTrackerCoords method must be used by an eye trackers implementation
        of the common eye tracker interface to convert any gaze positions provided
        by the ioHub to the appropriate x,y gaze position coordinate space for the eye tracking device in use.
        
        This method is simply the inverse operation performed by the _eyeTrackerToDisplayCoords
        method.
        
        Default implementation is to just return the gaze_x,gaze_y values unchanged.

        Args:
            display_x (float): The horizontal eye position on the calibrated 2D surface in ioHub.devices.Display coordinate space.
            display_y (float): The vertical eye position on the calibrated 2D surface in ioHub.devices.Display coordinate space.
            
        Returns:
            (object): eye tracker implementation specific data type representing an x, y position on the calibrated 2D plane (typically a computer display screen).
        """
        # do mapping if necessary
        # default is no mapping 
        gaze_x=display_x
        gaze_y=display_y
        
        return gaze_x,gaze_y
    
#    def _poll(self):
#        """
#        The _poll method is used when the ioHub Device needs to periodically
#        check for new events received from the native device / device API.
#        Normally this means that the native device interface is using some form
#        data buffer or que to place new device events in until the ioHub Device 
#        reads them.
#
#        The ioHub Device can *poll* and check for any new events that
#        are available, retrieve the new events, and process them 
#        to create ioHub Events as necessery. Each subclass of ioHub.devives.Device
#        that wishes to use event polling **must** override the _poll method
#        in the Device classes implementation. The configuration section of the
#        iohub_config.yaml for the device **must** also contain the device_timer: interval
#        parameter as explained below. 
#
#        **See the comments in the ioHub.devices.Device._poll() method for more important details.  
#        and a simple generic sudo code implementation.**
#
#        If the eye tracker device uses the event callback method for notifying 
#        the ioHub Server of new native device interface events as they become available,
#        then the _handleNativeEvent() and _getIOHubEventObject() methods must 
#        implemented for the EyeTracker class being implemented and it must **not**
#        extend the _poll() method. Furthermore, the EyeTracker device configuration
#        section of the iohub_config.yaml must **not** contain a 'device_timer'
#        setting, as the ioHub Server uses the presence of this device setting to
#        determine of a Device class uses the polling vs. callback event detection 
#        approach.             
#        """
#        
#        # Replace the following line with your Device classes implementation of the method if the device is polling.
#        # Remove this method from your class if the device is not using event polling for event detection
#        # and are using an event callback approach instead.
#        Device._poll(self)
#        
#    def _handleNativeEvent(self,*args,**kwargs):
#        """
#        The _handleEvent method can be used by the native device interface that
#        the ioHub Device class implements to register new native device events
#        by calling this method of the ioHub Device class. 
#        
#        **See the comments in the ioHub.devices.Device._handleNativeEvent() 
#        method for more important details and a simple generic sudo code implementation.**
#
#        """
#        # Replace the following line with your Device classes implementation of
#        # the method if the device is using event callbacks.
#        # Remove this method from your class if the device is using a polling model
#        # to detect new events.
#        Device._handleNativeEvent(self,*args,**kwargs)
# 
#    def _getIOHubEventObject(self,native_event_data):
#        """
#        The _getIOHubEventObject method is called by the ioHub Server to convert 
#        new native device event objects that have been received to the appropriate 
#        ioHub Event type representation. 
#        
#        If the ioHub Device has been implemented to use the _poll() method of checking for
#        new events, then this method simply should return what it is passed, and is the
#        default implmentation for the method.
#        
#        If the ioHub Device has been implemented to use the evnt callback method
#        to register new native device events with the ioHub Server, then this method should be
#        overwritten by the Device subclass to convert the native event data into
#        an appropriate ioHub Event representation. See the implementation of the 
#        Keyboard or Mouse device classes for an example of such an implementation.
#        
#        Args:
#            native_event_data: object or tuple of (callback_time, native_event_object)
#           
#        Returns:
#            tuple: The appropriate ioHub Event type in list form.
#        """
#        # Replace the following line with your Device classes implementation of
#        # the method if the device is using event callbacks.
#        # Remove this method from your class if the device is using a polling model
#        # to detect new events.
#        ioHub.print2err("EyeTrackerDevice_getIOHubEventObject being called!!")
#
#        #return Device._getIOHubEventObject(self,native_event_data)
        
    def __del__(self):
        """
        Do any final cleanup of the eye tracker before the object is destroyed.
        """
        self.__class__._INSTANCE=None

# The below methods have been removed, as they all relate to attributes of the 
# eye tracker that are really related to the eyetracker config file setup
# and many eye trackers will not support these methods anyhow, so they over complicate
# the interface for little extra value (IMO).

#    def createNativeDataFile(self, native_file_name, eye_tracker_native_file_directory=None, over_write=True):
#        """
#        The createNativeDataFile method instructs the eye tracker to open a new 
#        native data file in the eye tracker computer / application. The currently
#        open eye tracker native can be closed using the closeNativeDataFile() method.
#       
#        Note that using native data files is not supported by all eye tracking hardware 
#        and is not required when using the ioHub if the eye tracker send the eye tracker
#        events needed during experiment runtime. If this is the case, the ioDataStore 
#        can save all events received from the eye tracker into the ioHub Servers
#        event data file and this file can be used to access eye tracker events post hoc.
#        
#        If the ExperimentRuntime device has also sent appropriate Message events
#        to the ioHub during the experiment runtime, everything needed to perform
#        data analysis should be available in the ioDataStore file saved.
#        
#        Args: 
#            native_file_name (str): the name of the native data file to open by the eye tracker Host application. The file name should *not* include any path information. The file type extension is optional when specifying the file_name.
#        
#        Kwargs:
#            eye_tracker_native_file_directory (str): Directory to save the name data file to (eye tracker host computer or application relative). 
#           
#            over_write (bool): If True, the eye tracker will over write an existing data file that has the same name and directory provided. If False, no data file will be created and EyeTrackerConstants.EYETRACKER_ERROR will be returned by the method. 
#        
#        Note that if either of the optional Kwargs are provided by the experiment script,
#        but are not supported by the eye tracker implementation being used, 
#        they will be ignored and a warning message will be printed to stdout.
#        
#        Return:
#            (bool): EyeTrackerConstants.EYETRACKER_OK, EyeTrackerConstants.EYETRACKER_ERROR, or EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED             
#            
#        """
#
#        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
#        
#    def closeNativeDataFile(self):
#        """
#        The closeNativeDataFile is used to close a currently open native eye tracker data file.
#        If no native data file has been openned, then calling this method does nothing.
#        
#        Once a native data file has been closed, on eye tracker systems that run on a seperate
#        computer than the Experiment computer, the getNativeDataFile() method
#        may be used to transfer the native data file from the eye tracker computer
#        to the experiment / ioHub computer.
#        
#        Args:
#            None
#            
#        Return:
#            int: EyeTrackerConstants.EYETRACKER_OK if this method is supported, a native data file was open on the eye tracker host software, and it was successfully closed
#                 EyeTrackerConstants.EYETRACKER_ERROR if this method is supported, but either no native data file was open when closeNativeDataFile() was called, or another eye tracker host error occurred.
#                 EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED if the eye tracker implementation does not support this method.
#        """
#        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
#
#    
#    def getNativeDataFile(self, native_file_name, eye_tracker_native_file_directory=None, prompt_for_local_save_location=False):
#        """
#        The getNativeDataFile method is only of relevence on eye tracker systems
#        that run on a seperate computer than the experiment / ioHub computer
#        
#        In such cases, the method may be used to transfer the a native eye tracker data file
#        from the eye tracker computer to the experiment computer.
#        
#        If the requested naive eye tracker file is open when this method is called, the eye tracker
#        will close the file prior to transfering it.
#
#        Args: 
#            native_file_name (str): the name of the native data file to transfer from the eye tracker Host application. The file name should *not* include any path information. The file type extension is optional when specifying the file_name.
#        
#        Kwargs:
#            eye_tracker_native_file_directory (str): Directory that the native file should be retrieved from on the Eye Tracker Host computer.  
#            
#            prompt_for_local_save_location (bool): If True, a file save dialog will be displayed allowing the selection of the location to save the native data file to. If False (the default), no dialog will be displayed and the native data file will ve saved in the same directory the experiment script is in.
#        
#        Return: 
#            int: EyeTrackerConstants.EYETRACKER_OK if this method is supported, the requested native data file was successfully transfered.
#                 EyeTrackerConstants.EYETRACKER_ERROR if this method is supported, but the requested native data file was not transfered to the experiment computer; either because the supplied file name and / or path could not be found, or another file transfer error occurred.
#                 EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED if the eye tracker implementation does not support this method.
#            
#        """
#        
#        # Implementation Suggestions:
#        # It is suggested that implementions of this mehtod first check that 
#        # the requested file exists on the host computer. If the file exists and can be transfered, 
#        # then use the value of prompt_for_local_save_location to determine if 
#        # a file save dialog should be displayed or not. 
#        # The ioHub.util.experiment.dialogs.FileDialog can be used for this purpose
#        # if needed.
#        
#        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED      
#    def getSampleFilterLevel(self,data_stream=EyeTrackerConstants.FILTER_ALL):
#        """
#        The getSampleFilterLevel method returns the eye tracker hardware controlled
#        *temporal* eye sample data filter level for the specified data_stream (if any).
#        The degree to which this method is supported is eye tracker implementation dependent. 
#        A specific eye tracker may fully support the method, not support this 
#        method at all, or may only support a subset of the defined data_stream constants. 
#
#        The defined possible data stream types are:
#            
#            EyeTrackerConstants.FILTER_ALL : The eye tracker applies the same filter to all filterable data streams it supports.
#            EyeTrackerConstants.FILTER_FILE : The eye tracker supports an eye sample filter that is applied only to samples saved to the eye trackers native data file.
#            EyeTrackerConstants.FILTER_NET : The eye tracker supports an eye sample filter that is applied only to samples sent over the supported network interface.
#            EyeTrackerConstants.FILTER_SERIAL : The eye tracker supports an eye sample filter that is applied only to samples sent over the supported serial interface.
#            EyeTrackerConstants.FILTER_ANALOG : The eye tracker supports an eye sample filter that is applied only to samples sent over the supported analog interface.
#
#        The defined possible filter level values for any supported data stream types are:
#            
#            EyeTrackerConstants.FILTER_LEVEL_OFF : No temporal eye sample filtering is being performed by the eye tracking device for the given data stream.
#            EyeTrackerConstants.FILTER_LEVEL_1 : The lowest level of eye sample filtering is being performed by the eye tracking device for the given data stream.
#            EyeTrackerConstants.FILTER_LEVEL_2 : A mid level of eye sample filtering is being performed by the eye tracking device for the given data stream.
#            EyeTrackerConstants.FILTER_LEVEL_3 : A mid level of eye sample filtering is being performed by the eye tracking device for the given data stream.
#            EyeTrackerConstants.FILTER_LEVEL_4 : A mid level of eye eye sample filtering is being performed by the eye tracking device for the given data stream.
#            EyeTrackerConstants.FILTER_LEVEL_5 : The highest level of eye eye sample filtering is being performed by the eye tracking device for the given data stream.
#         
#        If the eye tracker implementation for the device being used does not support this method, EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED will be returned
#         
#        If the eye tracker implementation for the device being used does not support the data_stream value provided, EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED will be returned
#
#        If the eye tracker implementation for the device being used supports the data_stream value provided, one of the EyeTrackerConstants.FILTER_LEVEL_* constants will be returned.
#        
#        Note that the filter levels specified by the common eye tracker interface are intended to be as general purpose as possible.
#        Refer to the eye tracker implementation notes page for the eye tracker being used to determine how these filter level constants map to vendor specific filter levels or types.
#        
#        Args:
#            data_stream (int): Specifies which data stream is being queried for the active sample data filter level. Must be one of the constants refernced above. 
#        
#        Return: 
#            int: EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED if the method or data_stream specified is not supported by the eye tracker implementation being used. Otherwise, the EyeTrackerConstants.FILTER_LEVEL_* that is in place for the specified data_stream type.
#            
#        """
#        method_is_supported=True
#        
#        if method_is_supported:
#            all_possible_data_streams=[EyeTrackerConstants.FILTER_FILE,
#                                    EyeTrackerConstants.FILTER_NET,
#                                    EyeTrackerConstants.FILTER_SERIAL,
#                                    EyeTrackerConstants.FILTER_ANALOG,
#                                    EyeTrackerConstants.FILTER_ALL]
#            
#            if data_stream not in all_possible_data_streams:
#                return ioHub.server.createErrorResult("INVALID_METHOD_ARGUMENT_VALUE",error_message="The data_stream arguement value provided is not a valid data stream constant.",method="EyeTracker.getDataFilterLevel",arguement='data_stream', value=data_stream)
#                
#            supported_data_streams=[EyeTrackerConstants.FILTER_FILE,
#                                    EyeTrackerConstants.FILTER_NET,
#                                    EyeTrackerConstants.FILTER_SERIAL,
#                                    EyeTrackerConstants.FILTER_ANALOG,
#                                    EyeTrackerConstants.FILTER_ALL]
#     
#            if data_stream in supported_data_streams:
#                # Implementation Note: Run your custom implementation logic for the method here
#                ioHub.print2err("EyeTracker should handle getDataFilterLevel method now.")
#                
#                # Implementation Note: result should be changed to return one of
#                #       EyeTrackerConstants.EyeTrackerConstants.FILTER_LEVEL_
#                result = EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
#                return result
#                
#        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED     
#        
#    def setSampleFilterLevel(self,filter_settings_dict):
#        """
#        The setSampleFilterLevel method sets the eye tracker hardware controlled
#        *temporal* eye sample data filter level for the specified data_stream(s).
#        
#        The degree to which this method is supported is eye tracker implementation dependent. 
#        A specific eye tracker may fully support the method, not support this 
#        method at all, or may only support a subset of the defined data_stream constants. 
#
#        The defined possible data stream types are:
#            
#            EyeTrackerConstants.FILTER_ALL : The eye tracker applies the same filter to all filterable data streams it supports.
#            EyeTrackerConstants.FILTER_FILE : The eye tracker supports an eye sample filter that is applied only to samples saved to the eye trackers native data file.
#            EyeTrackerConstants.FILTER_ONLINE : The eye tracker supports an eye sample filter that is applied only to samples over realtime interfaces during recording.
#            EyeTrackerConstants.FILTER_NET : The eye tracker supports an eye sample filter that is applied only to samples sent over the supported network interface.
#            EyeTrackerConstants.FILTER_SERIAL : The eye tracker supports an eye sample filter that is applied only to samples sent over the supported serial interface.
#            EyeTrackerConstants.FILTER_ANALOG : The eye tracker supports an eye sample filter that is applied only to samples sent over the supported analog interface.
#
#        The defined possible filter level values for any supported data stream types are:
#            
#            EyeTrackerConstants.FILTER_LEVEL_OFF : No temporal eye sample filtering is being performed by the eye tracking device for the given data stream.
#            EyeTrackerConstants.FILTER_LEVEL_1 : The lowest level of eye sample filtering is being performed by the eye tracking device for the given data stream.
#            EyeTrackerConstants.FILTER_LEVEL_2 : A mid level of eye sample filtering is being performed by the eye tracking device for the given data stream.
#            EyeTrackerConstants.FILTER_LEVEL_3 : A mid level of eye sample filtering is being performed by the eye tracking device for the given data stream.
#            EyeTrackerConstants.FILTER_LEVEL_4 : A mid level of eye eye sample filtering is being performed by the eye tracking device for the given data stream.
#            EyeTrackerConstants.FILTER_LEVEL_5 : The highest level of eye eye sample filtering is being performed by the eye tracking device for the given data stream.
#         
#        If the eye tracker implementation for the device being used does not support this method, EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED will be returned
#         
#        If the eye tracker implementation for the device being used does not support one of the data_stream values provided, that EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED will be returned for that data stream key in the result dictionary.
#
#        If the eye tracker implementation for the device being used supports the data_stream value provided, the filter level for that stream will be updated and the current filter level will be returned as the value for the associated data_stream key in the returned dictionary.
#        
#        Note that the filter levels specified by the common eye tracker interface are intended to be as general purpose as possible.
#        Refer to the eye tracker implementation notes page for the eye tracker being used to determine how these filter level constants map to vendor specific filter levels or types.
#        
#        Args:
#            filter_settings_dict (dict): A dictionary indicating the data streams (dict keys) and associated filter level constants (values) to update the eye tracker settings with. 
#        
#        Return: 
#            dict: EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED if the method is not supported, or a dict with the same data stream keys as were passed in the filter_settings_dict, with the value for each key being the updated filter level, or EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED if the data steam key provided is not supported by the eye tracker implementation.        
#        """
#        
#        functionality_supported=True        
#        
#        if not functionality_supported:
#            return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED     
#
#        if not isinstance(filter_settings_dict,dict):
#            return ioHub.server.createErrorResult("INVALID_METHOD_ARGUMENT_VALUE",
#                                    error_message="The filter_settings_dict arguement value provided is not a dict.",
#                                    method="EyeTracker.setSampleFilterLevel",arguement='filter_settings_dict', value=filter_settings_dict)
#
#        ALL_STREAM_TYPES=(EyeTrackerConstants.FILTER_ALL,
#                          EyeTrackerConstants.FILTER_NET,
#                          EyeTrackerConstants.FILTER_FILE,
#                          EyeTrackerConstants.FILTER_SERIAL,
#                          EyeTrackerConstants.FILTER_ANALOG)
#
#        ALL_FILTER_LEVELS=(EyeTrackerConstants.FILTER_LEVEL_OFF,
#                           EyeTrackerConstants.FILTER_LEVEL_1,
#                           EyeTrackerConstants.FILTER_LEVEL_2,
#                           EyeTrackerConstants.FILTER_LEVEL_3,
#                           EyeTrackerConstants.FILTER_LEVEL_4,
#                           EyeTrackerConstants.FILTER_LEVEL_5)
#                           
#        supportedDataStreams=(EyeTrackerConstants.FILTER_ALL,)
#
#        result_dict={}
#        for data_stream, filter_level in filter_settings_dict.iteritems():
#
#            if data_stream not in ALL_STREAM_TYPES:
#                return ioHub.server.createErrorResult("INVALID_METHOD_ARGUMENT_VALUE",
#                                    error_message="One of the provided data stream types is not a valid.",
#                                    method="EyeTracker.setSampleFilterLevel",arguement='filter_settings_dict', invalid_data_stream_key=data_stream)
#    
#            if data_stream not in ALL_FILTER_LEVELS:
#               return ioHub.server.createErrorResult("INVALID_METHOD_ARGUMENT_VALUE",
#                                    error_message="One of the provided filter level values is not a valid.",
#                                    method="EyeTracker.setSampleFilterLevel",arguement='filter_settings_dict', invalid_filter_level_value=filter_level)
#                     
#            if data_stream in supportedDataStreams:
#                # Implementation Note: Add your filter level setting code for the current data stream here.
#                ioHub.print2err("EyeTracker should handle setSampleFilterLevel method for data stream {0} now.".format(filter_level))
#                result_dict[data_stream]=filter_level
#            else:
#                result_dict[data_stream]=EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
#                
#        return result_dict
#        
#    def getEyesToTrack(self):
#        """
#        The getEyesToTrack method returns the eye(s) that the tracker is set to record for and provide events from.
#        The return value is an EyeTrackerConstants associated with one of the valid 'eye recording types':
#
#        EyeTrackerConstants.LEFT_EYE : The left eye is being tracked; Monocular Eye Sample events will be created by the ioHub.
#        EyeTrackerConstants.RIGHT_EYE : The right eye is being tracked; Monocular Eye Sample events will be created by the ioHub.
#        EyeTrackerConstants.UNKNOWN_MONOCULAR : The either the left or right eye is being tracked, however the eye tracker is unable to specify which. Monocular Eye Sample events will be created by the ioHub.
#        EyeTrackerConstants.BINOCULAR : Both eyes of the participant are being tracked. Binocular Eye Sample events will be created by the ioHub.
#        EyeTrackerConstants.BINOCULAR_AVERAGED : Both eyes of the participant are being tracked and the x and y data for each eye has been averaged. Monocular Eye Sample events will be created by the ioHub.
#        EyeTrackerConstants.SIMULATED_MONOCULAR : The eye tracking device is providing simulated monocular eye data. Monocular Eye Sample events will be created by the ioHub.
#        EyeTrackerConstants.SIMULATED_BINOCULAR :  The eye tracking device is providing simulated binocular eye data. Binocular Eye Sample events will be created by the ioHub.
#            
#        Different eye tracker implementations will support a different subset of these eye recording types.
#        
#        To get the string representation of an int EyeTrackerConstants value, use:
#
#            EyeTrackerConstants.getName(constant_id)
#
#        Args:
#            None
#            
#        Return:
#            int: If the method is not supported, EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED is returned. Otherwise, the currently set eye(s) to track value is returned, as one of the EyeTrackerConstants eye to track values.
#        """
#        
#        # Implementation Note: Add the code needed to return the current eye(s) be tracked constant.
#        
#        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
#
#    def setEyesToTrack(self,track_eyes):
#        """
#        The setEyesToTrack method sets the eye(s) that the eye tracker should track and provide events for.
#        The track_eyes arguement must be one of the EyeTrackerConstants associated with one of the valid 'eye recording types':
#
#            EyeTrackerConstants.LEFT_EYE : The left eye is being tracked; Monocular Eye Sample events will be created by the ioHub.
#            EyeTrackerConstants.RIGHT_EYE : The right eye is being tracked; Monocular Eye Sample events will be created by the ioHub.
#            EyeTrackerConstants.UNKNOWN_MONOCULAR : The either the left or right eye is being tracked, however the eye tracker is unable to specify which. Monocular Eye Sample events will be created by the ioHub.
#            EyeTrackerConstants.BINOCULAR : Both eyes of the participant are being tracked. Binocular Eye Sample events will be created by the ioHub.
#            EyeTrackerConstants.BINOCULAR_AVERAGED : Both eyes of the participant are being tracked and the x and y data for each eye has been averaged. Monocular Eye Sample events will be created by the ioHub.
#            EyeTrackerConstants.SIMULATED_MONOCULAR : The eye tracking device is providing simulated monocular eye data. Monocular Eye Sample events will be created by the ioHub.
#            EyeTrackerConstants.SIMULATED_BINOCULAR :  The eye tracking device is providing simulated binocular eye data. Binocular Eye Sample events will be created by the ioHub.
#            
#        Different eye tracker implementations will support a different subset of these eye recording types.
#        
#        To get the string representation of an int EyeTrackerConstants value, use:
#
#            EyeTrackerConstants.getName(constant_id)
#
#        Args:
#            track_eyes (int) : The EyeTrackerConstants value for one of the eye recording types.
#            
#        Return:
#            int: If the method in general, or the specified eyes to track type,  is not supported EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED is returned. Otherwise, the currently set eye(s) to track value is returned, as one of the EyeTrackerConstants eye to track values.
#        """
#
#        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
#
#    def getSamplingRate(self,all_supported_rates=False):
#        """
#        The getSamplingRate method returns different values based on the value of the all_supported_rates arguement.
#        If all_supported_rates = False (the default), then the current sampling rate of the eye tracker (in Hz) is returned.
#        If all_supported_rates = True, then a tuple of all valid sampling rates (in Hz) the eye tracker supports is returned. 
#        In both cases, sampling rate values are returned as floats.
#
#        Args:
#            all_supported_rates (bool): If False (the default), return all possible sampling rates the eye tracker will support. If True, the current sample rate of the eye tracker is returned in hz.    
#
#        Return:
#            int: If the method is not supported by the eye tracker implementation, or the given value for all_supported_rates is not supported, then EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED is returned.
#           
#            float: If all_supported_rates = False, the current Hz sampling rate of the eye tracker is returned. 
#
#            tuple of floats: If all_supported_rates = True, the all supported sampling rates for the eye tracker are returned. 
#        """
#
#        functionality_supported=True        
#        
#        if not functionality_supported:
#            return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED     
#
#        if not isinstance(all_supported_rates,bool):
#            return ioHub.server.createErrorResult("INVALID_METHOD_ARGUMENT_VALUE",
#                                    error_message="The all_supported_rates arguement value provided is not a bool.",
#                                    method="EyeTracker.getSamplingRate",
#                                    arguement='all_supported_rates', 
#                                    value=all_supported_rates)
#
#        if all_supported_rates is False:
#             # Implementation Note: Add code to return the eye trackers current sample rate setting in Hz.
#             EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
#        else:
#            # Implementation Note: Add code to return a tuple of all supported sampling rates of the current eye tracker in Hz.
#            # If This can not be supported, return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
#            return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
#
#    def setSamplingRate(self,sampling_rate):
#        """
#        The setSamplingRate method sets the eye tracker to use the requested sampling rate (in Hz).
#        If the specified sampling rate is not valid for the eye tracker, an exception is created.
#        If this method is not supported by the eye tracker interface, EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED is returned.
#        Otherwise, the updated sampling rate value is returned.
# 
#        Args:
#            sampling_rate (float): The sample rate in Hz to set the eye tracker to.
#            
#        Return:
#            int: If the method is not supported, EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED is returned.
#
#            exception: If the provided sampling_rate value is not supported by the eye tracker, an exception is created.
#
#            float: The sampling rate the eye tracker is actually now set to in Hz.
#        """
#        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
#    def drawToHostApplicationWindow(self,graphic_type,**graphic_attributes):
#        """
#        The drawToHostApplicationWindow method provides a generic interface for 
#        ET devices that support having graphics drawn to the 
#        Host / Control Computer / Application gaze overlay area that used used 
#        by the eye tracker operator during experiment runtime to monitor eye 
#        tracking performance, or other similar graphics area functionality.
#
#        The define drawing operation types, one of which is passed to the graphic_type
#        input parameter of the method, are specified in the EyeTrackerConstants class:
#
#            #. EyeTrackerConstants.CLEAR_GRAPHICS: Clear all graphics from the eye trackers drawing reagion.
#            #. EyeTrackerConstants.IMAGE_GRAPHIC: Draw an image to the eye trackers drawing region.
#            #. EyeTrackerConstants.LINE_GRAPHIC: Draw a line to the eye trackers drawing region.
#            #. EyeTrackerConstants.MULTILINE_GRAPHIC: Draw amultiple connected lines to the eye trackers drawing region.
#            #. EyeTrackerConstants.RECTANGLE_GRAPHIC: Draw a rectangle to the eye trackers drawing region.
#            #. EyeTrackerConstants.CIRCLE_GRAPHIC: Draw a circle to the eye trackers drawing region.
#            #. EyeTrackerConstants.ELLIPSE_GRAPHIC: Draw an ellipse to the eye trackers drawing region.
#            #. EyeTrackerConstants.TEXT_GRAPHIC=107: Draw text to the eye trackers drawing region.
#        
#        The kwargs (graphic_attributes) passed to the method will be used as 
#        the required settings for the given graphic_type.
#        
#        If the implementation of the common eye tracker interface does not 
#        support this method, or does not support the provided graphic_type 
#        EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED is returned. 
#
#        If the implementation of the common eye tracker interface supports this
#        method and the provided graphic_type, the request will be processed.
#        Any graphic_attribute kwargs that are not used by the implementation 
#        being used will simply be ignored. graphic_attributes' that are required
#        but missing from the method call, or contain an invalid value for the given
#        graphic_attribute key, will return an exception with details on the error.
#        
#        If the method is successfully handled, EyeTrackerConstants.EYETRACKER_OK is reeturned.
#
#        Args:
#            graphic_type (int): One of the EyeTrackerConstants.*_GRAPHIC[S] constants
#            
#        Kwargs:
#            *various*: The valid kwargs for the method depend on the graphic_type value provided.
#            
#        Returns:
#            int: Either EyeTrackerConstants.EYETRACKER_OK or EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED.
#        """
#        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED    
#
#    def getDigitalPortState(self, port):
#        """
#        The getDigitalPortState method returns the current value of the specified 
#        digital port on the eye tracker computer.
#        
#        This method be used to read the parallel port or idigial lines on the
#        eye tracker computer if the eye tracker has such functionality.
#
#        If the implementation of the common eye tracker interface does not 
#        support this method EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED is returned. 
#
#        If the provided port number is not valid for the eye tracker computer, an exception will be returned.
#        
#        Args:
#            port (int): The base 10 equivelent of the digital port address to from on the eye tracker PC. Consult your eye tracker device  documentation for appropriate values.
#            
#        Kwargs:
#            None
#            
#        Returns:
#            int: The base 10 representation of the value read from the port. The maximum value of the result will depend on the number of bits read from the port on the eye tracker, but should not exceed 2**32 (i.e. 32 bits).
#        """ 
#        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
#         
#    def setDigitalPortState(self, port, value):
#        """
#        The setDigitalPortState method sets the value of the specified 
#        digital port on the eye tracker computer.
#        
#        This method can be used to set the parallel port or idigial lines on the
#        eye tracker computer if the eye tracker has such functionality.
#
#        If the implementation of the common eye tracker interface does not 
#        support this method EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED is returned. 
#
#        If the provided port number is not valid for the eye tracker computer, or the value is not within the valid range for the specified port, an exception will be returned.
#        
#        Args:
#            port (int): The base 10 equivelent of the digital port address to from on the eye tracker PC. Consult your eye tracker device  documentation for appropriate values.
#            value (int): The base 10 equivelent of the value to set on the specified port. Consult your eye tracker device documentation for appropriate values.
#            
#        Kwargs:
#            None
#            
#        Returns:
#            int: Either EyeTrackerConstants.EYETRACKER_OK or EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED.
#        """
#        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
#


    
    #
    # After some actual use, it is not clear to me that the idea of the experiment flow generic 
    # eye tracker methods are really of any practical use. Nice idea that does not 
    # work well in practice. ;)
    #
    # So for now these methods are being removed from the interface specification,
    # None of the existing implementations officially used or implemented them anyhow.
    #

#
#    def experimentStartDefaultLogic(self,*args,**kwargs):
#        """
#        Experiment Centered Generic method that is used to perform a set of
#        eye tracker default code associated with the start of an experiment.
#        """
#        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
# 
#    def blockStartDefaultLogic(self,*args,**kwargs):
#        """
#        Experiment Centered Generic method that can be used to perform a set of
#        eye tracker default code associated with the start of an experiment block.
#        """
#        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
#
#    def trialStartDefaultLogic(self,*args,**kwargs):
#        """
#        Experiment Centered Generic method that can be used to perform a set of
#        eye tracker default code associated with the start of an experiment trial.
#        """
#        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
#         
#    def trialEndDefaultLogic(self,*args,**kwargs):
#        """
#        Experiment Centered Generic method that can be used to perform a set of
#        eye tracker default code associated with the end of an experiment trial.
#        """
#        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
#         
#    def blockEndDefaultLogic(self,*args,**kwargs):
#        """
#        Experiment Centered Generic method that can be used to perform a set of
#        eye tracker default code associated with the end of an experiment block.
#        """
#        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED
#
#    def experimentEndDefaultLogic(self,*args,**kwargs):
#        """
#        Experiment Centered Generic method that can be used to perform a set of
#        eye tracker default code associated with the end of an experiment session.
#        """
#        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED