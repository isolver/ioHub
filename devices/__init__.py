"""
ioHub
.. file: ioHub/devices/__init__.py

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""
from __future__ import division
import gc, os, platform
import collections
from collections import deque
from operator import itemgetter
import numpy as N
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

        cls._dataType=cls._baseDataTypes+cls._newDataTypes
        cls.CLASS_ATTRIBUTE_NAMES=[e[0] for e in cls._dataType]
        cls.NUMPY_DTYPE=N.dtype(cls._dataType)

        if len(cls.__subclasses__())==0 and 'DeviceEvent' in [c.__name__ for c in cls.mro()]:
            cls.namedTupleClass=collections.namedtuple(name+'NT',cls.CLASS_ATTRIBUTE_NAMES)


    def _findDeviceParent(cls,bases):
        parent=None
        if len(bases)==1:
            parent=bases[0]
        else:
            for p in bases:
                if 'Device' in p.__name__:
                    parent=p
                    break
        if parent is None or 'object' in parent.__name__:
            return None
        return parent

class ioObject(object):
    """
    The ioObject class is the base class for all ioHub Device and DeviceEvent classes.

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

    def _asDict(self):
        """
        Return the ioObject in dictionary format, with keys as the ioObject's
        attribute names, and dictionary values equal to the attribute values.

        Return (dict): dictionary of ioObjects attribute_name, attributes values.
        """
        return dict(zip(self.CLASS_ATTRIBUTE_NAMES,self._attribute_values))

    def _asList(self):
        """
        Return the ioObject in list format, which is a 1D list of the ioObject's
        attribute values, in the order the ioObject expects them if passed to a class constructor.

        Return (list): 1D list of ioObjects _attribute_values
        """
        return self._attribute_values

    def _asNumpyArray(self):
        """
        Return the ioObject as a numpy array, with the array values being equal to
        what would be returned by the asList() method, and the array cell data types
        being specified by NUMPY_DTYPE class constant.

        Return (numpy.array): numpy array representation of object.
        """
        return N.array([tuple(self._attribute_values),],self.NUMPY_DTYPE)

    def _getRPCInterface(self):
        rpcList=[]
        dlist = dir(self)
        for d in dlist:
            if d[0] is not '_' and d not in ['asNumpyArray',]:
                if callable(getattr(self,d)):
                    rpcList.append(d)
        return rpcList

