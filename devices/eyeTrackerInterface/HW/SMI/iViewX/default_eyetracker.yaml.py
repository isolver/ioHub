eyeTrackerInterface.HW.SMI.iViewX.EyeTracker:
    enable: True
    name: tracker
    saveEvents: True
    streamEvents: True
    device_timer:
        interval: 0.001
    event_buffer_length: 1024
    display_settings: *DisplaySettings
    runtime_settings:
        sampling_rate: 250
        track_eyes: BOTH
        default_calibration: HV9
        auto_calibration: True
        runtime_filtering:
            ALL: OFF
        default_native_data_file_name: et_data
        vog_settings:
            pupil_measure_types: DIAMETER
            tracking_mode: PUPIL-CR
            pupil_center_algorithm: CENTROID
