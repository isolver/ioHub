# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 18:52:59 2013

@author: isolver
"""

from ctypes import cdll
from . import MouseDevice
from ... import print2err
from .. import Computer

currentSec=Computer.getTime

class Mouse(MouseDevice):
    """
    The Mouse class and related events represent a standard computer mouse device
    and the events a standard mouse can produce. Mouse position data is mapped to
    the coordinate space defined in the ioHub configuration file for the Display.
    """
    
    _xdll=None
    _xfixsdll=None
    _xdisplay=None
    _xscreen_count=None

    __slots__=['_cursorVisible']
    def __init__(self,*args,**kwargs):          
        MouseDevice.__init__(self,*args,**kwargs['dconfig'])      

        self._cursorVisible=True
        
        if Mouse._xdll is None:
            Mouse._xdll = cdll.LoadLibrary('libX11.so') 
            Mouse._xdisplay = self._xdll.XOpenDisplay(None) 
            Mouse._xscreen_count = self._xdll.XScreenCount(self._xdisplay)  
            try:
                Mouse._xfixsdll=cdll.LoadLibrary('libXfixes.so')
            except:
                Mouse._xfixsdll=None
                
        if self._display_device and self._display_device._xwindow is None:
            self._display_device._xwindow= self._xdll.XRootWindow(Mouse._xdisplay, self._display_device.getIndex())

    def _nativeSetMousePos(self,px,py):
        Mouse._xdll.XWarpPointer(Mouse._xdisplay,None,self._display_device._xwindow,0,0,0,0,int(px),int(py)) 
        Mouse._xdll.XFlush(Mouse._xdisplay);   
         
    def _nativeGetSystemCursorVisibility(self):
        return self._cursorVisible
        
    def _nativeSetSystemCursorVisibility(self,v):
        if Mouse._xfixsdll is None:
            print2err("Xfixes DLL could not be loaded. Cursor visiblity support is unavailable.")
            return True
            
        if v is True and self._nativeGetSystemCursorVisibility() is False:
            Mouse._xfixsdll.XFixesShowCursor(Mouse._xdisplay,self._display_device._xwindow)
            Mouse._xfixsdll.XFlush(Mouse._xdisplay)   
            self._cursorVisible=True
        elif v is False and self._nativeGetSystemCursorVisibility() is True:
            Mouse._xfixsdll.XFixesHideCursor(Mouse._xdisplay,self._display_device._xwindow)
            Mouse._xfixsdll.XFlush(Mouse._xdisplay)   
            self._cursorVisible=False
            
        return self._nativeGetSystemCursorVisibility()
          
    def _nativeLimitCursorToBoundingRect(self,clip_rect):
        print2err('WARNING: Mouse._nativeLimitCursorToBoundingRect not implemented on Linux yet.')
        native_clip_rect=None
        return native_clip_rect

                     
    def _nativeEventCallback(self,event):
        try:
           if self.isReportingEvents():
                logged_time=currentSec()
                
                event_array=event[0]
                event_array[3]=Computer._getNextEventID()
                
                display_index=self._display_device.getIndex()                
                x,y=self._display_device._pixel2DisplayCoord(event_array[15],event_array[16],display_index)  
                event_array[15]=x
                event_array[16]=y
                
                self._lastPosition=self._position
                self._position=x,y

                self._last_display_index=self._display_index
                self._display_index=display_index
                
                self._addNativeEventToBuffer(event_array)
                
                self._last_callback_time=logged_time
        except:
            printExceptionDetailsToStdErr()
        
        # Must return original event or no mouse events will get to OSX!
        return 1
            
    def _getIOHubEventObject(self,native_event_data):
        return native_event_data

    def _close(self):
        if Mouse._xdll:
            if Mouse._xfixsdll and self._nativeGetSystemCursorVisibility() is False:
                Mouse._xfixsdll.XFixesShowCursor(Mouse._xdisplay,self._display_device._xwindow)   
            Mouse._xdll.XCloseDisplay(Mouse._xdisplay)
            Mouse._xdll=None
            Mouse._xfixsdll=None
            Mouse._xdisplay=None
            Mouse._xscreen_count=None
            
            try:
                self._display_device._xwindow=None
            except:
                pass
