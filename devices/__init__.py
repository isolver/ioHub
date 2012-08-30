"""
ioHub Python Module

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""
import numpy as N
import platform
import timeit
from collections import deque

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
        return Computer.currentSec()*1000.0

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
    dataType=[]
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=['I_tuple','I_np_array']+attributeNames
    def __init__(self,*args,**kwargs):
        self.I_np_array=None
        self.I_tuple=None
        
        ovalues=[]
        for key in self.attributeNames:
            value=kwargs[key]
            setattr(self,key,value)
            if key[:2] is not 'I_':
                ovalues.append(value)
        self.I_tuple=tuple(ovalues)
    
    def _asTuple(self):
        return self.I_tuple

    def _asNumpyArray(self):
        if self.I_np_array is None:
            #print '=================='
            #print len(self.I_tuple)
            #print self.I_tuple
            #print '-------------'
            #print self.ndType
            self.I_np_array=N.array([self.I_tuple,],self.ndType) 
        return self.I_np_array
        
########### Base Abstract Device that all other Devices inherit from ##########
class Device(ioObject):
    dataType=ioObject.dataType+[('instance_code','a48'),('category_id','u1'),('type_id','u1'),('device_class','a24'),('user_label','a24'),('os_device_code','a64'),('max_event_buffer_length','u2')]
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    DEVICE_TIMEBASE_TO_USEC=1.0
    __slots__=attributeNames+['I_nativeEventBuffer','I_eventListeners','I_ioHubEventBuffer']
    def __init__(self,*args,**kwargs):
        ioObject.__init__(self,**kwargs)
        self.I_ioHubEventBuffer=deque(maxlen=self.max_event_buffer_length)
        self.I_nativeEventBuffer=deque(maxlen=self.max_event_buffer_length)
        self.I_eventListeners=list()

    def getEvents(self):
        eventList=[]
        while len(self.I_ioHubEventBuffer) > 0:
            eventList.append(self.I_ioHubEventBuffer.popleft().I_tuple)
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
    dataType=ioObject.dataType+[('experiment_id','u8'),('session_id','u4'),('event_id','u8'),('event_type','u1'),
                                ('device_instance_code','a48'),('device_time','u8'), ('logged_time', 'u8'), ('hub_time','u8'),
                                ('confidence_interval', 'f4'),('delay', 'f4')]
    attributeNames=[e[0] for e in dataType]
    defaultValueDict=None
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames
    def __init__(self,*args,**kwargs):
        ioObject.__init__(self,**kwargs)
                   
    def __cmp__(self,other):
        return self.hub_time-other.hub_time
        
    def hubTime(self):
        return self.hub_time

    @classmethod
    def createFromOrderedList(cls,list):
        combo = zip(cls.attributeNames,eventValueList)
        kwargs = dict(combo)
        return cls(**kwargs)
        
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

typeCodeToClass=dict()

def buildTypeCodeToClassDict():
    global typeCodeToClass
    
    import ioHub
    from ioHub import EVENT_TYPES
    
    typeCodeToClass[EVENT_TYPES['KEYBOARD_PRESS']]=KeyboardPressEvent
    typeCodeToClass[EVENT_TYPES['KEYBOARD_RELEASE']]=KeyboardReleaseEvent
    typeCodeToClass[EVENT_TYPES['MOUSE_MOVE']]=MouseMoveEvent
    typeCodeToClass[EVENT_TYPES['MOUSE_WHEEL']]=MouseWheelEvent
    typeCodeToClass[EVENT_TYPES['MOUSE_PRESS']]=MouseButtonDownEvent
    typeCodeToClass[EVENT_TYPES['MOUSE_RELEASE']]=MouseButtonUpEvent
    typeCodeToClass[EVENT_TYPES['MOUSE_DOUBLE_CLICK']]=MouseDoubleClickEvent
    typeCodeToClass[EVENT_TYPES['PARALLEL_PORT_INPUT']]=ParallelPortEvent
    typeCodeToClass[EVENT_TYPES['MESSAGE']]=MessageEvent
    typeCodeToClass[EVENT_TYPES['COMMAND']]=CommandEvent
    typeCodeToClass[EVENT_TYPES['EYE_SAMPLE']]=MonocularEyeSample
    typeCodeToClass[EVENT_TYPES['BINOC_EYE_SAMPLE']]=BinocularEyeSample
    typeCodeToClass[EVENT_TYPES['FIXATION_START']]=FixationStartEvent
    typeCodeToClass[EVENT_TYPES['FIXATION_END']]=FixationEndEvent
    typeCodeToClass[EVENT_TYPES['SACCADE_START']]=SaccadeStartEvent
    typeCodeToClass[EVENT_TYPES['SACCADE_END']]=SaccadeEndEvent
    typeCodeToClass[EVENT_TYPES['BLINK_START']]=BlinkStartEvent
    typeCodeToClass[EVENT_TYPES['BLINK_END']]=BlinkEndEvent
    #typeCodeToClass['']=
    #typeCodeToClass['']=
    #typeCodeToClass['']=
    #typeCodeToClass['']=
    #typeCodeToClass['']=
    #typeCodeToClass['']=
