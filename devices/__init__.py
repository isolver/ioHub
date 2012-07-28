"""
ioHub.devices module __init__

Part of the Eye Movement Research Toolkit
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
    defaultValueDict={}
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=['I_tuple','I_np_array','I_public_dict','I_tables_row']+attributeNames
    def __init__(self,*args,**kwargs):
        self.I_public_dict=dict()
        self.I_np_array=None
        self.I_tables_row=None
        
        ovalues=[]
        for key in self.attributeNames:
            value=kwargs[key]
            setattr(self,key,value)
            if key[:2] is not 'I_':
                ovalues.append(value)
                self.I_public_dict[key]=value
        #print "ovalues:",len(ovalues)," <> ",ovalues
        #print "self.ndType:",self.ndType.__len__()," <> ",self.ndType
        self.I_tuple=tuple(ovalues) 

    @classmethod
    def getAttributesList(cls):
        return [e[0] for e in cls.dataType]
    
    def asTuple(self):
        return self.I_tuple
        
    def asDict(self):
        return self.I_public_dict

    def asNumpyArray(self):
        if self.I_np_array is None:
            self.I_np_array=N.array([self.I_tuple,],self.ndType) 
        return self.I_np_array
    
    def getTablesRow(self):
        return self.I_tables_row
        
########### Base Abstract Device that all other Devices inherit from ##########
class Device(ioObject):
    dataType=ioObject.dataType+[('instance_code','a24'),('category_id','u1'),('type_id','u1'),('user_label','a24'),('os_device_code','a64'),('max_event_buffer_length','u2'),('events_ipc','b'),('data_presistance','b')]
    attributeNames=[e[0] for e in dataType]
    defaultValueDict=dict(ioObject.defaultValueDict,**{'instance_code':'INSTANCE_CODE_NOT_SET','category_id':0,'type_id':0,'user_label':'USER_LABEL_NOT_SET','os_device_code':'OS_DEV_CODE_NOT_SET','max_event_buffer_length':512,'events_ipc':True,'data_presistance':True})
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames+['I_eventBuffer',]
    
    def __init__(self,*args,**kwargs):
        ioObject.__init__(self,**kwargs)
        self.I_eventBuffer=deque(maxlen=self.max_event_buffer_length)

    def getEventBuffer(self):
        return self.I_eventBuffer
            
    @classmethod
    def getDefaultAtrributeValueDict(cls):
        return dict(cls.defaultValueDict)
        
########### Base Device Event that all other Device Events inherit from ##########

class DeviceEvent(ioObject):
    dataType=ioObject.dataType+[('experiment_id','u8'),('session_id','u4'),('event_id','u8'),('event_type','u1'),
                                ('device_instance_code','a24'),('device_time','u8'), ('logged_time', 'u8'), ('hub_time','u8'),
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
        if self.hub_time is None:
            self.hub_time=self.log_time
            print 'Warning: Using Log Time as Hub Time', self.label
        return self.hub_time#(currentMsec()-self.device.offset)*self.device.drift-self.delay

    @classmethod
    def createFromOrderedList(cls,list):
        vdict={n:list[i] for i,n in enumerate(cls.attributeNames)}
        print 'vdict:',vdict
        return cls(**vdict)
        
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
from experiment import ExperimentRuntimeDevice
from experiment import Message, Command
#import commonETI as eyeTrackerInterface
