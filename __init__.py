"""
ioHub Python Module
.. file: ioHub/__init__.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""
from __future__ import division
import timeit
from __version__ import iohub_version
#version info for ioHub
__version__=iohub_version
__license__='GNU GPLv3 (or more recent equivalent)'
__author__='Sol Simpson'
__author_email__='sol@isolver-software.com'
__maintainer_email__='sol@isolver-software.com'
__users_email__='sol@isolver-software.com'
__url__='http://www.github.com/isolver/ioHub/wiki/'

from __builtin__ import isinstance, repr, dict
from exceptions import Exception
import inspect
import sys
import platform

class ioHubError(Exception):
    def __init__(self, msg, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.msg = msg

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "ioHubError:\nMsg: {0:>s}\n".format(self.msg)

global highPrecisionTimer
def highPrecisionTimer():
    raise ioHubError("highPrecisionTimer function must be overwritten by a platform specific implementation.")


if platform.system() == 'Windows':
    global _fcounter,_ffreq,_Kernel32,highPrecisionTimer
    from ctypes import byref, c_int64, windll
    _Kernel32=windll.Kernel32
    _fcounter = c_int64()
    _ffreq = c_int64()
    def highPrecisionTimer():
        _Kernel32.QueryPerformanceCounter(byref(_fcounter))
        _Kernel32.QueryPerformanceFrequency(byref(_ffreq))
        return  _fcounter.value/_ffreq.value
elif platform.system() == 'Linux':
    highPrecisionTimer = timeit.default_timer
else: # assume OS X?
    highPrecisionTimer = timeit.default_timer


def print2err(*args):
    for a in args:
        sys.stderr.write(str(a))
    sys.stderr.write('\n\r')
    sys.stderr.flush()

from collections import Iterable,OrderedDict

def isIterable(o):
    return isinstance(o, Iterable)

def module_path(local_function):
    """ returns the module path without the use of __file__.  Requires a function defined
   locally in the module. from http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module"""
    return os.path.abspath(inspect.getsourcefile(local_function))

def module_directory(local_function):
    mp=module_path(local_function)
    moduleDirectory,mname=os.path.split(mp)
    return moduleDirectory

def printExceptionDetailsToStdErr():
        """
        No idea if all of this is needed, infact I know it is not. But for now why not.
        Taken straight from the python manual on Exceptions.
        """
        import sys, traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print2err("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        print2err("*** print_exception:")
        traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2, file=sys.stdout)
        print2err("*** print_exc:")
        traceback.print_exc()
        print2err("*** format_exc, first and last line:")
        formatted_lines = traceback.format_exc().splitlines()
        print2err(str(formatted_lines[0]))
        print2err((formatted_lines[-1]))
        print2err("*** format_exception:")
        print2err(repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
        print2err("*** extract_tb:")
        print2err(repr(traceback.extract_tb(exc_traceback)))
        print2err("*** format_tb:")
        print2err(repr(traceback.format_tb(exc_traceback)))
        print2err("*** tb_lineno:"+str( exc_traceback.tb_lineno))

class LastUpdatedOrderedDict(OrderedDict):
    """Store items in the order the keys were last added"""

    #noinspection PyMethodOverriding
    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        OrderedDict.__setitem__(self, key, value)

import os
global IO_HUB_DIRECTORY
IO_HUB_DIRECTORY=module_directory(isIterable)