"""
ioHub
.. file: ioHub/devices/keyboard/_linux.py

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>

"""

import ujson
import ioHub
from .. import Computer
#import ioHub
#from ioHub.constants import KeyboardConstants, EventConstants

currentSec=Computer.currentSec

#ModifierKeyStrings={'Lcontrol':'CONTROL_LEFT','Rcontrol':'CONTROL_RIGHT','Lshift':'SHIFT_LEFT','Rshift':'SHIFT_RIGHT','Lalt':'ALT_LEFT','Ralt':'ALT_RIGHT','Lmenu':'MENU_LEFT','Rmenu':'MENU_RIGHT','Lwin':'WIN_LEFT'}

class KeyboardLinux(object):
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
            
            self._lastCallbackTime=notifiedTime
        return True

    def _poll(self):
        pass
    
    def _getIOHubEventObject(self,native_event):
        if  len(native_event) >2:
            # it is a KeyboardCharEvent
            return native_event
            
        notifiedTime,event=native_event
                        
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
