# -*- coding: utf-8 -*-
"""
ioHub
.. file: ioHub/devices/keyboard/__init__.py

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

#
# Some possibly useful python modules / functions for unicode support:
#
# http://docs.python.org/2/library/unicodedata.html

global Keyboard
Keyboard=None

import numpy as N

try:
    import ujson as json
except Exception:
    try:
        import cjson as json
    except Exception:
        import json


from ioHub import print2err,printExceptionDetailsToStdErr
from ioHub.constants import KeyboardConstants, DeviceConstants, EventConstants
from .. import Device, Computer

getTime = Computer.getTime

##### Modifier Keys #####
mod_dtype=[('CONTROL_LEFT',N.bool),('CONTROL_RIGHT',N.bool),('SHIFT_LEFT',N.bool),
            ('SHIFT_RIGHT',N.bool),('ALT_LEFT',N.bool),('ALT_RIGHT',N.bool),
            ('COMMAND_LEFT',N.bool),('COMMAND_RIGHT',N.bool), ('CAPLOCKS',N.bool)]

_positional_modifier_names=[i[0] for i in mod_dtype]

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
    __slots__=['_keyStatusDict','_lastProcessedEventID','_active_modifiers']
    def __init__(self,*args,**kwargs):
        self._keyStatusDict=dict()
        self._lastProcessedEventID=0
        self._active_modifiers=dict(zip(_positional_modifier_names,(False,False,False,False,False,False,False,False,False)))
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
if Computer.system == 'win32':
    import pyHook
    import ctypes
    
    class Keyboard(ioHubKeyboardDevice):
        _OS_MODIFIERS=dict(Lcontrol='CONTROL_LEFT',Rcontrol='CONTROL_RIGHT',
                        Lshift='SHIFT_LEFT',Rshift='SHIFT_RIGHT',
                        Lalt='ALT_LEFT',Ralt='ALT_RIGHT',
                        Lwin='COMMAND_LEFT',Rwin='COMMAND_RIGHT')

        __slots__=['_modifier_name_list','_user32','_modifierValue','_keyboard_state','_unichar']
        
        def __init__(self,*args,**kwargs):                        
            ioHubKeyboardDevice.__init__(self,*args,**kwargs['dconfig'])
            self._modifier_name_list=[]
            self._user32=ctypes.windll.user32
            self._keyboard_state=(ctypes.c_byte*256)()
            self._unichar=(ctypes.c_wchar*16)()
            
        def _nativeEventCallback(self,event):
            if self.isReportingEvents():
                notifiedTime=getTime()
                #
                # Start Tracking Modifiers that are pressed
                #
                k=event.GetKey()
                
                mod_key=Keyboard._OS_MODIFIERS.get(k,None)
                if mod_key:
                    self._active_modifiers[mod_key]=not self._active_modifiers[mod_key]
                
                self._modifier_name_list=[]
                self._modifierValue=0
                for mod_name in _positional_modifier_names:
                    mstate=self._active_modifiers[mod_name]
                    if mstate:                    
                         self._modifierValue+=KeyboardConstants._modifierCodes.getID(mod_name)
                         self._modifier_name_list.append(mod_name)
                #
                # End Tracking Modifiers that are pressed
                #
                event.ModifierNames=self._modifier_name_list
                event.Modifiers=self._modifierValue
                
                self._addNativeEventToBuffer((notifiedTime,event))
                self._last_callback_time=notifiedTime
                
            #endtime=getTime()
            #print2err("callback dur: %.3f msec"%((endtime-notifiedTime)*1000.0))
            # pyHook require the callback to return True to inform the windows 
            # low level hook functionality to pass the event on.
            return True
    
        def _getIOHubEventObject(self,native_event_data):
            if  len(native_event_data) >2:
                # it is a KeyboardCharEvent
                return native_event_data
    
            #stime=getTime()
            notifiedTime, event=native_event_data
            etype = EventConstants.KEYBOARD_RELEASE
            if event.Message in [pyHook.HookConstants.WM_KEYDOWN,pyHook.HookConstants.WM_SYSKEYDOWN]:
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
    
            key,_=KeyboardConstants._getKeyNameAndModsForEvent(event)

            
            uchar=0
            if key is None or len(key)==0:            
                self._user32.GetKeyboardState(ctypes.byref(self._keyboard_state))
                result=self._user32.ToUnicode(event.KeyID, event.ScanCode,ctypes.byref(self._keyboard_state),ctypes.byref(self._unichar),16,0)
                if result > 0:
                    # result == the number of wchars filled in the _unichar buffer
                    uchar=self._unichar[0:result]
                    key=(u''+uchar).encode('utf-8')
                elif result == 0:
                    # The specified virtual key has no translation for the current
                    # state of the keyboard. Nothing was written to the buffer 
                    # specified by pwszBuff.
                    # WHAT TO DO??                
                    print2err( 'ToUnicode found no Translation. Result {0} for [{1}]'.format(result,key))
       
                else:
                    # The specified virtual key is a dead-key character (accent or diacritic). 
                    # This value is returned regardless of the keyboard layout, even if several
                    # characters have been typed and are stored in the keyboard state. If possible,
                    # even with Unicode keyboard layouts, the function has written a spacing version
                    # of the dead-key character to the buffer specified by pwszBuff. For example,
                    # the function writes the character SPACING ACUTE (0x00B4), 
                    # rather than the character NON_SPACING ACUTE (0x0301).  
                    # WHAT TO DO??                
                    print2err( 'ToUnicode detected DEAD KEY. Result {0} for [{1}]'.format(result,key))
            else:
                key=unicode(key).encode('utf-8')
                
            #endtime=getTime()
            #print2err("io event create dur: %.3f msec"%((endtime-stime)*1000.0))

            return [0,
                    0,
                    0, #device id (not currently used)
                    Computer._getNextEventID(),
                    etype,
                    device_time,
                    notifiedTime,
                    time,
                    confidence_interval,
                    delay,
                    0,
                    event.ScanCode,
                    event.KeyID,
                    uchar,
                    key,
                    event.Modifiers,
                    event.Window
                    ]

elif Computer.system == 'linux2':
    class Keyboard(ioHubKeyboardDevice):
        def __init__(self,*args,**kwargs):
            ioHubKeyboardDevice.__init__(self,*args,**kwargs['dconfig'])

        def _nativeEventCallback(self,event):
            try:
                if self.isReportingEvents():             
                    logged_time=getTime()
                    
                    event_array=event[0]
                    event_array[3]=Computer._getNextEventID()
                    
                    self._addNativeEventToBuffer(event_array)
                    
                    self._last_callback_time=logged_time
            except:
                import ioHub
                ioHub.printExceptionDetailsToStdErr()
            
            # Must return original event or no mouse events will get to OSX!
            return 1
                
        def _getIOHubEventObject(self,native_event_data):
            #ioHub.print2err('Event: ',native_event_data)
            return native_event_data


            

else: # assume OS X
    from copy import copy
    import Quartz
    import Quartz as Qz
    from AppKit import NSKeyUp, NSSystemDefined, NSEvent
    
    eventHasModifiers = lambda v: Qz.kCGEventFlagMaskNonCoalesced - v != 0     
    keyFromNumpad = lambda v: Qz.kCGEventFlagMaskNumericPad & v > 0   
    caplocksEnabled = lambda v : Qz.kCGEventFlagMaskAlphaShift & v > 0 
    shiftModifierActive = lambda v : Qz.kCGEventFlagMaskShift & v > 0
    altModifierActive = lambda v : Qz.kCGEventFlagMaskAlternate & v > 0
    controlModifierActive = lambda v : Qz.kCGEventFlagMaskControl & v > 0
    commandModifierActive = lambda v : Qz.kCGEventFlagMaskCommand & v > 0

    class Keyboard(ioHubKeyboardDevice):       
        _OS_MODIFIERS=([(0x00001,'CONTROL_LEFT'),(0x02000,'CONTROL_RIGHT'),
                        (0x00002,'SHIFT_LEFT'),(0x00004,'SHIFT_RIGHT'),
                        (0x00020,'ALT_LEFT'),(0x00040,'ALT_RIGHT'),
                        (0x000008, 'COMMAND_LEFT'),(0x000010,'COMMAND_RIGHT'),
                        (Qz.kCGEventFlagMaskAlphaShift, 'CAPLOCKS')])
#                    (Qz.kCGEventFlagMaskHelp ,             "MOD_HELP"),         # 0x400000   
#                    (Qz.kCGEventFlagMaskSecondaryFn ,      "MOD_FUNC2"),        # 0x800000   
       
        DEVICE_TIME_TO_SECONDS=0.000000001
        
        _EVENT_TEMPLATE_LIST=[0, # experiment id
                            0,  # session id
                            0, #device id (not currently used)
                            0,  # Computer._getNextEventID(),
                            0,  # ioHub Event type
                            0.0,# event device time,
                            0.0,# event logged_time,
                            0.0,# event iohub Time,
                            0.0,# confidence_interval, 
                            0.0,# delay,
                            0,  # filtered by ID (always 0 right now)             
                            0,  # ScanCode
                            0,  # Ascii char value (if applicable) 
                            0,  # KeyID
                            u'',# Unicode Value / Key Name Constant ( i.e. SPACE, ESCAPE, ENTER, etc )
                            None,# mods
                            0 ] # event.Window]
        
        __slots__=['_loop_source','_tap','_device_loop','_CGEventTapEnable','_loop_mode','_last_general_mod_states','_ring_buffer']

        def __init__(self,*args,**kwargs):
            ioHubKeyboardDevice.__init__(self,*args,**kwargs['dconfig'])
            
            # TODO: This dict should be reset whenever monitoring is turned off for the device OR
            # whenever events are cleared fpr the device.
            # Same to do for the _active_modifiers bool lookup array
            self._last_general_mod_states=dict(shift_on=False,alt_on=False,cmd_on=False,ctrl_on=False)
            
            self._loop_source=None
            self._tap=None
            self._device_loop=None
            self._loop_mode=None            

            self._tap = Qz.CGEventTapCreate(
                Qz.kCGSessionEventTap,
                Qz.kCGHeadInsertEventTap,
                Qz.kCGEventTapOptionDefault,
                Qz.CGEventMaskBit(Qz.kCGEventKeyDown) |
                Qz.CGEventMaskBit(Qz.kCGEventKeyUp)|
                Qz.CGEventMaskBit(Qz.kCGEventFlagsChanged),
                self._nativeEventCallback,
                None)            
                
            self._CGEventTapEnable=Qz.CGEventTapEnable
            self._loop_source = Qz.CFMachPortCreateRunLoopSource(None, self._tap, 0)
            
            self._device_loop = Qz.CFRunLoopGetCurrent()
            
            self._loop_mode=Qz.kCFRunLoopDefaultMode
            
            from ioHub.util import NumPyRingBuffer
            self._ring_buffer=NumPyRingBuffer(100)
            Qz.CFRunLoopAddSource(self._device_loop, self._loop_source, self._loop_mode)
        
        def getKeyNameForEvent(self,ns_event):
            key_name=None
            key_code=ns_event.keyCode()
            if key_code:
                key_name=KeyboardConstants._virtualKeyCodes.getName(key_code)
            
            if key_name is None or len(key_name) == 0:
                uchar=ns_event.charactersIgnoringModifiers()
                key_name=None
                if uchar:
                    key_name=KeyboardConstants._unicodeChars.getName(uchar)
                    
                if key_name is None or len(key_name) == 0:
                    uchar=ns_event.characters()
                    key_name= KeyboardConstants._unicodeChars.getName(uchar)
                    if not key_name:
                        key_name=uchar
            if key_name.startswith('VK_'):
                key_name=key_name[3:]
            return (u''+key_name).encode('utf-8')
        
        def _poll(self):
            self._last_poll_time=getTime()            
            while Qz.CFRunLoopRunInMode(self._loop_mode, 0.0, True) == Qz.kCFRunLoopRunHandledSource:
                pass
                            
        def _nativeEventCallback(self,*args):
            try:
                proxy, etype, event, refcon = args
                
                if self.isReportingEvents():
                    logged_time=getTime()

                      
                    if etype == Qz.kCGEventTapDisabledByTimeout:
                        print2err("** WARNING: Keyboard Tap Disabled due to timeout. Re-enabling....: ", etype)
                        Qz.CGEventTapEnable(self._tap, True)
                        return event
                    else:                
                        confidence_interval=logged_time-self._last_poll_time
                        delay=0.0 # No point trying to guess for the keyboard or mouse.
                                  # May add a 'default_delay' prefernce to the device config settings,
                                  # so if a person knows the average delay for something like the kb or mouse
                                  # they are using, then they could specify it in the config file and it could be used here.
                        iohub_time = logged_time-delay
                        device_time=Qz.CGEventGetTimestamp(event)*self.DEVICE_TIME_TO_SECONDS                        
                        key_code = Qz.CGEventGetIntegerValueField(event, Qz.kCGKeyboardEventKeycode)                    

                        window_number=0       
                        event_mod=None
                        mod_str_list=[]
                        ioe_type=None
                        ucode=0 # the int version of the unicode utf-8 ichar
                        is_auto_repeat= Qz.CGEventGetIntegerValueField(event, Qz.kCGKeyboardEventAutorepeat)
                        flags=Qz.CGEventGetFlags(event)
                        np_key=keyFromNumpad(flags)     
                                                
                        # This is a modifier state change event, so we need to manually determine
                        # which mod key was either pressedor released that resulted in the state change....
                        if etype == Qz.kCGEventFlagsChanged:
                            mods_total,mod_str_list=Keyboard._checkForLeftRightModifiers(flags)
                            mod_presses=[]
                            mod_releases=[]
                            for mod_name in _positional_modifier_names:
                                mstate=self._active_modifiers[mod_name]
                                if mod_name in mod_str_list and not mstate:
                                    self._active_modifiers[mod_name]=True
                                    mod_presses.append(mod_name)
                                elif mod_name not in mod_str_list and mstate:   
                                    self._active_modifiers[mod_name]=False
                                    mod_releases.append(mod_name)                                

                            if (len(mod_presses) + len(mod_releases)) > 1:
                                print2err("\nWARNING: Multiple modifiers reported a state change in one event. BUG??:", mod_presses, mod_releases)
                                print2err("Using ONLY first change detected for event.\n")
                            
                            # OK, so if there is an element in mod presses or releases, then
                            # we know the mod key that changed the state transition is a left_*,
                            # or right_* or the cap locks key and we have the key we need.
                            if len(mod_presses) > 0:
                                ioe_type=EventConstants.KEYBOARD_PRESS
                                event_mod=mod_presses[0]
                            elif len(mod_releases) > 0:
                                event_mod=mod_releases[0]
                                ioe_type=EventConstants.KEYBOARD_RELEASE
                            
                            #TODO: What keyCode should we use for each modifier events?
                            # key_code = ???
                            
                            if event_mod != None:
                                # TODO: These modifier 'unistrs' are just the unqiue value assigned by ioHub for each
                                # modifier. They are not ' official unicode reps for the mod key in question.
                                # They should be. ;) SO determine what the valid unicode hex value is for each mod key and use that for
                                # the ioHub constant value for each.
                                key_name=(u''+event_mod).encode('utf-8')
                            else:
                                # So no modifiers matching the left_, right_ mod codes were found,
                                # so lets check the generic non position based mode codes that are 'officially'
                                # defined by OS X
                                shift_on=shiftModifierActive(flags)
                                alt_on=altModifierActive(flags)
                                ctrl_on=controlModifierActive(flags)
                                cmd_on=commandModifierActive(flags)    

                                if shift_on != self._last_general_mod_states['shift_on']:
                                    if shift_on is True:
                                        ioe_type=EventConstants.KEYBOARD_PRESS
                                    else:
                                        ioe_type=EventConstants.KEYBOARD_RELEASE
                                    self._last_general_mod_states['shift_on']=shift_on
                                    event_mod=u'MOD_SHIFT'
                                    key_name=event_mod.encode('utf-8')
                                elif alt_on != self._last_general_mod_states['alt_on']:
                                    if alt_on is True:
                                        ioe_type=EventConstants.KEYBOARD_PRESS
                                    else:
                                        ioe_type=EventConstants.KEYBOARD_RELEASE
                                    self._last_general_mod_states['alt_on']=alt_on
                                    event_mod=u'MOD_ALT'
                                    key_name=event_mod.encode('utf-8')
                                elif ctrl_on != self._last_general_mod_states['ctrl_on']:
                                    if ctrl_on is True:
                                        ioe_type=EventConstants.KEYBOARD_PRESS
                                    else:
                                        ioe_type=EventConstants.KEYBOARD_RELEASE
                                    self._last_general_mod_states['ctrl_on']=ctrl_on
                                    event_mod=u'MOD_CTRL'
                                    key_name=event_mod.encode('utf-8')
                                elif cmd_on != self._last_general_mod_states['cmd_on']:
                                    if cmd_on is True:
                                        ioe_type=EventConstants.KEYBOARD_PRESS
                                    else:
                                        ioe_type=EventConstants.KEYBOARD_RELEASE
                                    event_mod=u'MOD_CTRL'
                                    key_name=event_mod.encode('utf-8')
                                    self._last_general_mod_states['cmd_on']=cmd_on
                        else:
                            # This is an actual button press / release event, so handle it....
                            try:
                                keyEvent = NSEvent.eventWithCGEvent_(event)
                                key_name=self.getKeyNameForEvent(keyEvent)
                                key_code=keyEvent.keyCode()
                                window_number=keyEvent.windowNumber()

                                if etype == Qz.kCGEventKeyUp:
                                    ioe_type=EventConstants.KEYBOARD_RELEASE
                                elif etype == Qz.kCGEventKeyDown:
                                    ioe_type=EventConstants.KEYBOARD_PRESS
    
                            except Exception,e:
                                print2err("Create NSEvent failed: ",e)
                        
                        if ioe_type: 
                            # The above logic resulted in finding a key press or release event
                            # from the expected events OR from modifier state changes. So,
                            # send the iohub event version to ioHub.
                            #
                            # FILL IN AND CREATE EVENT
                            # index 0 and 1 are session and exp. ID's
                            # index 3 is device id (not yet supported)
                            if key_name is None or len(key_name)==0:
                                # TO DO: dead char we need to deal with??
                                key_name=u'DEAD_KEY?'.encode('utf-8')
                                print2err("DEAD KEY KIT?")
                            ioe=self._EVENT_TEMPLATE_LIST
                            ioe[3]=Computer._getNextEventID()
                            ioe[4]=ioe_type #event type code
                            ioe[5]=device_time
                            ioe[6]=logged_time
                            ioe[7]=iohub_time
                            ioe[8]=confidence_interval
                            ioe[9]=delay
                            # index 10 is filter id, not used at this time
                            ioe[11]=0 # Quartz does not give the scancode
                            ioe[12]=key_code #key_code
                            ioe[13]=ucode
                            ioe[14]=key_name 
                            ioe[15]=json.dumps(mod_str_list) 
                            ioe[16]=window_number
                            
                            self._addNativeEventToBuffer(copy(ioe))
                        else:
                            # So we did not find a key event out of the logic above,
                            # likely due to a state change event that had no modifier
                            # changes in it??? Spit out a warning for now so we can see
                            # if this ever actually happens.
                            print2err("\nWARNING: KEYBOARD RECEIVED A [ {0} ] KB EVENT, BUT COULD NOT GENERATE AN IOHUB EVENT FROM IT !!".format(etype))
                            
                        self._last_callback_time=logged_time                
                
                    #cdur=getTime()-logged_time
                    #print2err('callback dur: ',cdur)        
                    # Must return original event or no keyboard events will get to OSX!
                return event
            except:
                printExceptionDetailsToStdErr()
                Qz.CGEventTapEnable(self._tap, False)
            
            return event
        
        @classmethod
        def _checkForLeftRightModifiers(cls,mod_state):
            mod_value=0
            mod_strs=[]
            for k,v in cls._OS_MODIFIERS:
                if mod_state & k > 0:
                    mod_value+=KeyboardConstants._modifierCodes.getID(v)
                    mod_strs.append(v)
            return mod_value,mod_strs            
            
        def _getIOHubEventObject(self,native_event_data):
            return native_event_data
        
        def _close(self):            
            try:
                Qz.CGEventTapEnable(self._tap, False)
            except:
                pass
            try:
                if Qz.CFRunLoopContainsSource(self._device_loop,self._loop_source,self._loop_mode) is True:    
                    Qz.CFRunLoopRemoveSource(self._device_loop,self._loop_source,self._loop_mode)
            finally:
                self._loop_source=None
                self._tap=None
                self._device_loop=None
                self._loop_mode=None            
            ioHubKeyboardDevice._close(self)
    
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
    _newDataTypes = [ ('scan_code',N.uint32),  # the scan code for the key that was pressed.
                                            # Represents the physical key id on the keyboard layout

                    ('key_id',N.uint32),  # the ASCII byte value for the key (0 - 255)

                    ('ucode',N.uint32),      # the translated key ID, should be keyboard layout independent,
                                           # based on the keyboard local settings of the OS.

                    ('key',N.str,12),       # a string representation of what key was pressed.

                    ('modifiers',N.uint32),  # indicates what modifier keys were active when the key was pressed.

                    ('window_id',N.uint64)  # the id of the window that had focus when the key was pressed.
                    ]
    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self,*args,**kwargs):
        #: The scan code for the keyboard event.
        #: This represents the physical key id on the keyboard layout.
        #: int value
        self.scan_code=0
        
        #: The translated key ID, based on the keyboard local settings of the OS.
        #: int value.
        self.key_id=0
        
        #: The unicode utf-8 encoded int value for teh char.
        #: int value between 0 and 2**16.
        self.ucode=''

        #: A string representation of what key was pressed. For standard character
        #: ascii keys (a-z,A-Z,0-9, some punctuation values), and 
        #: unicode utf-8 encoded characters that have been successfully detected,
        #: *key* will be the
        #: the actual key value pressed. For other keys, like the *up arrow key*
        #: or key modifiers like the left or right *shift key*, a string representation
        #: of the key press is given, for example 'UP', 'SHIFT_LEFT', and 'SHIFT_RIGHT' for
        #: the examples given here. 
        self.key=''
        
        #: Logical & of all modifier keys pressed just before the event was created.
        self.modifiers=0

        #: The id or handle of the window that had focus when the key was pressed.
        #: long value.
        self.window_id=0

        DeviceEvent.__init__(self,*args,**kwargs)
        
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
        self.duration=0
        
        KeyboardReleaseEvent.__init__(self,*args,**kwargs)
