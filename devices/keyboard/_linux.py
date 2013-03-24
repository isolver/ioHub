"""
ioHub
.. file: ioHub/devices/keyboard/_linux.py

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>

"""

import ujson
from .. import Computer

currentSec=Computer.currentSec

#ModifierKeyStrings={'Lcontrol':'CONTROL_LEFT','Rcontrol':'CONTROL_RIGHT','Lshift':'SHIFT_LEFT','Rshift':'SHIFT_RIGHT','Lalt':'ALT_LEFT','Ralt':'ALT_RIGHT','Lmenu':'MENU_LEFT','Rmenu':'MENU_RIGHT','Lwin':'WIN_LEFT'}

class KeyboardLinux(object):
    def __init__(self, *args, **kwargs):
        self._modifierValue = 0;
        self._last_callback_time=0
        
