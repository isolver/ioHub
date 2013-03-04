"""
ioHub
.. file: ioHub/devices/mouse/_linux.py

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>

"""
import ioHub
from .. import Computer
from ioHub.constants import EventConstants, MouseConstants
import ctypes

currentSec=Computer.currentSec

class MouseLinux(object):
#    _mouse_event_mapper={
#        WM_MOUSEMOVE : [0, EventConstants.MOUSE_MOVE, MouseConstants.MOUSE_BUTTON_NONE],
#        WM_RBUTTONDOWN : [MouseConstants.MOUSE_BUTTON_STATE_PRESSED, EventConstants.MOUSE_PRESS, MouseConstants.MOUSE_BUTTON_RIGHT],
#        WM_MBUTTONDOWN : [MouseConstants.MOUSE_BUTTON_STATE_PRESSED, EventConstants.MOUSE_PRESS, MouseConstants.MOUSE_BUTTON_MIDDLE],
#        WM_LBUTTONDOWN : [MouseConstants.MOUSE_BUTTON_STATE_PRESSED, EventConstants.MOUSE_PRESS, MouseConstants.MOUSE_BUTTON_LEFT],
#        WM_RBUTTONUP : [MouseConstants.MOUSE_BUTTON_STATE_RELEASED, EventConstants.MOUSE_RELEASE, MouseConstants.MOUSE_BUTTON_RIGHT],
#        WM_MBUTTONUP : [MouseConstants.MOUSE_BUTTON_STATE_RELEASED, EventConstants.MOUSE_RELEASE, MouseConstants.MOUSE_BUTTON_MIDDLE],
#        WM_LBUTTONUP : [MouseConstants.MOUSE_BUTTON_STATE_RELEASED, EventConstants.MOUSE_RELEASE, MouseConstants.MOUSE_BUTTON_LEFT],
#        WM_RBUTTONDBLCLK : [MouseConstants.MOUSE_BUTTON_STATE_DOUBLE_CLICK, EventConstants.MOUSE_DOUBLE_CLICK, MouseConstants.MOUSE_BUTTON_RIGHT],
#        WM_MBUTTONDBLCLK : [MouseConstants.MOUSE_BUTTON_STATE_DOUBLE_CLICK, EventConstants.MOUSE_DOUBLE_CLICK, MouseConstants.MOUSE_BUTTON_MIDDLE],
#        WM_LBUTTONDBLCLK : [MouseConstants.MOUSE_BUTTON_STATE_DOUBLE_CLICK, EventConstants.MOUSE_DOUBLE_CLICK, MouseConstants.MOUSE_BUTTON_LEFT],
#        WM_MOUSEWHEEL : [0, EventConstants.MOUSE_WHEEL_DOWN, MouseConstants.MOUSE_BUTTON_NONE]
#    }


    def __init__(self, *args,**kwargs):
        self._lastCallbackTime=None

        self._scrollPositionY=0
        self._position=0,0
        self._lastPosition=0,0
        self._isVisible=0
        self.activeButtons={
            MouseConstants.MOUSE_BUTTON_LEFT:0,
            MouseConstants.MOUSE_BUTTON_RIGHT:0,
            MouseConstants.MOUSE_BUTTON_MIDDLE:0,
                            }
        
        #self.getSystemCursorVisibility()
        
        self._display = ioHub.devices.Display

    def getCurrentButtonStates(self):
        return (self.activeButtons[MouseConstants.MOUSE_BUTTON_LEFT]!=0,
                self.activeButtons[MouseConstants.MOUSE_BUTTON_MIDDLE]!=0,
                self.activeButtons[MouseConstants.MOUSE_BUTTON_RIGHT]!=0)
                
    def getPosition(self):
        """
        Returns the current position of the ioHub Mouse Device. Mouse Position is in display
        coordinate units, with 0,0 being the center of the screen.

        Args: None
        Return (tuple): (x,y) position of mouse in Display coordinate space.
        """
#        if self._display is None:
#            self._display = ioHub.devices.Display
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
            #if updateSystemMousePosition is True:
            #    pixLocation=self._display.displayCoord2Pixel(pos[0],pos[1])
                #ioHub.print2stderr('pixLocation:'+str(pixLocation))
                #  >> WIN32_ONLY
                #self._user32.SetCursorPos(*pixLocation)
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
        #v=self._user32.ShowCursor(False)    
        #self._isVisible = self._user32.ShowCursor(True)
        #  << WIN32_ONLY
        ioHub.print2err("Mouse.getSystemCursorVisibility is not currently supported on Linux.")
        return False#self._isVisible >= 0
 
    def setSystemCursorVisibility(self,v):
        """
        Set whether the system cursor is visible on the currently active Window.
        Args:
            v (bool): True = make system cursor visible. False = Hide system cursor
        Returns (bool): True if system cursor is visible on currently active Window. False otherwise.

        """
        #  >> WIN32_ONLY
        #self._isVisible=self._user32.ShowCursor(v)
        #  << WIN32_ONLY
        ioHub.print2err("Mouse.setSystemCursorVisibility is not currently supported on Linux.")
        return False#self._isVisible >= 0
            
    def _nativeEventCallback(self,event):
        if self.isReportingEvents():
            logged_time=currentSec()

            self._scrollPositionY+= event.Wheel
            event.WheelAbsolute=self._scrollPositionY

            p=ioHub.devices.Display.pixel2DisplayCoord(event.Position[0],event.Position[1])
            self.setPosition(p,updateSystemMousePosition=False)
            event.Position=p

            if event.ioHubButtonID is not MouseConstants.MOUSE_BUTTON_NONE:
                self.activeButtons[event.ioHubButtonID]= int(event.ioHubButtonState==MouseConstants.MOUSE_BUTTON_STATE_PRESSED)

            abuttonSum=0
            for k,v in self.activeButtons.iteritems():
                abuttonSum+=k*v

            event.ActiveButtons=abuttonSum

            self._addNativeEventToBuffer((logged_time,event))

            self._lastCallbackTime=logged_time

        return True
    
    def _poll(self):
        pass
 

    def _getIOHubEventObject(self,native_event):
        logged_time, event=native_event
        #import ioHub
        #ioHub.print2err("Mouse event start....")
        px,py = event.Position

        confidence_interval=0.0
        delay=0.0
        hubTime = logged_time #TODO correct mouse times to factor in offset.

        r= [0,
            0,
            Computer._getNextEventID(),
            event.ioHubEventID,
            event.Time,
            logged_time,
            hubTime,
            confidence_interval, 
            delay,
            0, # filtered by ID (always 0 right now) 
            event.ioHubButtonState, 
            event.ioHubButtonID,
            event.ActiveButtons, 
            px, 
            py,
            event.Wheel,
            event.WheelAbsolute, 
            event.Window]
             
        #ioHub.print2err("Mouse event built.\n-----------------")
        
        return r