"""
ioHub
.. file: ioHub/devices/mouse/_win32.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""
import ioHub
from .. import Device,Computer
currentUsec=Computer.currentUsec
import numpy as N
import ctypes

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
    
    BUTTON_STATE_NONE=0  # No Button activity for event (mouse move or wheel scrool only)
    BUTTON_STATE_PRESSED=1 # at least one button is pressed
    BUTTON_STATE_RELEASED=2 # a button was released
    BUTTON_STATE_DOUBLE_CLICK=3 # a button double click event
    
    BUTTON_ID_NONE=0
    BUTTON_ID_LEFT=1
    BUTTON_ID_RIGHT=2
    BUTTON_ID_MIDDLE=3
    
    def __init__(self, *args,**kwargs):
        self._lastCallbackTime=None

        self._scrollPositionX=0
        self._position=0,0
        self._lastPosition=0,0
        self._isVisible=0
        self._user32=ctypes.windll.user32
        self.getSysCursorVisibility()
        
        self._display = ioHub.devices.Display


    def getPosition(self):
        if self._display is None:
            self._display = ioHub.devices.Display
        return tuple(self._position)

    def setPosition(self,p, updateSystemMousePosition=True):
        if isinstance(p[0], (int, long, float, complex)) and isinstance(p[1], (int, long, float, complex)):
            if self._display is None:
                self._display = ioHub.devices.Display
            self._lastPosition=self._position
            self._position=p[0],p[1]
            if updateSystemMousePosition is True:
                pixLocation=self._display.displayCoord2Pixel(p[0],p[1])
                #ioHub.print2stderr('pixLocation:'+str(pixLocation))
                self._user32.SetCursorPos(*pixLocation)
        return self._position

    def getPositionAndChange(self):
        try:
            cpos=self._position
            lpos=self._lastPosition
            change_x=cpos[0]-lpos[0]
            change_y=cpos[1]-lpos[1]
            if change_x or change_y:
                return cpos, (change_x,change_y)
            return cpos, None
        except Exception, e:
            ioHub.print2stderr(">>ERROR getPositionAndChange: "+str(e))
            ioHub.printExceptionDetailsToStdErr()
            return (0.0,0.0),(0.0,0.0)

    def getVerticalScroll(self):
        return self._scrollPositionX
     
    def setVerticalScroll(self,s):
        if isinstance(s, (int, long, float, complex)):
            self._scrollPositionX=s
        return self._scrollPositionX
                
    def getSysCursorVisibility(self):
        v=self._user32.ShowCursor(False)    
        self._isVisible = self._user32.ShowCursor(True)
        return self._isVisible >= 0
 
    def setSysCursorVisibility(self,v):
        self._isVisible=self._user32.ShowCursor(v)
        return self._isVisible >= 0,self._isVisible
            
    def _nativeEventCallback(self,event):
        ctime=int(currentUsec())

        ci=0.0
        if self._lastCallbackTime:
            ci=ctime-self._lastCallbackTime
        #event.ConfidenceInterval=ci
        self._lastCallbackTime=ctime
        
        notifiedTime=int(ctime)

        self._scrollPositionX+= event.Wheel
        p=ioHub.devices.Display.pixel2DisplayCoord(event.Position[0],event.Position[1])
        self.setPosition(p,updateSystemMousePosition=False)
        #ioHub.print2stderr(str(event.Position)+" = px : coord = "+str(self._positionXY))
        event.Position=p
        self.I_nativeEventBuffer.append((notifiedTime,event))
        return True
    
    def _poll(self):
        pass
 
    @staticmethod
    def _getIOHubEventObject(event,device_instance_code):
        from . import MouseMoveEvent,MouseWheelEvent,MouseButtonDownEvent,MouseButtonUpEvent,MouseDoubleClickEvent
        notifiedTime, event=event
        p = event.Position
        px=p[0]
        py=p[1]

        bstate=MouseWindows32.BUTTON_STATE_NONE
        etype=ioHub.EVENT_TYPES['MOUSE_MOVE']
        if event.Message in (MouseWindows32.WM_RBUTTONDOWN,MouseWindows32.WM_MBUTTONDOWN,MouseWindows32.WM_LBUTTONDOWN):
            bstate=MouseWindows32.BUTTON_STATE_PRESSED
            etype=ioHub.EVENT_TYPES['MOUSE_PRESS']
        elif event.Message in (MouseWindows32.WM_RBUTTONUP,MouseWindows32.WM_MBUTTONUP,MouseWindows32.WM_LBUTTONUP):     
            bstate=MouseWindows32.BUTTON_STATE_RELEASED
            etype=ioHub.EVENT_TYPES['MOUSE_RELEASE']
        elif event.Message in (MouseWindows32.WM_RBUTTONDBLCLK,MouseWindows32.WM_MBUTTONDBLCLK,MouseWindows32.WM_LBUTTONDBLCLK):     
            bstate=MouseWindows32.BUTTON_STATE_DOUBLE_CLICK
            etype=ioHub.EVENT_TYPES['MOUSE_DOUBLE_CLICK']
        elif event.Message == MouseWindows32.WM_MOUSEWHEEL:
            etype=ioHub.EVENT_TYPES['MOUSE_WHEEL']
            
        bnum=MouseWindows32.BUTTON_ID_NONE        
        if event.Message in (MouseWindows32.WM_RBUTTONDOWN,MouseWindows32.WM_RBUTTONUP,MouseWindows32.WM_RBUTTONDBLCLK):
                bnum=MouseWindows32.BUTTON_ID_RIGHT
        elif event.Message in (MouseWindows32.WM_LBUTTONDOWN,MouseWindows32.WM_LBUTTONUP,MouseWindows32.WM_LBUTTONDBLCLK):
                bnum=MouseWindows32.BUTTON_ID_LEFT
        elif event.Message in (MouseWindows32.WM_MBUTTONDOWN,MouseWindows32.WM_MBUTTONUP,MouseWindows32.WM_MBUTTONDBLCLK):
                bnum=MouseWindows32.BUTTON_ID_MIDDLE
        
        confidence_interval=0.0
        delay=0.0

        # From MSDN: http://msdn.microsoft.com/en-us/library/windows/desktop/ms644939(v=vs.85).aspx
        # The time is a long integer that specifies the elapsed time, in milliseconds, from the time the system was started to the time the message was 
        # created (that is, placed in the thread's message queue).REMARKS: The return value from the GetMessageTime function does not necessarily increase
        # between subsequent messages, because the value wraps to zero if the timer count exceeds the maximum value for a long integer. To calculate time
        # delays between messages, verify that the time of the second message is greater than the time of the first message; then, subtract the time of the
        # first message from the time of the second message.
        device_time = int(event.Time)*1000 # convert to usec
        
        hubTime = notifiedTime #TODO correct mouse times to factor in offset.
        
        r= [0,0,Computer.getNextEventID(),etype,device_instance_code,device_time,notifiedTime,hubTime,
                    confidence_interval, delay, bstate, bnum, px, py, event.Wheel, event.Window]
            
        return r