#####################################################
SR Research EyeLink EyeTracker Class
#####################################################

.. note::
    #. Supported Platforms: Windows (XP SP2, SP3, Windows 7)
    #. Supported EyeLink Eye Tracker Models:         
        All models of EyeLink should work with the ioHub eye tracker interface, however
        most testing has been done on an EyeLink 1000 monocular head supported system.
        Please report any issues found with using the interface with the EyeLink.

.. autoclass:: iohub.devices.eyetracker.hw.sr_research.eyelink.EyeTracker
    :exclude-members: ALL_EVENT_CLASSES, CLASS_ATTRIBUTE_NAMES, DEVICE_BUFFER_LENGTH_INDEX, DEVICE_CLASS_NAME_INDEX, DEVICE_MAX_ATTRIBUTE_INDEX, DEVICE_TIMEBASE_TO_SEC, DEVICE_TYPE_ID, DEVICE_TYPE_ID_INDEX, DEVICE_TYPE_STRING, DEVICE_USER_LABEL_INDEX, NUMPY_DTYPE, e, DEVICE_FIRMWARE_VERSION_INDEX, DEVICE_HARDWARE_VERSION_INDEX,DEVICE_MANUFACTURER_NAME_INDEX,DEVICE_MODEL_NAME_INDEX, DEVICE_MODEL_NUMBER_INDEX, DEVICE_NUMBER_INDEX, DEVICE_SERIAL_NUMBER_INDEX, DEVICE_SOFTWARE_VERSION_INDEX, EVENT_CLASS_NAMES, EYELINK, EYELINK_1000, EYELINK_II    

Installing other Necessary SR Research Software
##################################################

The EyeLink implementation of the ioHub common eye tracker interface uses the 
pyLink module written by SR Research. This package is bundled with the ioHub package, so
no display side software should be needed to use the ioHub with the EyeLink Common
Eye Tracker Interface.
    
EyeLink Device iohub_config.yaml Settings
###########################################

