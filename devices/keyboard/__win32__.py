"""
ioHub Python Module

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License
(GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors,
   please see credits section of documentation.
"""
from .. import Device, Computer
import ioHub
from ioHub.devices import EventConstants

currentUsec=Computer.currentUsec
import numpy as N

from . import MODIFIER_ACTIVE,MODIFIER_KEYS

ModifierKeyStrings={'Lcontrol':'L_CONTROL','Rcontrol':'R_CONTROL','Lshift':'L_SHIFT','Rshift':'R_SHIFT','Lalt':'L_ALT','Ralt':'R_ALT','Lmenu':'L_MENU','Rmenu':'R_MENU','Lwin':'L_WIN'}

class KeyboardWindows32(object):
    WIN32_KEYBOARD_PRESS=EventConstants.WM_KEYDOWN
    WIN32_KEYBOARD_SYSKEY_PRESS=EventConstants.WM_SYSKEYDOWN    
    WIN32_KEYBOARD_RELEASE=EventConstants.WM_KEYUP
    WIN32_KEYBOARD_PRESS_EVENT_TYPES=(WIN32_KEYBOARD_PRESS,WIN32_KEYBOARD_SYSKEY_PRESS)
    def __init__(self,*args,**kwargs):      
        self.I_modifierValue=0;
        
    def _nativeEventCallback(self,event):
        notifiedTime=int(currentUsec())
        #
        # Start Tracking Modifiers that are pressed
        #
        k=event.GetKey()
        if k in ModifierKeyStrings:
            v=ModifierKeyStrings[k]                  
            if (KeyboardWindows32.WIN32_KEYBOARD_RELEASE==event.Message and MODIFIER_ACTIVE[v]) or (event.Message in KeyboardWindows32.WIN32_KEYBOARD_PRESS_EVENT_TYPES and not MODIFIER_ACTIVE[v]):
                MODIFIER_ACTIVE[v] = not MODIFIER_ACTIVE[v]
                i=MODIFIER_KEYS[v]
                if MODIFIER_ACTIVE[v]:
                    self.I_modifierValue+=i
                else:
                    self.I_modifierValue-=i
        #
        # End Tracking Modifiers that are pressed
        #
        event.Modifiers=self.I_modifierValue
        self.I_nativeEventBuffer.append((notifiedTime,event))
        return True

    def _poll(self):
        pass
            
    @staticmethod
    def _getIOHubEventObject(event,device_instance_code):
        notifiedTime, event=event
        etype = ioHub.EVENT_TYPES['KEYBOARD_RELEASE']
        pressed=0
        if event.Message in KeyboardWindows32.WIN32_KEYBOARD_PRESS_EVENT_TYPES:
            etype = ioHub.EVENT_TYPES['KEYBOARD_PRESS']
            pressed=1
        
        chrv=chr(event.Ascii)
                        
        # From MSDN: http://msdn.microsoft.com/en-us/library/windows/desktop/ms644939(v=vs.85).aspx
        # The time is a long integer that specifies the elapsed time, in milliseconds, from the time the system was started to the time the message was 
        # created (that is, placed in the thread's message queue).REMARKS: The return value from the GetMessageTime function does not necessarily increase
        # between subsequent messages, because the value wraps to zero if the timer count exceeds the maximum value for a long integer. To calculate time
        # delays between messages, verify that the time of the second message is greater than the time of the first message; then, subtract the time of the
        # first message from the time of the second message.
        device_time = int(event.Time)*1000 # convert to usec
        
        hub_time = notifiedTime #TODO correct mouse times to factor in offset.
 
        confidence_interval=0.0
        delay=0.0
 
        #return (experiment_id=0,session_id=0,event_id=Computer.getNextEventID(),event_type=etype,device_type=ioHub.DEVICE_TYPE_LABEL['KEYBOARD_DEVICE'],
        #                        device_instance_code=device_instance_code,device_time=int(event.Time),logged_time=notifiedTime,hub_time=0,
        #                        confidence_interval=0.0,delay=0.0,is_pressed=pressed,flags=event.flags,
        #                        alt=event.IsAlt(),extended=event.IsExtended(),transition=event.IsTransition(),
        #                        scan_code=event.ScanCode,ascii_code=event.Ascii,key_id=event.KeyID,
        #                        key=unicode(event.GetKey()),char=unicode(chrv),modifiers=event.Modifiers,window_id=event.Window)  
        return [0,0,Computer.getNextEventID(),etype,
                device_instance_code,device_time,notifiedTime,hub_time,confidence_interval,delay,pressed,event.flags,
                event.IsAlt(),event.IsExtended(),event.IsTransition(),event.ScanCode,event.Ascii,event.KeyID,
                unicode(event.GetKey()),unicode(chrv),event.Modifiers,event.Window]  
