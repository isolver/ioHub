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
import numpy as N
import inspect
import sys
import platform
import util
from __version__ import iohub_version

#version info for ioHub
__version__=iohub_version
__license__='GNU GPLv3 (or more recent equivalent)'
__author__='Sol Simpson'
__author_email__='sol@isolver-software.com'
__maintainer_email__='sol@isolver-software.com'
__users_email__='sol@isolver-software.com'
__url__='http://www.github.com/isolver/ioHub/wiki/'


class ioObjectMetaClass(type):
    def __new__(meta, name, bases, dct):
        return type.__new__(meta, name, bases, dct)
    def __init__(cls, name, bases, dct):
        type.__init__(cls,name, bases, dct)

        if '_newDataTypes' not in dct:
            cls._newDataTypes=[]

        if '_baseDataTypes' not in dct:
            parent = cls._findDeviceParent(bases)
            if parent:
                cls._baseDataTypes=parent._dataType
            else:
                cls._baseDataTypes=[]
                #print 'parent:',parent

        cls._dataType=cls._baseDataTypes+cls._newDataTypes
        cls.CLASS_ATTRIBUTE_NAMES=[e[0] for e in cls._dataType]
        cls.NUMPY_DTYPE=N.dtype(cls._dataType)

        #print 'bases',bases
        #print 'cls._baseDataTypes',cls._baseDataTypes
        #print 'cls._newDataTypes',cls._newDataTypes

        #print 'cls:',cls
        #print 'cls.NUMPY_DTYPE:',cls.NUMPY_DTYPE
        #print 'cls.CLASS_ATTRIBUTE_NAMES:',cls.CLASS_ATTRIBUTE_NAMES
        #print '-----------------------------------'

    def _findDeviceParent(cls,bases):
        parent=None
        if len(bases)==1:
            parent=bases[0]
        else:
            for p in bases:
                if 'Device' in p.__name__:
                    parent=p
                break
        if 'object' in parent.__name__:
            return None
        return parent

class ioObject(object):
    """
    The ioObject class is the base class for all ioHub Device and DeviceEvent types.

    Any ioHub Device or DeviceEvent class (i.e devices like Keyboard Device, Mouse Device, etc;
    and device events like Message, KeyboardPressEvent, MouseMoveEvent, etc.)
    also include the methods and attributes of this class.
    """
    __metaclass__= ioObjectMetaClass
    __slots__=['_attribute_values',]
    def __init__(self,*args,**kwargs):
        self._attribute_values=[]

        if len(args) > 0:
            for i,n in enumerate(self.CLASS_ATTRIBUTE_NAMES):
                setattr(self,n,args[i])
                self._attribute_values.append(args[i])

        elif len(kwargs)>0:
            for key in self.CLASS_ATTRIBUTE_NAMES:
                value=kwargs[key]
                setattr(self,key,value)
                self._attribute_values.append(value)


    def asDict(self):
        """
        Return the ioObject in dictionary format, with keys as the ioObject's
        attribute names, and dictionary values equal to the attribute values.

        Return (dict): dictionary of ioObjects attribute_name, attributes values.
        """
        return dict(zip(self.CLASS_ATTRIBUTE_NAMES,self._attribute_values))

    def asList(self):
        """
        Return the ioObject in list format, which is a 1D list of the ioObject's
        attribute values, in the order the ioObject expects them if passed to a class constructor.

        Return (list): 1D list of ioObjects _attribute_values
        """
        return self._attribute_values

    def asNumpyArray(self):
        """
        Return the ioObject as a numpy array, with the array values being equal to
        what would be returned by the asList() method, and the array cell data types
        being specified by NUMPY_DTYPE class constant.

        Return (numpy.array): numpy array representation of object.
        """
        return N.array([tuple(self._attribute_values),],self.NUMPY_DTYPE)

    @classmethod
    def createObjectFromParamList(cls,args):
        """
        Create an ioObject of class type 'cls', using the values from the 'args' list
        as the parameters to the class constructor.

        Args:
            args(list): 1D list of the ioObject's attribute values, in the order the ioObject
                        expects them when passed to a class constructor.
        Return (ioObject): The created ioObject of type cls
        """
        return cls(*args)

    def _getRPCInterface(self):
        rpcList=[]
        dlist = dir(self)
        for d in dlist:
            if d[0] is not '_':
                if callable(getattr(self,d)):
                    rpcList.append(d)
        return rpcList

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
    global _fcounter, _ffreq, _winQueryPerformanceCounter, _winQueryPerformanceFrequency
    from ctypes import byref, c_int64, windll
    _Kernel32=windll.Kernel32
    _fcounter = c_int64()
    _ffreq = c_int64()
    _winQueryPerformanceCounter=_Kernel32.QueryPerformanceCounter
    _winQueryPerformanceFrequency=_Kernel32.QueryPerformanceFrequency
    def highPrecisionTimer():
        _winQueryPerformanceCounter(byref(_fcounter))
        _winQueryPerformanceFrequency(byref(_ffreq))
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