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
        """
        The Mouse class and related events represent a standard computer mouse device
        and the events a standard mouse can produce. Mouse position data is mapped to
        the coordinate space defined in the ioHub configuration file for the Display.
        """
        CATEGORY_LABEL='MOUSE'
        DEVICE_LABEL='MOUSE_DEVICE'
        __slots__=[]
        def __init__(self,*args,**kwargs):
            deviceConfig=kwargs['dconfig']
            deviceSettings={
                'instance_code':deviceConfig['instance_code'],
                'category_id':EventConstants.DEVICE_CATERGORIES[Mouse.CATEGORY_LABEL],
                'type_id':EventConstants.DEVICE_TYPES[Mouse.DEVICE_LABEL],
                'device_class':deviceConfig['device_class'],
                'name':deviceConfig['name'],
                'os_device_code':'OS_DEV_CODE_NOT_SET',
                '_isReportingEvents':deviceConfig.get('auto_report_events',True),
                'max_event_buffer_length':deviceConfig['event_buffer_length']
                }          
            Device.__init__(self,*args,**deviceSettings)
            MouseWindows32.__init__(self,*args,**deviceSettings)
elif computer.system == 'Linux':
    import _linux
    print 'Mouse not implemented on Linux yet.'
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
    EVENT_TYPE_STRING='MOUSE'
    EVENT_TYPE_ID=EventConstants.MOUSE_EVENT
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
        DeviceEvent.__init__(self,*args,**kwargs)

class MouseMoveEvent(MouseEvent):
    """
    MouseMoveEvents occur when the mouse position changes. Mouse position is mapped to the coordinate space
    defined in the ioHub configuration file for the Display.
    """
    EVENT_TYPE_STRING='MOUSE_MOVE'
    EVENT_TYPE_ID=EventConstants.MOUSE_MOVE_EVENT
    IOHUB_DATA_TABLE=MouseEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        MouseEvent.__init__(self, *args, **kwargs)

class MouseWheelEvent(MouseEvent):
    EVENT_TYPE_STRING='MOUSE_WHEEL'
    EVENT_TYPE_ID=EventConstants.MOUSE_WHEEL_EVENT
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
    MouseWheelUpEvent's are generated when the vertical scroll wheel on the Mouse Device (if it has one)
    is turned in the direction toward the front of the mouse. Horizontal scrolling is not currently supported.
    Each MouseWheelUpEvent provides the number of units the wheel was turned ( +1 ) as well as the absolute scroll
    value for the mouse, which is an ioHub Mouse attribute that is simply modified by the change value of
    MouseWheelUpEvent and MouseWheelDownEvent types.
    """
    EVENT_TYPE_STRING='MOUSE_WHEEL_UP'
    EVENT_TYPE_ID=EventConstants.MOUSE_WHEEL_UP_EVENT
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
    MouseWheelDownEvent's are generated when the vertical scroll wheel on the Mouse Device (if it has one)
    is turned in the direction toward the back of the mouse. Horizontal scrolling is not currently supported.
    Each MouseWheelDownEvent provides the number of units the wheel was turned as a negative value ( -1 )
    as well as the absolute scroll value for the mouse, which is an ioHub Mouse attribute that is simply modified
    by the change value of MouseWheelUpEvent and MouseWheelDownEvent types.
    """
    EVENT_TYPE_STRING='MOUSE_WHEEL_DOWN'
    EVENT_TYPE_ID=EventConstants.MOUSE_WHEEL_DOWN_EVENT
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
    EVENT_TYPE_ID=EventConstants.MOUSE_BUTTON_EVENT
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
    MouseButtonDownEvent's are created when a button on the mouse is pressed. The button_state of
    the event will equal EventConstants.MOUSE_BUTTON_STATE_PRESSED, and the button that was pressed
    (button_id) will be EventConstants.MOUSE_BUTTON_ID_LEFT, EventConstants.MOUSE_BUTTON_ID_RIGHT, or
    EventConstants.MOUSE_BUTTON_ID_MIDDLE, assuming you have a 3 button mouse.

    To get the current state of all three buttons on the Mouse Device, the pressed_buttons attribute can be
    read, which tracks the state of all three mouse buttons as an int that is equal to the sum of any pressed
    button id's ( EventConstants.MOUSE_BUTTON_ID_LEFT,  EventConstants.MOUSE_BUTTON_ID_RIGHT, or
    EventConstants.MOUSE_BUTTON_ID_MIDDLE ).

    To tell if a given mouse button was depressed when the event occurred, regardless of which
    button triggered the event, you can use the following:

    isButtonPressed = event['pressed_buttons']&EventConstants.MOUSE_BUTTON_ID_xxx ==  \
                      EventConstants.MOUSE_BUTTON_ID_xxx,

    where xxx is LEFT, RIGHT, or MIDDLE.

    For example, if at the time of the event both the left and right mouse buttons were in a pressed state:

    buttonToCheck=EventConstants.MOUSE_BUTTON_ID_RIGHT
    isButtonPressed = event['pressed_buttons']&buttonToCheck==buttonToCheck

    print isButtonPressed

    >> True

    buttonToCheck=EventConstants.MOUSE_BUTTON_ID_LEFT
    isButtonPressed = event['pressed_buttons']&buttonToCheck==buttonToCheck

    print isButtonPressed

    >> True

    buttonToCheck=EventConstants.MOUSE_BUTTON_ID_MIDDLE
    isButtonPressed = event['pressed_buttons']&buttonToCheck==buttonToCheck

    print isButtonPressed

    >> False

    """
    EVENT_TYPE_STRING='MOUSE_PRESS'
    EVENT_TYPE_ID=EventConstants.MOUSE_PRESS_EVENT
    IOHUB_DATA_TABLE=MouseEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        MouseButtonEvent.__init__(self, *args, **kwargs)

class MouseButtonUpEvent(MouseButtonEvent):
    """
    MouseButtonUpEvent's are created when a button on the mouse is released. The button_state of
    the event will equal EventConstants.MOUSE_BUTTON_STATE_RELEASED, and the button that was pressed
    (button_id) will be EventConstants.MOUSE_BUTTON_ID_LEFT, EventConstants.MOUSE_BUTTON_ID_RIGHT, or
    EventConstants.MOUSE_BUTTON_ID_MIDDLE, assuming you have a 3 button mouse.
    """
    EVENT_TYPE_STRING='MOUSE_RELEASE'
    EVENT_TYPE_ID=EventConstants.MOUSE_RELEASE_EVENT
    IOHUB_DATA_TABLE=MouseEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        MouseButtonEvent.__init__(self, *args, **kwargs)

class MouseDoubleClickEvent(MouseButtonEvent):
    """
    MouseDoubleClickEvent's are created when you rapidly press and release a mouse button twice.
    This event may never get triggered if your OS does not support it. The button that was double
    clicked (button_id) will be EventConstants.MOUSE_BUTTON_ID_LEFT, EventConstants.MOUSE_BUTTON_ID_RIGHT,
    or EventConstants.MOUSE_BUTTON_ID_MIDDLE, assuming you have a 3 button mouse.
    """
    EVENT_TYPE_STRING='MOUSE_DOUBLE_CLICK'
    EVENT_TYPE_ID=EventConstants.MOUSE_DOUBLE_CLICK_EVENT
    IOHUB_DATA_TABLE=MouseEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        MouseButtonEvent.__init__(self, *args, **kwargs)
