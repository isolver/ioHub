===============================
Gamepad Device and Events API
===============================

The ioHub supports the use of XInput compatible gamepads, such as the XBOX 360
controller for PCs or the Logitech F310 or F710. The full XInput 1.3 specification 
is supported. The XBOX 360 and Logitech F710 gamepads are wireless devices that 
also support providing 'rumble' (vibration) feedback to the user. The F310
gamepad is a wired device that does not have rumble support.
 

.. note:: 
    Supported Platforms: Windows (XP SP2, SP3, Windows 7).
    
    For the Logitech gamepads, be sure that the switch on the gamepad is set to the 
    'X' position, indicating that the gamepad will use the XInput protocal.
    
GamePad Device Configuration Settings
=======================================

**TODO: Update XInput Gamepad device config settings**

To add the GamePad device to the iohub_config.yaml configuration file for and experiment,
add the following entry to the **monitor_devices** list::
 
    - GamePad:
        # name: The name you want to assign to the device for the experiment
        #   This name is what will be used to access the device within the experiment
        #   script via the devices.[device_name] property of the ioHubConnection or
        #   ioHubExperimentRuntime classes.
        name: gamepad
        
        # enable: Specifies if the device should be enabled by ioHub and monitored
        #   for events. 
        #   True = Enable the device on the ioHub Server Process
        #   False = Disable the device on the ioHub Server Process. No events for 
        #       this device will be reported by the ioHub Server.
        enable: True

        # Up to 4 XInput 'users' can be connected to the computer at one time. The
        # gamepad's user ID is based on how many other gamepads are already connected to the
        # computer when the new gamepad turns on. If a gamepad with a lower user id
        # the disconnects from the computer, other gamepad user ids remain the same.
        # Therefore XInput user id is not equal to the index of the gamepad in a set 
        # of gamepads. If experiment should connect to the first active gamepad found, enter -1.
        # Otherwise enter the user_id (1-4) of he gamepad you wish to connect to.
        user_id: -1

        # saveEvents: *If* the ioHubDataStore is enabled for the experiment, then
        #   indicate if events for this device should be saved to the 
        #   data_collection/keyboard event group in the hdf5 event file.
        #   True = Save events for this device to the ioDataStore.
        #   False = Do not save events for this device in the ioDataStore.
        saveEvents: True
        
        
        # streamEvents: Indicate if events from this device should be made available
        #   during experiment runtime to the Experiment / PsychoPy Process.
        #   True = Send events for this device to  the Experiment Process in real-time.
        #   False = Do *not* send events for this device to the Experiment Process in real-time.
        streamEvents: True
        
        # auto_report_events: Indicate if events from this device should start being
        #   processed by the ioHub as soon as the device is loaded at the start of an experiment,
        #   or if events should only start to be monitored on the device when a call to the
        #   device's enableEventReporting method is made with a parameter value of True.
        #   True = Automatically start reporting events for this device when the experiment starts.
        #   False = Do not start reporting events for this device until enableEventReporting(True)
        #       is set for the device during experiment runtime.
        auto_report_events: True
        
        # interval: For device types that require the ioHub to poll for new events from the
        #   device continiously, the device_time: interval setting specifies how 
        #   requently the the device should be scheduled to be checked for new events.
        #   In general, setting the interval to be 50% of the event update rate 
        #   results in a good conbination of relatively small delays between when the ioHub
        #   detects the event compared to when the event was made available by the device 
        #   driver or other device related software, while at the same time not over polling
        #   the device and getting a very high percentage of polls where no new events are detected.
        #   So a balance between timing delays and CPU overhead is made. Depending on the device
        #   and how it is being used in the experiment, you may want to decrease or increase the polling interval.        
        device_timer:
            interval: 0.0025

        # event_buffer_length: Specify the maximum number of events (for each 
        #   event type the device produces) that can be stored by the ioHub Server
        #   before each new event results in the oldest event of the same type being
        #   discarded from the ioHub device event buffer.
        event_buffer_length: 256


GamePad Class Definition 
=========================

.. autoclass:: iohub.devices.xinput.Gamepad
    :exclude-members: DEVICE_LABEL , ALL_EVENT_CLASSES, CLASS_ATTRIBUTE_NAMES, DEVICE_BUFFER_LENGTH_INDEX, DEVICE_CLASS_NAME_INDEX, DEVICE_MAX_ATTRIBUTE_INDEX, DEVICE_TIMEBASE_TO_SEC, DEVICE_TYPE_ID, DEVICE_TYPE_ID_INDEX, DEVICE_TYPE_STRING, DEVICE_USER_LABEL_INDEX, NUMPY_DTYPE, e, DEVICE_FIRMWARE_VERSION_INDEX, DEVICE_HARDWARE_VERSION_INDEX,DEVICE_MANUFACTURER_NAME_INDEX,DEVICE_MODEL_NAME_INDEX, DEVICE_MODEL_NUMBER_INDEX, DEVICE_NUMBER_INDEX, DEVICE_SERIAL_NUMBER_INDEX, DEVICE_SOFTWARE_VERSION_INDEX, EVENT_CLASS_NAMES


GamePad Event Types
====================

.. autoclass:: iohub.devices.xinput.GamepadStateChangeEvent
    :exclude-members: DEVICE_ID_INDEX, filter_id, device_id, NUMPY_DTYPE, BASE_EVENT_MAX_ATTRIBUTE_INDEX, CLASS_ATTRIBUTE_NAMES, EVENT_CONFIDENCE_INTERVAL_INDEX, EVENT_DELAY_INDEX, EVENT_DEVICE_TIME_INDEX, EVENT_EXPERIMENT_ID_INDEX, EVENT_FILTER_ID_INDEX, EVENT_HUB_TIME_INDEX, EVENT_ID_INDEX, EVENT_LOGGED_TIME_INDEX, EVENT_SESSION_ID_INDEX, EVENT_TYPE_ID, EVENT_TYPE_ID_INDEX, EVENT_TYPE_STRING, IOHUB_DATA_TABLE, PARENT_DEVICE, createEventAsClass, createEventAsDict, createEventAsNamedTuple, e, namedTupleClass


.. autoclass:: iohub.devices.xinput.GamepadDisconnectEvent
    :exclude-members: DEVICE_ID_INDEX, filter_id, device_id, NUMPY_DTYPE, BASE_EVENT_MAX_ATTRIBUTE_INDEX, CLASS_ATTRIBUTE_NAMES, EVENT_CONFIDENCE_INTERVAL_INDEX, EVENT_DELAY_INDEX, EVENT_DEVICE_TIME_INDEX, EVENT_EXPERIMENT_ID_INDEX, EVENT_FILTER_ID_INDEX, EVENT_HUB_TIME_INDEX, EVENT_ID_INDEX, EVENT_LOGGED_TIME_INDEX, EVENT_SESSION_ID_INDEX, EVENT_TYPE_ID, EVENT_TYPE_ID_INDEX, EVENT_TYPE_STRING, IOHUB_DATA_TABLE, PARENT_DEVICE, createEventAsClass, createEventAsDict, createEventAsNamedTuple, e, namedTupleClass

