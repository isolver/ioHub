"""
ioHub Python Module

Copyright (C) 2012 Sol Simpson 
Distributed under the terms of the GNU General Public License 
(GPL version 3 or any later version). 

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors,
   please see credits section of documentation.
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
        self._devicePosition=0,0
        self._lastDevicePosition=0,0
        self._displayPosition=0,0
        self._lastDisplayPosition=0,0
        
        self._isVisible=0
        self._user32=ctypes.windll.user32
        self.getVisibility()
        
        display = ioHub.devices.Display
        h,v=display.getScreenResolution()
        self.setDevicePosition((h/2,v/2))

    def getDevicePosition(self):
        return tuple(self._devicePosition)

    def setDevicePosition(self,p):
        if isinstance(p[0], (int, long, float, complex)) and isinstance(p[1], (int, long, float, complex)):
            self._lastDevicePosition=self._devicePosition
            self._devicePosition=p[0],p[1]
            self._user32.SetCursorPos(p[0],p[1])
        return self._devicePosition

    def getDisplayPositionAndChange(self):
        dvp=self._devicePosition
        ldvp=self._lastDevicePosition
        change_x=dvp[0]-ldvp[0]
        change_y=dvp[1]-ldvp[1]
        dsp=ioHub.devices.Display.pixel2DisplayCoord(self._devicePosition[0],self._devicePosition[1])
        self._displayPosition=dsp
        if change_x or change_y:
            self._lastDevicePosition=self._devicePosition
            self._displayPosition=dsp
            ldsp=self._lastDisplayPosition
            self._lastDisplayPosition=self._displayPosition
            dchange_x=dsp[0]-ldsp[0]
            dchange_y=dsp[1]-ldsp[1]            
            return dsp, (dchange_x,dchange_y), (change_x,change_y)
        return dsp, None, None

    def setDisplayPosition(self,p):
        #if isinstance(p[0], (int, long, float, complex)) and isinstance(p[1], (int, long, float, complex)):
        #    self._positionXY=p[0],p[1]
        #    self._user32.SetCursorPos(p[0],p[1])
        ioHub.print2stderr('Mouse.setDisplayPosition not yet implemented. Use Mouse.setDevicePosition')
        return self._displayPosition
        
    def getVerticalScroll(self):
        return self._scrollPositionX
     
    def setVerticalScroll(self,s):
        if isinstance(s, (int, long, float, complex)):
            self._scrollPositionX=s
        return self.scrollPositionX
                
    def getVisibility(self):
        v=self._user32.ShowCursor(False)    
        self._isVisible = self._user32.ShowCursor(True)
        return self._isVisible >= 0
 
    def setVisibility(self,v):
        self._isVisible=self._user32.ShowCursor(v)
        return self._isVisible >= 0
            
    def _nativeEventCallback(self,event):
        ctime=int(currentUsec())

        ci=0.0
        if self._lastCallbackTime:
            ci=ctime-self._lastCallbackTime
        #event.ConfidenceInterval=ci
        self._lastCallbackTime=ctime
        
        notifiedTime=int(ctime)

        self._scrollPositionX+= event.Wheel
        self._devicePosition = event.Position[0],event.Position[1]
        #ioHub.print2stderr(str(event.Position)+" = px : coord = "+str(self._positionXY))
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