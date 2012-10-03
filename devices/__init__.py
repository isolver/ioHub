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
from ioHub import ioObject

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


####################### Device & DeviceEvent Constants ########################

class _EventConstantsBase(object):
    NOT_SUPPORTED_FIELD=0

    LEFT=1
    RIGHT=2
    BINOCULAR=4
    LEFT_RIGHT_AVERAGED=8
    SIMULATED=16

    AREA = 1
    DIAMETER = 2
    WIDTH = 3
    HEIGHT = 4
    MAJOR_AXIS = 5
    MINOR_AXIS = 6

    UNDEFINED_EVENT=0
    MESSAGE_EVENT=1
    KEYBOARD_KEY_EVENT =20
    KEYBOARD_PRESS_EVENT =21
    KEYBOARD_RELEASE_EVENT =22
    MOUSE_EVENT=30
    MOUSE_BUTTON_EVENT =31
    MOUSE_PRESS_EVENT =32
    MOUSE_RELEASE_EVENT =33
    MOUSE_DOUBLE_CLICK_EVENT =34
    MOUSE_WHEEL_EVENT =35
    MOUSE_WHEEL_UP_EVENT =36
    MOUSE_WHEEL_DOWN_EVENT =37
    MOUSE_MOVE_EVENT =39
    JOYSTICK_BUTTON_EVENT=50
    JOYSTICK_BUTTON_PRESS_EVENT=51
    JOYSTICK_BUTTON_RELEASE_EVENT=52
    JOYSTICK_POSITION_X_EVENT=53
    JOYSTICK_POSITION_Y_EVENT=54
    BUTTON_BOX_PRESS_EVENT=61
    BUTTON_BOX_RELEASE_EVENT=62
    TTL_INPUT_EVENT=71
    EYE_SAMPLE_EVENT=101
    BINOC_EYE_SAMPLE_EVENT=102
    FIXATION_START_EVENT=106
    FIXATION_END_EVENT=108
    SACCADE_START_EVENT=111
    SACCADE_END_EVENT=112
    BLINK_START_EVENT=116
    BLINK_END_EVENT=117

    UNKNOWN_DEVICE  = 0
    KEYBOARD_DEVICE  = 1
    MOUSE_DEVICE  = 2
    KB_MOUSE_COMBO_DEVICE  = 3
    TOUCH_PAD_DEVICE  = 5
    TOUCH_SCREEN_DEVICE  = 6
    DISPLAY_DEVICE  = 7
    EYE_TRACKER_DEVICE  = 8
    EXPERIMENT_DEVICE  = 9
    BUTTON_BOX_DEVICE  = 10
    JOYSTICK_DEVICE  = 11
    AUDIO_CAPTURE_DEVICE  = 12
    AUDIO_RECORING_DEVICE = 13
    VIDEO_CAPTURE_DEVICE  = 14
    VIDEO_RECORDING_DEVICE = 15
    HAPTIC_FEEDBACK_DEVICE  = 16
    COMPUTER_DEVICE  = 17
    PARALLEL_PORT_DEVICE  = 18
    TTL_INPUT_DEVICE  = 19
    TTL_OUTPUT_DEVICE  = 20
    TTL_IO_DEVICE  = 21
    A2D_INPUT_DEVICE  = 22
    D2A_OUTPUT_DEVICE  = 23
    ANALOG_IO_DEVICE  = 24
    GPIO_DEVICE  = 25
    PHOTOSENSOR_DEVICE = 26
    IR_MEASUREMENT_DEVICE = 27
    ARTIFICIAL_EYE_DEVICE = 28
    SPEAKER_DEVICE  = 29
    AMPLIFIER_DEVICE  = 30
    EEG_DEVICE  = 31
    MRI_DEVICE  = 32
    MEG_DEVICE  = 33
    SERIAL_DEVICE = 34
    NETWORK_DEVICE = 35
    OTHER_DEVICE  = 2048

    MOUSE_BUTTON_STATE_RELEASED=0 # a button was released
    MOUSE_BUTTON_STATE_PRESSED=1 # a button was pressed
    MOUSE_BUTTON_STATE_DOUBLE_CLICK=2 # a button double click event

    MOUSE_BUTTON_ID_NONE=0
    MOUSE_BUTTON_ID_LEFT=1
    MOUSE_BUTTON_ID_RIGHT=2
    MOUSE_BUTTON_ID_MIDDLE=4

    EVENT_TYPES = dict(UNDEFINED=0,
        MESSAGE =1,
        KEYBOARD_KEY =20,
        KEYBOARD_PRESS =21,
        KEYBOARD_RELEASE =22,
        MOUSE=30,
        MOUSE_BUTTON =31,
        MOUSE_PRESS =32,
        MOUSE_RELEASE =33,
        MOUSE_DOUBLE_CLICK =34,
        MOUSE_WHEEL =35,
        MOUSE_WHEEL_UP =36,
        MOUSE_WHEEL_DOWN =37,
        MOUSE_MOVE =39,
        JOYSTICK_BUTTON=50,
        JOYSTICK_BUTTON_PRESS =51,
        JOYSTICK_BUTTON_RELEASE =52,
        JOYSTICK_POSITION_X =53,
        JOYSTICK_POSITION_Y =54,
        BUTTON_BOX_PRESS =61,
        BUTTON_BOX_RELEASE =62,
        TTL_INPUT =71,
        EYE_SAMPLE =101,
        BINOC_EYE_SAMPLE =102,
        FIXATION_START =106,
        FIXATION_END =108,
        SACCADE_START =111,
        SACCADE_END =112,
        BLINK_START =116,
        BLINK_END =117)

    DEVICE_TYPES = dict( UNKNOWN_DEVICE  = 0,
        KEYBOARD_DEVICE  =1,
        MOUSE_DEVICE  =2,
        KB_MOUSE_COMBO_DEVICE  =3,
        TOUCH_PAD_DEVICE  = 5,
        TOUCH_SCREEN_DEVICE  = 6,
        DISPLAY_DEVICE  = 7,
        EYE_TRACKER_DEVICE  = 8,
        EXPERIMENT_DEVICE  = 9,
        BUTTON_BOX_DEVICE  = 10,
        JOYSTICK_DEVICE  = 11,
        AUDIO_CAPTURE_DEVICE  = 12,
        AUDIO_RECORING_DEVICE = 13,
        VIDEO_CAPTURE_DEVICE  = 14,
        VIDEO_RECORDING_DEVICE = 15,
        HAPTIC_FEEDBACK_DEVICE  = 16,
        COMPUTER_DEVICE  = 17,
        PARALLEL_PORT_DEVICE  = 18,
        TTL_INPUT_DEVICE  = 19,
        TTL_OUTPUT_DEVICE  = 20,
        TTL_IO_DEVICE  = 21,
        A2D_INPUT_DEVICE  = 22,
        D2A_OUTPUT_DEVICE  = 23,
        ANALOG_IO_DEVICE  = 24,
        GPIO_DEVICE  = 25,
        PHOTOSENSOR_DEVICE = 26,
        IR_MEASUREMENT_DEVICE = 27,
        ARTIFICIAL_EYE_DEVICE = 28,
        SPEAKER_DEVICE  = 29,
        AMPLIFIER_DEVICE  = 30,
        EEG_DEVICE  = 31,
        MRI_DEVICE  = 32,
        MEG_DEVICE  = 33,
        SERIAL_DEVICE = 34,
        NETWORK_DEVICE = 35,
        OTHER_DEVICE  = 2048)

    EVENT_CLASSES=dict()

    DEVICE_CATERGORIES={
        0:'UNKNOWN',
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

class EventConstants(_EventConstantsBase):
    def __init__(self):
        EventConstants.__init__(self)

########### Base Abstract Device that all other Devices inherit from ##########

class Device(ioObject):
    """
    The Device class is the base class for all ioHub Device types.
    Any ioHub Device class (i.e Keyboard Device, Mouse Device, etc)
    also include the methods and attributes of this class.
    """
    DEVICE_INSTANCE_CODE_INDEX=0
    DEVICE_CATEGORY_ID_INDEX=1
    DEVICE_TYPE_ID_INDEX=2
    DEVICE_CLASS_NAME_INDEX=3
    DEVICE_USER_LABEL_INDEX=4
    DEVICE_OS_CODE_INDEX=5
    DEVICE_BUFFER_LENGTH_INDEX=6
    DEVICE_MAX_ATTRIBUTE_INDEX=DEVICE_BUFFER_LENGTH_INDEX

    # Multiplier to use to convert this devices event time stamps to usec format.
    # This is set by the author of the device class or interface implementation.
    DEVICE_TIMEBASE_TO_USEC=1.0

    # The device category label. Should be one of the string keys in EventConstants.DEVICE_CATEGORIES,
    # the value of which is the category id. This is set by the author of the device class
    # or interface implementation.
    CATEGORY_LABEL='UNKNOWN'

    # The device type label. Should be one of the string keys in EventConstants.DEVICE_TYPES,
    # the value of which is the device type id. This is set by the author of the device class
    # or interface implementation.
    DEVICE_LABEL='UNKNOWN_DEVICE'

    _baseDataTypes=ioObject._baseDataTypes
    _newDataTypes=[('instance_code',N.str,48),  # The instance code assigned to the device. User defined.
                                                # The devices serial number is a good candidate for this. It
                                                # must be unique within and between experiment sites.

                   ('category_id',N.uint8),     # The id of the device category for the device type.
                                                # = EventConstants.DEVICE_CATERGORIES[CATEGORY_LABEL]

                   ('type_id',N.uint8),         # The id of the device type = EventConstants.DEVICE_TYPES[DEVICE_LABEL]

                   ('device_class',N.str,24),   # The name of the Device Class used to create an instance
                                                # of this device type. = self.__class__.__name__

                   ('name',N.str,24),           # The name given to this device instance. User Defined. Should be
                                                # unique within all devices of the same type_id for a given experiment.

                   ('os_device_code',N.str,64), # If the device can be associated with a unique OS level identifier
                                                # the string rep. of that could be entered here. This would allow for
                                                # consistent mappings between device names and physical devices if
                                                # > 1 device of a given type_id is in use.
                                                # CURRENTLY NOT USED

                   ('max_event_buffer_length',N.uint16) # The maximum size of the device level event buffer for this
                                                        # device instance. If the buffer becomes full, when a new event
                                                        # is added, the oldest event in the buffer is removed.
                ]


    __slots__=[e[0] for e in _newDataTypes]+['_nativeEventBuffer','_eventListeners','_ioHubEventBuffer']
    def __init__(self,*args,**kwargs):
        ioObject.__init__(self,*args,**kwargs)
        self._ioHubEventBuffer=deque(maxlen=self.max_event_buffer_length)
        self._nativeEventBuffer=deque(maxlen=self.max_event_buffer_length)
        self._eventListeners=list()

    def getEvents(self,**kwargs):
        """
        Returns any DeviceEvents that have occurred since the last call to the devices getEvents() or
        clearEvents() methods.

        Note that calling the ioHub Server level getEvents() or clearEvents() methods does *not* effect
        device level event buffers.

        Args:
            kwargs (dict): dictionary of parameter key, value object pairs.

        Return (tuple): a list of lists, with each inner list being an ordered list of event attribute
                        values, as would be taken by the events constructor, representing an event related
                        to this device type. If no events are available, an empty list is returned.

                        getEvents() clears the device event buffer after getting the event list, so
                        duplicate events are never received.
        """
        currentEvents=list(self._ioHubEventBuffer)
        self._ioHubEventBuffer.clear()

        if len(currentEvents)>0:
            sorted(currentEvents, key=itemgetter(DeviceEvent.EVENT_HUB_TIME_INDEX))
        return currentEvents
    
    def clearEvents(self):
        """
        Clears any DeviceEvents that have occurred since the last call to the devices getEvents()
        or clearEvents() methods.

        Note that calling the ioHub Server level getEvents() or clearEvents() methods does *not*
        effect device level event buffers.

        Args: None
        Return: None
        """
        self._ioHubEventBuffer.clear()
        
    def _handleEvent(self,e):
        self._ioHubEventBuffer.append(e)
        
    def _getNativeEventBuffer(self):
        return self._nativeEventBuffer
    
    def _addEventListener(self,l):
        if l not in self._eventListeners:
            self._eventListeners.append(l)
    
    def _removeEventListener(self,l):
       if l in self._eventListeners:
            self._eventListeners.remove(l)
            
    def _getEventListeners(self):
        return self._eventListeners

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
    EVENT_DEVICE_INSTANCE_CODE_INDEX=4
    EVENT_DEVICE_TIME_INDEX=5
    EVENT_LOGGED_TIME_INDEX=6
    EVENT_HUB_TIME_INDEX=7
    EVENT_CONFIDENCE_INTERVAL_INDEX=8
    EVENT_DELAY_INDEX=9
    BASE_EVENT_MAX_ATTRIBUTE_INDEX=EVENT_DELAY_INDEX

    # The string label for the given DeviceEvent type. Should be one of the string keys in
    # EventConstants.EVENT_TYPES, the value of which is the event type id. This is set by
    # the author of the event class implementation.
    EVENT_TYPE_STRING='UNDEFINED_EVENT'

    # The type id int for the given DeviceEvent type. Should be one of the int values in
    # EventConstants.EVENT_TYPES, = EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]. This is set by
    # the author of the event class implementation.
    EVENT_TYPE_ID=EventConstants.UNDEFINED_EVENT

    # The name of the hdf5 table used to store events of this type in the ioDataStore pytables file.
    # This is set by the author of the event class implementation.
    IOHUB_DATA_TABLE=None

    _baseDataTypes=ioObject._baseDataTypes
    _newDataTypes=[
                ('experiment_id',N.uint32), # The ioDataStore experiment ID assigned to the experiment code
                                            # specified in the experiment configuration file for the experiment.

                ('session_id',N.uint32),    # The ioDataStore session ID assigned to the currently running
                                            # experiment session. Each time the experiment script is run,
                                            # a new session id is generated for use within the hdf5 file.

                ('event_id',N.uint64),      # The id assigned to the current device event instance. Every device
                                            # event generated by monitored devices during an experiment session is
                                            # assigned a unique id, starting from 0 for each session, incrementing
                                            # by +1 for each new event.

                ('event_type',N.uint8),     # The type id for the event. This is used to create DeviceEvent objects
                                            # or dictionary representations of an event based on the data from an
                                            # event value list.

                ('device_instance_code',N.str,48), # The instance_code of the device that generated the event.

                ('device_time',N.uint64),   # If the device that generates the given device event type also time stamps
                                            # events, this field is the time of the event as given by the device,
                                            # converted to usec for consistancy with all other ioHub device times.
                                            # If the device that generates the given event type does not time stamp
                                            # events, then the device_time is set to the logged_time for the event.

                ('logged_time', N.uint64),  # The usec time that the event was 'received' by the ioHub Server Process.
                                            # For devices that poll for events, this is the usec time that the poll
                                            # method was called for the device and the event was retrieved. For
                                            # devices that use the event callback, this is the usec time the callback
                                            # executed and accept the event.

                ('hub_time',N.uint64),      # The hub_time is in the normalized time base that all events share,
                                            # regardless of device type. hub_time is calculated differently depending
                                            # on the device and perhaps event types.
                                            # The hub_time is what should be used when comparing times of events across
                                            # different devices.

                ('confidence_interval', N.float32), # This property attempts to give a sense of the amount to which
                                                    # the event time may be off relative to the true time the event
                                                    # occurred. confidence_interval is calculated differently depending
                                                    # on the device and perhaps event types. In general though, the
                                                    # smaller the confidence_interval, the more likely it is that the
                                                    # calculated hub_time of the event is correct. For devices where
                                                    # a realistic confidence_interval can not be calculated,
                                                    # for example if the event device delay is unknown, then a value
                                                    # of 0.0 should be used. Valid confidence_interval values are
                                                    # in usec and will range from 1.0 usec and higher.

                ('delay',N.float32)         # The delay of an event is the known (or estimated) delay from when the
                                            # real world event occurred to when the ioHub received the event for
                                            # processing. This is often called the real-time end-to-end delay
                                            # of an event. If the delay for an event can not be reasonably estimated
                                            # or is not known, a delay of 0.0 is set. Delays are in usec.nsec and valid
                                            # values will range from 1.0 and higher.
                ]
    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self,*args,**kwargs):
        ioObject.__init__(self,*args,**kwargs)
                   
    def __cmp__(self,other):
        return self.hub_time-other.hub_time

    @staticmethod
    def createEventFromParamList(eventParamList):
        """
        Create a DeviceEvent subclass using the eventValueList as the values for the event attributes.

        Args:
            eventParamList (tuple): an ordered list of event attribute values, ordered based on how the
                                    DeviceEvent constructor specifies them.
        Return (DeviceEvent): a DeviceEvent instance of the correct DeviceEvent Class type based on the
                              'event_type' element of the eventParamList, which is
                              eventParamList[DeviceEvent.EVENT_TYPE_ID_INDEX]
        """
        eclass=EventConstants.EVENT_CLASSES[eventParamList[DeviceEvent.EVENT_TYPE_ID_INDEX]]
        return eclass.createObjectFromParamList(*eventParamList)



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
from keyboard import KeyboardEvent,KeyboardKeyEvent,KeyboardPressEvent,KeyboardReleaseEvent