To specify the use of an EyeLink eye tracking device within your experiment,
the following can be added to the iohub_config.yaml file of your experiment in 
the devices list section. Note that this includes every supported parameter for 
the EyeLink eye tracker device in ioHub; most of the parameters can be left out of your 
experiment device listing as any parameters not included at the experiment configuration
level are filled in with the default value for the device implementation. The values
listed below are the default values for the EyeLink configuration:: 

    -eyetracker.hw.sr_research.eyelink.EyeTracker:
        # Indicates if the device should actually be loaded at experiment runtime.
        enable: True

        # The variable name of the device that will be used to access the ioHub Device class
        # during experiment run-time, via the devices.[name] attribute of the ioHub
        # connection or experiment runtime class.
        name: tracker

        # Should eye tracker events be saved to the ioHub DataStore file when the device
        # is recording data ?
        save_events: True

        # Should eye tracker events be sent to the PsychoPy process when the device
        # is recording data ?
        stream_events: True

        # The eyetracker.hw.sr_research.eyelink.EyeTracker class uses the polling method to
        # check for new events received from the eyelink device. device_timer.interval
        # specifies the sec.msec time between device polls. 0.001 = 1 msec, so the device will
        # be polled at a maxximum rate of 1000 Hz. This polling rate is a 'target' value,
        # and may not always be achieved depending on your computer specifications and the
        # number and type of other devices being used.
        device_timer:
            interval: 0.001

        # How many eye events (including samples) should be saved in the ioHub event buffer before
        # old eye events start being replaced my new events when the event buffer reaches
        # the maximum event length of the buffer defined here.
        event_buffer_length: 1024

        # The eyelink implementation of the common eye tracker interface supports the
        # following event types. If you would like to exclude certain events from being
        # saved or streamed during runtime, remove them from the list below.
        monitor_event_types: [ MonocularEyeSampleEvent, BinocularEyeSampleEvent, FixationStartEvent, FixationEndEvent, SaccadeStartEvent, SaccadeEndEvent, BlinkStartEvent, BlinkEndEvent]

        calibration:
            # eyetracker.hw.sr_research.eyelink.EyeTracker supports the following
            type: NINE_POINTS

            # auto_pace can be True or False. If True, the eye tracker will 
            # automatically progress from one calibration point to the next.
            # If False, a manual key or button press is needed to progress to
            # the next point.
            auto_pace: True
            
            # pacing_speed is the number of sec.msec that a calibration point should
            # be displayed before moving onto the next point when auto_pace is set to true.
            # If auto_pace is False, pacing_speed is ignored.
            pacing_speed: 1.5
            
            # screen_background_color specifies the r,g,b,a background color to 
            # set the calibration, validation, etc, screens to. Each element of the color
            # should be a value between 0 and 255. 0 == black, 255 == white. In general
            # the last value of the color list (alpha) can be left at 255, indicating
            # the color not mixed with the background color at all.
            screen_background_color: [128,128,128,255]
            
            # target type defines what form of calibration graphic should be used
            # during calibration, validation, etc. modes.
            # eyetracker.hw.sr_research.eyelink.EyeTracker supports the following
            # target types CIRCLE_TARGET      
            target_type: CIRCLE_TARGET

            # The asociated target attributes sub properties must be supplied
            # for the given target_type. If target type attribute sections are provided
            # for target types other than the entry associated with the specified target_type value
            # they will simple be ignored.
            target_attributes:
                outer_diameter: 33
                inner_diameter: 6
                outer_color: [255,255,255,255]
                inner_color: [0,0,0,255]

        # network_settings can be used to specify relevent network settings 
        # by eye tracker implementations that use a net interface to connect the
        # ioHub eye tracker interface to the eye tracking system.
        # The eyetracker.hw.sr_research.eyelink.EyeTracker implementation uses this
        # setting to specify the Host computer IP address. Normally leaving it set
        # to the default value is fine.
        network_settings: 100.1.1.1
        
        # The eyetracker.hw.sr_research.eyelink.EyeTracker supports saving a native eye
        # tracker edf data file, the default_native_data_file_name value is
        # used to set the default name for the file that will be saved, not including
        # the .edf file type extension
        default_native_data_file_name: et_data
        
        # simulation_mode can be True or False. This indicates if the eye tracker
        # should provide simulated eye data instead of sending eye data based on a 
        # participants actual eye movements. 
        simulation_mode: False
        
        # enable_interface_without_connection is a boolean specifying if the ioHub Device
        # should be enabled without truely connecting to the underlying eye tracking
        # hardware. If True, ioHub EyeTracker methods can be called but will
        # provide no-op results and no eye data will be received by the ioHub Server.
        # This mode can be useful for working on aspects of an eye tracking experiment when the
        # actual eye tracking device is not available, for example stimulus presentation
        # or other non eye tracker dependent experiment functionality.
        enable_interface_without_connection: False
        
        # VOG settings allow you to specify some eye tracker parameters related to
        # the image processing or data collection procedure used by the eye tracker
        # device. 
        runtime_settings:
            # eyetracker.hw.sr_research.eyelink.EyeTracker supports, dependent on 
            # model and mode, sampling rates of 250, 500, 1000, and 2000 Hz
            sampling_rate: 250
        
            # eyetracker.hw.sr_research.eyelink.EyeTracker supports the 
            # following track_eyes values:  LEFT_EYE, RIGHT_EYE, BINOCULAR
            track_eyes: RIGHT_EYE
            
            # Sample filtering defines the native eye tracker filtering level to be 
            # applied to the sample event data before it is sent to the specified data stream.
            # The sample filter section can contain multiple key : value entries if 
            # the tracker implementation supports it, where each key is a sample stream type,
            # and each value is the accociated filter level for that sample data stream.
            # eyetracker.hw.sr_research.eyelink.EyeTracker supported stream 
            # types are: FILTER_ALL, FILTER_FILE, FILTER_ONLINE
            # Supported eyetracker.hw.sr_research.eyelink.EyeTracker filter levels are:
            # FILTER_LEVEL_OFF, FILTER_LEVEL_1, FILTER_LEVEL_2
            # Note that if FILTER_ALL is specified, and other sample data stream values are
            # ignored.
            sample_filtering:
                FILTER_ALL: FILTER_LEVEL_OFF
            
            vog_settings:
                # The eyetracker.hw.sr_research.eyelink.EyeTracker supports one
                # pupil_measure_types parameter that is used for all eyes being tracked. 
                # The following is a list of valid pupil measure types for the
                # eyetracker.hw.sr_research.eyelink.EyeTracker:
                # PUPIL_AREA, PUPIL_DIAMETER,
                pupil_measure_types: PUPIL_AREA
            
                # tracking_mode defines whether the eye tracker should run in a pupil only
                # mode or run in a pupil-cr mode. Valid options are: 
                # PUPIL_CR_TRACKING, PUPIL_ONLY_TRACKING
                # Depending on other settngs on the eyelink Host and the model and mode of
                # eye tracker being used, this parameter may not be able to set the
                # specified tracking mode. CHeck the mode listed on the camera setup
                # screen of the Host PC after the experiment has started to confirm if
                # the requested tracking mode was enabled.
                tracking_mode: PUPIL_CR_TRACKING
                
                # The pupil_center_algorithm defines what type of image processing approach should
                # be used to determine the pupil center during image processing. 
                # Valid possible values are for eyetracker.hw.sr_research.eyelink.EyeTracker are:
                # ELLIPSE_FIT, or CENTROID_FIT
                pupil_center_algorithm: ELLIPSE_FIT
        
        # The model_name setting allows the definition of the eye tracker model being used.
        # For the eyelink implementation, valid values are:
        # 'EYELINK 1000 DESKTOP', 'EYELINK 1000 TOWER', 'EYELINK 1000 REMOTE', 'EYELINK 1000 LONG RANGE', 'EYELINK 2'
        model_name: EYELINK 1000 DESKTOP
        
        # manufacturer_name is used to store the name of the maker of the eye tracking
        # device. This is for informational purposes only.
        manufacturer_name: SR Research Ltd.
        
        # The below parameters are not used by the EyeLink Common Eye Tracker
        # Interface implementation, so they can either be ignored and not included
        # in the device configuration, or the relevent properties can be completed for
        # informational purposes only.        
        device_number: 0
        
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

