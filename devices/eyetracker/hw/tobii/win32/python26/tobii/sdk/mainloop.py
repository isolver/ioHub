
import threading

from tobii.sdk import _check_init, CoreException
from tobii.sdk._native import tobiisdkpy

class Mainloop(object):
    """A mainloop is used by all asynchronous objects to
    defer handlers and callbacks to. 
    
    The function run() blocks until the function quit()
    has been called (and all queued handlers have been
    executed). The run() function will then execute all
    the handlers in order.
    """
    def __init__(self):
        _check_init()
        self.mainloop = tobiisdkpy.Mainloop()
    
    def run(self):
        """Executes deferred handles until quit() is called.
        
        WARNING: This function blocks until quit() is called.
        """
        try:
            self.mainloop.run()
        except CoreException, ce:
            print "Mainloop stopped because of unhandled CoreException,", ce
        except Exception, ex:
            print "Mainloop stopped because of unhandled Exception: ", ex
    
    def quit(self):
        """Signals to the run() function that it should quit
        as soon as all deferred handles have been run.
        """
        self.mainloop.quit() 


class MainloopThread(object):
    """A convenience thread wrapper around Mainloop.
    """
    def __init__(self, mainloop=None, delay_start=False):
        """Creates a new MainloopThread and either attaches an
        existing Mainloop to it or creates a new Mainloop.
        The argument delay_start (default: False) controls whether
        the thread should be started directly or not.
        """
        _check_init()
        
        if mainloop is None:
            self._mainloop = Mainloop()
        else:
            self._mainloop = mainloop
        
        self._thread = None
        if not delay_start:
            self.start()
    
    def start(self):
        """Starts the mainloop thread. If the thread has already been
        started, then this function does nothing.
        """
        if self._thread is not None:
            return
        self._thread = threading.Thread(target = self._mainloop.run)
        self._thread.start ()

    def stop(self):
        """Stops the mainloop thread. If the thread is not currently
        running then this function does nothing.
        """
        if self._thread is None:
            return
        self._mainloop.quit()
        self._thread.join()
        self._thread = None
    
    @property
    def mainloop(self):
        """Returns the attached mainloop.
        """
        return self._mainloop

def _get_native_mainloop(mainloop, argument_name="mainloop"):
    if isinstance(mainloop, Mainloop):
        return mainloop.mainloop
    
    if isinstance(mainloop, MainloopThread):
        return mainloop.mainloop.mainloop
    
    raise TypeError("Argument '%s' was expected to be either a Mainloop or MainloopThread" % (argument_name))
