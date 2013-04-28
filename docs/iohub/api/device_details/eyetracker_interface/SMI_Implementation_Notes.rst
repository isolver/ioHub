############################################
SMI iViewX EyeTracker Implementation
############################################

.. note::
    Supported Platforms:
    
    Windows (XP SP2, SP3, Windows 7)
    

.. note::
    Supported iViewX Eye Tracker Models: 
    
    iViewX High Speed, iViewX RED, iViewX RED-m, iViewX fMRI, iViewX EEG  
    
.. note::
    An example gaze contingent eye tracking project that is preconfigured for the SMI iViewX eye tracker implementation is available in the examples folder, under eyetrackerExamples/smiTrackerTest.

.. autoclass:: iohub.devices.eyetracker.hw.smi.iviewx.EyeTracker
    :exclude-members: ALL_EVENT_CLASSES, CLASS_ATTRIBUTE_NAMES, DEVICE_BUFFER_LENGTH_INDEX, DEVICE_CLASS_NAME_INDEX, DEVICE_MAX_ATTRIBUTE_INDEX, DEVICE_TIMEBASE_TO_SEC, DEVICE_TYPE_ID, DEVICE_TYPE_ID_INDEX, DEVICE_TYPE_STRING, DEVICE_USER_LABEL_INDEX, NUMPY_DTYPE, e, DEVICE_FIRMWARE_VERSION_INDEX, DEVICE_HARDWARE_VERSION_INDEX,DEVICE_MANUFACTURER_NAME_INDEX,DEVICE_MODEL_NAME_INDEX, DEVICE_MODEL_NUMBER_INDEX, DEVICE_NUMBER_INDEX, DEVICE_SERIAL_NUMBER_INDEX, DEVICE_SOFTWARE_VERSION_INDEX, EVENT_CLASS_NAMES, EYELINK, EYELINK_1000, EYELINK_II    

Installing other Necessary SMI Software
##################################################

The SMI iViewX implementation of the ioHub common eye tracker interface uses the 
32 bit SMI C SDK written by SensoMotoric Instruments. 

Please ensure the location of the 32-bit SMI iViewX SDK DLLs are in a directory 
listed in your system PATH variable; or add the 32-bit SMI iViewX SDK bin directory to your
system PATH. For a 64 bit OS, this path is usually:

    >> C:\Program Files (x86)\SMI\iView X SDK\bin

For a 32 bit OS, the path is likely:

    >> C:\Program Files\SMI\iView X SDK\bin

SMI iViewX Device iohub_config.yaml Settings
#############################################

