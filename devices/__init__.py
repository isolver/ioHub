"""
ioHub
.. file: ioHub/devices/__init__.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""
from __future__ import division
import gc
import os
import numpy as N
import platform
from collections import deque
from operator import itemgetter
import psutil

class ioDeviceError(Exception):
    def __init__(self, device, msg, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.device = device
        self.msg = msg

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "ioDeviceError:\nMsg: {0:>s}\nDevice: {1:>s}\n".format(self.msg),repr(self.device)



class Computer(object):
    _instance=None
    _nextEventID=1
    isIoHubProcess=False
    _inHighPriorityMode=False
    def __init__(self):
        if Computer._instance is not None:
            raise "Error creating Computer object; instance already exists. \
                   Use Computer.getInstance() to existing instance, or Computer. \
                   deleteInstance() to delete the existing instance before creating a new one."
        else:
            system, node, release, version, machine, processor = platform.uname()

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

    def getCurrentProcess(self):
        return self.currentProcess

    def enableHighPriority(self,disable_gc=True):
        if Computer._inHighPriorityMode is False:
            if disable_gc:
                gc.disable()
            self.currentProcess.nice=psutil.HIGH_PRIORITY_CLASS
            Computer._inHighPriorityMode=True

    def disableHighPriority(self):
        if Computer._inHighPriorityMode is True:
            gc.enable()
            self.currentProcess.nice=psutil.NORMAL_PRIORITY_CLASS
            Computer._inHighPriorityMode=False

    def getCurrentProcessAffinity(self):
        return self.currentProcess.get_cpu_affinity()

    def setCurrentProcessAffinity(self,processorList):
        return self.currentProcess.set_cpu_affinity(processorList)

    def setProcessAffinityByID(self,processID,processorList):
        p=psutil.Process(processID)
        return p.set_cpu_affinity(processorList)

    def getProcessAffinityByID(self,processID):
        p=psutil.Process(processID)
        return p.get_cpu_affinity()

    def setAllOtherProcessesAffinity(self, processorList, excludeProcessByIDList=[]):
        """

        """
        for p in psutil.process_iter():
            if p.pid not in excludeProcessByIDList:
                try:
                    p.set_cpu_affinity(processorList)
                    print2err('Set OK process affinity: '+str(p.name)+" : "+str(p.pid))
                except Exception:
                    print2err('Error setting process affinity: '+str(p.name)+" : "+str(p.pid))

    # return time in sec.msec format
    @staticmethod
    def currentSec():
        return highPrecisionTimer()

    #return time in msec.usec format
    @staticmethod
    def currentMsec():
        return highPrecisionTimer()*1000.0

    #return time in usec format
    @staticmethod
    def currentUsec():
        return int(highPrecisionTimer()*1000000.0)

    @staticmethod
    def getNextEventID():
        n = Computer._nextEventID
        Computer._nextEventID+=1
        return n

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
            
Computer._instance=Computer()
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
    DEVICE_INSTANCE_CODE_INDEX=0
    DEVICE_CATEGORY_ID_INDEX=1
    DEVICE_TYPE_ID_INDEX=2
    DEVICE_CLASS_NAME_INDEX=3
    DEVICE_USER_LABEL_INDEX=4
    DEVICE_OS_CODE_INDEX=5
    DEVICE_BUFFER_LENGTH_INDEX=6
    BASE_DEVICE_MAX_ATTRIBUTE_INDEX=DEVICE_BUFFER_LENGTH_INDEX

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
        return currentEvents
    
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
    EVENT_EXPERIMENT_ID_INDEX=0
    EVENT_SESSION_ID_INDEX=1
    EVENT_ID_INDEX=2
    EVENT_TYPE_ID_INDEX=3
    EVENT_DEVICE_INSTANCE_CODE_INDEX=4
    EVENT_DEVICE_TIME_INDEX=5
    EVENT_LOGGED_TIME_INDEX=6
    EVENT_HUB_TIME_INDEX=7
    EVENT_CONFIDENCE_INTERVAL_INDEX=8
    EVENT_DELAY_INDEX=9
    BASE_EVENT_MAX_ATTRIBUTE_INDEX=EVENT_DELAY_INDEX

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

class _EventConstantsBase(object):
    EVENT_TYPES = dict(UNDEFINED_EVENT=0, EXPERIMENT_EVENT=1, MESSAGE=2, COMMAND=3, KEYBOARD_EVENT=50, KEYBOARD_PRESS=51,
        KEYBOARD_RELEASE=52, BUTTON_BOX_PRESS=60, BUTTON_BOX_RELEASE=61, JOYSTICK_BUTTON_PRESS=63,
        JOYSTICK_BUTTON_RELEASE=64, JOYSTICK_POSITION=65, MOUSE_EVENT=54, MOUSE_PRESS=55, MOUSE_RELEASE=56, MOUSE_WHEEL=57,
        MOUSE_MOVE=58, MOUSE_DOUBLE_CLICK=59, PARALLEL_PORT_INPUT=73, TTL_INPUT=70, EYE_SAMPLE=100, BINOC_EYE_SAMPLE=101,
        FIXATION_START=106, FIXATION_UPDATE=107, FIXATION_END=108, SACCADE_START=111, SACCADE_END=112, BLINK_START=116,
        BLINK_END=117, SMOOTH_PURSUIT_START=119, SMOOTH_PURSUIT_END=120)

    DEVICE_TYPES = {1: 'KEYBOARD_DEVICE',
                    2: 'MOUSE_DEVICE',
                    3: 'DISPLAY_DEVICE',
                    4: 'PARALLEL_PORT_DEVICE',
                    5: 'EXPERIMENT_DEVICE',
                    #6:'ANALOG_INPUT_DEVICE',         #        7:'ANALOG_OUTPUT_DEVICE',         8:'BUTTON_BOX_DEVICE',         9:'JOYSTICK_DEVICE',         #        10:'SPEAKER_DEVICE',         #        11:'AMPLIFIER_DEVICE',         #        12:'MICROPHONE_DEVICE',         13:'EYE_TRACKER_DEVICE',         #        14:'EEG_DEVICE',         #        15:'MRI_DEVICE',         #        16:'MEG_DEVICE',         17:'OTHER_DEVICE'
    }

    EVENT_CLASSES=dict()

    DEVICE_CATERGORIES={
                    1:'KEYBOARD',
                    2:'MOUSE',
                    4:'VISUAL_STIMULUS_PRESENTER',
                    8:'VIRTUAL',
                    16:'DIGITAL_IO',
                    #        32:'DA_CONVERTER',
                    #        64:'AD_CONVERTER',
                    #        128:'BUTTON_BOX',
                    256:'JOYSTICK',
                    #        512:'SPEAKER',
                    #        1024:'AMPLIFIER',
                    #        2048:'MICROPHONE',
                    4096:'EYE_TRACKER',
                    #        8192:'EEG',
                    #        16384:'MRI',
                    #        32768:'MEG',
                    18446744073709551616:'OTHER'
                }

    _prepped=False
    def __init__(self):
        pass

    @classmethod
    def eventIDtoClass(cls,eid):
        '''
        Class method. Converts a an ioHub event id to the associated ioHub event class name.
        '''
        return cls.EVENT_CLASSES[eid]

    @staticmethod
    def eventIDtoName(eid):
        '''
        Static method. Converts a an ioHub event id to the associated ioHub event name.
        '''
        return EventConstants.EVENT_TYPES[eid]

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


# Windows Version of Constants Class

if computer.system == 'Windows':
    import pyHook
    from pyHook.HookManager import HookConstants as _win32EventConstants

    class EventConstants(_EventConstantsBase):
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

        #VK_0 thru VK_9 are the same as ASCII '0' thru '9' (0x30 -' : 0x39)
        #VK_A thru VK_Z are the same as ASCII 'A' thru 'Z' (0x41 -' : 0x5A)

        #virtual keycode constant names to virtual keycodes numerical id
        vk_to_id = _win32EventConstants.vk_to_id

        # virtual keycodes numerical id to virtual keycode constant names
        id_to_vk = _win32EventConstants.id_to_vk

        #event_to_name =

        def __init__(self):
            _EventConstantsBase.__init__(self)

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

import joystick as joystick_module
from joystick import Joystick
from joystick import JoystickButtonPressEvent, JoystickButtonReleaseEvent

import experiment
from experiment import ExperimentDevice
from experiment import MessageEvent #, CommandEvent

import eyeTrackerInterface
from eyeTrackerInterface.HW import *
from eyeTrackerInterface.eye_events import *

import display
from display import Display
from ioHub import print2err, highPrecisionTimer

if EventConstants._prepped is False:
    EventConstants._prepped=True

    EventConstants.EVENT_CLASSES.update({EventConstants.EVENT_TYPES['KEYBOARD_PRESS']:KeyboardPressEvent,
                                         EventConstants.EVENT_TYPES['KEYBOARD_RELEASE']:KeyboardReleaseEvent,
                                         EventConstants.EVENT_TYPES['MOUSE_MOVE']:MouseMoveEvent,
                                         EventConstants.EVENT_TYPES['MOUSE_WHEEL']:MouseWheelEvent,
                                         EventConstants.EVENT_TYPES['MOUSE_PRESS']:MouseButtonDownEvent,
                                         EventConstants.EVENT_TYPES['MOUSE_RELEASE']:MouseButtonUpEvent,
                                         EventConstants.EVENT_TYPES['MOUSE_DOUBLE_CLICK']:MouseDoubleClickEvent,
                                         EventConstants.EVENT_TYPES['JOYSTICK_BUTTON_PRESS']:JoystickButtonPressEvent,
                                         EventConstants.EVENT_TYPES['JOYSTICK_BUTTON_RELEASE']:JoystickButtonReleaseEvent,
                                         EventConstants.EVENT_TYPES['PARALLEL_PORT_INPUT']:ParallelPortEvent,
                                         EventConstants.EVENT_TYPES['MESSAGE']:MessageEvent,
                                         EventConstants.EVENT_TYPES['EYE_SAMPLE']:MonocularEyeSample,
                                         EventConstants.EVENT_TYPES['BINOC_EYE_SAMPLE']:BinocularEyeSample,
                                         EventConstants.EVENT_TYPES['FIXATION_START']:FixationStartEvent,
                                         EventConstants.EVENT_TYPES['FIXATION_END']:FixationEndEvent,
                                         EventConstants.EVENT_TYPES['SACCADE_START']:SaccadeStartEvent,
                                         EventConstants.EVENT_TYPES['SACCADE_END']:SaccadeEndEvent,
                                         EventConstants.EVENT_TYPES['BLINK_START']:BlinkStartEvent,
                                         EventConstants.EVENT_TYPES['BLINK_END']:BlinkEndEvent
                                        })

    EventConstants.EVENT_TYPES.update(dict([(v,k) for k,v in EventConstants.EVENT_TYPES.items()]))
    EventConstants.DEVICE_TYPES.update(dict([(v,k) for k,v in EventConstants.DEVICE_TYPES.items()]))
    EventConstants.EVENT_CLASSES.update(dict([(v,k) for k,v in EventConstants.EVENT_CLASSES.items()]))
    EventConstants.DEVICE_CATERGORIES.update(dict([(v,k) for k,v in EventConstants.DEVICE_CATERGORIES.items()]))
