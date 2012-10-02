"""
ioHub
.. file: ioHub/devices/keyboard/__init__.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

import numpy as N

from .. import Device, computer, EventConstants

##### Modifier Keys #####

L_CONTROL = 1
R_CONTROL = 2
L_SHIFT = 4
R_SHIFT = 8
L_ALT = L_MENU = 16
R_ALT = R_MENU = 32
L_WIN= 64

MODIFIER_KEYS={}
MODIFIER_KEYS[L_CONTROL]='L_CONTROL'
MODIFIER_KEYS[R_CONTROL]='R_CONTROL'
MODIFIER_KEYS[L_SHIFT]='L_SHIFT'
MODIFIER_KEYS[R_SHIFT]='R_SHIFT'
MODIFIER_KEYS[L_ALT]='L_ALT'
MODIFIER_KEYS[R_ALT]='R_ALT'
MODIFIER_KEYS[L_MENU]='L_MENU'
MODIFIER_KEYS[R_MENU]='R_MENU'
MODIFIER_KEYS[L_WIN]='L_WIN'

mkeystemp={}
for key, value in MODIFIER_KEYS.iteritems():
    mkeystemp[value]=key
for key, value in mkeystemp.iteritems():
    MODIFIER_KEYS[key]=value
    
dt=N.dtype([('L_CONTROL',N.bool),('R_CONTROL',N.bool),('L_SHIFT',N.bool),('R_SHIFT',N.bool),('L_MENU',N.bool),('R_MENU',N.bool),('L_WIN',N.bool)])
MODIFIER_ACTIVE=N.array((False,False,False,False,False,False,False),dtype=dt)


###### recast based on OS ##########

if computer.system == 'Windows':
    global Keyboard
    from  _win32 import  KeyboardWindows32
    
    class Keyboard(Device,KeyboardWindows32):
        CATEGORY_LABEL='KEYBOARD'
        DEVICE_LABEL='KEYBOARD_DEVICE'
        __slots__=[]
        def __init__(self,*args,**kwargs):
            deviceConfig=kwargs['dconfig']
            deviceSettings={'instance_code':deviceConfig['instance_code'],
                'category_id':EventConstants.DEVICE_CATERGORIES[Keyboard.CATEGORY_LABEL],
                'type_id':EventConstants.DEVICE_TYPES[Keyboard.DEVICE_LABEL],
                'device_class':deviceConfig['device_class'],
                'name':deviceConfig['name'],
                'os_device_code':'OS_DEV_CODE_NOT_SET',
                'max_event_buffer_length':deviceConfig['event_buffer_length']
                }          
            Device.__init__(self,*args,**deviceSettings)
            KeyboardWindows32.__init__(self,*args,**deviceSettings)
elif computer.system == 'Linux':
    import _linux
    print 'Keyboard not implemented on Linux yet.'
else: # assume OS X
    print 'Keyboard not implemented on OS X yet.'
    
############# OS independent Keyboard Event classes ####################
from .. import DeviceEvent

class KeyboardEvent(DeviceEvent):
    # TODO: Determine real maximum key name string and modifiers string
    # lengths and set appropriately.
    _newDataTypes = [
                    ('is_pressed',N.uint8), # 1 if key was pressed, 0 if key was released

                    ('flags',N.uint8),      # flags from the key event. Meaning TBD.

                    ('alt',N.uint8),        # 1 if alt was depressed when key event occurred, 0 otherwise

                    ('extended',N.uint8),   # 1 if this is an extended key, 0 if it is a ASCII key

                    ('transition',N.uint8), # 1 if the key event is the first key event for that keys event sequence

                    ('scan_code',N.uint8),  # the scan code for the key that was pressed.
                                            # Represents the physical key id on the keyboard layout

                    ('ascii_code',N.uint),  # the ASCII byte value for the key (0 - 255)

                    ('key_id',N.uint),      # the translated key ID, based on the keyboard local settings of the OS.

                    ('key',N.str,12),       # a string representation of what key was pressed.
                                            # Letters will always be upper case.

                    ('char',N.str,1),       # the converted ascii code into a character. char will be upper
                                            # or lower case depending on SHIFT key state.

                    ('modifiers',N.uint8),  # indicates what modifier keys were active when the key was pressed.

                    ('window_id',N.uint32)  # the id of the window that had focus when the key was pressed.
                    ]
    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self,*args,**kwargs):
        kwargs['device_type']=EventConstants.DEVICE_TYPES['KEYBOARD_DEVICE']
        DeviceEvent.__init__(self,*args,**kwargs)

class KeyboardKeyEvent(KeyboardEvent):
    EVENT_TYPE_STRING='KEYBOARD_KEY'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING
    __slots__=[]
    def __init__(self,*args,**kwargs):
        """

        :rtype : object
        :param kwargs:
        """
        KeyboardEvent.__init__(self,*args,**kwargs)

class KeyboardPressEvent(KeyboardKeyEvent):
    """
    A KeyboardPressEvent is generated when a key on a monitored keyboard is depressed.
    The event is created prior to the keyboard key being released. If a key is held down for
    an extended period of time, multiple KeyboardPressEvent events may be generated depending
    on your OS and the OS's settings for key repeat event creation.
    """
    EVENT_TYPE_STRING='KEYBOARD_PRESS'
    EVENT_TYPE_ID=EventConstants.KEYBOARD_PRESS_EVENT
    IOHUB_DATA_TABLE=KeyboardKeyEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self,*args,**kwargs):
        KeyboardKeyEvent.__init__(self,*args,**kwargs)


class KeyboardReleaseEvent(KeyboardKeyEvent):
    """
    A KeyboardReleaseEvent is generated when a key on a monitored keyboard is released.
    """
    EVENT_TYPE_STRING='KEYBOARD_RELEASE'
    EVENT_TYPE_ID=EventConstants.KEYBOARD_RELEASE_EVENT
    IOHUB_DATA_TABLE=KeyboardKeyEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self,*args,**kwargs):
        KeyboardKeyEvent.__init__(self,*args,**kwargs)
