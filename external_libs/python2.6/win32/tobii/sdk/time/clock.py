
from tobii.sdk._native import tobiisdkpy

class Clock(object):
    def __init__(self):
        self._clock = tobiisdkpy.Clock()
    
    def get_time(self):
        """Returns the current time according to this Clock, in microseconds."""
        return self._clock.get_time()
    
    def get_resolution(self):
        """Returns the resolution of this Clock, in microseconds."""
        return self._clock.get_resolution()
