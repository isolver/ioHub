############################################
Tobii EyeTracker Class
############################################

.. note::
    Supported Platforms:
    
    Windows (XP SP2, SP3, Windows 7), Linux should work as well, but has yet to be tested.
    
    Supported Tobii Eye Tracker Models: 
    
    Tobii Analytics SDK 3.0 RC 1, which is the Tobii software that the Tobii implementation of the ioHub common eye tracker interface relies on, supports the following eye trackers out-of-the-box: Tobii X60, Tobii X120, Tobii T60, Tobii T120, Tobii T60 XL, Tobii TX300 and Tobii IS-1. 
    Tobii Analytics SDK 3.0 RC 1 does **not** support the following eye trackers, and therefore neither does the ioHub common eye tracker interface: Tobii 1750, Tobii X50, Tobii 2150, Tobii 1740 (D10), Tobii P10, C-Eye, and PCEye. Support for Tobii 1750, Tobii X50 and Tobii 2150 models will be added in a later firmware release.
    
.. note::    
    Currently Python 2.6 must be used to use the Tobii eye tracker, Python 2.7 is not supported. When a Python 2.7 compatible version of the Tobii Python package becomes available, the Tobii system will also be able to use used within PsychoPy and ioHub when running Python 2.7.

.. autoclass:: iohub.devices.eyetracker.hw.tobii.EyeTracker
    :exclude-members: ALL_EVENT_CLASSES, CLASS_ATTRIBUTE_NAMES, DEVICE_BUFFER_LENGTH_INDEX, DEVICE_CLASS_NAME_INDEX, DEVICE_MAX_ATTRIBUTE_INDEX, DEVICE_TIMEBASE_TO_SEC, DEVICE_TYPE_ID, DEVICE_TYPE_ID_INDEX, DEVICE_TYPE_STRING, DEVICE_USER_LABEL_INDEX, NUMPY_DTYPE, e, DEVICE_FIRMWARE_VERSION_INDEX, DEVICE_HARDWARE_VERSION_INDEX,DEVICE_MANUFACTURER_NAME_INDEX,DEVICE_MODEL_NAME_INDEX, DEVICE_MODEL_NUMBER_INDEX, DEVICE_NUMBER_INDEX, DEVICE_SERIAL_NUMBER_INDEX, DEVICE_SOFTWARE_VERSION_INDEX, EVENT_CLASS_NAMES

Installing other Necessary Tobii Software
##################################################

The ioHub Common Eye Tracker Interface implementation for Tobii uses the Python 2.6
package that is provided by Tobii as part of their 32-bit Tobii Analytics SDK 3.0 RC 1 package. 

Please ensure that the Following files and folder are in your Python Path and system PATH.
This is often most easily done by copying these file and folder to your Python 2.6
site-packages folder, located at something like C:\Python26\Lib\site-packages.

Required files / folder from the Tobii Analytics SDK 3.0 RC 1 package:

    *.  The directory named 'tobii' found in the Python files area of the 32-bit Tobii Analytics SDK 3.0 RC 1 package.
    *.  tobiisdk.dll
    *.  _tobiisdkpy26.pyd
    *.  boost_python-vc90-mt-1_41.dll

Again, the one directory and 3 files listed above must be in a directory that is in your
Python 2.6 Python Path, as well as in your system PATH environment variable setting.
By placing these four items in your Python 2.6 site packages directory, this can be
achieved without needing to change your system environment variables.

Tobii Device iohub_config.yaml settings
#########################################

