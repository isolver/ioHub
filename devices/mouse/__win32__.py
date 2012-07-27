"""
XioHub Windows 32 bit Mouse Class and Event Generator

Part of the XioHub Module
Copyright (C) 2012 Sol Simpson 
Distributed under the terms of the GNU General Public License 
(GPL version 3 or any later version). 

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors,
   please see credits section of documentation.
"""
import ioHub
from .. import Device,Computer
currentMsec=Computer.currentMsec
import pythoncom
import numpy as N


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
        print 'Created MouseWindows32 device.....'

    def eventCallback(self,event):
        notifiedTime=int(currentMsec())
        self.I_eventBuffer.append((notifiedTime,event))
        return True
    
    def poll(self):
        pass
 
    @staticmethod
    def getIOHubEventObject(event,device_instance_code):
        from . import MouseMoveEvent,MouseWheelEvent,MouseButtonDownEvent,MouseButtonUpEvent,MouseDoubleClickEvent
        notifiedTime, event=event
        p = event.Position
        px=p[0]
        py=p[1]
        
        bstate=MouseWindows32.BUTTON_STATE_NONE
        etype=ioHub.EVENT_TYPES['MOUSE_MOVE']
        eclass=MouseMoveEvent
        if event.Message in (MouseWindows32.WM_RBUTTONDOWN,MouseWindows32.WM_MBUTTONDOWN,MouseWindows32.WM_LBUTTONDOWN):
            bstate=MouseWindows32.BUTTON_STATE_PRESSED
            etype=ioHub.EVENT_TYPES['MOUSE_PRESS']
            eclass=MouseButtonDownEvent
        elif event.Message in (MouseWindows32.WM_RBUTTONUP,MouseWindows32.WM_MBUTTONUP,MouseWindows32.WM_LBUTTONUP):     
            bstate=MouseWindows32.BUTTON_STATE_RELEASED
            etype=ioHub.EVENT_TYPES['MOUSE_RELEASE']
            eclass=MouseButtonUpEvent
        elif event.Message in (MouseWindows32.WM_RBUTTONDBLCLK,MouseWindows32.WM_MBUTTONDBLCLK,MouseWindows32.WM_LBUTTONDBLCLK):     
            bstate=MouseWindows32.BUTTON_STATE_DOUBLE_CLICK
            etype=ioHub.EVENT_TYPES['MOUSE_DOUBLE_CLICK']
            eclass=MouseDoubleClickEvent
        elif event.Message == MouseWindows32.WM_MOUSEWHEEL:
            etype=ioHub.EVENT_TYPES['MOUSE_WHEEL']
            eclass=MouseWheelEvent
            
        bnum=MouseWindows32.BUTTON_ID_NONE        
        if event.Message in (MouseWindows32.WM_RBUTTONDOWN,MouseWindows32.WM_RBUTTONUP,MouseWindows32.WM_RBUTTONDBLCLK):
                bnum=MouseWindows32.BUTTON_ID_RIGHT
        elif event.Message in (MouseWindows32.WM_LBUTTONDOWN,MouseWindows32.WM_LBUTTONUP,MouseWindows32.WM_LBUTTONDBLCLK):
                bnum=MouseWindows32.BUTTON_ID_LEFT
        elif event.Message in (MouseWindows32.WM_MBUTTONDOWN,MouseWindows32.WM_MBUTTONUP,MouseWindows32.WM_MBUTTONDBLCLK):
                bnum=MouseWindows32.BUTTON_ID_MIDDLE
        
        return eclass(experiment_id=0,session_id=1,event_id=2,event_type=etype,device_type=ioHub.DEVICE_TYPE_LABEL['MOUSE_DEVICE'],
                                device_instance_code=device_instance_code,device_time=int(event.Time),logged_time=notifiedTime,hub_time=0,
                                confidence_interval=0.0 ,delay=0.0,button_state=bstate,button_id=bnum,
                                x_position=px,y_position=py,wheel=event.Wheel,windowID=event.Window)
