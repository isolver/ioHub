"""
ioHub
.. file: ioHub/devices/keyboard/_win32.py

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

import ujson

from .. import Computer
import ioHub
from ioHub.constants import KeyboardConstants, EventConstants

currentSec=Computer.currentSec

from . import MODIFIER_ACTIVE,MODIFIER_KEYS

ModifierKeyStrings={'Lcontrol':'CONTROL_LEFT','Rcontrol':'CONTROL_RIGHT','Lshift':'SHIFT_LEFT','Rshift':'SHIFT_RIGHT','Lalt':'ALT_LEFT','Ralt':'ALT_RIGHT','Lmenu':'MENU_LEFT','Rmenu':'MENU_RIGHT','Lwin':'WIN_LEFT'}

class KeyboardWindows32(object):
    WH_KEYBOARD = 2
    WH_KEYBOARD_LL = 13
    WH_MAX = 15

    WM_KEYFIRST = 0x0100
    WM_KEYDOWN = 0x0100
    WM_KEYUP = 0x0101
    WM_CHAR = 0x0102
    WM_DEADCHAR = 0x0103
    WM_SYSKEYDOWN = 0x0104
    WM_SYSKEYUP = 0x0105
    WM_SYSCHAR = 0x0106
    WM_SYSDEADCHAR = 0x0107
    WM_KEYLAST = 0x0108

    WIN32_KEYBOARD_PRESS_EVENT_TYPES=(WM_KEYDOWN,WM_SYSKEYDOWN)

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
        return True


    def _getIOHubEventObject(self,event):
        if  len(event) >2:
            # it is a KeyboardCharEvent
            return event

        notifiedTime, event=event
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
