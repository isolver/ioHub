"""
ioHub
.. file: ioHub/devices/__init__.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

import numpy as N
import platform
import timeit
from collections import deque
from operator import itemgetter

class Computer(object):
    _instance=None
    _nextEventID=1
    def __init__(self,system, node, release, version, machine, processor):
        if Computer._instance!=None:
            raise "Error creating Computer object; instance already exists. \
                   Use Computer.getInstance() to existing instance, or Computer. \
                   deleteInstance() to delete the existing instance before creating a new one."
        else:
            import psutil, os
            
            self.system=system
            self.node=node
            self.release=release
            self.version=version
            self.machine=machine
            self.processor=processor
            self.cpuCount=psutil.NUM_CPUS
            
            
            self.currentProcessID=os.getpid()
            self.currentProcess=psutil.Process(self.currentProcessID)
 
    # return time in sec.msec format
    @classmethod
    def getInstance(cls):
        return cls._instance

    # return time in sec.msec format
    @classmethod
    def deleteInstance(cls):
        i=cls._instance
        cls._instance=None
        del i

        # return time in sec.msec format
    @staticmethod
    def currentSec():
        return timeit.default_timer()

    #return time in msec.usec format
    @staticmethod
    def currentMsec():
        return timeit.default_timer()*1000.0

    #return time in usec format
    @staticmethod
    def currentUsec():
        return int(timeit.default_timer()*1000000.0)

    @staticmethod
    def getNextEventID():
        n = Computer._nextEventID
        Computer._nextEventID+=1
        return n
        
    # From Python 2.6 Doc
    # timeit.timeit(stmt, setup='pass', timer=default_timer, number=1000000)
    # Create a Timer instance with the given statement, setup code and timer
    # function and run its timeit() method with number executions.
    @staticmethod
    def profileCode(stmt, setup='pass', timer=timeit.default_timer, number=1000000):
        return timeit.timeit(stmt, setup, timer, number)

    # From Python 2.6 Doc
    # timeit.repeat(stmt, setup='pass', timer=default_timer, repeat=3, number=1000000)
    # Create a Timer instance with the given statement, setup code and
    # timer function and run its repeat() method with the given repeat count
    # and number executions.
    @staticmethod
    def repeatedProfile(stmt, setup='pass', timer=timeit.default_timer, repeat=3, number=1000000):
        return timeit.repeat(stmt, setup, timer, repeat, number)

    def printProcessInfo(self):
        tcount= self.currentProcess.get_num_threads()
        pthreads=self.currentProcess.get_threads()
        
        print '--------------------------------------'
        print 'Process ( %d ): '%(self.currentProcessID,)
        print p
        print 'Thread Count:', tcount
        print 'Thread Info:'
        for t in pthreads:
            print t

    def getProcessInfoString(self):
        tcount= self.currentProcess.get_num_threads()
        pthreads=self.currentProcess.get_threads()
        
        r='--------------------------------------\n'
        r+='Process ( %d ):\n'%(self.currentProcessID,)
        r+=str(self.currentProcess)
        r+='Thread Count: %d\n'%(tcount,)
        r+='Thread Info:\n'
        for t in pthreads:
            r+=str(t)+'\n'
            
    def __del__(self):
        self._instance=None
        del self._instance
            
Computer._instance=Computer(*platform.uname())
computer=Computer.getInstance()

class ioObject(object):
    newDataTypes=[]
    baseDataType=[]
    dataType=baseDataType+newDataTypes
    attributeNames=[]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in newDataTypes]+['I_np_array',]
    def __init__(self,*args,**kwargs):
        values=[]
        for key in self.attributeNames:
            value=kwargs[key]
            setattr(self,key,value)
            values.append(value)
        self.I_np_array=N.array([tuple(values),],self.ndType)         

    def _asList(self):
        return self.I_np_array[0].tolist()

    def _asNumpyArray(self):
        return self.I_np_array
        
########### Base Abstract Device that all other Devices inherit from ##########
class Device(ioObject):
    newDataTypes=[('instance_code','a48'),('category_id','u1'),('type_id','u1'),('device_class','a24'),('user_label','a24'),('os_device_code','a64'),('max_event_buffer_length','u2')]
    baseDataType=ioObject.dataType
    dataType=baseDataType+newDataTypes
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in newDataTypes]+['I_nativeEventBuffer','I_eventListeners','I_ioHubEventBuffer']
    DEVICE_TIMEBASE_TO_USEC=1.0
    def __init__(self,*args,**kwargs):
        ioObject.__init__(self,**kwargs)
        self.I_ioHubEventBuffer=deque(maxlen=self.max_event_buffer_length)
        self.I_nativeEventBuffer=deque(maxlen=self.max_event_buffer_length)
        self.I_eventListeners=list()

    def getEvents(self):
        currentEvents=list(self.I_ioHubEventBuffer)
        self.I_ioHubEventBuffer.clear()

        if len(currentEvents)>0:
            sorted(currentEvents, key=itemgetter(7))
        return eventList
    
    def clearEvents(self):
        self.I_ioHubEventBuffer.clear()
        
    def _handleEvent(self,e):
        self.I_ioHubEventBuffer.append(e)
        
    def _getNativeEventBuffer(self):
        return self.I_nativeEventBuffer
    
    def _addEventListener(self,l):
        if l not in self.I_eventListeners:
            self.I_eventListeners.append(l)
    
    def _removeEventListener(self,l):
       if l in self.I_eventListeners:
            self.I_eventListeners.remove(l)
            
    def _getEventListeners(self):
        return self.I_eventListeners
        
    def _getRPCInterface(self):
        rpcList=[]
        dlist = dir(self)
        for d in dlist:
            if d[0] is not '_' and not d.startswith('I_'):
                if callable(getattr(self,d)):
                    rpcList.append(d)
        return rpcList
        
########### Base Device Event that all other Device Events inherit from ##########

class DeviceEvent(ioObject):
    newDataTypes=[('experiment_id','u4'),('session_id','u4'),('event_id','u8'),('event_type','u1'),
                  ('device_instance_code','a48'),('device_time','u8'), ('logged_time', 'u8'), ('hub_time','u8'),
                  ('confidence_interval', 'f4'),('delay', 'f4')]
    baseDataType=ioObject.dataType
    dataType=baseDataType+newDataTypes
    attributeNames=[e[0] for e in dataType]
    defaultValueDict=None
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in newDataTypes] 
    def __init__(self,*args,**kwargs):
        ioObject.__init__(self,**kwargs)
                   
    def __cmp__(self,other):
        return self.hub_time-other.hub_time
        
    def hubTime(self):
        return self.hub_time

    @classmethod
    def createFromOrderedList(cls,eventValueList):
        combo = zip(cls.attributeNames,eventValueList)
        kwargs = dict(combo)
        return cls(**kwargs)
        

        
class EventConstantsBase(object):
    eventTypeCodeToClass=dict()    
    def __init__(self):    
        pass
    
    @classmethod
    def eventIDtoClass(cls,eid):
        '''
        Class method. Converts a an ioHub event id to the associated ioHub event class name.
        '''
        return cls.eventTypeCodeToClass[eid]

    @staticmethod
    def eventIDtoName(eid):
        '''
        Static method. Converts a an ioHub event id to the associated ioHub event name.
        '''
        return EVENT_TYPES[eid]
        
    @staticmethod
    def VKeyToID(vkey):
        '''
        Static method. Converts a virtual keycode name to its value.

        @param vkey: Virtual keycode name
        @type vkey: string
        @return: Virtual keycode value
        @rtype: integer
        '''
        return None

    @staticmethod
    def IDToName(cls, code):
        '''
        Static method. Gets the keycode name for the given value.

        @param code: Virtual keycode value
        @type code: integer
        @return: Virtual keycode name
        @rtype: string
        '''
        return None

    @staticmethod
    def GetKeyState(key_id):
        return None

        
if computer.system == 'Windows':
    import pyHook
    from pyHook.HookManager import HookConstants as _win32EventConstants
    
    class EventConstants(EventConstantsBase):
        WH_MIN = _win32EventConstants.WH_MIN
        WH_MSGFILTER = _win32EventConstants.WH_MSGFILTER
        WH_JOURNALRECORD = _win32EventConstants.WH_JOURNALRECORD
        WH_JOURNALPLAYBACK = _win32EventConstants.WH_JOURNALPLAYBACK
        WH_KEYBOARD = _win32EventConstants.WH_KEYBOARD
        WH_GETMESSAGE = _win32EventConstants.WH_GETMESSAGE
        WH_CALLWNDPROC =_win32EventConstants.WH_CALLWNDPROC
        WH_CBT = _win32EventConstants.WH_CBT
        WH_SYSMSGFILTER = _win32EventConstants.WH_SYSMSGFILTER
        WH_MOUSE = _win32EventConstants.WH_MOUSE
        WH_HARDWARE = _win32EventConstants.WH_HARDWARE
        WH_DEBUG = _win32EventConstants.WH_DEBUG
        WH_SHELL = _win32EventConstants.WH_SHELL
        WH_FOREGROUNDIDLE = _win32EventConstants.WH_FOREGROUNDIDLE
        WH_CALLWNDPROCRET = _win32EventConstants.WH_CALLWNDPROCRET
        WH_KEYBOARD_LL = _win32EventConstants.WH_KEYBOARD_LL
        WH_MOUSE_LL = _win32EventConstants.WH_MOUSE_LL
        WH_MAX = _win32EventConstants.WH_MAX

        WM_MOUSEFIRST = _win32EventConstants.WM_MOUSEFIRST
        WM_MOUSEMOVE = _win32EventConstants.WM_MOUSEMOVE
        WM_LBUTTONDOWN = _win32EventConstants.WM_LBUTTONDOWN
        WM_LBUTTONUP = _win32EventConstants.WM_LBUTTONUP
        WM_LBUTTONDBLCLK = _win32EventConstants.WM_LBUTTONDBLCLK
        WM_RBUTTONDOWN = _win32EventConstants.WM_RBUTTONDOWN
        WM_RBUTTONUP = _win32EventConstants.WM_RBUTTONUP
        WM_RBUTTONDBLCLK = _win32EventConstants.WM_RBUTTONDBLCLK
        WM_MBUTTONDOWN = _win32EventConstants.WM_MBUTTONDOWN
        WM_MBUTTONUP = _win32EventConstants.WM_MBUTTONUP
        WM_MBUTTONDBLCLK = _win32EventConstants.WM_MBUTTONDBLCLK
        WM_MOUSEWHEEL = _win32EventConstants.WM_MOUSEWHEEL
        WM_MOUSELAST = _win32EventConstants.WM_MOUSELAST

        WM_KEYFIRST = _win32EventConstants.WM_KEYFIRST
        WM_KEYDOWN = _win32EventConstants.WM_KEYDOWN
        WM_KEYUP = _win32EventConstants.WM_KEYUP
        WM_CHAR = _win32EventConstants.WM_CHAR
        WM_DEADCHAR = _win32EventConstants.WM_DEADCHAR
        WM_SYSKEYDOWN = _win32EventConstants.WM_SYSKEYDOWN
        WM_SYSKEYUP = _win32EventConstants.WM_SYSKEYUP
        WM_SYSCHAR = _win32EventConstants.WM_SYSCHAR
        WM_SYSDEADCHAR = _win32EventConstants.WM_SYSDEADCHAR
        WM_KEYLAST = _win32EventConstants.WM_KEYLAST    
        def __init__(self):
            EventConstantsBase.__init__(self)
        
        @classmethod
        def VKeyToID(cls, vkey):
            '''
            Class method. Converts a virtual keycode name to its value.

            @param vkey: Virtual keycode name
            @type vkey: string
            @return: Virtual keycode value
            @rtype: integer
            '''
            return _win32EventConstants.VKeyToID(vkey)

        @classmethod
        def IDToName(cls, code):
            '''
            Class method. Gets the keycode name for the given value.

            @param code: Virtual keycode value
            @type code: integer
            @return: Virtual keycode name
            @rtype: string
            '''
            return _win32EventConstants.IDToName(code)

        @staticmethod
        def GetKeyState(key_id):
            return pyHook.HookManager.GetKeyState(key_id)
            
import keyboard as keyboard_module
from keyboard import Keyboard
from keyboard import KeyboardPressEvent,KeyboardReleaseEvent

import mouse as mouse_module
from mouse import Mouse
from mouse import MouseEvent,MouseMoveEvent,MouseWheelEvent,MouseButtonDownEvent,MouseButtonUpEvent,MouseDoubleClickEvent

import parallelPort as parallelPort_module
from parallelPort import ParallelPort
from parallelPort import ParallelPortEvent

import experiment
from experiment import ExperimentDevice
from experiment import MessageEvent, CommandEvent

import eyeTrackerInterface
from eyeTrackerInterface.HW import *
from eyeTrackerInterface.eye_events import *

import display
from display import Display

import ioHub
from ioHub import EVENT_TYPES

if len(EventConstantsBase.eventTypeCodeToClass)==0:
    EventConstantsBase.eventTypeCodeToClass[EVENT_TYPES['KEYBOARD_PRESS']]=KeyboardPressEvent
    EventConstantsBase.eventTypeCodeToClass[EVENT_TYPES['KEYBOARD_RELEASE']]=KeyboardReleaseEvent
    EventConstantsBase.eventTypeCodeToClass[EVENT_TYPES['MOUSE_MOVE']]=MouseMoveEvent
    EventConstantsBase.eventTypeCodeToClass[EVENT_TYPES['MOUSE_WHEEL']]=MouseWheelEvent
    EventConstantsBase.eventTypeCodeToClass[EVENT_TYPES['MOUSE_PRESS']]=MouseButtonDownEvent
    EventConstantsBase.eventTypeCodeToClass[EVENT_TYPES['MOUSE_RELEASE']]=MouseButtonUpEvent
    EventConstantsBase.eventTypeCodeToClass[EVENT_TYPES['MOUSE_DOUBLE_CLICK']]=MouseDoubleClickEvent
    EventConstantsBase.eventTypeCodeToClass[EVENT_TYPES['PARALLEL_PORT_INPUT']]=ParallelPortEvent
    EventConstantsBase.eventTypeCodeToClass[EVENT_TYPES['MESSAGE']]=MessageEvent
    EventConstantsBase.eventTypeCodeToClass[EVENT_TYPES['COMMAND']]=CommandEvent
    EventConstantsBase.eventTypeCodeToClass[EVENT_TYPES['EYE_SAMPLE']]=MonocularEyeSample
    EventConstantsBase.eventTypeCodeToClass[EVENT_TYPES['BINOC_EYE_SAMPLE']]=BinocularEyeSample
    EventConstantsBase.eventTypeCodeToClass[EVENT_TYPES['FIXATION_START']]=FixationStartEvent
    EventConstantsBase.eventTypeCodeToClass[EVENT_TYPES['FIXATION_END']]=FixationEndEvent
    EventConstantsBase.eventTypeCodeToClass[EVENT_TYPES['SACCADE_START']]=SaccadeStartEvent
    EventConstantsBase.eventTypeCodeToClass[EVENT_TYPES['SACCADE_END']]=SaccadeEndEvent
    EventConstantsBase.eventTypeCodeToClass[EVENT_TYPES['BLINK_START']]=BlinkStartEvent
    EventConstantsBase.eventTypeCodeToClass[EVENT_TYPES['BLINK_END']]=BlinkEndEvent