To specify the use of an SMI iViewX eye tracking device within your experiment,
the following can be added to the iohub_config.yaml file of your experiment in 
the devices list section. Note thatthis includes every supported parameter for 
the iViewX eye tracker device in ioHub; most of the parameters can be left out of your 
experiment device listing as any parameters not included at the experiment configuration
level are filled in with the default value for the device implementation. The values
listed below are the default values for the iViewX configuration:: 

    eyetracker.hw.smi.iviewx.EyeTracker:
        # Indicates if the device should actually be loaded at experiment runtime.
        enable: True

        # The variable name of the device that will be used to access the ioHub Device class
        # during experiment run-time, via the devices.[name] attribute of the ioHub
        # connection or experiment runtime class.
        name: tracker

        # Should eye tracker events be saved to the ioHub DataStore file when the device
        # is recording data ?
        save_events: True
        
        # Should eye tracker events be sent to the Experiment process when the device
        # is recording data ?
        stream_events: True
        
        # The iViewX implementation fo the ioHub eye tracker interface uses the polling method to
        # check for new events received from the iViewX device. device_timer.interval
        # specifies the sec.msec time between device polls. 0.002 = 2 msec, so the device will
        # be polled at a maxximum rate of 500 Hz. This polling rate is a 'target' value,
        # and may not always be achieved depending on your computer specifications and the
        # number and type of other devices being used. Valid polling intervals are between
        # 0.001 and 0.20 seconds.
        device_timer:
            interval: 0.002

        # How many eye events (including samples) should be saved in the ioHub event buffer before
        # old eye events start being replaced my new events when the event buffer reaches
        # the maximum event length of the buffer defined here.
        # Valid values are between 32 and 2048 events.
        event_buffer_length: 1024

        # The iViewX implementation of the common eye tracker interface supports the
        # following event types:
        # BinocularEyeSampleEvent, FixationStartEvent, FixationEndEvent  
        # If you would like to exclude certain events from being saved or streamed during runtime, 
        # remove them from the list below.
        monitor_event_types: [ BinocularEyeSampleEvent, FixationStartEvent, FixationEndEvent]

        # This section of settings is related to the eye tracker calibration 
        # procedure.  
        calibration:
            # How many points should be presented during the calibration phase of the
            # setup method? Different models of the SMI iViewX system support different
            # numbers of calibration points, as follows:
            #   RED: TWO_POINTS,FIVE_POINTS,NINE_POINTS
            #   REDm: NO_POINTS,ONE_PONT,TWO_POINTS,FIVE_POINTS,NINE_POINTS
            #   High Speed or MRI: FIVE_POINTS, NINE_POINTS, THIRTEEN_POINTS
            #   HED: FIVE_POINTS, THIRTEEN_POINTS (with HT)
            type: FIVE_POINTS
            
            # Should the presentation of the calibration points automatically proceed
            # when the eye tracking device has detected a period of eye stability?
            # If False, points will only progress when the SPACE key is pressed.
            auto_pace: True
            
            # If auto_pace is True, how fast should the system move to the next point?
            # Valid options are SLOW and FAST
            pacing_speed: SLOW
            
            # The calibration screen background color can be specified as an integer
            # representing the greyscale value to set the calibration screen background
            # color to. The value can be between 0 and 255, where 0 is black and 255 is white.
            screen_background_color: 20
            
            # What type of target shape should be used for the calibration procedure?
            # Valid options are currently CIRCLE_TARGET and CROSS_TARGET
            target_type: CIRCLE_TARGET
            
            # Define settable attributes of the target......
            target_attributes:
                # The pixel radius of the target shape.
                target_size: 10
                
                # The target color can be specified as an integer
                # representing the greyscale color value. Valid values can be 
                # between 0 and 255, where 0 is black and 255 is white.
                target_color: 239

            # Should a Window showing the validation accuracy as a gaze point 
            # overlay be displayed following a validation procedure?
            show_validation_accuracy_window: False
                        
        # The iViewX network settings specify the ioHub computer IP and port and the
        # iViewX Application / Server Computer IP and port. By default the configuration
        # is set to the popular single PC configuration for the system.
        network_settings:
            # IP address of iViewX Apllication or Server computer
            send_ip_address: 127.0.0.1
            
            # Port being used by iView X SDK for sending data to iView X 
            send_port: 4444
            
            # IP address of local computer
            receive_ip_address: 127.0.0.1
            
            # port being used by iView X SDK for receiving data from iView X
            receive_port: 5555	            
        
        # The iViewX supports saving a native eye tracker data file, the 
        # default_native_data_file_name value is used to set the name for
        # the file that will be saved, not including the file type extension.
        # If no native data file is required, set this value to an empty string, ''
        default_native_data_file_name: et_data
        
        # The runtime_settings section of the eye tracker configuration allows the control
        # settings related to data collection parameters supported by the eye tracker. 
        runtime_settings:
            # The sampling rate setting in the iViewX implementation is used only to
            # compare the sampling rate read from the device to ensure it matches
            # the rate specified here. It is not possible to 'set' the sampling rate
            # via the SMI API however. 
            sampling_rate: 60
            
            # The SMI supports enabling or disabling sample filtering. Use the
            # sample stream type 'FILTER_ALL' with a filter level of either
            # FILTER_OFF or FILTER_ON
            sample_filtering:
                FILTER_ALL: FILTER_OFF
                
            # The iViewX supports the following track_eyes values:  
            # LEFT_EYE, RIGHT_EYE, BINOCULAR_AVERAGED
            track_eyes: BINOCULAR_AVERAGED
            
            # VOG settings allow you to specify some eye tracker parameters related to
            # the image processing or data collection procedure used by the eye tracker
            # device. 
            vog_settings:
                # The iViewX supports one pupil_measure_types parameter that is used
                # for any eyes being tracked. PUPIL_DIAMETER_MM, PUPIL_DIAMETER are
                # the valid pupil measure types for the iViewX, depending on the model being used.
                pupil_measure_types: PUPIL_DIAMETER_MM
                
        # The model_name setting allows the definition of the eye tracker model being used.
        # For the iViewX implementation, valid values are:
        # RED, REDm, HiSpeed, MRI, HED, ETG, or Custom
        model_name: REDm
        
        # manufacturer_name is used to store the name of the maker of the eye tracking
        # device. This is for informational purposes only.
        manufacturer_name: SensoMotoric Instruments GmbH
        
        # The below parameters are not used by the SMI iViewX Common Eye Tracker
        # Interface implementation, however they can be completed for FYI purposes
        # at this time. Some of these properties will also be filled in at runtime by
        # the eye tracker interface once a connection as been made to the hardware.
        
        # The model number of the eye tracker device being used (if any).
        model_number: N/A

        # The serial number of the eye tracker device being used (if any).
        serial_number: N/A

        # The date of manufacture of the eye tracker device being used (if any).
        manufacture_date: DD-MM-YYYY

        # The software version of the eye tracker device being used (if any).
        software_version: N/A

        # The hardware of the eye tracker device being used (if any).
        hardware_version: N/A

        # The firmware number of the eye tracker device being used (if any).
        firmware_version: N/A 

Minimal SMI iViewX Device iohub_config.yaml Example
#####################################################