To specify the use of a Tobii eye tracking device within your experiment,
add the following to the iohub_config.yaml file in the devices list::
 
    -eyetracker.hw.tobii.EyeTracker:
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

        # How many eye events (including samples) should be saved in the ioHub event buffer before
        # old eye events start being replaced by new events. When the event buffer reaches
        # the maximum event length of the buffer defined here, older events will start to be dropped.
        event_buffer_length: 1024

        # The Tobii implementation of the common eye tracker interface supports the
        # BinocularEyeSampleEvent event type.
        monitor_event_types: [ BinocularEyeSampleEvent,]

        # The model name of the Tobii device that you wish to connect to can be specified here,
        # and only Tobii systems matching that model name will be considered as possible candidates for connection.
        # If you only have one Tobii system connected to the computer, this field can just be left empty.
        model_name:

        # The serial number of the Tobii device that you wish to connect to can be specified here,
        # and only the Tobii system matching that serial number will be connected to, if found.
        # If you only have one Tobii system connected to the computer, this field can just be left empty,
        # in which case the first Tobii device found will be connected to.
        serial_number:

        calibration:
            # The Tobii ioHub Common Eye Tracker Interface currently support 
            # a 3, 5 and 9 point calibration mode.
            # THREE_POINTS,FIVE_POINTS,NINE_POINTS
            type: NINE_POINTS

            # Should the target positions be randomized?
            randomize: True
            
            # auto_pace can be True or False. If True, the eye tracker will 
            # automatically progress from one calibration point to the next.
            # If False, a manual key or button press is needed to progress to
            # the next point.
            auto_pace: True
            
            # pacing_speed is the number of sec.msec that a calibration point should
            # be displayed before moving onto the next point when auto_pace is set to true.
            # If auto_pace is False, pacing_speed is ignored.
            pacing_speed: 1.5
            
            # screen_background_color specifies the r,g,b background color to 
            # set the calibration, validation, etc, screens to. Each element of the color
            # should be a value between 0 and 255. 0 == black, 255 == white.
            screen_background_color: [128,128,128]
            
            # Target type defines what form of calibration graphic should be used
            # during calibration, validation, etc. modes.
            # Currently the Tobii implementation supports the following
            # target type: CIRCLE_TARGET. 
            # To do: Add support for other types, etc.
            target_type: CIRCLE_TARGET
            
            # The associated target attribute properties can be supplied
            # for the given target_type. 
            target_attributes:
                # the outer diameter of the circle, in pixels.
                outer_diameter: 33
                
                # the inner diameter of the circle, in pixels.
                inner_diameter: 6
                
                # The color to use for the outer target 'ring'.
                outer_color: [255,255,255]
                
                # The color to use for the center of the target.
                inner_color: [0,0,0]
        
        runtime_settings:
            # The supported sampling rates for Tobii are model dependent. 
            # Using a defualt of 60 Hz, with the assumption it is the most common.
            sampling_rate: 60

            # Tobii supports BINOCULAR tracking mode only.
            track_eyes: BINOCULAR
                
        # manufacturer_name is used to store the name of the maker of the eye tracking
        # device. This is for informational purposes only.
        manufacturer_name: Tobii Technology
        
        # The below parameters are not used by the Tobii common eye tracker
        # interface implementation. They can be ignored an left out of your
        # device configuration, or you can complete any ones that are relevent for FYI
        # purposes only at this time.
        device_number: 0
        
        model_number: N/A
        
        manufacture_date: DD-MM-YYYY
        
        software_version: N/A
        
        hardware_version: N/A
        
        firmware_version: N/A

Minimal Tobii Device iohub_config.yaml Example
#####################################################

