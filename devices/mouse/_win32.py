"""
ioHub
.. file: ioHub/devices/mouse/_win32.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""
import ioHub
from .. import Device,Computer, EventConstants
import ctypes

currentUsec=Computer.currentUsec

class MouseWindows32(object):
    WM_MOUSEMOVE = int(0x0200)
    WM_RBUTTONDOWN = int(0x0204)
    WM_MBUTTONDOWN = int(0x0207)
    WM_LBUTTONDOWN = int(0x0201)
    WM_RBUTTONUP = int(0x0205)
    WM_MBUTTONUP = int(0x0208)
    WM_LBUTTONUP = int(0x0202)
    WM_RBUTTONDBLCLK = int(0x0206)
    WM_MBUTTONDBLCLK = int(0x0209)
    WM_LBUTTONDBLCLK = int(0x0203)
    WM_MOUSEWHEEL = int(0x020A)

    _mouse_event_mapper={
        WM_MOUSEMOVE : [0, EventConstants.MOUSE_MOVE_EVENT, EventConstants.MOUSE_BUTTON_ID_NONE],
        WM_RBUTTONDOWN : [EventConstants.MOUSE_BUTTON_STATE_PRESSED, EventConstants.MOUSE_PRESS_EVENT, EventConstants.MOUSE_BUTTON_ID_RIGHT],
        WM_MBUTTONDOWN : [EventConstants.MOUSE_BUTTON_STATE_PRESSED, EventConstants.MOUSE_PRESS_EVENT, EventConstants.MOUSE_BUTTON_ID_MIDDLE],
        WM_LBUTTONDOWN : [EventConstants.MOUSE_BUTTON_STATE_PRESSED, EventConstants.MOUSE_PRESS_EVENT, EventConstants.MOUSE_BUTTON_ID_LEFT],
        WM_RBUTTONUP : [EventConstants.MOUSE_BUTTON_STATE_RELEASED, EventConstants.MOUSE_RELEASE_EVENT, EventConstants.MOUSE_BUTTON_ID_RIGHT],
        WM_MBUTTONUP : [EventConstants.MOUSE_BUTTON_STATE_RELEASED, EventConstants.MOUSE_RELEASE_EVENT, EventConstants.MOUSE_BUTTON_ID_MIDDLE],
        WM_LBUTTONUP : [EventConstants.MOUSE_BUTTON_STATE_RELEASED, EventConstants.MOUSE_RELEASE_EVENT, EventConstants.MOUSE_BUTTON_ID_LEFT],
        WM_RBUTTONDBLCLK : [EventConstants.MOUSE_BUTTON_STATE_DOUBLE_CLICK, EventConstants.MOUSE_DOUBLE_CLICK_EVENT, EventConstants.MOUSE_BUTTON_ID_RIGHT],
        WM_MBUTTONDBLCLK : [EventConstants.MOUSE_BUTTON_STATE_DOUBLE_CLICK, EventConstants.MOUSE_DOUBLE_CLICK_EVENT, EventConstants.MOUSE_BUTTON_ID_MIDDLE],
        WM_LBUTTONDBLCLK : [EventConstants.MOUSE_BUTTON_STATE_DOUBLE_CLICK, EventConstants.MOUSE_DOUBLE_CLICK_EVENT, EventConstants.MOUSE_BUTTON_ID_LEFT],
        WM_MOUSEWHEEL : [0, EventConstants.MOUSE_WHEEL_DOWN_EVENT, EventConstants.MOUSE_BUTTON_ID_NONE]
    }


    def __init__(self, *args,**kwargs):
        self._lastCallbackTime=None

        self._scrollPositionY=0
        self._position=0,0
        self._lastPosition=0,0
        self._isVisible=0
        self.activeButtons={
                            EventConstants.MOUSE_BUTTON_ID_LEFT:0,
                            EventConstants.MOUSE_BUTTON_ID_RIGHT:0,
                            EventConstants.MOUSE_BUTTON_ID_MIDDLE:0,
                            }
        self._user32=ctypes.windll.user32

        self.getSystemCursorVisibility()
        
        self._display = ioHub.devices.Display


    def getPosition(self):
        """
        Returns the current position of the ioHub Mouse Device. Mouse Position is in display
        coordinate units, with 0,0 being the center of the screen.

        Args: None
        Return (tuple): (x,y) position of mouse in Display coordinate space.
        """
        if self._display is None:
            self._display = ioHub.devices.Display
        return tuple(self._position)

    def setPosition(self,pos, updateSystemMousePosition=True):
        """
        Sets the current position of the ioHub Mouse Device. Mouse position ( pos ) should be specified in
        Display coordinate units, with 0,0 being the center of the screen. If you would like the OS system
        mouse position to also be updated, set updateSystemMousePosition to True (the default). Otherwise,
        set it to False. When the system mouse position is updated, your position ( pos ) is converted
        to the associated screen pixel position expected by the OS.

        Args:
             pos: The position, in Display coordinate space, to set the mouse position too.
             updateSystemMousePosition: True = the OS mouse position will also be updated,
                                        False = it will not.
        Return (tuple): new (x,y) position of mouse in Display coordinate space.
        """
        if isinstance(pos[0], (int, long, float, complex)) and isinstance(pos[1], (int, long, float, complex)):
            if self._display is None:
                self._display = ioHub.devices.Display
            self._lastPosition=self._position
            self._position=pos[0],pos[1]
            if updateSystemMousePosition is True:
                pixLocation=self._display.displayCoord2Pixel(pos[0],pos[1])
                #ioHub.print2stderr('pixLocation:'+str(pixLocation))
                #  >> WIN32_ONLY
                self._user32.SetCursorPos(*pixLocation)
                #  << WIN32_ONLY
        return self._position

    def getPositionAndDelta(self):
        """
        Returns a tuple of tuples, being the current position of the ioHub Mouse Device as an (x,y) tuple,
        and the amount the mouse position changed the last time it was updated (dx,dy).
        Mouse Position and Delta are in display coordinate units.

        Args: None
        Return (tuple): ( (x,y), (dx,dy) ) position of mouse, change in mouse position,
                                           both in Display coordinate space.
        """
        try:
            cpos=self._position
            lpos=self._lastPosition
            change_x=cpos[0]-lpos[0]
            change_y=cpos[1]-lpos[1]
            if change_x or change_y:
                return cpos, (change_x,change_y)
            return cpos, None
        except Exception, e:
            ioHub.print2err(">>ERROR getPositionAndDelta: "+str(e))
            ioHub.printExceptionDetailsToStdErr()
            return (0.0,0.0),(0.0,0.0)

    def getVerticalScroll(self):
        """
        Returns the current vertical scroll value for the mouse. The vertical scroll value changes when the
        scroll wheel on a mouse is moved up or down. The vertical scroll value is in an arbitrary value space
        ranging for -32648 to +32648. Scroll position is initialize to 0 when the experiment starts.
        Args: None
        Returns (int): current vertical scroll value.
        """
        return self._scrollPositionY

    def setVerticalScroll(self,s):
        """
        Sets the current vertical scroll value for the mouse. The vertical scroll value changes when the
        scroll wheel on a mouse is moved up or down. The vertical scroll value is in an
        arbitrary value space ranging for -32648 to +32648. Scroll position is initialize to 0 when
        the experiment starts. This method allows you to change the scroll value to anywhere in the
        valid value range.
        Args (int): The scroll position you want to set the vertical scroll to. Should be a number
                    between -32648 to +32648.
        Returns (int): current vertical scroll value.
        """
        if isinstance(s, (int, long, float, complex)):
            self._scrollPositionY=s
        return self._scrollPositionY
                
    def getSystemCursorVisibility(self):
        """
        Returns whether the system cursor is visible on the currently active Window.
        Args: None
        Returns (bool): True if system cursor is visible on currently active Window. False otherwise.
        """
        #  >> WIN32_ONLY
        v=self._user32.ShowCursor(False)    
        self._isVisible = self._user32.ShowCursor(True)
        #  << WIN32_ONLY
        return self._isVisible >= 0
 
    def setSystemCursorVisibility(self,v):
        """
        Set whether the system cursor is visible on the currently active Window.
        Args:
            v (bool): True = make system cursor visible. False = Hide system cursor
        Returns (bool): True if system cursor is visible on currently active Window. False otherwise.

        """
        #  >> WIN32_ONLY
        self._isVisible=self._user32.ShowCursor(v)
        #  << WIN32_ONLY
        return self._isVisible >= 0
            
    def _nativeEventCallback(self,event):
        logged_time=int(currentUsec())

        self._scrollPositionY+= event.Wheel
        event.WheelAbsolute=self._scrollPositionY

        p=ioHub.devices.Display.pixel2DisplayCoord(event.Position[0],event.Position[1])
        self.setPosition(p,updateSystemMousePosition=False)
        event.Position=p

        bstate,etype,bnum=MouseWindows32._mouse_event_mapper[event.Message]
        if bnum is not EventConstants.MOUSE_BUTTON_ID_NONE:
            self.activeButtons[bnum]= int(bstate==EventConstants.MOUSE_BUTTON_STATE_PRESSED)

        abuttonSum=0
        for k,v in self.activeButtons.iteritems():
            abuttonSum+=k*v

        event.ActiveButtons=abuttonSum

        self._nativeEventBuffer.append((logged_time,event))

        self._lastCallbackTime=logged_time

        return True
    
    def _poll(self):
        pass
 
    @staticmethod
    def _getIOHubEventObject(event,device_instance_code):
        logged_time, event=event
        p = event.Position
        px=p[0]
        py=p[1]

        bstate,etype,bnum=MouseWindows32._mouse_event_mapper[event.Message]

        if event.Message == MouseWindows32.WM_MOUSEWHEEL:
            if event.Wheel > 0:
                etype=EventConstants.MOUSE_WHEEL_UP_EVENT

        confidence_interval=0.0
        delay=0.0

        # From MSDN: http://msdn.microsoft.com/en-us/library/windows/desktop/ms644939(v=vs.85).aspx
        # The time is a long integer that specifies the elapsed time, in milliseconds, from the time the system was started to the time the message was 
        # created (that is, placed in the thread's message queue).REMARKS: The return value from the GetMessageTime function does not necessarily increase
        # between subsequent messages, because the value wraps to zero if the timer count exceeds the maximum value for a long integer. To calculate time
        # delays between messages, verify that the time of the second message is greater than the time of the first message; then, subtract the time of the
        # first message from the time of the second message.
        device_time = int(event.Time)*1000 # convert to usec
        
        hubTime = logged_time #TODO correct mouse times to factor in offset.

        r= [0,0,Computer.getNextEventID(),etype,device_instance_code,device_time,logged_time,hubTime,
                    confidence_interval, delay, bstate, bnum,event.ActiveButtons, px, py,event.Wheel,event.WheelAbsolute, event.Window]
            
        return r