import mouse as mouse_module
from mouse import Mouse
from mouse import MouseEvent,MouseButtonEvent,MouseMoveEvent,MouseWheelEvent,MouseWheelUpEvent,MouseWheelDownEvent,MouseButtonDownEvent,MouseButtonUpEvent,MouseDoubleClickEvent

import parallelPort as parallelPort_module
from parallelPort import ParallelPort
from parallelPort import ParallelPortEvent

import joystick as joystick_module
from joystick import Joystick
from joystick import JoystickButtonEvent,JoystickButtonPressEvent, JoystickButtonReleaseEvent

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

    EventConstants.EVENT_CLASSES.update({EventConstants.EVENT_TYPES['KEYBOARD_KEY']:KeyboardKeyEvent,
                                         EventConstants.EVENT_TYPES['KEYBOARD_PRESS']:KeyboardPressEvent,
                                         EventConstants.EVENT_TYPES['KEYBOARD_RELEASE']:KeyboardReleaseEvent,
                                         EventConstants.EVENT_TYPES['MOUSE_MOVE']:MouseMoveEvent,
                                         EventConstants.EVENT_TYPES['MOUSE_WHEEL']:MouseWheelEvent,
                                         EventConstants.EVENT_TYPES['MOUSE_WHEEL_UP']:MouseWheelUpEvent,
                                         EventConstants.EVENT_TYPES['MOUSE_WHEEL_DOWN']:MouseWheelDownEvent,
                                         EventConstants.EVENT_TYPES['MOUSE_BUTTON']:MouseButtonEvent,
                                         EventConstants.EVENT_TYPES['MOUSE_PRESS']:MouseButtonDownEvent,
                                         EventConstants.EVENT_TYPES['MOUSE_RELEASE']:MouseButtonUpEvent,
                                         EventConstants.EVENT_TYPES['MOUSE_DOUBLE_CLICK']:MouseDoubleClickEvent,
                                         EventConstants.EVENT_TYPES['JOYSTICK_BUTTON_PRESS']:JoystickButtonPressEvent,
                                         EventConstants.EVENT_TYPES['JOYSTICK_BUTTON_RELEASE']:JoystickButtonReleaseEvent,
                                         EventConstants.EVENT_TYPES['TTL_INPUT']:ParallelPortEvent,
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
