
import threading

from tobii.sdk.mainloop import (Mainloop, MainloopThread)
from tobii.sdk.browsing import (EyetrackerInfo)

from tobii.sdk._native import tobiisdkpy

class ProtocolError(Exception):
    def __init__(self, opcode, error, message=None):
        self.opcode = opcode
        self.error = error
        self.message = message
    
    def __str__(self):
        msg = "Protocol error occured during opcode %d: 0x%08x" % (self.opcode, self.error)
        if self.message is not None and len(self.message):
            msg += ": " + self.message
        return msg
    
class EyetrackerException(Exception):
    def __init__(self, error):
        self.error = error

class BasicEyetracker(object):
    """Internal base class for Eyetracker objects.
    """
    class ResponseHandlerFunctor(object):
        def __init__(self, data_converter, response_callback):
            self._data_converter = data_converter
            self._response_callback = response_callback
            self._subscribe_to = None
            self._subscribe_callback = None
            self._subscriber = None
            self._error = None
            self._result = None
            self._condition = threading.Condition()
            self._has_signaled = False
            
    
        def subscribe_to(self, subscriber, channel, callback):
            if subscriber is None:
                raise ValueError("Missing argument subscriber")
            
            if channel is None:
                raise ValueError("Cannot subscribe to a channel which is None")
            
            if callback is None or not callable(callback):
                raise ValueError("Callback may not be None and must be callable")
            
            self._subscriber = subscriber
            self._subscribe_to = channel
            self._subscribe_callback = callback
        
        def __call__(self, opcode, error, payload):
            # Set error code and result
            self._error = error
            if error != 0:
                self._result = None
            elif self._data_converter is None:
                self._result = None
            else:
                self._result = self._data_converter(payload)
                
            
            if self._subscribe_to is not None:
                self._subscriber._do_subscribe(self._subscribe_to, self._subscribe_callback)
            
            
            # Notify callback
            try:
                if self._response_callback is not None:
                    self._response_callback (self._error, self._result)
            except Exception, ex:
                print "Exception during response_callback:", ex
        
            
            # Notify waiting threads
            self._condition.acquire()
            self._condition.notify_all()
            self._has_signaled = True
            self._condition.release()       
            
        def wait_for_result(self):
            self._condition.acquire()
            if not self._has_signaled:
                self._condition.wait()
            self._condition.release()
            
            if self._error != 0:
                raise EyetrackerException(self._error)
                
            return self._result
                

    class ChannelHandlerFunctor(object):
        def __init__(self, data_converter, callback):
            self._data_converter = data_converter
            self._callback = callback
        
        def __call__(self, opcode, error, payload):
            try:
                if error != 0:
                    self._callback(error, None)
                else:
                    if self._data_converter is not None:
                        self._callback(error, self._data_converter(payload))
                    else:
                        self._callback(error, None)
            except Exception, ex:
                print "Exception during ChannelHandlerFunctor.__call__(): ", ex
    
    def __init__(self, message_passer):
        """Creates a new Eyetracker instance from the supplied EyetrackerInfo.
        Attaches the eyetracker to the supplied mainloop which can be either
        a Mainloop or MainloopThread object.        
        """
        self._message_passer = message_passer
        if self._message_passer is None:
            raise ValueError("message_passer cannot be None")
    
        self._connections_lock = threading.Lock()
        self._connections = {}
    
    @classmethod
    def create_async(cls, mainloop, eyetracker_info, callback, *args, **kwargs):
        """Creates a new Eyetracker instance from the supplied EyetrackerInfo.
        Attaches the eyetracker to the supplied mainloop which can be either
        a Mainloop or MainloopThread object.
        
        The Eyetracker is delivered asynchronously to the supplied
        callback.
        
        callback is invoked as such:
            callback(eyetracker, *args, **kwargs)
        """
        ml = None
        if isinstance(mainloop, Mainloop):
            ml = mainloop
        elif isinstance(mainloop, MainloopThread):
            ml = mainloop.mainloop
        else:
            raise TypeError("mainloop must be of type Mainloop or MainloopThread")
        
        fi = None
        if isinstance(eyetracker_info, EyetrackerInfo):
            fi = eyetracker_info.factory_info
        else:
            raise TypeError("info must be an instance of EyetrackerInfo")
        
        def trampoline(error, message_passer, cls, callback, *args, **kwargs):
            if error:
                callback(error, None, *args, **kwargs)
            else:
                callback(0, cls(message_passer), *args, **kwargs)
        tobiisdkpy.get_message_passer(fi, ml.mainloop, lambda e, m: trampoline(e, m, cls, callback, *args, **kwargs))
        
    
    def _do_subscribe(self, channel, callback):
        self._connections_lock.acquire()
        try:
            self._connections[channel] = self._message_passer.add_data_handler (channel, callback)
        except:
            self._connections_lock.release()
            raise
        self._connections_lock.release()
    
    def _do_unsubscribe(self, channel):
        self._connections_lock.acquire()
        try:
            del self._connections[channel]
        except:
            self._connections_lock.release()
            raise
        self._connections_lock.release()
