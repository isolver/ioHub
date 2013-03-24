"""
ioHub Python Module
.. file: ioHub/__init__.py

fileauthor: Sol Simpson <sol@isolver-software.com>

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""
from __future__ import division
import timeit
import numpy as N
import inspect
import sys
import platform
import os
import collections
from collections import namedtuple,Iterable

import constants

   
#version info for ioHub
__version__='0.6b2'#util.validate_version("0.5a1")
__license__='GNU GPLv3 (or more recent equivalent)'
__author__='iSolver Software Solutions'
__author_email__='sol@isolver-software.com'
__maintainer_email__='sol@isolver-software.com'
__users_email__='sol@isolver-software.com'
__url__='http://www.github.com/isolver/ioHub/wiki/'

def module_path(local_function):
    """ returns the module path without the use of __file__.  Requires a function defined
   locally in the module. from http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module"""
    return os.path.abspath(inspect.getsourcefile(local_function))

def module_directory(local_function):
    mp=module_path(local_function)
    moduleDirectory,mname=os.path.split(mp)
    return moduleDirectory

import external_libs

if sys.version_info<(2,7):
    from ordereddict import OrderedDict
else:
    from collections import OrderedDict

def isIterable(o):
    return isinstance(o, Iterable)

global highPrecisionTimer
def highPrecisionTimer():
    raise ioHubError("highPrecisionTimer function must be overwritten by a platform specific implementation.")

if platform.system() == 'Windows':
    global _fcounter, _qpfreq, _winQueryPerformanceCounter
    from ctypes import byref, c_int64, windll
    _Kernel32=windll.Kernel32
    _fcounter = c_int64()
    _qpfreq = c_int64()
    _Kernel32.QueryPerformanceFrequency(byref(_qpfreq))
    _winQueryPerformanceCounter=_Kernel32.QueryPerformanceCounter

    def highPrecisionTimer():
        _winQueryPerformanceCounter(byref(_fcounter))
        return  _fcounter.value/_qpfreq.value
elif platform.system() == 'Linux':
    highPrecisionTimer = timeit.default_timer
else: # assume OS X?
    highPrecisionTimer = timeit.default_timer

class ioClock(object):
    """
    Modified from psychopy.core.Clock, so ioClock supports the psychopy
    Clock interface, and can be used in most situations where a clock
    object can be given to a psychopy function or method.
    
    ioHub only supports one Clock object, which is automatically
    created and associated with the ioHub.devices.Computer class.
    
    *Do not create other instances of ioClock within your experiment.*
    
    To get the current ioHub time, call Computer.getTime(). If the ioClock
    that Computer uses needs to be accessed directly for come reason, 
    it can be accessed via Computer.globalClock.

    ioHub uses an instance of ioClock instead of the standard psychopy Clock 
    class so that when timeAtLastReset is set on the Experiment Process,
    the offset is also sent to the ioHub Process so that the 
    ioHub Process uses the same time offset and therefore both processes time
    base are identical.
    """
    def __init__(self,hubConnection,offset=None,sendOffsetToHub=True):
        if offset is None:
            offset=highPrecisionTimer()
        self.hubConnection=hubConnection
        if hubConnection and sendOffsetToHub is True:
            offset=hubConnection.updateGlobalHubTimeOffset(offset)
        self.timeAtLastReset=offset

    def getTime(self):
        """Returns the current time on this clock in secs (sub-ms precision)
        """
        return highPrecisionTimer()-self.timeAtLastReset

    def reset(self, newT=0.0):
        """Reset the time on the clock. With no args time will be
        set to zero. If a float is received this will be the new
        time on the clock
        """
        offset=highPrecisionTimer()+newT
        if self.hubConnection:
            r=self.hubConnection.updateGlobalHubTimeOffset(offset)
        self.timeAtLastReset=r

    def setOffset(self,offset):
        self.timeAtLastReset=offset

    def add(self,t):
        """Add more time to the clock's 'start' time (t0).

        Note that, by adding time to t0, you make the current time appear less.
        Can have the effect that getTime() returns a negative number that will
        gradually count back up to zero.

        e.g.::

            timer = core.Clock()
            timer.add(5)
            while timer.getTime()<0:
                #do something
        """
        offset= self.timeAtLastReset + t
        if self.hubConnection:
            r=self.hubConnection.updateGlobalHubTimeOffset(offset)
        self.timeAtLastReset = r

def quickStartHubServer(experimentCode, sessionCode, **deviceConfigs):
    from ioHub.client import ioHubConnection

    devices=deviceConfigs
    
    if len(devices)==0:
        # Specify devices you want to use in the ioHub
        devices=OrderedDict()
        devices['Display']={'origin':'center','reporting_unit_type':'pix'}
        devices['Keyboard']={}
        devices['Mouse']={}
    # Create an ioHub configuration dictionary.
    ioConfig=dict(monitor_devices=devices)
    
    if experimentCode and sessionCode:    
        # Enable saving of all keyboard and mouse events to the 'ioDataStore'
        ioConfig['data_store']=dict(experiment_info=dict(code=experimentCode),session_info=dict(code=sessionCode))
    
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

def print2err(*args):
    for a in args:
        sys.stderr.write(unicode(a))
    sys.stderr.write('\n\r')
    sys.stderr.flush()
   
def printExceptionDetailsToStdErr():
        import sys, traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print2err('ioHub Exception:\n exc_type: {0} \nexc_value {1}'.format(exc_type,exc_value))
        for t in traceback.format_tb(exc_traceback):            
            print2err(t)
        print2err('\n')

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

global IO_HUB_DIRECTORY
IO_HUB_DIRECTORY=module_directory(isIterable)