class Computer(object):
    """
    The Computer class does not extend the ioHub.devices.Device class, however
    it is conseptually convienient to think of the Computer class as a type of
    Device. The Computer class contains the ioHub Clock used to access the ioHub time
    from the Experiment process as well as time stamp all Device Events.
    
    The Computer Class also contains methods allowing the Experiment and ioHub 
    Process affinities to be set to particular processing units of the computer
    if desired. The operating system priority of either process can also be
    increased if desired.
    
    There is also a long list of methods that can be used to access the current processes
    memory usage, CPU usage, network and disk access, and more, as the Computer
    class provides an interface to the very useful Process class of the `psutil Python package <https://code.google.com/p/psutil/>`_.
    
    The Computer class only contains static or class level methods, so an instance 
    of the class does **not** need to be created. The Computer device can either be accessed 
    via the ioHub package using 'ioHub.devices.Computer', or using the 'devices.computer'
    attribute of the ioClientConnection class or the ioHubExperimentRuntime class.    
    """
    _nextEventID=1
    
    #: True if the current process is the ioHub Server Process. False if the
    #: current process is the Experiment Runtime Process.
    isIoHubProcess=False
    
    #: True if the current process is currently in high or real-time priority mode
    #: (enabled by calling Computer.enableHighPriority() or Computer.enableRealTimePriority() )
    #: False otherwise.
    inHighPriorityMode=False
    
    #: The ioHub.ioClock instance used as the common time base for all devices
    #: and between the ioHub Server and Experiment Runtime Process. Do not 
    #: access this class directly, instead use the Computer.getTime()
    #: and associated method name alias's to actually get the current ioHub time.
    globalClock=None
    
    _platform_uname = platform.uname()

    #: The name of the current operating system Python is running on.
    #: i.e. Windows or Linux
    system=_platform_uname[0]
    
    #node, release, version, machine, processor = _platform_uname[1:]
    
    #: Attribute representing the number of *processing units* available on the current computer. 
    #: This includes cpu's, cpu cores, and hyperthreads. Notes:
    #:      - processingUnitCount = num_cpus*num_cores_per_cpu*num_hyperthreads.
    #:      - For single core CPU's,  num_cores_per_cpu = 1.
    #:      - For CPU's that do not support hyperthreading,  num_hyperthreads = 1
    #:        otherwise num_hyperthreads = 2.  
    processingUnitCount=psutil.NUM_CPUS
    
    #: The system ID of the current Python process.
    currentProcessID=os.getpid()
    
    #: Access to the psutil.Process class for the current system Process.
    currentProcess=psutil.Process(currentProcessID)
    
    #: The system ID of the ioHub Server process.
    ioHubServerProcessID=None
    
    #: The psutil Process object for the ioHub Server.
    ioHubServerProcess=None
    
    _process_original_nice_value=-1 # used on linux.
    
    def __init__(self):
        print2err("WARNING: Computer is a static class, no need to create an instance. just use Computer.xxxxxx")


    @staticmethod
    def enableHighPriority(disable_gc=True):
        """        
        Sets the priority of the current process to high priority
        and optionally (default is true) disable the python GC. This is very
        useful for the duration of a trial, for example, where you enable at
        start of trial and disable at end of trial. 
        
        On Linux, the process is set to a nice level of 10.

        Args:
            disable_gc(bool): True = Turn of the Python Garbage Collector. 
                              False = Leave the Garbage Collector running.
                              Default: True
        """
        if Computer.inHighPriorityMode is False:
            if disable_gc:
                gc.disable()
            if Computer.system=='Windows':
                Computer.currentProcess.set_nice(psutil.HIGH_PRIORITY_CLASS)
                Computer.inHighPriorityMode=True
            elif Computer.system=='Linux':
                current_nice=Computer.currentProcess.get_nice()
                Computer._process_original_nice_value=current_nice
                import ioHub
                ioHub.print2err("Current nice is: ", current_nice,' pid is ',Computer.currentProcessID)
                if current_nice <10:
                    Computer.currentProcess.set_nice(10)
                    Computer.currentProcess.get_nice()
                    ioHub.print2err("Set nice to 10; now reads: ", 
                                    Computer.currentProcess.get_nice())
                    Computer.inHighPriorityMode = True
                    

    @staticmethod
    def enableRealTimePriority(disable_gc=True):
        """
        Sets the priority of the current process to real-time priority class
        and optionally (default is true) disable the python GC. This is very
        useful for the duration of a trial, for example, where you enable at
        start of trial and disable at end of trial. Note that on Windows 7
        it is not possible to set a process to real-time priority, so high-priority
        is used instead.
        
        On Linux, the process is set to a nice level of 16.
        
        Args:
            disable_gc(bool): True = Turn of the Python Garbage Collector.
                              False = Leave the Garbage Collector running.
                              Default: True
        """
        if Computer.inHighPriorityMode is False:
            if disable_gc:
                gc.disable()
            if Computer.system=='Windows':
                Computer.currentProcess.set_nice(psutil.REALTIME_PRIORITY_CLASS)
                Computer.inHighPriorityMode = True
            elif Computer.system=='Linux':
                current_nice=Computer.currentProcess.get_nice()
                Computer._process_original_nice_value=current_nice
                import ioHub
                ioHub.print2err("Current nice and process id are: ", current_nice, " , ",Computer.currentProcessID)
                if current_nice <16:
                    Computer.currentProcess.set_nice(16)
                    Computer.currentProcess.get_nice()
                    ioHub.print2err("Set nice to 16; now reads: ", 
                                    Computer.currentProcess.get_nice())
                    Computer.inHighPriorityMode = True

    @staticmethod
    def disableRealTimePriority():
        """
        Sets the priority of the Current Process back to normal priority
        and enables the python GC. In general you would call 
        enableRealTimePriority() at start of trial and call 
        disableHighPriority() at end of trial.

        On Linux, sets the nice level of the process back to the value being used
        prior to the call to enableRealTimePriority()
        
        Return: None
        """
        Computer.disableHighPriority()

    @staticmethod
    def disableHighPriority():
        """
        Sets the priority of the Current Process back to normal priority
        and enables the python GC. In general you would call 
        enableHighPriority() at start of trial and call 
        disableHighPriority() at end of trial.

        On Linux, sets the nice level of the process back to the value being used
        prior to the call to enableHighPriority()
        
        Return: None
        """
        try:
            if Computer.inHighPriorityMode is True:
                gc.enable()
                if Computer.system=='Windows':
                    Computer.currentProcess.set_nice(psutil.NORMAL_PRIORITY_CLASS)
                    Computer.inHighPriorityMode=False
                elif Computer.system=='Linux' and Computer._process_original_nice_value > 0:
                    Computer.currentProcess.set_nice(Computer._process_original_nice_value)
                    Computer.inHighPriorityMode=False
        except psutil.AccessDenied:
            import ioHub            
            ioHub.print2err("WARNING: Could not disable increased priority for process {0}".format(Computer.currentProcessID))

    @staticmethod
    def getProcessAffinities():
        """Retrieve the current Experiment Process affinity list and ioHub Process affinity list.
    
        Returns:
           (list,list) Tuple of two lists: Experiment Process affinity ID list and ioHub Server Process affinity ID list. 
           
        For example, on a 2 core CPU with hyper-threading, the possible 'processor'
        list would be [0,1,2,3], and by default both the Experiment and ioHub Server
        processes can run on any of these 'processors', so::


            psychoCPUs,ioHubCPUS=Computer.getProcessAffinities()
            print psychoCPUs,ioHubCPUS

            >> [0,1,2,3], [0,1,2,3]


        If setProcessAffinities was used to set the Experiment process to core 1
        (index 0 and 1) and the ioHub Server process to core 2 (index 2 and 3),
        with each using both hyper threads of the given core, the set call would look like::


            Computer.setProcessAffinities([0,1],[2,3])

            psychoCPUs,ioHubCPUS=Computer.getProcessAffinities()
            print psychoCPUs,ioHubCPUS

            >> [0,1], [2,3]


        If the ioHub is not being used (i.e self.hub == None), then only the Experiment
        process affinity list will be returned and None will be returned for the
        ioHub process affinity::

            psychoCPUs,ioHubCPUS=Computer.getProcessAffinities()
            print psychoCPUs,ioHubCPUS

            >> [0,1,2,3], None

        But in this case, why are you using the ioHub package at all? ;)
        """
        return Computer.currentProcess.get_cpu_affinity(),Computer.ioHubServerProcess.get_cpu_affinity()

    @staticmethod
    def setProcessAffinities(experimentProcessorList, ioHubProcessorList):
        """Sets the processor affinity for the Experiment Runtime Process and the ioHub Server Process.
        
        Args:
           experimentProcessorList (list): list of int processor ID's to set the Experiment Process affinity to. An empty list means all processors.
           
           ioHubProcessorList (list): list of int processor ID's to set the ioHub Server Process affinity to. An empty list means all processors.
    
        Returns:
           None

        For example, on a 2 core CPU with hyper-threading, the possible 'processor'
        list would be [0,1,2,3], and by default both the experiment and ioHub
        server processes can run on any of these 'processors',
        so to have both processes have all processors available 
        (which is the default), you would call::

            Computer.setProcessAffinities([0,1,2,3], [0,1,2,3])

            # check the process affinities
            psychoCPUs,ioHubCPUS=Computer.getProcessAffinities()
            print psychoCPUs,ioHubCPUS

            >> [0,1,2,3], [0,1,2,3]

        based on the above CPU example.

        If setProcessAffinities was used to set the experiment process to core 1
        (index 0,1) and the ioHub server process to core 2 (index 2,3), with 
        each using both hyper threads of the given core, the set call would look
        like::

            Computer.setProcessAffinities([0,1],[2,3])

            # check the process affinities
            psychoCPUs,ioHubCPUS=Computer.getProcessAffinities()
            print psychoCPUs,ioHubCPUS

            >> [0,1], [2,3]
        """
        Computer.currentProcess.set_cpu_affinity(experimentProcessorList)
        Computer.ioHubServerProcess.set_cpu_affinity(ioHubProcessorList)

    @staticmethod
    def autoAssignAffinities():
        """Auto sets the experiment process and ioHub process processor affinities
        based on some very simple logic.

        Args:
            None
            
        Returns:
            None

        It is not known at this time if the implementation of this method makes
        any sense in terms of actually improving performance. Field tests and 
        feedback will need to occur, based on which the algorithm can be improved.

        Currently, if the system is detected to have 1 processing unit, 
        or greater than 8 processing units, nothing is done by the method.

        For a system that has two processing units, the PsychoPy Process is 
        assigned to index 0, ioHub Process assigned to 1.

        For a system that has four processing units, the Experiment Process is 
        assigned to index's 0,1 and the ioHub Process assigned to 2,3.

        For a system that has eight processing units, the PsychoPy Process is 
        assigned to index 2,3, ioHub Server assigned to 4,5. All other processes
        running on the OS are attempted to be assigned to indexes 0,1,6,7.
        """
        cpu_count=Computer.cpuCount
        print "System processor count:", cpu_count
        if cpu_count == 2:
            print 'Assigning experiment process to CPU 0, ioHubServer process to CPU 1'
            Computer.setProcessAffinities([0,],[1,])
        elif cpu_count == 4:
            print 'Assigning experiment process to CPU 0,1, ioHubServer process to CPU 2,3'
            Computer.setProcessAffinities([0,1],[2,3])
        elif cpu_count == 8:
            print 'Assigning experiment process to CPU 2,3, ioHubServer process to CPU 4,5, attempting to assign all others to 0,1,6,7'
            Computer.setProcessAffinities([2,3],[4,5])
            Computer.setAllOtherProcessesAffinity([0,1,6,7],[Computer.currentProcessID,Computer.ioHubServerProcessID])
        else:
            print "autoAssignAffinities does not support %d processors."%(cpu_count,)
            
    @staticmethod
    def getCurrentProcessAffinity():
        """
        Returns a list of 'processor' ID's (from 0 to Computer.processingUnitCount-1)
        that the current (calling) process is able to run on.

        Args:
            None
            
        Returns:
            None        
        """
        return Computer.currentProcess.get_cpu_affinity()

    @staticmethod
    def setCurrentProcessAffinity(processorList):
        """
        Sets the list of 'processor' ID's (from 0 to Computer.processingUnitCount-1)
        that the current (calling) process should only be allowed to run on.

        Args:
           processorList (list): list of int processor ID's to set the Experiment Process affinity to. An empty list means all processors.
            
        Returns:
            None
        
        """
        return Computer.currentProcess.set_cpu_affinity(processorList)

    @staticmethod
    def setProcessAffinityByID(processID,processorList):
        """
        Sets the list of 'processor' ID's (from 0 to Computer.processingUnitCount-1)
        that the process with the provided processID is able to run on.

        Args:
           processID (int): The system process ID that the affinity should be set for.

           processorList (list): list of int processor ID's to set process with the given processID too. An empty list means all processors.
            
        Returns:
            None
        """
        p=psutil.Process(processID)
        return p.set_cpu_affinity(processorList)

    @staticmethod
    def getProcessAffinityByID(processID):
        """
        Returns a list of 'processor' ID's (from 0 to Computer.processingUnitCount-1)
        that the process with the provided processID is able to run on.

        Args:
           processID (int): The system process ID that the affinity should be set for.
            
        Returns:
           processorList (list): list of int processor ID's to set process with the given processID too. An empty list means all processors.
        """
        p=psutil.Process(processID)
        return p.get_cpu_affinity()

    @staticmethod
    def setAllOtherProcessesAffinity(processorList, excludeProcessByIDList=[]):
        """
        Sets the list of 'processor' ID's (from 0 to Computer.processingUnitCount-1)
        that all processes, other than those specified in the excludeProcessByIDList,
        are able to run on. excludeProcessByIDList should be a list of process ID
        integers, or an empty list. Note that the OS may not allow the calling process
        to set the affinity of every other process running on the system. For
        example, some system level processing can not have their affinity set
        by a user level application. However, in general, many 
        processes can have their affinity set by another user process.

        Args:
           processorList (list): list of int processor ID's to set all non Experiment or ioHub Server Process's to. An empty list means all processors.
           
        Kwargs:
           excludeProcessByIDList (list): A list of process ID's that should not have their process affinity settings changed.
           
        Returns:
           None
        """
        for p in psutil.process_iter():
            if p.pid not in excludeProcessByIDList:
                try:
                    p.set_cpu_affinity(processorList)
                    print2err('Set OK process affinity: %s : %ld'%(p.name,p.pid))
                except Exception:
                    print2err('ERROR setting process affinity: %s : %ld'%(p.name,p.pid))

    @staticmethod
    def currentTime():
        """
        Alias for Computer.currentSec()
        """
        return Computer.globalClock.getTime()
        
    @staticmethod
    def currentSec():
        """
        Returns the current sec.msec-msec time of the system. 
        
        Args:
           None
                      
        Returns:
           None
           
        On Windows this is implemented by directly calling the Windows QPC functions using ctypes.
        
        This is done so that no offset is applied to the time base used by either
        the Experiment or ioHub Server Process. The standard Python high resolution 
        timer can not be used on Windows, as it starts at 0.0 based on when the first
        call to the python time function is called, which will be different between
        Experiment and ioHub Server Processes since they do not start at exactly the same time.
        
        By using a 0 offset root time base, both interpreters have a totally 
        common / shared time-base to use. This means that either process knows
        the current time of the other process, since they are the same. ;)

        For other OS's, right now the timeit.base_timer function is used, 
        which as of python 2.7 correctly selects the best high resolution clock
        for the OS the interpreter is running on.
        """

        return Computer.globalClock.getTime()

    @staticmethod
    def getTime():
        """
        Alias for Computer.currentSec()        
        """
        return Computer.globalClock.getTime()

    @staticmethod
    def _getNextEventID():
        n = Computer._nextEventID
        Computer._nextEventID+=1
        return n

    @staticmethod
    def getPhysicalSystemMemoryInfo():
        """Return a class containing information about current memory usage.

        Args:
           None
                      
        Returns:
           vmem(total=long, available=long, percent=float, used=long, free=long) 
           
               vmem.total: the total amount of memory in bytes.
               vmem.available: the available amount of memory in bytes.
               vmem.percent: the percent of memory in use by the system.
               vmem.used: the used amount of memory in bytes.
               vmem.free: the amount of memory that is free in bytes.On Windows, this is the same as vmem.available.
           
        """
        m= psutil.virtual_memory()
        return m

    @staticmethod
    def getCPUTimeInfo(percpu=False):
        """Return information about the computers CPU usage.
        
        Kwargs:
           percpu (bool): If True, a list of cputimes objects is returned, one for each processing unit for the computer. If False, only a single cputimes object is returned.
                      
        Returns:
           cputimes(user=float, system=float, idle=float)
        """
        return psutil.cpu_times(percpu)

    #
    # Local / Current Process Related
    #

    @staticmethod
    def getCurrentProcess():
        """
        Get the current / Local process (as a psutil Process object).
        The psutil Process object has some nice methods you can access. 
        See the `psutil project documentation <https://code.google.com/p/psutil/wiki/Documentation#Classes>`_ for details.

        Args:
           None
                      
        Returns:
           psutil.Process object for the current system process.
           
        """
        return Computer.currentProcess


