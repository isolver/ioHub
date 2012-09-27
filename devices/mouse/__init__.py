"""
ioHub
.. file: ioHub/devices/mouse/__init__.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

from .. import computer, Device, EventConstants
import numpy as N

# Mouse Device Instance Settings Data


# OS ' independent' view of the Mouse Device

if computer.system == 'Windows':
    global Mouse
    from _win32 import MouseWindows32

    class Mouse(Device,MouseWindows32):
        newDataTypes=[]
        baseDataType=Device.dataType
        dataType=baseDataType+newDataTypes
        attributeNames=[e[0] for e in dataType]
        ndType=N.dtype(dataType)
        fieldCount=ndType.__len__()
        categoryTypeString='MOUSE'
        deviceTypeString='MOUSE_DEVICE'        
        def __init__(self,*args,**kwargs):
            """
            
            :rtype : Mouse
            :param args: 
            :param kwargs: 
            """
            deviceConfig=kwargs['dconfig']
            deviceSettings={'instance_code':deviceConfig['instance_code'],
                'category_id':EventConstants.DEVICE_CATERGORIES[Mouse.categoryTypeString],
                'type_id':EventConstants.DEVICE_TYPES[Mouse.deviceTypeString],
                'device_class':deviceConfig['device_class'],
                'user_label':deviceConfig['name'],
                'os_device_code':'OS_DEV_CODE_NOT_SET',
                'max_event_buffer_length':deviceConfig['event_buffer_length']
                }          
            Device.__init__(self,**deviceSettings)
            MouseWindows32.__init__(self,**deviceSettings)        
elif computer.system == 'Linux':
    import _linux
    print 'Mouse not implemented on Linux yet.'
else: # assume OS X
    import _osx
    print 'Mouse not implemented on OS X yet.'

############# OS Independent Mouse Event Classes ####################

from .. import DeviceEvent

class MouseEvent(DeviceEvent):
    # TODO: Determine real maximum key name string and modifiers string
    # lengths and set appropriately.
    newDataTypes = [('button_state',N.uint8),('button_id',N.uint8),('x_position',N.uint16),
                                    ('y_position',N.uint16), ('wheel', N.int8),('windowID',N.uint64)]
    baseDataType=DeviceEvent.dataType
    dataType=baseDataType+newDataTypes
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in newDataTypes]
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)

class MouseMoveEvent(MouseEvent):
    __slots__=[]

    EVENT_TYPE_STRING='MOUSE_MOVE'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING

    def __init__(self, *args, **kwargs):
        """

        :rtype : MouseMoveEvent
        :param args:
        :param kwargs:
        """
        MouseEvent.__init__(self, *args, **kwargs)

class MouseWheelEvent(MouseEvent):
    __slots__=[]

    EVENT_TYPE_STRING='MOUSE_WHEEL'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING

    def __init__(self, *args, **kwargs):
        """

        :rtype : MouseWheelEvent
        :param args:
        :param kwargs:
        """
        MouseEvent.__init__(self, *args, **kwargs)

class MouseWheelUpEvent(MouseWheelEvent):
    __slots__=[]

    EVENT_TYPE_STRING='MOUSE_WHEEL_UP'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=MouseWheelEvent.IOHUB_DATA_TABLE

    def __init__(self, *args, **kwargs):
        """

        :rtype : MouseWheelUpEvent
        :param args:
        :param kwargs:
        """
        MouseWheelEvent.__init__(self, *args, **kwargs)

class MouseWheelDownEvent(MouseWheelEvent):
    __slots__=[]

    EVENT_TYPE_STRING='MOUSE_WHEEL_DOWN'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=MouseWheelEvent.IOHUB_DATA_TABLE

    def __init__(self, *args, **kwargs):
        """

        :rtype : MouseWheelDownEvent
        :param args:
        :param kwargs:
        """
        MouseWheelEvent.__init__(self, *args, **kwargs)

class MouseButtonEvent(MouseEvent):
    __slots__=[]

    EVENT_TYPE_STRING='MOUSE_BUTTON'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING

    def __init__(self, *args, **kwargs):
        """

        :rtype : MouseButtonEvent
        :param args:
        :param kwargs:
        """
        MouseEvent.__init__(self, *args, **kwargs)

class MouseButtonDownEvent(MouseButtonEvent):
    __slots__=[]

    EVENT_TYPE_STRING='MOUSE_PRESS'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=MouseButtonEvent.IOHUB_DATA_TABLE

    def __init__(self, *args, **kwargs):
        """

        :rtype : MouseButtonDownEvent
        :param args:
        :param kwargs:
        """
        MouseButtonEvent.__init__(self, *args, **kwargs)

class MouseButtonUpEvent(MouseButtonEvent):
    __slots__=[]

    EVENT_TYPE_STRING='MOUSE_RELEASE'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=MouseButtonEvent.IOHUB_DATA_TABLE

    def __init__(self, *args, **kwargs):
        """

        :rtype : MouseButtonUpEvent
        :param args:
        :param kwargs:
        """
        MouseButtonEvent.__init__(self, *args, **kwargs)

class MouseDoubleClickEvent(MouseButtonEvent):
    __slots__=[]

    EVENT_TYPE_STRING='MOUSE_DOUBLE_CLICK'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=MouseButtonEvent.IOHUB_DATA_TABLE

    def __init__(self, *args, **kwargs):
        """

        :rtype : MouseDoubleClickEvent
        :param args:
        :param kwargs:
        """
        MouseButtonEvent.__init__(self, *args, **kwargs)
