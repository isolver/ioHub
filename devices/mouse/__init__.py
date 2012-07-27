"""
XioHub Mouse Device

Part of the XioHub Module
Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""

from .. import computer, Device
from collections import deque
import numpy as N
import ioHub

# Mouse Device Instance Settings Data


# OS ' independent' view of the Mouse Device

if computer.system == 'Windows':
    global Mouse
    from __win32__ import MouseWindows32         

    class Mouse(Device,MouseWindows32):
        dataType = Device.dataType+[]
        attributeNames=[e[0] for e in dataType]
        defaultValueDict=dict(Device.defaultValueDict,**{'category_id':ioHub.DEVICE_CATERGORY_ID_LABEL['MOUSE'],'type_id':ioHub.DEVICE_TYPE_LABEL['MOUSE_DEVICE'],'max_event_buffer_length':1024})
        ndType=N.dtype(dataType)
        fieldCount=ndType.__len__()
        __slots__=attributeNames
        
        def __init__(self,*args,**kwargs):
            dargs=dict(Mouse.defaultValueDict)
       
            for k,v in kwargs.iteritems():
                if k in dargs:
                    dargs[k]=v
             
            Device.__init__(self,**dargs)
            MouseWindows32.__init__(self,**dargs)           
            print "Mouse class set as ",self.__class__.__name__           
elif computer.system == 'Linux':
    import __linux__
    print 'Mouse not implemented on Linux yet.'
else: # assume OS X
    import __osx__
    print 'Mouse not implemented on OS X yet.'

############# OS Independent Mouse Event Classes ####################

from .. import DeviceEvent

class MouseEvent(DeviceEvent):
    # TODO: Determine real maximum key name string and modifiers string
    # lengths and set appropriately.
    dataType = DeviceEvent.dataType+[('button_state',N.uint8),('button_id',N.uint8),('x_position',N.uint16),
                                    ('y_position',N.uint16), ('wheel', N.uint8),('windowID',N.uint64)]
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)

class MouseMoveEvent(MouseEvent):
    dataType = MouseEvent.dataType
    ndType=MouseEvent.ndType
    fieldCount=MouseEvent.fieldCount
    def __init__(self,*args,**kwargs):
        MouseEvent.__init__(self,*args,**kwargs)

class MouseWheelEvent(MouseEvent):
    dataType = MouseEvent.dataType
    ndType=MouseEvent.ndType
    fieldCount=MouseEvent.fieldCount
    def __init__(self,*args,**kwargs):
        MouseEvent.__init__(self,*args,**kwargs)

class MouseButtonDownEvent(MouseEvent):
    dataType = MouseEvent.dataType
    ndType=MouseEvent.ndType
    fieldCount=MouseEvent.fieldCount
    def __init__(self,*args,**kwargs):
        MouseEvent.__init__(self,*args,**kwargs)

class MouseButtonUpEvent(MouseEvent):
    dataType = MouseEvent.dataType
    ndType=MouseEvent.ndType
    fieldCount=MouseEvent.fieldCount
    def __init__(self,*args,**kwargs):
        MouseEvent.__init__(self,*args,**kwargs)

class MouseDoubleClickEvent(MouseEvent):
    dataType = MouseEvent.dataType
    ndType=MouseEvent.ndType
    fieldCount=MouseEvent.fieldCount
    def __init__(self,*args,**kwargs):
        MouseEvent.__init__(self,*args,**kwargs)
