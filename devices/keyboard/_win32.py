"""
ioHub
.. file: ioHub/devices/keyboard/_win32.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""
from .. import Device, Computer, EventConstants

import ioHub
currentSec=Computer.currentSec

from . import MODIFIER_ACTIVE,MODIFIER_KEYS

ModifierKeyStrings={'Lcontrol':'L_CONTROL','Rcontrol':'R_CONTROL','Lshift':'L_SHIFT','Rshift':'R_SHIFT','Lalt':'L_ALT','Ralt':'R_ALT','Lmenu':'L_MENU','Rmenu':'R_MENU','Lwin':'L_WIN'}

class KeyboardWindows32(object):
    WIN32_KEYBOARD_PRESS=EventConstants.WM_KEYDOWN
    WIN32_KEYBOARD_SYSKEY_PRESS=EventConstants.WM_SYSKEYDOWN    
    WIN32_KEYBOARD_RELEASE=EventConstants.WM_KEYUP
    WIN32_KEYBOARD_PRESS_EVENT_TYPES=(WIN32_KEYBOARD_PRESS,WIN32_KEYBOARD_SYSKEY_PRESS)

    def __init__(self, *args, **kwargs):
        """
        
        :rtype : KeyboardWindows32
        :param args: 
        :param kwargs: 
        """
        self._modifierValue = 0;
        
    def _nativeEventCallback(self,event):
        if self.isReportingEvents():
            notifiedTime=currentSec()
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
                        self._modifierValue+=i
                    else:
                        self._modifierValue-=i
            #
            # End Tracking Modifiers that are pressed
            #
            event.Modifiers=self._modifierValue
            self._addNativeEventToBuffer((notifiedTime,event))
        return True

    def _poll(self):
        pass
            
    @staticmethod
    def _getIOHubEventObject(event):
        from . import KeyboardPressEvent,KeyboardReleaseEvent

        notifiedTime, event=event
        etype = KeyboardReleaseEvent.EVENT_TYPE_ID
        pressed=0
        if event.Message in KeyboardWindows32.WIN32_KEYBOARD_PRESS_EVENT_TYPES:
            etype = KeyboardPressEvent.EVENT_TYPE_ID
            pressed=1
        
        chrv=chr(event.Ascii)
                        
        # From MSDN: http://msdn.microsoft.com/en-us/library/windows/desktop/ms644939(v=vs.85).aspx
        # The time is a long integer that specifies the elapsed time, in milliseconds, from the time the system was started to the time the message was 
        # created (that is, placed in the thread's message queue).REMARKS: The return value from the GetMessageTime function does not necessarily increase
        # between subsequent messages, because the value wraps to zero if the timer count exceeds the maximum value for a long integer. To calculate time
        # delays between messages, verify that the time of the second message is greater than the time of the first message; then, subtract the time of the
        # first message from the time of the second message.
        device_time = event.Time/1000.0 # convert to sec
        #ioHub.print2err("dev_time,log_time, delta: "+ioHub.devices.EventConstants.EVENT_TYPES[etype]+" : "+str(device_time)+" : "+str(notifiedTime)+" : "+str(notifiedTime-device_time))
        hub_time = notifiedTime #TODO correct mouse times to factor in offset.
 
        confidence_interval=0.0 # since this is a keyboard device using a callback method, confidence_interval is not applicable
        delay=0.0 # since this is a keyboard, we 'know' there is a delay, but until we support setting a delay in the device properties based on external testing for a given keyboard, we will leave at 0.

        return [0,0,Computer.getNextEventID(),etype,
                device_time,notifiedTime,hub_time,confidence_interval,delay,pressed,event.flags,
                event.IsAlt(),event.IsExtended(),event.IsTransition(),event.ScanCode,event.Ascii,event.KeyID,
                str(event.GetKey()),str(chrv),event.Modifiers,event.Window]