########### Base Abstract Device that all other Devices inherit from ##########
class Device(ioObject):
    """
    The Device class is the base class for all ioHub Device types.
    Any ioHub Device class (i.e Keyboard Device, Mouse Device, etc)
    also include the methods and attributes of this class.
    """
    DEVICE_TYPE_ID_INDEX=0
    DEVICE_CLASS_NAME_INDEX=1
    DEVICE_USER_LABEL_INDEX=2
    DEVICE_BUFFER_LENGTH_INDEX=3
    DEVICE_MAX_ATTRIBUTE_INDEX=3

    # Multiplier to use to convert this devices event time stamps to sec format.
    # This is set by the author of the device class or interface implementation.
    DEVICE_TIMEBASE_TO_SEC=1.0

    _baseDataTypes=ioObject._baseDataTypes
    _newDataTypes=[('type_id',N.uint8),         # The id of the device type = ioHub.DeviceConstants.XXXXXXXXXX

                   ('device_class',N.str,24),   # The name of the Device Class used to create an instance
                                                # of this device type. = self.__class__.__name__

                   ('name',N.str,24),           # The name given to this device instance. User Defined. Should be
                                                # unique within all devices of the same type_id for a given experiment.

                   ('max_event_buffer_length',N.uint16) # The maximum size of the device level event buffer for this
                                                        # device instance. If the buffer becomes full, when a new event
                                                        # is added, the oldest event in the buffer is removed.
                ]

    ALL_EVENT_CLASSES=[]
    
    DEVICE_TYPE_ID=None
    DEVICE_TYPE_STRING=None
    
    __slots__=[e[0] for e in _newDataTypes]+['_nativeEventBuffer','_eventListeners','_ioHubEventBuffer',
                                            '_lastPollTime','_lastCallbackTime','_isReportingEvents','_startupConfiguration',
                                            'monitor_event_types']
    
    def __init__(self,*args,**kwargs):
        #: The id of the device type. Device type ID's are enumerated using class attributes of the DeviceConstants class.
        self.type_id=None

        #: The name of the Device Class used to create an instance
        #: of this device type. This str is retrieved from self.__class__.__name__
        self.device_class=None

        #: The user defined name given to this device instance. A device name must be
        #: unique within all devices of the same type_id for a given experiment.
        self.name=None

        #: The maximum size of the device level event buffer for this
        #: device instance. If the buffer becomes full, when a new event
        #: is added, the oldest event in the buffer is removed.
        self.max_event_buffer_length=None

        #: A list of event type ID's that can be generated by this device type
        #: which should be monitored and reported by the ioHub Server process.
        #: Event type ID's are enumerated using class attributes of the EventConstants class.
        self.monitor_event_types=kwargs.get('monitor_event_types',[])
        
        self._isReportingEvents=True
        self._ioHubEventBuffer=dict()
        self._eventListeners=dict()
        self._startupConfiguration=None
        self._lastPollTime=0
        self._lastCallbackTime=0
        ioObject.__init__(self,*args,**kwargs)
        self._nativeEventBuffer=deque(maxlen=self.max_event_buffer_length)

        
    def getStartupConfiguration(self):
        """
        Retrieve the configuration information used when the device was initialized by the ioHub Server Process. 
        
        Args:
            None
            
        Return:
            dict: dictionary of configuartion settings used when the device was originally created by the ioHub Server process.
        """
        return self._startupConfiguration

    def getEvents(self,*args,**kwargs):
        """
        Retrieve any DeviceEvents that have occurred since the last call to the
        device's getEvents() or clearEvents() methods.

        Note that calling the ioHub Server Process level getEvents() or clearEvents() methods
        via the ioHubClientConnection class does *not* effect device level event buffers.

        Args:
            eventTypeID (int): Specifies a specific event type to return from the device. Events that have occurred but do not match the event ID specified are ignored. Event type ID's can be accessed via the EventConstants class; all available event types are class atttributes of EventConstants.

            clearEvents (int): If True, clear the device event buffer before returning any events. If False, events are not removed from the device event buffer. Default is True.

            asType (str): The object type to return events as. Valid values are 'namedtuple' (default), 'dict', 'list', or 'object'.

        Kwargs:
            eventTypeID (int): Specifies a specific event type to return from the device. Events that have occurred but do not match the event ID specified are ignored. Event type ID's can be accessed via the EventConstants class; all available event types are class atttributes of EventConstants.

            clearEvents (int): If True, clear the device event buffer before returning any events. If False, events are not removed from the device event buffer. Default is True.

            asType (str): The object type to return events as. Valid values are 'namedtuple' (default), 'dict', 'list', or 'object'.
            
        Return (tuple): 
            A list of event objects, ordered by the ioHub time for each event.
            The event object type is determined by the asType parameter to the method;
            by default a namedtuple object is returned for each event. 
        """
        if len(args)==1:
            eventTypeID=args[0]
            clearEvents=kwargs.get('clearEvents',True)
        elif len(args)==2:
            eventTypeID=args[0]
            clearEvents=args[1]
        else:
            eventTypeID=kwargs.get('event_type_id',None)
            clearEvents=kwargs.get('clearEvents',True)

        currentEvents=[]
        if eventTypeID:
            currentEvents=list(self._ioHubEventBuffer.get(eventTypeID,[]))
            if clearEvents is True and len(currentEvents)>0:
                self._ioHubEventBuffer[eventTypeID]=[]
        else:
            [currentEvents.extend(l) for l in self._ioHubEventBuffer.values()]
            if clearEvents is True and len(currentEvents)>0:
                self.clearEvents()

        if len(currentEvents)>0:
            sorted(currentEvents, key=itemgetter(DeviceEvent.EVENT_HUB_TIME_INDEX))
        return currentEvents


    def clearEvents(self):
        """
        Clears any DeviceEvents that have occurred since the last call to the devices getEvents()
        with clearEvents = True, or the devices clearEvents() methods.

        Args:
            None
            
        Return: 
            None
            
        Note that calling the ioHub Server Process level getEvents() or clearEvents() methods
        via the ioHubClientConnection class does *not* effect device level event buffers.
        """
        self._ioHubEventBuffer.clear()

    def enableEventReporting(self,enabled=True):
        """
        Sets whether a Device should report events and provide them to the Experiment Process
        and / or save them to the ioDataStore.

        Args:
            enabled (bool): True (default), monitor and report device events as they occur. False, Do not report any events for the device until reporting is enabled.

        Return:
            bool: current reporting state
            
        """
        self._isReportingEvents=enabled
        return self._isReportingEvents

    def isReportingEvents(self):
        """
        Returns whether a Device is currently report events or whether the device is ignoring any events that occur.

        Args: 
            None

        Return: 
            bool: current reporting state
        """
        return self._isReportingEvents

    def _handleEvent(self,e):
        etypelist=self._ioHubEventBuffer.get(e[DeviceEvent.EVENT_TYPE_ID_INDEX],None)
        if etypelist is None:
            self._ioHubEventBuffer[e[DeviceEvent.EVENT_TYPE_ID_INDEX]]=[e,]
        else:
            etypelist.append(e)
        
    def _getNativeEventBuffer(self):
        return self._nativeEventBuffer

    def _addNativeEventToBuffer(self,e):
        if self.isReportingEvents():
            self._nativeEventBuffer.append(e)

    def _addEventListener(self,l,eventTypeIDs=None):
        if eventTypeIDs is None or eventTypeIDs=='ALL' or len(eventTypeIDs) == 0:
            eventTypeIDs=[ei.EVENT_TYPE_ID for ei in self.monitor_event_types]

        lca=0
        for ei in eventTypeIDs:
            if ei not in self._eventListeners:
                self._eventListeners[ei]=[l,]
                lca+1
            else:
                if l not in self._eventListeners[ei]:
                    self._eventListeners[ei].append(l)
                    lca+1
        return lca == len(eventTypeIDs)
    
    def _removeEventListener(self,l):
        for etypelisteners in self._eventListeners.values():
            if l in etypelisteners:
                etypelisteners.remove(l)
            
    def _getEventListeners(self,forEventType):
        return self._eventListeners.get(forEventType,[])
        
    def _close(self):
        pass