If the default value for a parameter is sufficient for your use of the device, the parameter
does not need to be included in your experiment iohub_config.yaml. Here is an example of
a *trimmed down* iViewX configuration, only including the parameters that may want to be changed.
This is just an example, your device configuration may need to be different::

    eyetracker.hw.smi.iviewx.EyeTracker:
        # Indicates if the device should actually be loaded at experiment runtime.
        enable: True

        # Use the default eye tracker variable name, but keep it here for reminders. ;)
        name: tracker
        
        # Given the high frame rate being used in this study, the polling interval has
        # been adjusted to 1 msec.
        device_timer:
            interval: 0.001

        # We only want Sample Events for this experiment.
        monitor_event_types: [ BinocularEyeSampleEvent,]

        # Keep most of the calibration settings so they can be tweaked for the
        # current experiments purposes.  
        calibration:
            # How many points should be presented during the calibration phase of the
            # setup method? 
            type: NINE_POINTS
            
            # Should the presentation of the calibration points automatically proceed
            # when the eye tracking device has detected a period of eye stability?
            # If False, points will only progress when the SPACE key is pressed.
            auto_pace: False

            # The calibration screen background color can be specified as an integer
            # representing the greyscale value to set the calibration screen background
            # color to. The value can be between 0 and 255, where 0 is black and 255 is white.
            screen_background_color: 128
            
            # Define settable attributes of the target......
            target_attributes:
                # The pixel radius of the target shape.
                target_size: 10
                
                # The target color can be specified as an integer
                # representing the greyscale color value. Valid values can be 
                # between 0 and 255, where 0 is black and 255 is white.
                target_color: 244
                        
        # Keep the network settings pulled out so we can switch to a
        # two computer setup if desired.
        network_settings:
            # IP address of iViewX Apllication or Server computer
            send_ip_address: 127.0.0.1
            
            # Port being used by iView X SDK for sending data to iView X 
            send_port: 4444
            
            # IP address of local computer
            receive_ip_address: 127.0.0.1
            
            # port being used by iView X SDK for receiving data from iView X
            receive_port: 5555	            
        
        # Do not save a native data file for this experiment.
        default_native_data_file_name:
        
        # In this example, an iViewX High Speed 1250 Hz system is being used
        # in monocular mode.
        runtime_settings:
            # The sampling rate setting in the iViewX implementation is used only to
            # compare the sampling rate read from the device to ensure it matches
            # the rate specified here. It is not possible to 'set' the sampling rate
            # via the SMI API however. 
            sampling_rate: 1250
                
            # The iViewX supports the following track_eyes values:  
            # LEFT_EYE, RIGHT_EYE, BINOCULAR_AVERAGED
            track_eyes: RIGHT_EYE
                
        # The model_name setting allows the definition of the eye tracker model being used.
        # For the iViewX implementation, valid values are:
        # RED, REDm, HiSpeed, MRI, HED, ETG, or Custom
        model_name: HiSpeed



Supported EyeTracker Device Event Types
########################################

The SMI iViewX implementation of the Common Eye Tracker Interface supports the 
following eye event types, with data being populated for the attributes listed 
with each event type:

    #. iohub.devices.eyetracker.BinocularEyeSampleEvent:
        #. Attributes supported:
            #. experiment_id
            #. session_id
            #. event_id
            #. event_type
            #. logged_time
            #. device_time
            #. time
            #. delay
            #. confidence_interval
            #. left_gaze_x
            #. left_gaze_y
            #. left_eye_cam_x (for remote models only)
            #. left_eye_cam_y (for remote models only)
            #. left_eye_cam_z (for remote models only)
            #. left_pupil_measure_1
            #. left_pupil_measure1_type
            #. right_gaze_x
            #. right_gaze_y
            #. right_eye_cam_x (for remote models only)
            #. right_eye_cam_y (for remote models only)
            #. right_eye_cam_z (for remote models only)
            #. right_pupil_measure_1
            #. right_pupil_measure1_type
            
    #. iohub.devices.eyetracker.FixationStartEvent: 
        
        Note that the iViewX system reports fixations when they end, so the FixationStartEvent is created at the same time as the FixationEndEvent in the current implementation.
        
        #. Attributes supported:
            #. experiment_id
            #. session_id
            #. event_id
            #. event_type
            #. logged_time
            #. device_time
            #. time
            #. delay
            #. confidence_interval
            #. eye

    #. iohub.devices.eyetracker.FixationEndEvent: 
        #. Attributes supported: 
            #. experiment_id
            #. session_id
            #. event_id
            #. event_type
            #. logged_time
            #. device_time
            #. time
            #. delay
            #. confidence_interval
            #. eye
            #. duration
            #. average_gaze_x
            #. average_gaze_y

General Considerations
#######################

**Last Updated:** April 11th, 2013

The following is a list of known limitations, issues, or untested areas of 
functionality in the iViewX Common Eye Tracker Interface             

    #. Dual tracker setup has noty been tested.
    #. Ensure screen physical settings are sent to tracker. 
    #. Handle the 'track_eyes' param. See pg 58 of SDK Manual.pdf.     
    #. Handle pupil_measure_types setting. (if possible)
    #. Use model_name setting (different logic may be needed for diff models.  
    #. Correctly set the pupil measure type and eyes_tracked setting. Currently set to constants.             
    #. Add support for fixation parsing criteria: SetEventDetectionParameter.
    #. Add native data file saving support.
    #. Implement sendCommand functionality.

Known Issues:              
---------------

    #. In RED-m, getTrackerTime function in C API returns last sample time, not current eye tracker time.