If the default value for a parameter is sufficient for your use of the device, the parameter
does not need to be included in your experiment iohub_config.yaml. Here is an example of
a *trimmed down* Tobii configuration, only including the parameters that may want to be changed.
This is just an example, your device configuration may need to be different::

    - eyetracker.hw.tobii.EyeTracker:
        # Indicates if the device should actually be loaded at experiment runtime.
        enable: True

        # The variable name of the device that will be used to access the ioHub Device class
        # during experiment run-time, via the devices.[name] attribute of the ioHub
        # connection or experiment runtime class.
        name: tracker

        # The model name of the Tobii device that you wish to connect to can be specified here,
        # and only Tobii systems matching that model name will be considered as possible candidates for connection.
        # If you only have one Tobii system connected to the computer, this field can just be left empty.
        model_name:

        # The serial number of the Tobii device that you wish to connect to can be specified here,
        # and only the Tobii system matching that serial number will be connected to, if found.
        # If you only have one Tobii system connected to the computer, this field can just be left empty,
        # in which case the first Tobii device found will be connected to.
        serial_number:

        calibration:
            # The Tobii ioHub Common Eye Tracker Interface currently support 
            # a 3, 5 and 9 point calibration mode.
            # THREE_POINTS,FIVE_POINTS,NINE_POINTS
            type: NINE_POINTS

            # Should the target positions be randomized?
            randomize: True
            
            # auto_pace can be True or False. If True, the eye tracker will 
            # automatically progress from one calibration point to the next.
            # If False, a manual key or button press is needed to progress to
            # the next point.
            auto_pace: True
            
            # pacing_speed is the number of sec.msec that a calibration point should
            # be displayed before moving onto the next point when auto_pace is set to true.
            # If auto_pace is False, pacing_speed is ignored.
            pacing_speed: 1.5
            
            # screen_background_color specifies the r,g,b background color to 
            # set the calibration, validation, etc, screens to. Each element of the color
            # should be a value between 0 and 255. 0 == black, 255 == white.
            screen_background_color: [128,128,128]
            
            # Target type defines what form of calibration graphic should be used
            # during calibration, validation, etc. modes.
            # Currently the Tobii implementation supports the following
            # target type: CIRCLE_TARGET. 
            # To do: Add support for other types, etc.
            target_type: CIRCLE_TARGET
            
            # The associated target attribute properties can be supplied
            # for the given target_type. 
            target_attributes:
                # the outer diameter of the circle, in pixels.
                outer_diameter: 33
                
                # the inner diameter of the circle, in pixels.
                inner_diameter: 6
                
                # The color to use for the outer target 'ring'.
                outer_color: [255,255,255]
                
                # The color to use for the center of the target.
                inner_color: [0,0,0]
        
        runtime_settings:
            # The supported sampling rates for Tobii are model dependent. 
            # Using a defualt of 60 Hz, with the assumption it is the most common.
            sampling_rate: 60

Supported EyeTracker Device Event Types
########################################

The Tobii Analytics SDK 3.0 RC 1 provides real-time access to binocular sample data.
Therefore the BinocularEyeSample event type is supported when using a Tobii as 
the ioHub EyeTracker device. The following fields of the BinocularEyeSample event are 
supported:
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
            #. left_gaze_x:             maps to Tobii eye sample field LeftGazePoint2D.x
            #. left_gaze_y:             maps to LeftGazePoint2D.y
            #. left_eye_cam_x:          maps to LeftEyePosition3D.x
            #. left_eye_cam_y:          maps to LeftEyePosition3D.y
            #. left_eye_cam_z:          maps to LeftEyePosition3D.z
            #. left_pupil_measure_1:    maps to LeftPupil
            #. left_pupil_measure1_type: PUPIL_DIAMETER_MM
            #. right_gaze_x:            maps to Tobii eye sample field RightGazePoint2D.x
            #. right_gaze_y:            maps to RightGazePoint2D.y
            #. right_eye_cam_x:         maps to RightEyePosition3D.x
            #. right_eye_cam_y:         maps to RightEyePosition3D.y
            #. right_eye_cam_z:         maps to RightEyePosition3D.z
            #. right_pupil_measure_1:   maps to RightPupil
            #. right_pupil_measure1_type: PUPIL_DIAMETER_MM
            #. status:                  both left and right eye validity codes are encoded as LeftValidity*10+RightValidity


General Considerations
#######################

An example gaze contingent eye tracking project that is preconfigured for the 
Tobii eye tracker implementation is available in the examples folder, under 
eyetrackerExamples/tobiiTrackerTest. 

The Tobii Analytics SDK 3.0 RC 1 software provides streaming eye sample functionality,
there is no functionality to save the data being streamed to disk by the Tobii Analytics SDK 3.0 RC 1
itself. Therefore it is highly recommended that the ioDataStore be enabled for experiments using
the Tobii system, as the ioDataStore will save all sample events received from the Tobii system
when the ioHub EyeTracking device interface is in 'recording mode'. The hdf5 file saved
by the ioDataStore can then be used to retrieve the Tobii sample data for post hoc analysis.
