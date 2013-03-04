"""
ioHub
.. file: ioHub/devices/mouse/__init__.py

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""
from .. import Computer, Device
from ioHub.constants import EventConstants, DeviceConstants
import numpy as N

global Mouse

# Mouse Device Instance Settings Data


# OS ' independent' view of the Mouse Device

if Computer.system == 'Windows':
    global Mouse
    from _win32 import MouseWindows32

    class Mouse(Device,MouseWindows32):
        """
        The Mouse class represents a standard USB or PS2 mouse device that has up to 
        three buttons and an optional vertical scroll wheel. Mouse position data is 
        mapped to the coordinate space defined in the ioHub configuration file for the Display.
        """
        ALL_EVENT_CLASSES=[]

        DEVICE_TYPE_ID=DeviceConstants.MOUSE
        DEVICE_TYPE_STRING=DeviceConstants.getName(DEVICE_TYPE_ID)
        __slots__=[]
        def __init__(self,*args,**kwargs):
            Mouse.ALL_EVENT_CLASSES=MouseMoveEvent, MouseWheelUpEvent, MouseWheelDownEvent,MouseButtonDownEvent,MouseButtonUpEvent,MouseDoubleClickEvent
            deviceConfig=kwargs['dconfig']
            deviceSettings={
                'type_id':self.DEVICE_TYPE_ID,
                'device_class':Mouse.__name__,
                'name':deviceConfig['name'],
                'monitor_event_types':deviceConfig.get('monitor_event_types',self.ALL_EVENT_CLASSES),
                'os_device_code':'OS_DEV_CODE_NOT_SET',
                '_isReportingEvents':deviceConfig.get('auto_report_events',True),
                'max_event_buffer_length':deviceConfig['event_buffer_length']
                }          
            Device.__init__(self,*args,**deviceSettings)
            MouseWindows32.__init__(self,*args,**deviceSettings)
            
            self._startupConfiguration=deviceConfig

elif Computer.system == 'Linux':
#    global Mouse
    from _linux import MouseLinux

    class Mouse(Device,MouseLinux):
        """
        The Mouse class and related events represent a standard computer mouse device
        and the events a standard mouse can produce. Mouse position data is mapped to
        the coordinate space defined in the ioHub configuration file for the Display.
        """
        ALL_EVENT_CLASSES=[]

        DEVICE_TYPE_ID=DeviceConstants.MOUSE
        DEVICE_TYPE_STRING=DeviceConstants.getName(DEVICE_TYPE_ID)
        __slots__=[]
        def __init__(self,*args,**kwargs):
            Mouse.ALL_EVENT_CLASSES=MouseMoveEvent, MouseWheelUpEvent, MouseWheelDownEvent,MouseButtonDownEvent,MouseButtonUpEvent,MouseDoubleClickEvent
            deviceConfig=kwargs['dconfig']
            deviceSettings={
                'type_id':self.DEVICE_TYPE_ID,
                'device_class':Mouse.__name__,
                'name':deviceConfig['name'],
                'monitor_event_types':deviceConfig.get('monitor_event_types',self.ALL_EVENT_CLASSES),
                'os_device_code':'OS_DEV_CODE_NOT_SET',
                '_isReportingEvents':deviceConfig.get('auto_report_events',True),
                'max_event_buffer_length':deviceConfig['event_buffer_length']
                }          
            Device.__init__(self,*args,**deviceSettings)
            MouseLinux.__init__(self,*args,**deviceSettings)
            
            self._startupConfiguration=deviceConfig


else: # assume OS X
    import _osx
    print 'Mouse not implemented on OS X yet.'

############# OS Independent Mouse Event Classes ####################

from .. import DeviceEvent

class MouseEvent(DeviceEvent):
    """
    The MouseEvent is an abstract class that is the parent of all MouseEvent types
    that are supported in the ioHub. Mouse position is mapped to the coordinate space
    defined in the ioHub configuration file for the Display.
    """
    PARENT_DEVICE=Mouse
    EVENT_TYPE_STRING='MOUSE_INPUT'
    EVENT_TYPE_ID=EventConstants.MOUSE_INPUT
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING

    _newDataTypes = [
                     ('button_state',N.uint8),    # 1 if button is pressed, 0 if button is released
                     ('button_id',N.uint8),       # 1, 2,or 4, representing left, right, and middle buttons
                     ('pressed_buttons',N.uint8), # sum of currently active button int values

                     ('x_position',N.int16),    # x position of the position when the event occurred
                     ('y_position',N.int16),    # y position of the position when the event occurred

                     ('wheel_change', N.int8),  # vertical scroll wheel position change when the event occurred
                     ('wheel_value', N.int16),  # vertical scroll wheel abs. position when the event occurred

                     ('windowID',N.uint64)      # window ID that the mouse was over when the event occurred
                                                # (window does not need to have focus)
                    ]
    # TODO: Determine real maximum key name string and modifiers string
    # lengths and set appropriately.

    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self,*args,**kwargs):
        #: 1 if button is pressed, 0 if button is released
        self.button_state=None

        #: MouseConstants.MOUSE_BUTTON_LEFT, MouseConstants.MOUSE_BUTTON_RIGHT
        #: and MouseConstants.MOUSE_BUTTON_MIDDLE are int constants 
        #: representing left, right, and middle buttons of the mouse.
        self.button_id=None

        #: 'All' currently pressed button id's
        self.pressed_buttons=None

        #: x position of the position when the event occurred; in display coordinate space
        self.x_position=None

        #: y position of the position when the event occurred; in display coordinate space
        self.y_position=None
        
        #: vertical scroll wheel position change when the event occurred
        self.wheel_change=None

        #: vertical scroll wheel absolute position when the event occurred
        self.wheel_value=None

        #: window ID that the mouse was over when the event occurred
        #: (window does not need to have focus)
        self.windowID=None

        DeviceEvent.__init__(self,*args,**kwargs)

class MouseMoveEvent(MouseEvent):
    """
    MouseMoveEvents occur when the mouse position changes. Mouse position is
    mapped to the coordinate space defined in the ioHub configuration file 
    for the Display.
    
    Event Type ID: EventConstants.MOUSE_MOVE
    Event Type String: 'MOUSE_MOVE'
    """
    EVENT_TYPE_STRING='MOUSE_MOVE'
    EVENT_TYPE_ID=EventConstants.MOUSE_MOVE
    IOHUB_DATA_TABLE=MouseEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        MouseEvent.__init__(self, *args, **kwargs)

class MouseWheelEvent(MouseEvent):
    EVENT_TYPE_STRING='MOUSE_WHEEL'
    EVENT_TYPE_ID=EventConstants.MOUSE_WHEEL
    IOHUB_DATA_TABLE=MouseEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        """

        :rtype : MouseWheelEvent
        :param args:
        :param kwargs:
        """
        MouseEvent.__init__(self, *args, **kwargs)

class MouseWheelUpEvent(MouseWheelEvent):
    """
    MouseWheelUpEvent's are generated when the vertical scroll wheel on the 
    Mouse Device (if it has one) is turned in the direction toward the front 
    of the mouse. Horizontal scrolling is not currently supported.
    Each MouseWheelUpEvent provides the number of units the wheel was turned 
    ( +1 ) as well as the absolute scroll value for the mouse, which is an 
    ioHub Mouse attribute that is simply modified by the change value of
    MouseWheelUpEvent and MouseWheelDownEvent types.

    Event Type ID: EventConstants.MOUSE_WHEEL_UP
    Event Type String: 'MOUSE_WHEEL_UP'
    """
    EVENT_TYPE_STRING='MOUSE_WHEEL_UP'
    EVENT_TYPE_ID=EventConstants.MOUSE_WHEEL_UP
    IOHUB_DATA_TABLE=MouseEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        """

        :rtype : MouseWheelUpEvent
        :param args:
        :param kwargs:
        """
        MouseWheelEvent.__init__(self, *args, **kwargs)

class MouseWheelDownEvent(MouseWheelEvent):
    """
    MouseWheelDownEvent's are generated when the vertical scroll wheel on the 
    Mouse Device (if it has one) is turned in the direction toward the back
    of the mouse. Horizontal scrolling is not currently supported.
    Each MouseWheelDownEvent provides the number of units the wheel was turned 
    as a negative value ( -1 ) as well as the absolute scroll value for the mouse,
    which is an ioHub Mouse attribute that is simply modified by the change value
    of MouseWheelUpEvent and MouseWheelDownEvent types.
    
    Event Type ID: EventConstants.MOUSE_WHEEL_DOWN
    Event Type String: 'MOUSE_WHEEL_DOWN'    
    """
    EVENT_TYPE_STRING='MOUSE_WHEEL_DOWN'
    EVENT_TYPE_ID=EventConstants.MOUSE_WHEEL_DOWN
    IOHUB_DATA_TABLE=MouseEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        """

        :rtype : MouseWheelDownEvent
        :param args:
        :param kwargs:
        """
        MouseWheelEvent.__init__(self, *args, **kwargs)

class MouseButtonEvent(MouseEvent):
    EVENT_TYPE_STRING='MOUSE_BUTTON'
    EVENT_TYPE_ID=EventConstants.MOUSE_BUTTON
    IOHUB_DATA_TABLE=MouseEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        """

        :rtype : MouseButtonEvent
        :param args:
        :param kwargs:
        """
        MouseEvent.__init__(self, *args, **kwargs)

class MouseButtonDownEvent(MouseButtonEvent):
    """
    MouseButtonDownEvent's are created when a button on the mouse is pressed. 
    The button_state of the event will equal MouseConstants.MOUSE_BUTTON_STATE_PRESSED,
    and the button that was pressed (button_id) will be MouseConstants.MOUSE_BUTTON_ID_LEFT,
    MouseConstants.MOUSE_BUTTON_ID_RIGHT, or MouseConstants.MOUSE_BUTTON_ID_MIDDLE, 
    assuming you have a 3 button mouse.

    To get the current state of all three buttons on the Mouse Device, 
    the pressed_buttons attribute can be read, which tracks the state of all three
    mouse buttons as an int that is equal to the sum of any pressed button id's 
    ( MouseConstants.MOUSE_BUTTON_ID_LEFT,  MouseConstants.MOUSE_BUTTON_ID_RIGHT, or
    MouseConstants.MOUSE_BUTTON_ID_MIDDLE ).

    To tell if a given mouse button was depressed when the event occurred, regardless of which
    button triggered the event, you can use the following::

        isButtonPressed = event.pressed_buttons & MouseConstants.MOUSE_BUTTON_ID_xxx == MouseConstants.MOUSE_BUTTON_ID_xxx

    where xxx is LEFT, RIGHT, or MIDDLE.

    For example, if at the time of the event both the left and right mouse buttons
    were in a pressed state::

        buttonToCheck=MouseConstants.MOUSE_BUTTON_ID_RIGHT
        isButtonPressed = event.pressed_buttons & buttonToCheck == buttonToCheck

        print isButtonPressed

        >> True

        buttonToCheck=MouseConstants.MOUSE_BUTTON_ID_LEFT
        isButtonPressed = event.pressed_buttons & buttonToCheck == buttonToCheck

        print isButtonPressed

        >> True

        buttonToCheck=MouseConstants.MOUSE_BUTTON_ID_MIDDLE
        isButtonPressed = event.pressed_buttons & buttonToCheck == buttonToCheck

        print isButtonPressed

        >> False

    Event Type ID: EventConstants.MOUSE_PRESS
    Event Type String: 'MOUSE_PRESS'    
    """
    EVENT_TYPE_STRING='MOUSE_PRESS'
    EVENT_TYPE_ID=EventConstants.MOUSE_PRESS
    IOHUB_DATA_TABLE=MouseEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        MouseButtonEvent.__init__(self, *args, **kwargs)

class MouseButtonUpEvent(MouseButtonEvent):
    """
    MouseButtonUpEvent's are created when a button on the mouse is released. 
    The button_state of the event will equal MouseConstants.MOUSE_BUTTON_STATE_RELEASED,
    and the button that was pressed (button_id) will be MouseConstants.MOUSE_BUTTON_ID_LEFT,
    MouseConstants.MOUSE_BUTTON_ID_RIGHT, or MouseConstants.MOUSE_BUTTON_ID_MIDDLE, 
    assuming you have a 3 button mouse.

    Event Type ID: EventConstants.MOUSE_RELEASE
    Event Type String: 'MOUSE_RELEASE'    
    """
    EVENT_TYPE_STRING='MOUSE_RELEASE'
    EVENT_TYPE_ID=EventConstants.MOUSE_RELEASE
    IOHUB_DATA_TABLE=MouseEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        MouseButtonEvent.__init__(self, *args, **kwargs)

class MouseDoubleClickEvent(MouseButtonEvent):
    """
    MouseDoubleClickEvent's are created when you rapidly press and release a 
    mouse button twice. This event may never get triggered if your OS does not support it.
    The button that was double clicked (button_id) will be MouseConstants.MOUSE_BUTTON_ID_LEFT,
    MouseConstants.MOUSE_BUTTON_ID_RIGHT, or MouseConstants.MOUSE_BUTTON_ID_MIDDLE, 
    assuming you have a 3 button mouse.

    Event Type ID: EventConstants.MOUSE_DOUBLE_CLICK
    Event Type String: 'MOUSE_DOUBLE_CLICK'    
    """
    EVENT_TYPE_STRING='MOUSE_DOUBLE_CLICK'
    EVENT_TYPE_ID=EventConstants.MOUSE_DOUBLE_CLICK
    IOHUB_DATA_TABLE=MouseEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        MouseButtonEvent.__init__(self, *args, **kwargs)
