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
        self._last_callback_time=0
        


