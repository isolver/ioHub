############################################
LC EyeGaze EyeTracker Implementation
############################################

.. note::
    Supported Platforms:
    
    Windows (XP SP2, SP3, Windows 7)
    

.. note::
    Supported LC EyeGaze Eye Tracker Models: 
    
    All LC EyeGaze Eye Tracking Systems sould work.  
    
.. note::
    An example gaze contingent eye tracking project that is preconfigured for the LC EyeGaze eye tracker implementation is available in the examples folder, under eyetrackerExamples/eyeGazeExploration.

.. autoclass:: iohub.devices.eyetracker.hw.lc_technologies.eyegaze.EyeTracker
    :exclude-members: ALL_EVENT_CLASSES, CLASS_ATTRIBUTE_NAMES, DEVICE_BUFFER_LENGTH_INDEX, DEVICE_CLASS_NAME_INDEX, DEVICE_MAX_ATTRIBUTE_INDEX, DEVICE_TIMEBASE_TO_SEC, DEVICE_TYPE_ID, DEVICE_TYPE_ID_INDEX, DEVICE_TYPE_STRING, DEVICE_USER_LABEL_INDEX, NUMPY_DTYPE, e, DEVICE_FIRMWARE_VERSION_INDEX, DEVICE_HARDWARE_VERSION_INDEX,DEVICE_MANUFACTURER_NAME_INDEX,DEVICE_MODEL_NAME_INDEX, DEVICE_MODEL_NUMBER_INDEX, DEVICE_NUMBER_INDEX, DEVICE_SERIAL_NUMBER_INDEX, DEVICE_SOFTWARE_VERSION_INDEX, EVENT_CLASS_NAMES, EYELINK, EYELINK_1000, EYELINK_II    

Installing other Necessary LC EyeGaze Software
##################################################

The LC EyeGaze implementation of the ioHub common eye tracker interface uses the 
LC EyeGaze C API written by LC Technologies.

All the necessary files are already in your LC EyeGaze software directory, which
**must** be located at C:\EyeGaze on the computer you are running the ioHub software
on. 

Please note that the minimum version of the LC EyeGaze client software supported by the ioHub
imperface is **??????**. 
    
LC EyeGaze Device iohub_config.yaml Settings
#############################################

To specify the use of an LC EyeGaze eye tracking device within your experiment,
the following can be added to the iohub_config.yaml file of your experiment in 
the devices list section. Note that this includes every supported parameter for 
the LC EyeGaze eye tracker device in ioHub; most of the parameters can be left out of your 
experiment device listing as any parameters not included at the experiment configuration
level are filled in with the default value for the device implementation. The values
listed below are the default values for the LC EyeGaze configuration:: 

    eyetracker.hw.lc_technologies.eyegaze.EyeTracker:
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
        
        # The LC EyeGaze implementation fo the ioHub eye tracker interface uses the polling method to
        # check for new events received from the LC EyeGaze device. device_timer.interval
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

        # The LC EyeGaze implementation of the common eye tracker interface supports the
        # following event types:
        # MonocularEyeSampleEvent, BinocularEyeSampleEvent  
        # The sample type used depends on the model of LC EyeGaze system being used.
        monitor_event_types: [ MonocularEyeSampleEvent, BinocularEyeSampleEvent]

        # This section of settings is related to the eye tracker calibration 
        # procedure.  
        calibration:
            # TBC
                        
        # The LC EyeGaze connection settings ... TBC ....
        
        # The LC EyeGaze supports saving a native eye tracker data file, the 
        # default_native_data_file_name value is used to set the name for
        # the file that will be saved, not including the file type extension.
        # If no native data file is required, set this value to an empty string, ''
        default_native_data_file_name: et_data
                
        # The model_name setting allows the definition of the eye tracker model being used.
        # For the LC EyeGaze implementation, valid values are:
        # 
        model_name: TBC
        
        # manufacturer_name is used to store the name of the maker of the eye tracking
        # device. This is for informational purposes only.
        manufacturer_name: LC Technologies
        
        # The below parameters are not used by the LC EyeGaze Common Eye Tracker
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

Minimal LC EyeGaze Device iohub_config.yaml Example
#####################################################

If the default value for a parameter is sufficient for your use of the device, the parameter
does not need to be included in your experiment iohub_config.yaml. Here is an example of
a *trimmed down* LC EyeGaze configuration, only including the parameters that may want to be changed.
This is just an example, your device configuration may need to be different::

    eyetracker.hw.hw.lc_technologies.eyegaze.EyeTracker:
        # Indicates if the device should actually be loaded at experiment runtime.
        enable: True

        # Use the default eye tracker variable name, but keep it here for reminders. ;)
        name: tracker
        
        # Given the high frame rate being used in this study, the polling interval has
        # been adjusted to 1 msec.
        device_timer:
            interval: 0.001

    **Section To Be Completed**



Supported EyeTracker Device Event Types
########################################

The LC EyeGaze implementation of the Common Eye Tracker Interface supports the 
following eye event types, with data being populated for the attributes listed 
with each event type:
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
            #. TBC

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
            #. TBC
            
General Considerations
#######################

** Last Updated:** April 11th, 2013

The following is a list of known limitations, issues, or untested areas of 
functionality in the LC EyeGaze Common Eye Tracker Interface implementation.           

    #. The calibration window that appears when eyetracker.runSetupProcedure() is called can only be displayed on the primary monitor of a multimonitor setup. Please factor this into your monitor configuration.
    #. The LC EyeGaze software **must** be installed on the computer running PsychoPy and ioHub in the C:\EyeGaze folder.
    #. Currently only monocular EyeGaze systems in a single PC configuration have been tested and are known to work. If you have an Eye Follower system, or use a two computer setup, please contact me if you would like to help test and work with me to fix any issues with binocular or dual PC setups for the EyeGaze.

Known Issues:              
---------------

    #. The eyetracker.runSetupProcedure() should be called 'before' creating the PsychoPy full screen window, otherwise the calibration screen may be blocked by the PsychoPy Window. This means that calibration can only be done at the start of the experiment. This issue is being looked into and will be resolved as soon as possible.