########### Base Device Event that all other Device Events inherit from ##########

class DeviceEvent(ioObject):
    """
    The DeviceEvent class is the base class for all ioHub DeviceEvent types.

    Any ioHub DeviceEvent classes (i.e MouseMoveEvent,MouseWheelUpEvent, MouseButtonDownEvent,
    KeyboardPressEvent, KeyboardReleaseEvent, etc) also include the methods and attributes of
    the DeviceEvent class.
    """
    EVENT_EXPERIMENT_ID_INDEX=0
    EVENT_SESSION_ID_INDEX=1
    EVENT_ID_INDEX=2
    EVENT_TYPE_ID_INDEX=3
    EVENT_DEVICE_TIME_INDEX=4
    EVENT_LOGGED_TIME_INDEX=5
    EVENT_HUB_TIME_INDEX=6
    EVENT_CONFIDENCE_INTERVAL_INDEX=7
    EVENT_DELAY_INDEX=8
    EVENT_FILTER_ID_INDEX=9
    BASE_EVENT_MAX_ATTRIBUTE_INDEX=EVENT_FILTER_ID_INDEX

    # The Device Class that generates the given type of event.    
    PARENT_DEVICE=None
    
    # The string label for the given DeviceEvent type. Should be usable to get Event type
    #  from ioHub.EventConstants.getName(EVENT_TYPE_STRING), the value of which is the
    # event type id. This is set by the author of the event class implementation.
    EVENT_TYPE_STRING='UNDEFINED_EVENT'

    # The type id int for the given DeviceEvent type. Should be one of the int values in
    # ioHub.EventConstants.EVENT_TYPE_ID. This is set by the author of the event class implementation.
    EVENT_TYPE_ID=0
    

    _baseDataTypes=ioObject._baseDataTypes
    _newDataTypes=[
                ('experiment_id',N.uint32), # The ioDataStore experiment ID assigned to the experiment code
                                            # specified in the experiment configuration file for the experiment.

                ('session_id',N.uint32),    # The ioDataStore session ID assigned to the currently running
                                            # experiment session. Each time the experiment script is run,
                                            # a new session id is generated for use within the hdf5 file.

                ('event_id',N.uint32),      # The id assigned to the current device event instance. Every device
                                            # event generated by monitored devices during an experiment session is
                                            # assigned a unique id, starting from 0 for each session, incrementing
                                            # by +1 for each new event.

                ('type',N.uint8),           # The type id for the event. This is used to create DeviceEvent objects
                                            # or dictionary representations of an event based on the data from an
                                            # event value list.

                ('device_time',N.float32),   # If the device that generates the given device event type also time stamps
                                            # events, this field is the time of the event as given by the device,
                                            # converted to sec.msec-usec for consistancy with all other ioHub device times.
                                            # If the device that generates the given event type does not time stamp
                                            # events, then the device_time is set to the logged_time for the event.

                ('logged_time', N.float32),  # The sec time that the event was 'received' by the ioHub Server Process.
                                            # For devices that poll for events, this is the sec time that the poll
                                            # method was called for the device and the event was retrieved. For
                                            # devices that use the event callback, this is the sec time the callback
                                            # executed and accept the event. Time is in sec.msec-usec

                ('time',N.float32),         # Time is in the normalized time base that all events share,
                                            # regardless of device type. Time is calculated differently depending
                                            # on the device and perhaps event type.
                                            # Time is what should be used when comparing times of events across
                                            # different devices. Time is in sec.msec-usec.

                ('confidence_interval', N.float32), # This property attempts to give a sense of the amount to which
                                                    # the event time may be off relative to the true time the event
                                                    # occurred. confidence_interval is calculated differently depending
                                                    # on the device and perhaps event types. In general though, the
                                                    # smaller the confidence_interval, the more likely it is that the
                                                    # calculated time of the event is correct. For devices where
                                                    # a realistic confidence_interval can not be calculated,
                                                    # for example if the event device delay is unknown, then a value
                                                    # of -1.0 should be used. Valid confidence_interval values are
                                                    # in sec.msec-usec and will range from 0.000000 sec.msec-usec
                                                    # and higher.

                ('delay',N.float32)  ,       # The delay of an event is the known (or estimated) delay from when the
                                            # real world event occurred to when the ioHub received the event for
                                            # processing. This is often called the real-time end-to-end delay
                                            # of an event. If the delay for an event can not be reasonably estimated
                                            # or is not known, a delay of -1.0 is set. Delays are in sec.msec-usec
                                            # and valid values will range from 0.000000 sec.msec-usec and higher.

                ('filter_id',N.int16)       # The filter identifier that the event passed through before being saved.
                                            # If the event did not pass through any filter devices, then the value will be 0.
                                            # Otherwise, the value is the | combination of the filter set that the
                                            # event passed through before being made available to the experiment,
                                            # or saved to the ioDataStore. The filter id can be used to determine
                                            # which filters an event was handled by, but not the order in which handling was done.
                                            # Default value is 0.
                ]

    # The name of the hdf5 table used to store events of this type in the ioDataStore pytables file.
    # This is set by the author of the event class implementation.
    IOHUB_DATA_TABLE=None

    __slots__=[e[0] for e in _newDataTypes]

    def __init__(self,*args,**kwargs):
        #: The ioDataStore experiment ID assigned to the experiment code
        #: specified in the experiment configuration file for the experiment.
        self.experiment_id=None

        #: The ioDataStore session ID assigned for each session of the experiment run.
        #: Each time the experiment script is run, a new session id is generated for use
        #: by the ioDataStore within the hdf5 file.
        self.session_id=None

        #: The id assigned to the current device event instance. Every device
        #: event generated by monitored devices during an experiment session is
        #: assigned a unique id, starting from 0 for each session, incrementing
        #: by +1 for each new event.
        self.event_id=None

        #: The type id for the event. This is used to create DeviceEvent objects
        #: or dictionary representations of an event based on the data from an
        #: event value list. Event types are all defined in the EventConstants class as class attributes.
        self.type=None
        
        #: If the device that generates an event type also time stamps
        #: the events, this field is the time of the event as given by the device,
        #: converted to sec.msec-usec for consistancy with all other ioHub device times.
        #: If the device that generates the event does not time stamp
        #: events, then the device_time is set to the logged_time for the event.
        self.device_time=None

        #: The sec.msec time that the event was 'received' by the ioHub Server Process.
        #: For devices where the ioHub polls for events, this is the time that the poll
        #: method was called for the device and the event was retrieved. For
        #: devices that use the event callback to inform the ioHub of new events,
        #: this is the time the callback began to be executed. Time is in sec.msec-usec
        self.logged_time=None

        #: The calculated ioHub time is in the normalized time base that all events share,
        #: regardless of device type. Time is calculated differently depending
        #: on the device and perhaps event type.
        #: Time is what should be used when comparing times of events across
        #: different devices. Time is in sec.msec-usec.
        self.time=None

        #: This property attempts to give a sense of the amount to which
        #: the event time may be off relative to the true time the event
        #: occurred. confidence_interval is calculated differently depending
        #: on the device and perhaps event types. In general though, the
        #: smaller the confidence_interval, the more likely it is that the
        #: calculated time of the event is correct. For devices where
        #: a realistic confidence_interval can not be calculated,
        #: for example if the event device delay is unknown, then a value
        #: of 0.0 is used. Valid confidence_interval values are
        #: in sec.msec-usec and will range from 0.000001 sec.msec-usec
        #: and higher.
        self.confidence_interval=None

        #: The delay of an event is the known (or estimated) delay from when the
        #: real world event occurred to when the ioHub received the event for
        #: processing. This is often called the real-time end-to-end delay
        #: of an event. If the delay for an event can not be reasonably estimated
        #: or is not known, a delay of -1.0 is set. Delays are in sec.msec-usec
        #: and valid values will range from 0.000000 sec.msec-usec and higher.
        self.delay=None

        #: The filter identifier that the event passed through before being saved.
        #: If the event did not pass through any filter devices, then the value will be 0.
        #: Otherwise, the value is the & combination of the filter set that the
        #: event passed through before being made available to the experiment,
        #: or saved to the ioDataStore. The filter id can be used to determine
        #: which filters an event was handled by, but not the order in which handling was done.
        #: Default value is 0.
        self.filter_id=None

        ioObject.__init__(self,*args,**kwargs)

    def __cmp__(self,other):
        return self.time-other.time

    @classmethod
    def createEventAsClass(cls,eventValueList):
        kwargs =cls.createEventAsDict(eventValueList)
        return cls(**kwargs)

    @classmethod
    def createEventAsDict(cls,values):
        return dict(zip(cls.CLASS_ATTRIBUTE_NAMES,values))

    #noinspection PyUnresolvedReferences
    @classmethod
    def createEventAsNamedTuple(cls,valueList):
        return cls.namedTupleClass(*valueList)
