
import threading

from tobii.sdk._native import tobiisdkpy
from tobii.sdk import _check_init

from tobii.sdk.mainloop import (Mainloop, MainloopThread)

class EyetrackerInfo(object):
    """EyetrackerInfo - An object describing a discovered eyetracker.
    
    The EyetrackerBrowser object returns this type of object when
    it discovers a new eyetracker. Only the EyetrackerBrowser may
    create instances of this object (at least only that makes sense).
    """
    def __init__(self, device_info):
        _check_init()

        self._device_info = device_info

    @property
    def product_id(self):
        """Returns this Eyetrackers' unique product id.
        
        This property is the discovered Eyetrackers' product id.
        The product id of an eyetracker is guaranteed to be unique.
        """
        return self._device_info["product-id"]
    
    @property
    def model(self):
        """Returns this Eyetrackers' model name, e.g. 'Tobii T120'."""
        return self._device_info["model"]
    
    @property
    def generation(self):
        """Returns this Eyetrackers' generation, e.g. 'TX'.
        
        The generation is mostly used to describe compatibility
        during upgrades as two eyetrackers with the same generation
        share the same firmware.
        """
        return self._device_info["generation"]
    
    @property
    def status(self):
        """Returns this Eyetrackers' current hardware status.
        
        The status can be any of:
           - "ok", the unit is working as expected
           - "upgrading", the unit is currently being upgraded
           - "not-working", the unit is not working as expected; this
               may however just be a transient error and no further
               information is available.
           - "error", the unit has encountered an error.
        """
        return self._device_info["status"]
    
    @property
    def firmware_version(self):
        """Returns this Eyetrackers' firmware version."""
        return self._device_info["firmware-version"]
    
    @property
    def factory_info(self):
        return self._device_info.get_factory_info()

    @property
    def given_name(self):
        """Returns this Eyetracker's user-assigned name."""
        return self._device_info["given-name"]
    
    def __str__(self):
        return self.product_id
    
    def __iter__(self):
        return self._device_info.__iter__()


class EyetrackerBrowser(object):
    """Browses for available eyetrackers.
    
    The constructor is given a mainloop and a callback. As
    soon as an eyetracker is found, has its properties updated
    or has been removed the callback is called on the mainloop.
    
    The callback shall be callable in the form:
    
        callback(event_type, event_name, eyetracker_info, *args)
        
    Where:
    
        - event_type: 0 for Found
                      1 for Updated
                      2 for Removed
        - event_name: either "Found", "Updated" or "Removed"
        - eyetracker_info: an EyetrackerInfo object
        - *args: (optional) more custom parameters
        
    """
    FOUND = 0
    UPDATED = 1
    REMOVED = 2
    
    def __init__(self, mainloop, callback, *args):
        """Creates an EyetrackerBrowser:
        
        Arguments:
           - mainloop: a Mainloop or MainloopThread to defer callbacks on
           - callback: the callable to use for events
           - *args: (optional) passed to the callback
        """
        _check_init()

        self._mainloop = None
        self._callback_args = args
        
        if not callable(callback):
            raise TypeError("callback must be callable")
        self._callback = callback
        self._callback_lock = threading.Lock()
        
        if mainloop is None:
            raise ValueError("EyetrackerBrowser requires the mainloop argument")
        
        if isinstance(mainloop, MainloopThread):
            self._mainloop = mainloop.mainloop
        elif isinstance(self._mainloop, Mainloop):
            self._mainloop = mainloop
        else:
            raise TypeError("EyetrackerBrowser requires the mainloop argument to be of type Mainloop or MainloopThread")
        
        self._device_browser = tobiisdkpy.DeviceBrowser(self._mainloop.mainloop, self._on_device_event_handler)
    
    def stop(self):
        """Stops the browsing for Eyetrackers.
        """
        self._callback_lock.acquire()
        self._callback = None
        self._callback_args = None
        self._device_browser = None
        self._callback_lock.release()
    
    #def current_list(self):
    #    """Gets a snapshot of available eyetrackers and their state."""
    #    return [EyetrackerInfo(dev) for dev in self._device_browser.get_current_list()]
    
    def _on_device_event_handler(self, event, device_info):
        if event < EyetrackerBrowser.FOUND or event > EyetrackerBrowser.REMOVED:
            return
        if device_info is None:
            return
        
        try:
            self._callback_lock.acquire()
            if self._callback is None:
                return
            else:
                callback = self._callback
                args = self._callback_args
            self._callback_lock.release()
            
            if event == EyetrackerBrowser.FOUND:
                event_name = "Found"
            elif event == EyetrackerBrowser.UPDATED:
                event_name = "Updated"
            else:
                event_name = "Removed"
               
            if args is None:
                callback(event, event_name, EyetrackerInfo(device_info))
            else:
                callback(event, event_name, EyetrackerInfo(device_info), *args)
        except Exception, ex:
            print "Exception during event trampoline: ", ex

def _get_native_device_info(device_info, argument_name="EyetrackerInfo"):
    if not isinstance(device_info, EyetrackerInfo):
        raise TypeError("Argument '%s' expected to be an EyetrackerInfo" % (argument_name))
    
    return device_info._device_info
