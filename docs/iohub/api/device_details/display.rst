================================
iohub.devices.display.Display
================================

Device description text TBC.

.. note:: 
    Supported Platforms: Linux, Windows (XP SP2, SP3, Windows 7)

.. autoclass:: iohub.devices.display.Display
    :exclude-members: ALL_EVENT_CLASSES, CLASS_ATTRIBUTE_NAMES, DEVICE_BUFFER_LENGTH_INDEX, DEVICE_CLASS_NAME_INDEX, DEVICE_MAX_ATTRIBUTE_INDEX, DEVICE_TIMEBASE_TO_SEC, DEVICE_TYPE_ID, DEVICE_TYPE_ID_INDEX, DEVICE_TYPE_STRING, DEVICE_USER_LABEL_INDEX, NUMPY_DTYPE, e, DEVICE_FIRMWARE_VERSION_INDEX, DEVICE_HARDWARE_VERSION_INDEX,DEVICE_MANUFACTURER_NAME_INDEX,DEVICE_MODEL_NAME_INDEX, DEVICE_MODEL_NUMBER_INDEX, DEVICE_NUMBER_INDEX, DEVICE_SERIAL_NUMBER_INDEX, DEVICE_SOFTWARE_VERSION_INDEX, EVENT_CLASS_NAMES

    
Display Device Configuration Settings
=======================================

**TODO: Update Display config settings**

To add the Display device to the iohub_config.yaml configuration file for and experiment,
add the following entry to the **monitor_devices** list::
 
    Display:
        # name: The name you want to assign to the device for the experiment
        #   This name is what will be used to access the device within the experiment
        #   script via the devices.[device_name] property of the ioHubConnection or
        #   ioHubExperimentRuntime classes.
        name: display

        # reporting_unit_type: Specify the coordinate space unit type that should
        #   be used for the stimulus screen during experiment runtime. 
        #   Currently only 'pixels' is supported, however 'degrees', 
        #   and 'normalized' will also be supported in the near future.
        reporting_unit_type: pixels
        
        # display_index: specify the diaply index to use to create the full 
        #   screen stimulus window on. The primary display is index 0, secondary
        #   display index 1, etc.
        display_index: 0  
        
        # physical_stimulus_area: specify the actual screen physical dimensions, in mm, 
        #   that is illuminated when the monitor and computer are on. 
        #   This should be measured when the monitor being used is in the screen
        #   resolution and refresh rate mode that will be used during the experiment,
        #   as the actual area of the screen that shows visual stimuli can change
        #   depending on the display mode it is in.
        #   This is true for many CRT monitors, but also for some LCD monitors 
        #   when they are not run at their native pixel resolution.
        #   screen stimulus window on. The primary display is index 0, secondary
        #   display index 1, etc.
        # width: the width of the active stimulus screen area in mm
        # height: the height of the active stimulus screen area in mm
        # unit_type: constant as mm
        physical_stimulus_area:
            width: 500
            height: 281
            unit_type: mm
        
        # default_eye_to_surface_distance: specify the distance from the eye to the
        #   defined point on the surface that is being used as the stimulus screen
        #   in mm. In situiations where a chin  rest or other form of head stabilization
        #   is not being used, enter the expected average distance of the eyes to
        #   the specified surface point.
        # surface_center: enter the distance from the eyes to the center of the 
        #   stimulus surface being used in mm.
        # unit_type: constant as mm
        default_eye_to_surface_distance:
            surface_center: 500
            unit_type: mm
            
        # display_pixel_origin: specify what the 0,0 point of the display is for
        # the experiment software being used. This defaults to what PsychoPy uses,
        # which is an origin in the center of the screen, or [0.5,0.5] of the
        # stimulus display screen width and height.
        # If using a stimulus package like pygame directly, set this to [0.0, 0.0],
        # to indicate that pygame has a screen origin of the top left hand  corner
        # of the screen.
        display_pixel_origin: [0.5,0.5]
        
        # psychopy_config_file: specify the name to give the psychopy Monitor 
        #   object that is created by the ioHub based on the ioHub Display 
        #   configuration settings.
        psychopy_config_file: ioHubDefault        

Display Event Types
====================

The Display Device currently has no associated event types.