#
# Import Devices and DeviceEvents
#
from ioHub import DeviceConstants, EventConstants

if Computer.system == 'Linux':
    from . import pyXHook

deviceModulesAvailable=[]


from ioHub import print2err,printExceptionDetailsToStdErr

try:
    import keyboard
    from keyboard import Keyboard
    from keyboard import KeyboardEvent,KeyboardKeyEvent,KeyboardPressEvent,KeyboardReleaseEvent,KeyboardCharEvent
    deviceModulesAvailable.append('keyboard')
except:
    print2err("Warning: keyboard device module could not be imported.")
    printExceptionDetailsToStdErr()

try:
    from mouse import Mouse
    from mouse import (MouseEvent,MouseButtonEvent,MouseMoveEvent,MouseWheelEvent,MouseWheelUpEvent,
                       MouseWheelDownEvent,MouseButtonDownEvent,MouseButtonUpEvent,MouseDoubleClickEvent)
    deviceModulesAvailable.append('mouse')
except:
    print2err("Warning: mouse device module could not be imported.")
    printExceptionDetailsToStdErr()

if Computer.system == 'Windows':
    try:
        from parallelPort import ParallelPort
        from parallelPort import ParallelPortEvent
        deviceModulesAvailable.append('parallelPort')
    except:
#        print2err("Warning: parallelPort device module could not be imported.")
#        printExceptionDetailsToStdErr()
        pass
