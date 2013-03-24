"""
ioHub
.. file: ioHub/devices/keyboard/__init__.py

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

global Keyboard
Keyboard=None

import numpy as N
import ujson

from ioHub.constants import KeyboardConstants, DeviceConstants, EventConstants
from .. import Device, Computer

##### Modifier Keys #####

MODIFIER_KEYS=KeyboardConstants._modifierCodes._names

dt=N.dtype([('CONTROL_LEFT',N.bool),('CONTROL_RIGHT',N.bool),('SHIFT_LEFT',N.bool),('SHIFT_RIGHT',N.bool),('MENU_LEFT',N.bool),('MENU_RIGHT',N.bool),('WIN_LEFT',N.bool)])
MODIFIER_ACTIVE=N.array((False,False,False,False,False,False,False),dtype=dt)

class ioHubKeyboardDevice(Device):
    """
    The Keyboard device is used to receive events from a standard USB or PS2 keyboard
    connected to the experiment computer. Only one keyboard device is supported in an 
    experiment at this time, if multiple keyboards are connected to the computer, 
    any keyboard events will be combined from all keyboard devices, appearing 
    to originate from a single keyboard device in the experiment.
    """
    
    EVENT_CLASS_NAMES=['KeyboardInputEvent','KeyboardKeyEvent','KeyboardPressEvent', 'KeyboardReleaseEvent','KeyboardCharEvent']

    DEVICE_TYPE_ID=DeviceConstants.KEYBOARD
    DEVICE_TYPE_STRING='KEYBOARD'
    __slots__=['_keyStatusDict','_lastProcessedEventID']
    def __init__(self,*args,**kwargs):
        self._keyStatusDict=dict()
        self._lastProcessedEventID=0
        Device.__init__(self,*args,**kwargs)



    def _getCharEvents(self):
        '''
        _getCharEvents is called automatically as part of the keyboard event handling process within ioHub.
        Users do not need to call it, thus why it is a _ 'private' method.

        _getCharEvents uses KeyPress and KeyRelease Events to generate KeyboardChar Events.
        A KeyboardChar event has the same base event structure as a KeyReleaseEvent, but adds a
        field to hold an associated key press event and a second field to hold the duration
        that the keyboard char was pressed.

        When a KeyPressEvent is detected, the event is stored in a dictionary using the event.key as the dict key.
        Repeated 'press' events for the same key are ignored (i.e. keyboard repeats when you hold a key down).

        When a KeyReleaseEvent is detected, the event.key is checked for in the char dict. If it is present,
        a KeyboardCharEvent is created using the KeyboardReleaseEvent as the basis for the Char event, and the
        KeyboardStartEvent that was stored in the dict for the startEvent, and duration calculated fields.
        '''
        press_events=[e for e in self.getEvents(event_type_id=EventConstants.KEYBOARD_PRESS,clearEvents=False) if e[DeviceEvent.EVENT_ID_INDEX] > self._lastProcessedEventID]
        release_events=[e for e in self.getEvents(event_type_id=EventConstants.KEYBOARD_RELEASE,clearEvents=False) if e[DeviceEvent.EVENT_ID_INDEX] > self._lastProcessedEventID]

        keypress_events=[]
        keyrelease_events=[]
        if len(press_events)>0:
            i=-1
            while press_events[i][DeviceEvent.EVENT_ID_INDEX] > self._lastProcessedEventID:
                self._lastProcessedEventID=press_events[i][DeviceEvent.EVENT_ID_INDEX]
                keypress_events.insert(0,press_events[i])
                if i+len(press_events)==0:
                    break
                i-=1

        if len(release_events)>0:
            i=-1
            while release_events[i][DeviceEvent.EVENT_ID_INDEX] > self._lastProcessedEventID:
                self._lastProcessedEventID=release_events[i][DeviceEvent.EVENT_ID_INDEX]
                keyrelease_events.insert(0,release_events[i])
                if i+len(release_events)==0:
                    break
                i-=1

        press_events=None
        release_events=None

        charEvents=[]

        for e in keypress_events:
            if e[-3] not in self._keyStatusDict.keys():

                self._keyStatusDict[e[-3]]=e

        for e in keyrelease_events:
            if e[-3] in self._keyStatusDict.keys():
                key_press= self._keyStatusDict.pop(e[-3])
                key_release=e
                charEvent=list(key_release)
                charEvent[DeviceEvent.EVENT_TYPE_ID_INDEX]=KeyboardCharEvent.EVENT_TYPE_ID
                charEvent[DeviceEvent.EVENT_ID_INDEX]=Computer._getNextEventID()
                charEvent.append(tuple(key_press))
                charEvent.append(key_release[DeviceEvent.EVENT_HUB_TIME_INDEX]-key_press[DeviceEvent.EVENT_HUB_TIME_INDEX])
                charEvents.append(charEvent)
        return charEvents

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
        cEvents=self._getCharEvents()
        [self._addNativeEventToBuffer(e) for e in cEvents]
        Device.clearEvents(self)

    def _handleEvent(self,e):
        Device._handleEvent(self,e)
        cEvents=self._getCharEvents()
        [self._addNativeEventToBuffer(e) for e in cEvents]

###### recast based on OS ##########

if Computer.system == 'Windows':
    from  _win32 import  KeyboardWindows32,ModifierKeyStrings,currentSec
    
    class Keyboard(ioHubKeyboardDevice,KeyboardWindows32):
        def __init__(self,*args,**kwargs):                        
            ioHubKeyboardDevice.__init__(self,*args,**kwargs['dconfig'])
            KeyboardWindows32.__init__(self,*args,**kwargs['dconfig'])

        def _nativeEventCallback(self,event):
            if self.isReportingEvents():
                notifiedTime=currentSec()
                #
                # Start Tracking Modifiers that are pressed
                #
                k=event.GetKey()
                if k in ModifierKeyStrings:
                    v=ModifierKeyStrings[k]
                    if (KeyboardWindows32.WM_KEYUP==event.Message and MODIFIER_ACTIVE[v]) or (event.Message in
                        KeyboardWindows32.WIN32_KEYBOARD_PRESS_EVENT_TYPES and not MODIFIER_ACTIVE[v]):
                        MODIFIER_ACTIVE[v] = not MODIFIER_ACTIVE[v]
                        i=MODIFIER_KEYS[v]
                        if MODIFIER_ACTIVE[v]:
                            self._modifierValue+=i
                        else:
                            self._modifierValue-=i
                #
                # End Tracking Modifiers that are pressed
                #
                event.Modifiers=self._modifierValue
                self._addNativeEventToBuffer((notifiedTime,event))
                self._last_callback_time=notifiedTime
                
            # pyHook require the callback to return True to inform the windows 
            # low level hook functionality to pass the event on.
            return True
    
        def _getIOHubEventObject(self,native_event_data):
            if  len(native_event_data) >2:
                # it is a KeyboardCharEvent
                return native_event_data
    
            notifiedTime, event=native_event_data
            etype = EventConstants.KEYBOARD_RELEASE
            if event.Message in KeyboardWindows32.WIN32_KEYBOARD_PRESS_EVENT_TYPES:
                etype = EventConstants.KEYBOARD_PRESS
                            
            # From MSDN: http://msdn.microsoft.com/en-us/library/windows/desktop/ms644939(v=vs.85).aspx
            # The time is a long integer that specifies the elapsed time, in milliseconds, from the time the system was started to the time the message was 
            # created (that is, placed in the thread's message queue).REMARKS: The return value from the GetMessageTime function does not necessarily increase
            # between subsequent messages, because the value wraps to zero if the timer count exceeds the maximum value for a long integer. To calculate time
            # delays between messages, verify that the time of the second message is greater than the time of the first message; then, subtract the time of the
            # first message from the time of the second message.
            device_time = event.Time/1000.0 # convert to sec
            time = notifiedTime #TODO correct kb times to factor in delay if possible.
     
            confidence_interval=0.0 # since this is a keyboard device using a callback method, confidence_interval is not applicable
            delay=0.0 # since this is a keyboard, we 'know' there is a delay, but until we support setting a delay in the device properties based on external testing for a given keyboard, we will leave at 0.
    
            key,mods=KeyboardConstants._getKeyNameAndModsForEvent(event)
            if mods is not None:
               mods=ujson.dumps(mods)
            return [0,0,Computer._getNextEventID(),etype,device_time,notifiedTime,time,confidence_interval,delay,0,
                    event.ScanCode,event.Ascii,event.KeyID,key,mods,event.Window]

elif Computer.system == 'Linux':
    from _linux import KeyboardLinux, currentSec
    class Keyboard(ioHubKeyboardDevice,KeyboardLinux):
        def __init__(self,*args,**kwargs):
            ioHubKeyboardDevice.__init__(self,*args,**kwargs['dconfig'])
            KeyboardLinux.__init__(self,*args,**kwargs['dconfig'])

        def _nativeEventCallback(self,event):
            if self.isReportingEvents():
                notifiedTime=currentSec()
    
                # TO DO: Add modifier support
                #
                # Start Tracking Modifiers that are pressed
                #
                #k=event.GetKey()
                #if k in ModifierKeyStrings:
                #    v=ModifierKeyStrings[k]
                #    if (KeyboardWindows32.WM_KEYUP==event.Message and MODIFIER_ACTIVE[v]) or (event.Message in
                #        KeyboardWindows32.WIN32_KEYBOARD_PRESS_EVENT_TYPES and not MODIFIER_ACTIVE[v]):
                #        MODIFIER_ACTIVE[v] = not MODIFIER_ACTIVE[v]
                #        i=MODIFIER_KEYS[v]
                #        if MODIFIER_ACTIVE[v]:
                #            self._modifierValue+=i
                #        else:
                #            self._modifierValue-=i
                #
                # End Tracking Modifiers that are pressed
                #
                #event.Modifiers=self._modifierValue
                self._addNativeEventToBuffer((notifiedTime,event))
                
                self._last_callback_time=notifiedTime
            
        def _getIOHubEventObject(self,native_event_data):
            if  len(native_event_data) >2:
                # it is a KeyboardCharEvent
                return native_event_data
                
            notifiedTime,event=native_event_data
                            
            device_time = event.Time/1000.0 # convert to sec
            ioHub_time = notifiedTime #TODO correct kb times to factor in delay if possible.
     
            confidence_interval=0.0 # since this is a keyboard device using a callback method, confidence_interval is not applicable
            delay=0.0 # since this is a keyboard, we 'know' there is a delay, but until we support setting a delay in the device properties based on external testing for a given keyboard, we will leave at 0.
    
    
            # TO DO: Add Modifier support
            
            mods=ujson.dumps([])
            #key,mods=KeyboardConstants._getKeyNameAndModsForEvent(event)
    #        if mods is not None:
               #mods=ujson.dumps(mods)
            return [0,
                    0,
                    Computer._getNextEventID(),
                    event.ioHubEventID,
                    device_time,
                    notifiedTime,
                    ioHub_time,
                    confidence_interval,
                    delay,
                    0, #filtered source (always 0 for now)
                    event.ScanCode,
                    event.Ascii,
                    event.KeyID,
                    event.Key,
                    mods,
                    event.Window
                    ]

else: # assume OS X
    print 'Keyboard not implemented on OS X yet.'
    
############# OS independent Keyboard Event classes ####################
from .. import DeviceEvent

class KeyboardInputEvent(DeviceEvent):
    """
    The KeyboardInputEvent class is an abstract class that is the parent of all
    Keyboard related event types.
    """
    
    PARENT_DEVICE=Keyboard

    # TODO: Determine real maximum key name string and modifiers string
    # lengths and set appropriately.
    _newDataTypes = [ ('scan_code',N.int),  # the scan code for the key that was pressed.
                                            # Represents the physical key id on the keyboard layout

                    ('ascii_code',N.uint16),  # the ASCII byte value for the key (0 - 255)

                    ('key_id',N.int),      # the translated key ID, based on the keyboard local settings of the OS.

                    ('key',N.str,12),       # a string representation of what key was pressed.

                    ('modifiers',N.str,80),  # indicates what modifier keys were active when the key was pressed.

                    ('window_id',N.uint64)  # the id of the window that had focus when the key was pressed.
                    ]
    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self,*args,**kwargs):
        #: The scan code for the keyboard event.
        #: This represents the physical key id on the keyboard layout.
        #: int value
        self.scan_code=None
        
        #: The ASCII byte value for the key.
        #: int value between 0 and 255.
        self.ascii_code=None

        #: The translated key ID, based on the keyboard local settings of the OS.
        #: int value.
        self.key_id=None
        
        #: A string representation of what key was pressed. For standard character
        #: keys like a-z,A-Z,0-9, and some punctuation values, *key* will be the
        #: the actual key value pressed. For other keys, like the *up arrow key*
        #: or key modifiers like the left or right *shift key*, a string representation
        #: of the key press is given, for example 'UP', 'LSHIFT', and 'RSHIFT' for
        #: the examples given here. 
        self.key=None
        
        #: Indicates what modifier keys were active when the key was pressed.
        #: list value, each element being a modifier name. An empty list indicates no modifiers were pressed.
        self.modifiers=None

        #: The id or handle of the window that had focus when the key was pressed.
        #: long value.
        self.window_id=None

        DeviceEvent.__init__(self,*args,**kwargs)
        
    @classmethod
    def createEventAsDict(cls,values):
        ed=super(KeyboardInputEvent,cls).createEventAsDict(values)
        if ed['modifiers'] is None:
            return ed
        ed['modifiers']=ujson.loads(ed['modifiers'])
        return ed

    #noinspection PyUnresolvedReferences
    @classmethod
    def createEventAsNamedTuple(cls,valueList):
        if valueList[-2] is None:
            return cls.namedTupleClass(*valueList)
        valueList[-2]=ujson.loads(valueList[-2])
        return cls.namedTupleClass(*valueList)


class KeyboardKeyEvent(KeyboardInputEvent):
    EVENT_TYPE_ID=EventConstants.KEYBOARD_KEY
    EVENT_TYPE_STRING='KEYBOARD_KEY'
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING
    __slots__=[]
    def __init__(self,*args,**kwargs):
        """

        :rtype : object
        :param kwargs:
        """
        KeyboardInputEvent.__init__(self,*args,**kwargs)

class KeyboardPressEvent(KeyboardKeyEvent):
    """
    A KeyboardPressEvent is generated when a key on a monitored keyboard is pressed down.
    The event is created prior to the keyboard key being released. If a key is held down for
    an extended period of time, multiple KeyboardPressEvent events may be generated depending
    on your OS and the OS's settings for key repeat event creation. 
    
    Event Type ID: EventConstants.KEYBOARD_PRESS
    
    Event Type String: 'KEYBOARD_PRESS'
    """
    EVENT_TYPE_ID=EventConstants.KEYBOARD_PRESS
    EVENT_TYPE_STRING='KEYBOARD_PRESS'
    IOHUB_DATA_TABLE=KeyboardKeyEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self,*args,**kwargs):
        KeyboardKeyEvent.__init__(self,*args,**kwargs)


class KeyboardReleaseEvent(KeyboardKeyEvent):
    """
    A KeyboardReleaseEvent is generated when a key on a monitored keyboard is released.
    
    Event Type ID: EventConstants.KEYBOARD_RELEASE
    
    Event Type String: 'KEYBOARD_RELEASE'
    """
    EVENT_TYPE_ID=EventConstants.KEYBOARD_RELEASE
    EVENT_TYPE_STRING='KEYBOARD_RELEASE'
    IOHUB_DATA_TABLE=KeyboardKeyEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self,*args,**kwargs):
        KeyboardKeyEvent.__init__(self,*args,**kwargs)

class KeyboardCharEvent(KeyboardReleaseEvent):
    """
    A KeyboardCharEvent is generated when a key on the keyboard is pressed and then
    released. The KeyboardKeyEvent includes information about the key that was
    released, as well as a refernce to the KeyboardPressEvent that is associated
    with the KeyboardReleaseEvent. Any auto-repeat functionality that may be 
    created by the OS keyboard driver is ignored.
    
    Event Type ID: EventConstants.KEYBOARD_CHAR
    
    Event Type String: 'KEYBOARD_CHAR'
    """
    _newDataTypes = [ ('pressEvent',KeyboardPressEvent.NUMPY_DTYPE),  # contains the keyboard press event that is
                                                                      # associated with the release event

                      ('duration',N.float32)  # duration of the Keyboard char event
    ]
    EVENT_TYPE_ID=EventConstants.KEYBOARD_CHAR
    EVENT_TYPE_STRING='KEYBOARD_CHAR'
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING
    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self,*args,**kwargs):
        """
        """
        
        #: The pressEvent attribute of the KeyboardCharEvent contains a reference
        #: to the associated keyboard key press event for the release event
        #: that the KeyboardCharEvent is based on. The press event is the *first*
        #: press of the key registered with the ioHub Server before the key is
        #: released, so any key auto repeat functionality of your OS settings are ignored.
        #: KeyboardPressEvent class type.        
        self.pressEvent=None
        
        #: The ioHub time deifference between the press and release events which
        #: constitute the KeyboardCharEvent.
        #: float type. seconds.msec-usec format
        self.duration=None
        
        KeyboardReleaseEvent.__init__(self,*args,**kwargs)

    @classmethod
    def createEventAsDict(cls,values):
        ed=super(KeyboardInputEvent,cls).createEventAsDict(values)
        if ed['pressEvent'] is None:
            return ed
        ed['pressEvent']=KeyboardPressEvent.createEventAsDict(ed['pressEvent'])
        return ed

    @classmethod
    def createEventAsNamedTuple(cls,valueList):
        if valueList[-2] is None:
            return cls.namedTupleClass(*valueList)
        valueList[-2]=KeyboardPressEvent.createEventAsNamedTuple(valueList[-2])
        return cls.namedTupleClass(*valueList)
