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
import pythoncom
currentMsec=Computer.currentMsec
import numpy as N

from . import MODIFIER_ACTIVE,MODIFIER_KEYS

ModifierKeyStrings={'Lcontrol':'L_CONTROL','Rcontrol':'R_CONTROL','Lshift':'L_SHIFT','Rshift':'R_SHIFT','Lalt':'L_ALT','Ralt':'R_ALT','Lmenu':'L_MENU','Rmenu':'R_MENU','Lwin':'L_WIN'}

class KeyboardWindows32(object):
    WIN32_KEYBOARD_PRESS=256
    WIN32_KEYBOARD_SYSKEY_PRESS=260    
    WIN32_KEYBOARD_RELEASE=257
    WIN32_KEYBOARD_PRESS_EVENT_TYPES=(WIN32_KEYBOARD_PRESS,WIN32_KEYBOARD_SYSKEY_PRESS)
    def __init__(self,*args,**kwargs):      
        self.I_modifierValue=0;
        
    def _nativeEventCallback(self,event):
        notifiedTime=int(currentMsec())
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
        from . import KeyboardPressEvent,KeyboardReleaseEvent
        notifiedTime, event=event
        etype = ioHub.EVENT_TYPES['KEYBOARD_RELEASE']
        pressed=0
        eclass=KeyboardReleaseEvent
        if event.Message in KeyboardWindows32.WIN32_KEYBOARD_PRESS_EVENT_TYPES:
            etype = ioHub.EVENT_TYPES['KEYBOARD_PRESS']
            pressed=1
            eclass=KeyboardPressEvent
        
        chrv=chr(event.Ascii)

        return eclass(experiment_id=0,session_id=0,event_id=Computer.getNextEventID(),event_type=etype,device_type=ioHub.DEVICE_TYPE_LABEL['KEYBOARD_DEVICE'],
                                device_instance_code=device_instance_code,device_time=int(event.Time),logged_time=notifiedTime,hub_time=0,
                                confidence_interval=0.0,delay=0.0,is_pressed=pressed,flags=event.flags,
                                alt=event.IsAlt(),extended=event.IsExtended(),transition=event.IsTransition(),
                                scan_code=event.ScanCode,ascii_code=event.Ascii,key_id=event.KeyID,
                                key=unicode(event.GetKey()),char=unicode(chrv),modifiers=event.Modifiers,window_id=event.Window)  
