
from tobii.sdk._native import tobiisdkpy
from tobii.sdk.time.clock import Clock
from tobii.sdk.mainloop import Mainloop, MainloopThread
from tobii.sdk.browsing import EyetrackerInfo

class State(object):
    UNSYNCHRONIZED = 0
    STABILIZING = 1
    SYNCHRONIZED = 2
    
    def __init__(self, internal_state):
        self._internal_state = internal_state
    
    @property
    def state_flag(self):
        """Returns either UNSYNCHRONIZED, STABILIZING or SYNCHRONIZED"""
        return self._internal_state.get_state_flag()
    
    @property
    def points_in_use(self):
        """Returns a list of tuples with three values in them, where the
            values in the tuple are:
              local_midpoint
              remote
              roundtrip
        """
        return self._internal_state.get_points_in_use()
    
    @property
    def error_approximation(self):
        """Returns an approximation of the current synchronization error."""
        return self._internal_state.get_error_approximation()
    

class SyncManager(object):
    def __init__(self, clock, eyetracker_info, mainloop, error_handler=None, status_handler=None):
        if not isinstance(clock, Clock):
            raise TypeError("clock should be of type Clock")
        if not isinstance(eyetracker_info, (tobiisdkpy.factory_info, EyetrackerInfo)):
            raise TypeError("factory_info should be of type EyetrackerInfo")
        if not isinstance(mainloop, Mainloop) and \
                not isinstance(mainloop, MainloopThread):
            raise TypeError("mainloop should of type Mainloop or MainloopThread")
        
        if error_handler is not None:
            if not callable(error_handler):
                raise TypeError("error_handler should be callable")
        if status_handler is not None:
            if not callable(status_handler):
                raise TypeError("status_handler should be callable")
        
        cl = clock._clock
        
        ml = None
        if isinstance(mainloop, MainloopThread):
            ml = mainloop._mainloop.mainloop
        else:
            ml = mainloop.mainloop
        
        fi = None
        if isinstance(eyetracker_info, EyetrackerInfo):
            fi = eyetracker_info.factory_info
        else:
            fi = eyetracker_info
        
        self._error_handler = error_handler
        self._status_handler = status_handler
        self._sync_manager = tobiisdkpy.SyncManager(cl, fi, ml,
                                                    self._on_error,
                                                    self._on_status)
    
    
    def convert_from_local_to_remote(self, local_usecs):
        return self._sync_manager.convert_from_local_to_remote(local_usecs)
    
    def convert_from_remote_to_local(self, remote_usecs):
        return self._sync_manager.convert_from_remote_to_local(remote_usecs)
    
    @property
    def sync_state(self):
        """Returns the current sync state"""
        return State(self._sync_manager.get_sync_state())
        
    
    def _on_error(self, error):
        if self._error_handler is None:
            return
        try:
            self._error_handler(error)
        except:
            pass
    
    def _on_status(self, state):
        if self._status_handler is None:
            return
        try:
            self._status_handler(State(state))
        except:
            pass
