"""
ioHub Python Module
.. file: iohub/__init__.py

fileauthor: Sol Simpson <sol@isolver-software.com>

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""
from __future__ import division


import inspect
import sys
import os
from collections import namedtuple,Iterable

from timebase import psychopy_available, MonotonicClock, monotonicClock
from util import (fix_encoding,OrderedDict,convertCamelToSnake,win32MessagePump,
                  print2err,printExceptionDetailsToStdErr,ioHubError,createErrorResult,
                  DeviceEventTrigger, ClearScreen, InstructionScreen,
                  getCurrentDateTimeString,FullScreenWindow)


fix_encoding.fix_encoding()

def addDirectoryToPythonPath(path_from_iohub_root,leaf_folder=''):
    dir_path=os.path.join(IO_HUB_DIRECTORY,path_from_iohub_root,sys.platform,"python{0}{1}".format(*sys.version_info[0:2]),leaf_folder)
    if os.path.isdir(dir_path) and dir_path not in sys.path:
        sys.path.append(dir_path)  
    else:
        print2err("Could not add path: ",dir_path)
        dir_path=None
    return dir_path
    
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

  
#version info for ioHub
__version__='0.7.0'
__license__='GNU GPLv3 (or more recent equivalent)'
__author__='iSolver Software Solutions'
__author_email__='sol@isolver-software.com'
__maintainer_email__='sol@isolver-software.com'
__users_email__='sol@isolver-software.com'
__url__='https://www.github.com/isolver/ioHub/'


# check module is being loaded on a supported platform
SUPPORTED_SYS_NAMES=['linux2','win32','cygwin','darwin']  
if sys.platform not in SUPPORTED_SYS_NAMES:
    print ''
    print "ERROR: ioHub is not supported on the current OS platform. Supported options are: ", SUPPORTED_SYS_NAMES
    print "EXITING......"
    print ''
    sys.exit(1)



def isIterable(o):
    return isinstance(o, Iterable)
        

RectangleBorder=namedtuple('RectangleBorderClass', 'left top right bottom')

from client import launchHubServer,ioHubExperimentRuntime
import constants
from constants import (DeviceConstants, EventConstants, KeyboardConstants, 
                       MouseConstants, EyeTrackerConstants)