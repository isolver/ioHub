
from tobii.sdk import _check_init, _require_callable
from tobii.sdk._native import tobiisdkpy
from tobii.sdk.mainloop import _get_native_mainloop
from tobii.sdk.browsing import _get_native_device_info

def _load_package_file(package_path):
    file = open(package_path, 'rb')
    try:
        package_bytes = file.read()
    finally:
        file.close()
    return package_bytes

def package_is_compatible_with_device(mainloop, package_path, device_info):
    _check_init()
    
    package_bytes = _load_package_file(package_path)    
    if len(package_bytes) == 0:
        raise ValueError("file '%s' was empty" % (package_path))
        
    return tobiisdkpy.upgrade_package_is_compatible(_get_native_mainloop(mainloop),
                                                    package_bytes,
                                                    _get_native_device_info(device_info))


def begin_upgrade(mainloop,
                  package_path,
                  device_info,
                  completed_handler,
                  progress_handler,
                  cancancel_handler):
    """
        Parameters:
            - mainloop: either a Mainloop or MainloopThread
            - package_path: path to a tobiipkg file
            - device_info: an EyetrackerInfo
            - completed_handler: will be called like this:
                    completed_handler(error_code)
            - progress_handler: will be called like this:
                    progress_handler(current_step, number_of_steps, step_percentage)
    """
    _check_init()
    
    _require_callable(completed_handler, optional=False, argument_name="completed_handler")
    _require_callable(progress_handler, optional=True, argument_name="progress_handler")
    _require_callable(cancancel_handler, optional=True, argument_name="cancancel_handler")
        
    package_bytes = _load_package_file(package_path)
    if len(package_bytes) == 0:
        raise ValueError("file '%s' was empty" % (package_path))
    
    tobiisdkpy.upgrade_begin(_get_native_mainloop(mainloop),
                             package_bytes,
                             _get_native_device_info(device_info),
                             completed_handler,
                             progress_handler,
                             cancancel_handler)

