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
        newDataTypes=[]
        baseDataType=Device.dataType
        dataType=baseDataType+newDataTypes
        attributeNames=[e[0] for e in dataType]
        ndType=N.dtype(dataType)
        fieldCount=ndType.__len__()
        __slots__=[e[0] for e in newDataTypes]
        categoryTypeString='KEYBOARD'
        deviceTypeString='KEYBOARD_DEVICE'
        def __init__(self,*args,**kwargs):
            deviceConfig=kwargs['dconfig']
            deviceSettings={'instance_code':deviceConfig['instance_code'],
                'category_id':EventConstants.DEVICE_CATERGORIES[Keyboard.categoryTypeString],
                'type_id':EventConstants.DEVICE_TYPES[Keyboard.deviceTypeString],
                'device_class':deviceConfig['device_class'],
                'user_label':deviceConfig['name'],
                'os_device_code':'OS_DEV_CODE_NOT_SET',
                'max_event_buffer_length':deviceConfig['event_buffer_length']
                }          
            Device.__init__(self,**deviceSettings)
            KeyboardWindows32.__init__(self,**deviceSettings)            
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
    newDataTypes = [('is_pressed',N.bool),('flags',N.uint8),('alt',N.uint8),
                                            ('extended',N.bool),('transition',N.uint8),('scan_code',N.uint8),
                                            ('ascii_code',N.uint),('key_id',N.uint),('key',N.string_,12),('char',N.string_,1),
                                            ('modifiers',N.uint8),('window_id',N.uint32)]
    baseDataType=DeviceEvent.dataType
    dataType=baseDataType+newDataTypes
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in newDataTypes]

    def __init__(self,*args,**kwargs):
        kwargs['device_type']=EventConstants.DEVICE_TYPES['KEYBOARD_DEVICE']
        DeviceEvent.__init__(self,*args,**kwargs)

class KeyboardKeyEvent(KeyboardEvent):
    __slots__=[]

    EVENT_TYPE_STRING='KEYBOARD_KEY'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING

    def __init__(self,*args,**kwargs):
        """

        :rtype : object
        :param kwargs:
        """
        KeyboardEvent.__init__(self,*args,**kwargs)

class KeyboardPressEvent(KeyboardKeyEvent):
    __slots__=[]

    EVENT_TYPE_STRING='KEYBOARD_PRESS'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=KeyboardKeyEvent.IOHUB_DATA_TABLE

    def __init__(self,*args,**kwargs):
        """

        :rtype : object
        :param kwargs:
        """
        KeyboardKeyEvent.__init__(self,*args,**kwargs)


class KeyboardReleaseEvent(KeyboardKeyEvent):
    __slots__=[]

    EVENT_TYPE_STRING='KEYBOARD_RELEASE'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=KeyboardKeyEvent.IOHUB_DATA_TABLE

    def __init__(self,*args,**kwargs):
        """

        :rtype : object
        :param kwargs:
        """
        KeyboardKeyEvent.__init__(self,*args,**kwargs)
