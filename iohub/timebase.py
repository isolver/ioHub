# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 08:10:06 2013

@author: Sol
"""
from __future__ import division


import sys

psychopy_available=False
try:
    import psychopy
    import psychopy.clock
    psychopy_available=True
except:
    pass

#: The getTime() function returns the heigh resolution clock time that is 
#: being used by ioHub (and PsychoPy). The getTime() function returns the
#: the time **without** applying an offset, as is done withe the actual time base
#: used by ioHub and PsychoPy. Therefore this function should rarely be called directly.
#: Instead get the current time by calling the ioHub Computer.getTime() method,
#: or the psychopy..logging.defaultClock.getTime() method. 
getTime=lambda x: x

monotonicClock=None
if psychopy_available:
    # Get abosolute time base
    getTime=psychopy.clock.getTime    
    # Get the MonotonicClock Class
    MonotonicClock = psychopy.clock.MonotonicClock
    # Get the default instance of the MonotonicClock class
    monotonicClock = psychopy.clock.monotonicClock
else:    
    # Select the timer to use as the ioHub high resolution time base. Selection
    # is based on OS and Python version. 
    # 
    # Three requirements exist for the ioHub time base implementation:
    #     A) The Python interpreter does not apply an offset to the times returned
    #        based on when the timer module being used was loaded or when the timer 
    #        fucntion first called was first called. 
    #     B) The timer implementation used must be monotonic and report elapsed time
    #        between calls, 'not' system or CPU usage time. 
    #     C) The timer implementation must provide a resolution of 50 usec or better.
    #
    # Given the above requirements, ioHub selects a timer implementation as follows:
    #     1) On Windows, the Windows Query Performance Counter API is used using ctypes access.
    #     2) On other OS's, if the Python version being used is 2.6 or lower,
    #        time.time is used. For Python 2.7 and above, the timeit.default_timer
    #        function is used.
    if sys.platform == 'win32':
        global _fcounter, _qpfreq, _winQPC
        from ctypes import byref, c_int64, windll
        _fcounter = c_int64()
        _qpfreq = c_int64()
        windll.Kernel32.QueryPerformanceFrequency(byref(_qpfreq))
        _qpfreq=float(_qpfreq.value)
        _winQPC=windll.Kernel32.QueryPerformanceCounter
    
        def getTime():
            _winQPC(byref(_fcounter))
            return  _fcounter.value/_qpfreq
    else:
        cur_pyver = sys.version_info
        if cur_pyver[0]==2 and cur_pyver[1]<=6: 
            import time
            getTime = time.time
        else:
            import timeit
            getTime = timeit.default_timer
    
    class MonotonicClock:
        """
        A convenient class to keep track of time in your experiments.
        When a MonotonicClock is created, it stores the current time
        from getTime and uses this as an offset for psychopy times returned.
        """
        def __init__(self,start_time=None):
            if start_time is None:
                self._timeAtLastReset=getTime()#this is sub-millisec timer in python
            else:
                self._timeAtLastReset=start_time
                
        def getTime(self):
            """Returns the current time on this clock in secs (sub-ms precision)
            """
            return getTime()-self._timeAtLastReset
            
        def getLastResetTime(self):
            """ 
            Returns the current offset being applied to the high resolution 
            timebase used by Clock.
            """
            return self._timeAtLastReset
        
        monotonicClock = psychopy.clock.MonotonicClock
