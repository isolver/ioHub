##################################
iohub.devices.daq.DAQDevice
##################################

Device description text TBC.

.. note:: 
    Supported Platforms: Windows (XP SP2, SP3, Windows 7)

.. autoclass:: iohub.devices.daq.AnalogInputDevice
    :exclude-members: ALL_EVENT_CLASSES, CLASS_ATTRIBUTE_NAMES, DEVICE_BUFFER_LENGTH_INDEX, DEVICE_CLASS_NAME_INDEX, DEVICE_MAX_ATTRIBUTE_INDEX, DEVICE_TIMEBASE_TO_SEC, DEVICE_TYPE_ID, DEVICE_TYPE_ID_INDEX, DEVICE_TYPE_STRING, DEVICE_USER_LABEL_INDEX, NUMPY_DTYPE, e, DEVICE_FIRMWARE_VERSION_INDEX, DEVICE_HARDWARE_VERSION_INDEX,DEVICE_MANUFACTURER_NAME_INDEX,DEVICE_MODEL_NAME_INDEX, DEVICE_MODEL_NUMBER_INDEX, DEVICE_NUMBER_INDEX, DEVICE_SERIAL_NUMBER_INDEX, DEVICE_SOFTWARE_VERSION_INDEX, EVENT_CLASS_NAMES
    
DAQ Device Configuration Settings
=======================================

**TODO: Update config file settings**

To add a DAQ device to the iohub_config.yaml configuration file for and experiment,
add the following entry to the **monitor_devices** list::
 
    XXXXXXXXXXXXXXX:
        # name: The name you want to assign to the device for the experiment
        #   This name is what will be used to access the device within the experiment
        #   script via the devices.[device_name] property of the ioHubConnection or
        #   ioHubExperimentRuntime classes.
        name: daq
        
        # enable: Specifies if the device should be enabled by ioHub and monitored
        #   for events. 
        #   True = Enable the device on the ioHub Server Process
        #   False = Disable the device on the ioHub Server Process. No events for 
        #       this device will be reported by the ioHub Server.
        enable: True
        
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
        
        # event_buffer_length: Specify the maximum number of events (for each 
        #   event type the device produces) that can be stored by the ioHub Server
        #   before each new event results in the oldest event of the same type being
        #   discarded from the ioHub device event buffer.
        event_buffer_length: 256

iohub.devices.daq.DAMultiChannelInputEvent
#############################################

.. autoclass:: iohub.devices.daq.MultiChannelAnalogInputEvent
    :members: 
    :inherited-members:

DAQ Hardware Implementations
######################################

The following links provide details on the common DAQ interface implementation
for each currently supported DAQ hardware device. It is very important to review
the documentation for the system you are using the common DAQ interface with.
By doing so it should be clear what areas of the common interface are supported by
a specific implementation and what areas are not.

.. toctree::
    :maxdepth: 2
    
    LabJack <daq_interface/LabJack_Implementation_Notes>
    Measurement Computing <daq_interface/MeasurementComputing_Implementation_Notes>