try:
    from serialIO import SerialIO
    from serialIO import SerialInputEvent

    deviceModulesAvailable.append('serial')
except:
#    print2err("Warning: serial device module could not be imported.")
#    printExceptionDetailsToStdErr()
    pass

if Computer.system == 'Windows':
    try:
        import xinput
        from xinput import GamePad
        from xinput import GamePadStateChangeEvent,GamePadDisconnectEvent,GamePadButtonEvent,GamePadThumbStickEvent,GamePadTriggerEvent
        deviceModulesAvailable.append('gamepad')
    except:
        print2err("Warning: gamepad device module could not be imported.")
        printExceptionDetailsToStdErr()

try:
    import experiment
    from experiment import ExperimentDevice
    from experiment import MessageEvent
    deviceModulesAvailable.append('experiment')
except:
    print2err("Warning: experiment device module could not be imported.")
    printExceptionDetailsToStdErr()

if Computer.system == 'Windows':
    try:
        import eyeTracker
        import eyeTracker.HW
        from eyeTracker.eye_events import *
        deviceModulesAvailable.append('eyetracker')
    except:
        print2err("Warning: eyetrackerinterface device module could not be imported.")
        printExceptionDetailsToStdErr()
    
try:
    import display
    from display import Display
    from ioHub import print2err, highPrecisionTimer
    deviceModulesAvailable.append('display')
except:
    print2err("Warning: display device module could not be imported.")
    printExceptionDetailsToStdErr()

if Computer.system == 'Windows':    
    try:
        import daq
        from daq import DAQDevice
        from daq import DAQEvent,DAMultiChannelInputEvent#,DASingleChannelInputEvent
        deviceModulesAvailable.append('daq')
    except:
        print2err("Warning: daq device module could not be imported.")
#        printExceptionDetailsToStdErr()
    
    try:
        import filters
        from filters import EventFilter
        from filters import GenericFilterEvent
        from filters import StampeFilter
        deviceModulesAvailable.append('filter')
    except:
        pass
#        print2err("Warning: daq device module could not be imported.")
#        printExceptionDetailsToStdErr()
    
try:
    import mbed
    from mbed import MBED1768
    deviceModulesAvailable.append('mbed')
except:
    pass
#    print2err("Warning: mbed device module could not be imported.")
#    printExceptionDetailsToStdErr()

DeviceConstants.addClassMappings()
EventConstants.addClassMappings()