Minimal EyeLink Device iohub_config.yaml Example
#####################################################
                
If the default value for a parameter is sufficient for your use of the device, the parameter
does not need to be included in your experiment iohub_config.yaml. Here is an example of
a *trimmed down* EyeLink configuration, only including the parameters that may want to be changed.
This is just an example, your device configuration may need to be different::

    -eyetracker.hw.sr_research.eyelink.EyeTracker:
        enable: True
        name: tracker
        device_timer:
            interval: 0.001
        calibration:
            type: NINE_POINTS
            auto_pace: True
            pacing_speed: 1.5
            screen_background_color: [128,128,128,255]
            target_attributes:
                outer_diameter: 33
                inner_diameter: 6
                outer_color: [255,255,255,255]
                inner_color: [0,0,0,255]
        simulation_mode: False
        runtime_settings:
            sampling_rate: 250
            track_eyes: RIGHT_EYE
            sample_filtering:
                FILTER_ALL: FILTER_LEVEL_OFF
            
            vog_settings:
                pupil_measure_types: PUPIL_AREA
                pupil_center_algorithm: ELLIPSE_FIT
                
Supported EyeTracker Device Event Types
########################################

**TO BE COMPLETED**

All EyeTracker event types are supported by the EyeLink implementation of the 
ioHub Common Eye Tracker Interface. The following is a list of the attributes
supported by the EyeLink for each event type::


    #. iohub.devices.eyetracker.MonocularEyeSampleEvent:
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
            #. gaze_x
            #. gaze_y
            #. pupil_measure_1
            #. pupil_measure1_type
            #. status
            
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
            #. status

    #. iohub.devices.eyetracker.FixationStartEvent: 
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

    #. iohub.devices.eyetracker.SaccadeStartEvent: 
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

    #. iohub.devices.eyetracker.SaccadeEndEvent: 
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

   #. iohub.devices.eyetracker.BlinkStartEvent: 
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

    #. iohub.devices.eyetracker.BlinkEndEvent: 
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


General Considerations
#######################

An example gaze contingent eye tracking project that is preconfigured for the 
SR Research EyeLink eye tracker implementation is available in the examples folder,
under eyetrackerExamples/srrTrackerTest.