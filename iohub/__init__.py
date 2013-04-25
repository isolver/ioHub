"""
ioHub Python Module
.. file: iohub/__init__.py

fileauthor: Sol Simpson <sol@isolver-software.com>

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""
from __future__ import division
from util import fix_encoding

fix_encoding.fix_encoding()

import numpy as N
import inspect
import sys
import platform
import os
import collections
from collections import namedtuple,Iterable

  
#version info for ioHub
__version__='0.7.0'
__license__='GNU GPLv3 (or more recent equivalent)'
__author__='iSolver Software Solutions'
__author_email__='sol@isolver-software.com'
__maintainer_email__='sol@isolver-software.com'
__users_email__='sol@isolver-software.com'
__url__='https://www.github.com/isolver/ioHub/'

psychopy_available=False
try:
    import psychopy
    psychopy_available=True
except:
    pass

SUPPORTED_SYS_NAMES=['linux2','win32','cygwin','darwin']  
if sys.platform not in SUPPORTED_SYS_NAMES:
    print ''
    print "ERROR: ioHub is not supported on the current OS platform. Supported options are: ", SUPPORTED_SYS_NAMES
    print "EXITING......"
    print ''
    sys.exit(1)
    
def module_path(local_function):
    """ returns the module path without the use of __file__.  Requires a function defined
   locally in the module. from http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module"""
    return os.path.abspath(inspect.getsourcefile(local_function))

def module_directory(local_function):
    mp=module_path(local_function)
    moduleDirectory,mname=os.path.split(mp)
    return moduleDirectory

global IO_HUB_DIRECTORY
IO_HUB_DIRECTORY=module_directory(module_path)

def print2err(*args):
    for a in args:
        sys.stderr.write(u"{0}".format(a))        
    sys.stderr.write(u"\n") 
    sys.stderr.flush()
   
def printExceptionDetailsToStdErr():
        import sys, traceback,pprint
        exc_type, exc_value, exc_traceback = sys.exc_info()
        pprint.pprint(exc_type, stream=sys.stderr, indent=1, width=80, depth=None)        
        pprint.pprint(exc_value, stream=sys.stderr, indent=1, width=80, depth=None)
        pprint.pprint(traceback.format_tb(exc_traceback), stream=sys.stderr, indent=1, width=80, depth=None)

class ioHubError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args)
        self.args = args
        self.kwargs=kwargs
        
    def __str__(self):
        return repr(self)

    def __repr__(self):
        r="ioHubError:\nArgs: {0}\n".format(self.args)
        for k,v in self.kwargs.iteritems():
            r+="\t{0}: {1}\n".format(k,v)
        return r
        
def getOsName():
    _os_name=platform.system()
    if _os_name == 'Windows':
        return 'win32'
    if _os_name == 'Linux':
        return 'linux'   
    return 'osx'
    
def getPythonVerStr():
    cur_version = sys.version_info
    return 'python%d%d'%(cur_version[0],cur_version[1])
    
def addDirectoryToPythonPath(path_from_iohub_root,leaf_folder=''):
    dir_path=os.path.join(IO_HUB_DIRECTORY,path_from_iohub_root,getOsName(),getPythonVerStr(),leaf_folder)
    if os.path.isdir(dir_path) and dir_path not in sys.path:
        sys.path.append(dir_path)  
    else:
        print2err("Could not add path: ",dir_path)
        dir_path=None
    return dir_path

if getPythonVerStr() != 'python27':
    from ordereddict import OrderedDict
else:
    from collections import OrderedDict

def isIterable(o):
    return isinstance(o, Iterable)

#set the default timing mechanism
getTime=None
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

import constants


def quickStartHubServer(**kwargs):
    """
    experiment_code=None, session_code=None, psychopy_monitor_name=None, **device_configs
    """
    from .client import ioHubConnection

    experiment_code=kwargs.get('experiment_code',-1)
    if experiment_code != -1:
        del kwargs['experiment_code']
    else:
        experiment_code = None

    session_code=kwargs.get('session_code',-1)
    if session_code != -1:
        del kwargs['session_code']
    else:
        session_code = None    
    
    psychopy_monitor_name=kwargs.get('psychopy_monitor_name',None)
    if psychopy_monitor_name:
        del kwargs['psychopy_monitor_name']

    device_dict=kwargs
    
    device_list=[]
    
    # Ensure a Display Device has been defined. If note, create one.
    # Insert Display device as first device in dev. list.
    if 'Display' not in device_dict: 
        if psychopy_monitor_name:
            device_list.append(dict(Display={'psychopy_monitor_name':psychopy_monitor_name,'override_using_psycho_settings':True}))
        else:
            device_list.append(dict(Display={'override_using_psycho_settings':True}))
    else:
        device_list.append(dict(Display=device_dict['Display']))
        del device_dict['Display']

    # Ensure a Experiment Device has been defined. If note, create one.
    if 'Experiment' not in device_dict:    
        device_list.append(dict(Experiment={}))
    else:
        device_list.append(dict(Experiment=device_dict['Experiment']))
        del device_dict['Experiment']

    # Ensure a Keyboard Device has been defined. If note, create one.
    if 'Keyboard' not in device_dict:    
        device_list.append(dict(Keyboard={}))
    else:
        device_list.append(dict(Keyboard=device_dict['Keyboard']))
        del device_dict['Keyboard']

    # Ensure a Mouse Device has been defined. If note, create one.
    if 'Mouse' not in device_dict:    
        device_list.append(dict(Mouse={}))
    else:
        device_list.append(dict(Mouse=device_dict['Mouse']))
        del device_dict['Mouse']
    
    # Add remaining defined devices to the device list.
    for class_name,device_config in device_dict.iteritems():
        device_list.append(dict(class_name=device_config))

    # Create an ioHub configuration dictionary.
    ioConfig=dict(monitor_devices=device_list)
    
    if experiment_code and session_code:    
        # Enable saving of all keyboard and mouse events to the 'ioDataStore'
        ioConfig['data_store']=dict(experiment_info=dict(code=experiment_code),
                                            session_info=dict(code=session_code))
    
    # Start the ioHub Server
    return ioHubConnection(ioConfig)

RectangleBorder=namedtuple('RectangleBorderClass', 'left top right bottom')

import re

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')

def convertCamelToSnake(name,lower_snake=True):
    s1 = first_cap_re.sub(r'\1_\2', name)
    if lower_snake:
        return all_cap_re.sub(r'\1_\2', s1).lower()
    return all_cap_re.sub(r'\1_\2', s1).upper()