# -*- coding: utf-8 -*-
"""
ioHub
.. file: ioHub/devices/mouse/__init__.py

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""
from ioHub.devices import Computer, Device
import ioHub
from ioHub.constants import EventConstants, DeviceConstants, MouseConstants
import numpy as N

currentSec=Computer.currentSec

# OS ' independent' view of the Mouse Device


class MouseDevice(Device):
    """
    The Mouse class represents a standard USB or PS2 mouse device that has up to 
    three buttons and an optional scroll wheel (1D on Windows and Linux, 2D on OSX). Mouse position data is 
    mapped to the coordinate space defined in the ioHub configuration file for the Display.
    """
    EVENT_CLASS_NAMES=['MouseInputEvent','MouseButtonEvent','MouseScrollEvent',
                       'MouseMoveEvent', 'MouseDragEvent','MouseButtonPressEvent','MouseButtonReleaseEvent',
                       'MouseMultiClickEvent']
                       
    DEVICE_TYPE_ID=DeviceConstants.MOUSE
    DEVICE_TYPE_STRING='MOUSE'

    __slots__=['_lock_mouse_to_display_id','_scrollPositionY','_position','_clipRectsForDisplayID',
               '_lastPosition','_display_index','_last_display_index','_isVisible','activeButtons'
               ]
    def __init__(self,*args,**kwargs):     
        Device.__init__(self,*args,**kwargs)
        self._clipRectsForDisplayID={}
        self._lock_mouse_to_display_id=None
        self._scrollPositionY=0
        self._position=0,0
        self._lastPosition=0,0
        self._isVisible=0
        self._display_index=None
        self._last_display_index=None
        self.activeButtons={
            MouseConstants.MOUSE_BUTTON_LEFT:0,
            MouseConstants.MOUSE_BUTTON_RIGHT:0,
            MouseConstants.MOUSE_BUTTON_MIDDLE:0,
                            }
        
    def getSystemCursorVisibility(self):
        """
        Returns whether the system cursor is visible on the currently active Window.
        
        Args: 
            None
            
        Returns: 
            bool: True if system cursor is visible on currently active Window. False otherwise.
        """
        return self._nativeGetSystemCursorVisibility()
 
    def setSystemCursorVisibility(self,v):
        """
        Set whether the system cursor is visible on the currently active Window.
        
        Args:
            v (bool): True = make system cursor visible. False = Hide system cursor
        
        Returns:
            (bool): True if system cursor is visible on currently active Window. False otherwise.

        """
        self._nativeSetSystemCursorVisibility(v)
        return self.getSystemCursorVisibility()

    def getCurrentButtonStates(self):
        return (self.activeButtons[MouseConstants.MOUSE_BUTTON_LEFT]!=0,
                self.activeButtons[MouseConstants.MOUSE_BUTTON_MIDDLE]!=0,
                self.activeButtons[MouseConstants.MOUSE_BUTTON_RIGHT]!=0)
                

    def lockMouseToDisplayID(self,display_id):
        self._lock_mouse_to_display_id=display_id    
        if display_id is not None:
            if display_id not in self._clipRectsForDisplayID:
                screen=self._display_device.getConfiguration()['runtime_info']              
                if screen:
                    left,top,right,bottom=screen['bounds']
                    clip_rect=ioHub.RectangleBorder(left,top,right,bottom)
                    native_clip_rect=self._nativeLimitCursorToBoundingRect(clip_rect)
                self._clipRectsForDisplayID[display_id]=native_clip_rect,clip_rect
        else:
            if None not in self._clipRectsForDisplayID:
                left,top,right,bottom=screen['bounds']
                clip_rect=ioHub.RectangleBorder(left,top,right,bottom)
                native_clip_rect=self._nativeLimitCursorToBoundingRect(clip_rect)
                self._clipRectsForDisplayID[display_id]=native_clip_rect,clip_rect
        return self._clipRectsForDisplayID[display_id][1]

    def getlockedMouseDisplayID(self):
        return self._lock_mouse_to_display_id   

    def getPosition(self,return_display_index=False):
        """
        Returns the current position of the ioHub Mouse Device. Mouse Position is in display
        coordinate units, with 0,0 being the center of the screen.

        Args: 
            return_display_index: if True, the display index that is associated with the mouse position will also be returned.
        Returns:
            tuple: If return_display_index is false (default), return (x,y) position of mouse. If return_display_index is True return ( (x,y), display_index). 
        """
        if return_display_index is True:        
            return (tuple(self._position), self._display_index)       
        return tuple(self._position)

    def getDisplayIndex(self):
        """
        Returns the current display index of the ioHub Mouse Device. 
        If the display index == the index of the display being used for stimulus
        presentation, then mouse position is in the display's coordinate units.
        If the display index != the index of the display being used for stimulus
        presentation, then mouse position is in OS system mouse ccordinate space.

        Args:
            None
        Returns:
            (int): index of the Display the mouse is over. Display index's range from 0 to N-1, where N is the number of Display's active on the Computer.
        """
        return self._display_index
        
    def getPositionAndDelta(self,return_display_index=False):
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
            if return_display_index is True:        
                return (cpos, (change_x,change_y), self._display_index)       
            return cpos, (change_x,change_y)

        except Exception, e:
            ioHub.print2err(">>ERROR getPositionAndDelta: "+str(e))
            ioHub.printExceptionDetailsToStdErr()
            if return_display_index is True:        
                return ((0.0,0.0),(0.0,0.0), self._display_index)       
            return (0.0,0.0),(0.0,0.0)

    def getScroll(self):
        """
        Returns the current vertical scroll value for the mouse. The vertical scroll value changes when the
        scroll wheel on a mouse is moved up or down. The vertical scroll value is in an arbitrary value space
        ranging for -32648 to +32648. Scroll position is initialize to 0 when the experiment starts.
        Args: None
        Returns (int): current vertical scroll value.
        """
        return self._scrollPositionY

    def setScroll(self,s):
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

    def setPosition(self,pos,display_index=None):
        """
        Sets the current position of the ioHub Mouse Device. Mouse position ( pos ) should be specified in
        Display coordinate units, with 0,0 being the center of the screen. If you would like the OS system
        mouse position to also be updated, set updateSystemMousePosition to True (the default). Otherwise,
        set it to False. When the system mouse position is updated, your position ( pos ) is converted
        to the associated screen pixel position expected by the OS.

        Args:
             pos ( (x,y) list or tuple ): The position, in Display coordinate space, to set the mouse position too.
             
             updateSystemMousePosition (bool): True = the OS mouse position will also be updated, False = it will not.
        
        Return:
            tuple: new (x,y) position of mouse in Display coordinate space.
        """
        if isinstance(pos[0], (int, long, float, complex)) and isinstance(pos[1], (int, long, float, complex)):
            display=self._display_device
            current_display_index=display.getIndex()

            if display_index is None:
                display_index=current_display_index

            if display_index==-1:
                ioHub.print2err(" !!! Display Index -1 received by mouse.setPosition. !!!")
                ioHub.print2err(" mouse.setPos did not update mouse pos")
                return self._position
                
            px,py=display.displayCoord2Pixel(pos[0],pos[1],display_index)

            result=self._validateMousePosition((px,py),display_index)
            
            if result !=True:
                px,py=result
            
            mouse_display_index=self.getDisplayIndexForMousePosition((px,py))
            
            if mouse_display_index == -1:
                ioHub.print2err(" !!! getDisplayIndexForMousePosition returned -1 in mouse.setPosition. !!!")
                ioHub.print2err(" mouse.setPos did not update mouse pos")
            elif mouse_display_index!=display_index:
                ioHub.print2err(" !!! requested display_index {0} != mouse_pos_index {1}".format(
                                display_index,mouse_display_index))
                ioHub.print2err(" mouse.setPos did not update mouse pos")
            else:                    
                self._lastPosition=self._position
                self._position=px,py

                self._last_display_index=self._display_index
                self._display_index=mouse_display_index
            
                self._nativeSetMousePos(px,py)     
                
        return self._position
            
    def getDisplayIndexForMousePosition(self,system_mouse_pos):
        return self._display_device.getDisplayIndexForNativePixelPosition(system_mouse_pos)

    def _validateMousePosition(self, pixel_pos,display_index):
        left,top,right,bottom=self._display_device.getRuntimeInfoByIndex(display_index)['bounds']
        mx,my=pixel_pos
        mousePositionNeedsUpdate=False
        
        if mx < left:
            mx=left
            mousePositionNeedsUpdate=True
        elif mx >= right:
            mx=right-1
            mousePositionNeedsUpdate=True
            
        if my < top:
            my=top
            mousePositionNeedsUpdate=True
        elif my >= bottom:
            my=bottom-1
            mousePositionNeedsUpdate=True
        
        if mousePositionNeedsUpdate: 
            return mx,my
        
        return True

    def _nativeSetMousePos(self,px,py):
        ioHub.print2err("ERROR: _nativeSetMousePos must be overwritten by OS dependent implementation")

    def _nativeGetSystemCursorVisibility(self):
        ioHub.print2err("ERROR: _nativeGetSystemCursorVisibility must be overwritten by OS dependent implementation")
        return True
        
    def _nativeSetSystemCursorVisibility(self,v):
        ioHub.print2err("ERROR: _nativeSetSystemCursorVisibility must be overwritten by OS dependent implementation")
        return True

    def _nativeLimitCursorToBoundingRect(self,clip_rect):
        ioHub.print2err("ERROR: _nativeLimitCursorToBoundingRect must be overwritten by OS dependent implementation")
        native_clip_rect=None
        return native_clip_rect
        
if Computer.system == 'win32':
    import ctypes
    
    class RECT(ctypes.Structure):
        _fields_ = [ ('left',ctypes.c_long),
                    ('top',ctypes.c_long),
                    ('right',ctypes.c_long),
                    ('bottom',ctypes.c_long)]

    class POINT(ctypes.Structure):
        _fields_ = [ ('x',ctypes.c_long),
                    ('y',ctypes.c_long)]
    
    class Mouse(MouseDevice):
        """
        The Mouse class and related events represent a standard computer mouse device
        and the events a standard mouse can produce. Mouse position data is mapped to
        the coordinate space defined in the ioHub configuration file for the Display.
        """
        WM_MOUSEFIRST = 0x0200
        WM_MOUSEMOVE = 0x0200
        WM_LBUTTONDOWN = 0x0201
        WM_LBUTTONUP = 0x0202
        WM_LBUTTONDBLCLK = 0x0203
        WM_RBUTTONDOWN =0x0204
        WM_RBUTTONUP = 0x0205
        WM_RBUTTONDBLCLK = 0x0206
        WM_MBUTTONDOWN = 0x0207
        WM_MBUTTONUP = 0x0208
        WM_MBUTTONDBLCLK = 0x0209
        WM_MOUSEWHEEL = 0x020A
        WM_MOUSELAST = 0x020A
    
        WH_MOUSE = 7
        WH_MOUSE_LL = 14
        WH_MAX = 15
       
        _mouse_event_mapper={
            WM_MOUSEMOVE : [0, EventConstants.MOUSE_MOVE, MouseConstants.MOUSE_BUTTON_NONE],
            WM_RBUTTONDOWN : [MouseConstants.MOUSE_BUTTON_STATE_PRESSED, EventConstants.MOUSE_BUTTON_PRESS, MouseConstants.MOUSE_BUTTON_RIGHT],
            WM_MBUTTONDOWN : [MouseConstants.MOUSE_BUTTON_STATE_PRESSED, EventConstants.MOUSE_BUTTON_PRESS, MouseConstants.MOUSE_BUTTON_MIDDLE],
            WM_LBUTTONDOWN : [MouseConstants.MOUSE_BUTTON_STATE_PRESSED, EventConstants.MOUSE_BUTTON_PRESS, MouseConstants.MOUSE_BUTTON_LEFT],
            WM_RBUTTONUP : [MouseConstants.MOUSE_BUTTON_STATE_RELEASED, EventConstants.MOUSE_BUTTON_RELEASE, MouseConstants.MOUSE_BUTTON_RIGHT],
            WM_MBUTTONUP : [MouseConstants.MOUSE_BUTTON_STATE_RELEASED, EventConstants.MOUSE_BUTTON_RELEASE, MouseConstants.MOUSE_BUTTON_MIDDLE],
            WM_LBUTTONUP : [MouseConstants.MOUSE_BUTTON_STATE_RELEASED, EventConstants.MOUSE_BUTTON_RELEASE, MouseConstants.MOUSE_BUTTON_LEFT],
            WM_RBUTTONDBLCLK : [MouseConstants.MOUSE_BUTTON_STATE_MULTI_CLICK, EventConstants.MOUSE_MULTI_CLICK, MouseConstants.MOUSE_BUTTON_RIGHT],
            WM_MBUTTONDBLCLK : [MouseConstants.MOUSE_BUTTON_STATE_MULTI_CLICK, EventConstants.MOUSE_MULTI_CLICK, MouseConstants.MOUSE_BUTTON_MIDDLE],
            WM_LBUTTONDBLCLK : [MouseConstants.MOUSE_BUTTON_STATE_MULTI_CLICK, EventConstants.MOUSE_MULTI_CLICK, MouseConstants.MOUSE_BUTTON_LEFT],
            WM_MOUSEWHEEL : [0, EventConstants.MOUSE_SCROLL, MouseConstants.MOUSE_BUTTON_NONE]
        }
    
        slots=['_user32','_original_system_cursor_clipping_rect']
        def __init__(self,*args,**kwargs):          
            MouseDevice.__init__(self,*args,**kwargs['dconfig'])
    
            self._user32=ctypes.windll.user32
    
            self.getSystemCursorVisibility()
            self._original_system_cursor_clipping_rect=RECT()
            self._user32.GetClipCursor(ctypes.byref(self._original_system_cursor_clipping_rect))
            
        def _nativeLimitCursorToBoundingRect(self,clip_rect):
            native_clip_rect=RECT()            
            if clip_rect:
                native_clip_rect.right=ctypes.c_long(clip_rect.right)
                native_clip_rect.bottom=ctypes.c_long(clip_rect.bottom)
                native_clip_rect.left=ctypes.c_long(clip_rect.left)
                native_clip_rect.top=ctypes.c_long(clip_rect.top)
                self._user32.ClipCursor(ctypes.byref(native_clip_rect))
            else:
                self._user32.ClipCursor(None)
                self._user32.GetClipCursor(ctypes.byref(native_clip_rect))
            return native_clip_rect
            
        def _nativeSetMousePos(self,px,py):
            self._user32.SetCursorPos(int(px),int(py))
            #ioHub.print2err(" mouse.setPos updated to {0}".format((px,py)))
            
        def _nativeGetSystemCursorVisibility(self):
            self._user32.ShowCursor(False)    
            self._isVisible = self._user32.ShowCursor(True)
            return self._isVisible >= 0
     
        def _nativeSetSystemCursorVisibility(self,v):
            self._isVisible=self._user32.ShowCursor(v)
            return self._isVisible >= 0
            
        def _nativeEventCallback(self,event):
            if self.isReportingEvents():
                logged_time=currentSec()
                #ioHub.print2err("Received mouse event pos: ", event.Position)
                self._scrollPositionY+= event.Wheel
                event.WheelAbsolute=self._scrollPositionY

                display_index=self.getDisplayIndexForMousePosition(event.Position)

                if display_index == -1:
                    if self._last_display_index is not None:
                        display_index=self._last_display_index
                    else:    
                        ioHub.print2err("!!! _nativeEventCallback error: mouse event pos {0} not in any display bounds!!!".format(event.Position))
                        ioHub.print2err("!!!  -> SKIPPING EVENT")
                        ioHub.print2err("===============")
                        return True
                
                result=self._validateMousePosition(event.Position,display_index)
                #ioHub.print2err("_validateMousePosition result: ", result)
                
                if result != True:
                    #ioHub.print2err("!!! _validateMousePosition made ajustment: {0} to {1}".format(
                    #                                   event.Position,result))
                    self._nativeSetMousePos(*result) 
                    event.Position=result
                    display_index=self.getDisplayIndexForMousePosition(event.Position)
                    
                mx,my=event.Position                
                event.DisplayIndex=display_index                
                p=self._display_device.pixel2DisplayCoord(mx,my,event.DisplayIndex)  
            
                #ioHub.print2err("Going to Update mousePosition: {0} => {1} on D {2}".format(
                #                    event.Position,p,event.DisplayIndex))

                event.Position=p
                
                self._lastPosition=self._position
                self._position=event.Position

                self._last_display_index=self._display_index
                self._display_index=display_index
 
                #ioHub.print2err("===============")
                
                # <<<<<<<<<
                
                bstate,etype,bnum=self._mouse_event_mapper[event.Message]
                if bnum is not MouseConstants.MOUSE_BUTTON_NONE:
                    self.activeButtons[bnum]= int(bstate==MouseConstants.MOUSE_BUTTON_STATE_PRESSED)
    
                abuttonSum=0
                for k,v in self.activeButtons.iteritems():
                    abuttonSum+=k*v
    
                event.ActiveButtons=abuttonSum
    
                self._addNativeEventToBuffer((logged_time,event))
    
                self._last_callback_time=logged_time
                

            # pyHook require the callback to return True to inform the windows 
            # low level hook functionality to pass the event on.
            return True

        def _getIOHubEventObject(self,native_event_data):
            logged_time, event=native_event_data
            p = event.Position
            px=p[0]
            py=p[1]
    
            bstate,etype,bnum=self._mouse_event_mapper[event.Message]
    
            if event.Message == self.WM_MOUSEMOVE and event.ActiveButtons>0:
                etype=EventConstants.MOUSE_DRAG
    
            confidence_interval=0.0
            delay=0.0
    
            # From MSDN: http://msdn.microsoft.com/en-us/library/windows/desktop/ms644939(v=vs.85).aspx
            # The time is a long integer that specifies the elapsed time, in milliseconds, from the time the system was started to the time the message was 
            # created (that is, placed in the thread's message queue).REMARKS: The return value from the GetMessageTime function does not necessarily increase
            # between subsequent messages, because the value wraps to zero if the timer count exceeds the maximum value for a long integer. To calculate time
            # delays between messages, verify that the time of the second message is greater than the time of the first message; then, subtract the time of the
            # first message from the time of the second message.
            device_time = event.Time/1000.0 # convert to sec
            
            hubTime = logged_time
    
            r= [0,
                0,
                0, #device id
                Computer._getNextEventID(),
                etype,
                device_time,
                logged_time,
                hubTime,
                confidence_interval, 
                delay,
                0, 
                event.DisplayIndex, 
                bstate, 
                bnum,
                event.ActiveButtons,
                px, 
                py,
                0, #scroll_dx not supported
                0, #scroll_x not supported   
                event.Wheel,
                event.WheelAbsolute,                      
                event.Window]    
            return r

        def __del__(self):
            self._user32.ClipCursor(ctypes.byref(self._original_system_cursor_clipping_rect))
            MouseDevice.__del__(self)
            
elif Computer.system == 'linux2':
    class Mouse(MouseDevice):
        """
        The Mouse class and related events represent a standard computer mouse device
        and the events a standard mouse can produce. Mouse position data is mapped to
        the coordinate space defined in the ioHub configuration file for the Display.
        """
        
        def __init__(self,*args,**kwargs):          
            MouseDevice.__init__(self,*args,**kwargs['dconfig'])            

        def _nativeSetMousePos(self,px,py):
            pass#ioHub.print2err('_nativeSetMousePos result: ',result)
                
        def _nativeGetSystemCursorVisibility(self):
            return False#CGCursorIsVisible()
            
        def _nativeSetSystemCursorVisibility(self,v):
            pass
            #if v and not CGCursorIsVisible():
            #    pass#CGDisplayShowCursor(CGMainDisplayID())
            #elif not v and CGCursorIsVisible():
            #    pass#CGDisplayHideCursor(CGMainDisplayID()
                
        def _nativeLimitCursorToBoundingRect(self,clip_rect):
            ioHub.print2err('WARNING: Mouse._nativeLimitCursorToBoundingRect not implemented on OSX yet.')
            native_clip_rect=None
            return native_clip_rect

                         
        def _nativeEventCallback(self,event):
            try:
               if self.isReportingEvents():
                    logged_time=currentSec()
                    
                    event_array=event[0]
                    event_array[3]=Computer._getNextEventID()
                    
                    self._addNativeEventToBuffer(event_array)
                    
                    self._last_callback_time=logged_time
            except:
                ioHub.printExceptionDetailsToStdErr()
            
            # Must return original event or no mouse events will get to OSX!
            return 1
                
        def _getIOHubEventObject(self,native_event_data):
            #ioHub.print2err('Event: ',native_event_data)
            return native_event_data


#          
#        def _nativeEventCallback(self,event):
#                if self.isReportingEvents():
#                    logged_time=currentSec()
#        
#                    self._scrollPositionY+= event.Wheel
#                    print event
#                    return 1
#
#                    event.WheelAbsolute=self._scrollPositionY
#        
#                    ioHub.print2err("UPDATE Linux _getIOHubEventObject to include event.DisplayIndex logic.")            
#                    event.DisplayIndex=0
#    
#                    p=self._display_device.pixel2DisplayCoord(event.Position[0],event.Position[1])
#                    event.Position=p
#    
#                    self._lastPosition=self._position
#                    self._position=event.Position
#    
#                    self._last_display_index=self._display_index
#                    self._display_index=event.DisplayIndex
#     
#                    if event.ioHubButtonID is not MouseConstants.MOUSE_BUTTON_NONE:
#                        self.activeButtons[event.ioHubButtonID]= int(event.ioHubButtonState==MouseConstants.MOUSE_BUTTON_STATE_PRESSED)
#        
#                    abuttonSum=0
#                    for k,v in self.activeButtons.iteritems():
#                        abuttonSum+=k*v
#        
#                    event.ActiveButtons=abuttonSum
#        
#                    self._addNativeEventToBuffer((logged_time,event))
#        
#                    self._last_callback_time=logged_time
#        
#    
#        def _getIOHubEventObject(self,native_event_data):
#            logged_time, event=native_event_data
#            #import ioHub
#            #ioHub.print2err("Mouse event start....")            
#            px,py = event.Position
#    
#            confidence_interval=0.0
#            delay=0.0
#            hubTime = logged_time #TODO correct mouse times to factor in offset.
#    
#            r= [0,
#                0,
#                0, #device id
#                Computer._getNextEventID(),
#                event.ioHubEventID,
#                event.Time,
#                logged_time,
#                hubTime,
#                confidence_interval, 
#                delay,
#                0, # filtered by ID (always 0 right now) 
#                event.DisplayIndex,
#                event.ioHubButtonState, 
#                event.ioHubButtonID,
#                event.ActiveButtons, 
#                px, 
#                py,
#                0, #scroll_dx not supported
#                0, #scroll_x not supported
#                event.Wheel,
#                event.WheelAbsolute, 
#                event.Window]
#             
#            #ioHub.print2err("Mouse event built.\n-----------------")
#            
#            return r
#
else: # assume OS X
    from copy import copy
    from Quartz import *
    from AppKit import NSEvent
    
    pressID = [None, kCGEventLeftMouseDown, kCGEventRightMouseDown, kCGEventOtherMouseDown]
    releaseID = [None, kCGEventLeftMouseUp, kCGEventRightMouseUp, kCGEventOtherMouseUp]
    dragID = [None, kCGEventLeftMouseDragged, kCGEventRightMouseDragged, kCGEventOtherMouseDragged]
    
    from ioHub.constants import EventConstants,MouseConstants
    
    class Mouse(MouseDevice):
        """
        The Mouse class and related events represent a standard computer mouse device
        and the events a standard mouse can produce. Mouse position data is mapped to
        the coordinate space defined in the ioHub configuration file for the Display.
        """
        __slots__=['_loop_source','_tap','_device_loop','_CGEventTapEnable',
                   '_loop_mode','_scrollPositionX']
    
        _IOHUB_BUTTON_ID_MAPPINGS={
            kCGEventLeftMouseDown:MouseConstants.MOUSE_BUTTON_LEFT,
            kCGEventRightMouseDown:MouseConstants.MOUSE_BUTTON_RIGHT,
            kCGEventOtherMouseDown:MouseConstants.MOUSE_BUTTON_MIDDLE,
            kCGEventLeftMouseUp:MouseConstants.MOUSE_BUTTON_LEFT,
            kCGEventRightMouseUp:MouseConstants.MOUSE_BUTTON_RIGHT,
            kCGEventOtherMouseUp:MouseConstants.MOUSE_BUTTON_MIDDLE
        }
        
        DEVICE_TIME_TO_SECONDS=0.000000001
        
        _EVENT_TEMPLATE_LIST=[0, # experiment id
                            0,  # session id
                            0, #device id
                            0,  # Computer._getNextEventID(),
                            0,  # ioHub Event type
                            0.0,# event device time,
                            0.0,# event logged_time,
                            0.0,# event iohub Time,
                            0.0,# confidence_interval, 
                            0.0,# delay,
                            0,  # filtered by ID (always 0 right now) 
                            0,  # Display Index,
                            0,  # ioHub Button State, 
                            0,  # ioHub Button ID,
                            0,  # Active Buttons, 
                            0.0,# x position of mouse in Display device coord's 
                            0.0,# y position of mouse in Display device coord's
                            0,  # Wheel dx
                            0,  # Wheel Absolute x 
                            0,  # Wheel dy
                            0,  # Wheel Absolute y 
                            0 ] # event.Window]            
    
        
        def __init__(self,*args,**kwargs):
            MouseDevice.__init__(self,*args,**kwargs['dconfig'])
            
            self._tap = CGEventTapCreate(
                kCGSessionEventTap,
                kCGHeadInsertEventTap,
                kCGEventTapOptionDefault,
                CGEventMaskBit(kCGEventMouseMoved) |
                CGEventMaskBit(kCGEventLeftMouseDown) |
                CGEventMaskBit(kCGEventLeftMouseUp) |
                CGEventMaskBit(kCGEventRightMouseDown) |
                CGEventMaskBit(kCGEventRightMouseUp) |
                CGEventMaskBit(kCGEventLeftMouseDragged) |
                CGEventMaskBit(kCGEventRightMouseDragged) |
                CGEventMaskBit(kCGEventOtherMouseDragged) |
                CGEventMaskBit(kCGEventOtherMouseDown) |
                CGEventMaskBit(kCGEventScrollWheel) |
                CGEventMaskBit(kCGEventOtherMouseUp),
                self._nativeEventCallback,
                None)            
            
            self._scrollPositionX=0
            self._CGEventTapEnable=CGEventTapEnable
            self._loop_source = CFMachPortCreateRunLoopSource(None, self._tap, 0)          
            self._device_loop = CFRunLoopGetCurrent()
            self._loop_mode=kCFRunLoopDefaultMode
            
            CFRunLoopAddSource(self._device_loop, self._loop_source, self._loop_mode)

        def _nativeSetMousePos(self,px,py):
            result=CGWarpMouseCursorPosition(CGPointMake(float(px),float(py)))
            ioHub.print2err('_nativeSetMousePos result: ',result)
                
        def _nativeGetSystemCursorVisibility(self):
            return CGCursorIsVisible()
            
        def _nativeSetSystemCursorVisibility(self,v):
            if v and not CGCursorIsVisible():
                CGDisplayShowCursor(CGMainDisplayID())
            elif not v and CGCursorIsVisible():
                CGDisplayHideCursor(CGMainDisplayID())

                
        def _nativeLimitCursorToBoundingRect(self,clip_rect):
            ioHub.print2err('WARNING: Mouse._nativeLimitCursorToBoundingRect not implemented on OSX yet.')
            native_clip_rect=None
            return native_clip_rect

        def getScroll(self):
            """
            TODO: Update docs for OSX
            Args: None
            Returns 
            """
            return self._scrollPositionX,self._scrollPositionY
    
        def setScroll(self,sp):
            """
            TODO: Update docs for OSX
            """
            self._scrollPositionX,self._scrollPositionY=sp
            return self._scrollPositionX,self._scrollPositionY

        def _poll(self):
            self._last_poll_time=currentSec()            
            while CFRunLoopRunInMode(self._loop_mode, 0.0, True) == kCFRunLoopRunHandledSource:
                pass
                            
        def _nativeEventCallback(self,*args):
            try:
                proxy, etype, event, refcon = args
                if self.isReportingEvents():
                    logged_time=currentSec()
    
                    if etype == kCGEventTapDisabledByTimeout:
                        ioHub.print2err("** WARNING: Mouse Tap Disabled due to timeout. Re-enabling....: ", etype)
                        CGEventTapEnable(self._tap, True)
                        return event
                    else:                
                        confidence_interval=0.0
                        delay=0.0
                        iohub_time = logged_time
                        device_time=CGEventGetTimestamp(event)*self.DEVICE_TIME_TO_SECONDS      
                        ioe_type=EventConstants.UNDEFINED
                        px,py = CGEventGetLocation(event)
                        multi_click_count=CGEventGetIntegerValueField(event,kCGMouseEventClickState)
                        mouse_event = NSEvent.eventWithCGEvent_(event)                                  
                        window_handle=mouse_event.windowNumber()                          
                                       
                        # TO DO: Implement multimonitor location based on mouse location support.
                        # Currently always uses monitor index 0
                        
                        display_index=self.getDisplayIndexForMousePosition((px,py))
                        if display_index == -1:
                            if self._last_display_index is not None:
                                display_index=self._last_display_index
                            else:    
                                ioHub.print2err("!!! _nativeEventCallback error: mouse event pos {0} not in any display bounds!!!".format(event.Position))
                                ioHub.print2err("!!!  -> SKIPPING EVENT")
                                ioHub.print2err("===============")
                                return event
                
                        result=self._validateMousePosition((px,py),display_index)
                        if result != True:
                            ioHub.print2err("!!! _validateMousePosition made ajustment: {0} to {1}".format((px,py),result))
                            nx,ny=result
                            display_index=self.getDisplayIndexForMousePosition((nx,ny))
                            ioHub.print2err("Going to Update mousePosition: {0} => {1} on D {2}".format((px,py),(ny,ny),display_index))            
                            px,py=nx,ny
                            self._nativeSetMousePos(px,py)   
                
                        px,py=self._display_device.pixel2DisplayCoord(px,py,display_index)                          
                        self._lastPosition=self._position
                        self._position=px,py
                        self._last_display_index=self._display_index
                        self._display_index=display_index
                        
                        # TO DO: Supported reporting scroll x info for OSX.
                        # This also suggests not having scoll up and down events and
                        # just having the one scroll event type, regardless of direction / dimension 
                        scroll_dx=0
                        scroll_dy=0
                        button_state=0
                        if etype in pressID:
                            button_state=MouseConstants.MOUSE_BUTTON_STATE_PRESSED
                            if multi_click_count>1:
                                ioe_type=EventConstants.MOUSE_MULTI_CLICK
                            else:
                                ioe_type=EventConstants.MOUSE_BUTTON_PRESS
                        elif etype in releaseID:
                            button_state=MouseConstants.MOUSE_BUTTON_STATE_RELEASED
                            ioe_type=EventConstants.MOUSE_BUTTON_RELEASE
                        elif etype in dragID:
                            ioe_type=EventConstants.MOUSE_DRAG
                        elif etype == kCGEventMouseMoved:
                            ioe_type=EventConstants.MOUSE_MOVE
                        elif etype == kCGEventScrollWheel:    
                            ioe_type=EventConstants.MOUSE_SCROLL
                            scroll_dy= CGEventGetIntegerValueField(event,kCGScrollWheelEventPointDeltaAxis1)
                            scroll_dx= CGEventGetIntegerValueField(event,kCGScrollWheelEventPointDeltaAxis2)
                            self._scrollPositionX+= scroll_dx
                            self._scrollPositionY+= scroll_dy
                                                
                        iohub_button_id=self._IOHUB_BUTTON_ID_MAPPINGS.get(etype,0)
    
                        if iohub_button_id in self.activeButtons:
                            self.activeButtons[iohub_button_id]= int(button_state==MouseConstants.MOUSE_BUTTON_STATE_PRESSED)
            
                        pressed_buttons=0
                        for k,v in self.activeButtons.iteritems():
                            pressed_buttons+=k*v
                        
                        # Create Event List
                        # index 0 and 1 are session and exp. ID's
                        # index 2 is (yet to be used) device_id
                        ioe=self._EVENT_TEMPLATE_LIST
                        ioe[3]=Computer._getNextEventID()
                        ioe[4]=ioe_type #event type code
                        ioe[5]=device_time
                        ioe[6]=logged_time
                        ioe[7]=iohub_time
                        ioe[8]=confidence_interval
                        ioe[9]=delay
                        # index 10 is filter id, not used at this time
                        ioe[11]=display_index
                        ioe[12]=button_state
                        ioe[13]=iohub_button_id
                        ioe[14]=pressed_buttons 
                        ioe[15]=px 
                        ioe[16]=py
                        ioe[17]=int(scroll_dx)
                        ioe[18]=int(self._scrollPositionX) 
                        ioe[19]=int(scroll_dy)
                        ioe[20]=int(self._scrollPositionY) 
                        ioe[21]=window_handle
                        
                        self._addNativeEventToBuffer(copy(ioe))
                        
                    self._last_callback_time=logged_time
            except:
                ioHub.printExceptionDetailsToStdErr()
                CGEventTapEnable(self._tap, False)
            
            # Must return original event or no mouse events will get to OSX!
            return event
                
        def _getIOHubEventObject(self,native_event_data):
            #ioHub.print2err('Event: ',native_event_data)
            return native_event_data
        
        def _close(self):
            try:
                self._nativeSetSystemCursorVisibility(True)
            except Exception:
                pass
            
            try:
                CGEventTapEnable(self._tap, False)
            except:
                pass
            
            try:
                if CFRunLoopContainsSource(self._device_loop,self._loop_source,self._loop_mode) is True:    
                    CFRunLoopRemoveSource(self._device_loop,self._loop_source,self._loop_mode)
            finally:
                self._loop_source=None
                self._tap=None
                self._device_loop=None
                self._loop_mode=None
            
            MouseDevice._close(self)
    # END OF OSX MOUSE CLASS
    
        """
        CGEventTapInformation
        Defines the structure used to report information about event taps.
        typedef struct CGEventTapInformation
           {
           uint32_t            eventTapID;
           CGEventTapLocation  tapPoint;
           CGEventTapOptions   options;
           CGEventMask         eventsOfInterest;
           pid_t               tappingProcess;
           pid_t               processBeingTapped;
           bool                enabled;
           float               minUsecLatency;
           float               avgUsecLatency;
           float               maxUsecLatency;
        } CGEventTapInformation;
        Fields
        
        eventTapID
        The unique identifier for the event tap.
        
        tapPoint
        The location of the event tap. See "Event Tap Locations."
        
        options
        The type of event tap (passive listener or active filter).
        
        eventsOfInterest
        The mask that identifies the set of events to be observed.
        
        tappingProcess
        The process ID of the application that created the event tap.
        
        processBeingTapped
        The process ID of the target application (non-zero only if the 
        event tap was created using the function CGEventTapCreateForPSN.
        
        enabled
        TRUE if the event tap is currently enabled; otherwise FALSE.
        
        minUsecLatency
        Minimum latency in microseconds. In this data structure, 
        latency is defined as the time in microseconds it takes 
        for an event tap to process and respond to an event passed to it.
        
        avgUsecLatency
        Average latency in microseconds. This is a weighted average
        that gives greater weight to more recent events.
        
        maxUsecLatency
        Maximum latency in microseconds.
        
        Discussion
        To learn how to obtain information about event taps, see the 
        function CGGetEventTapList.
        Availability
        Available in OS X v10.4 and later.
        Declared In
        CGEventTypes.h        
        """
############# OS Independent Mouse Event Classes ####################

from .. import DeviceEvent

class MouseInputEvent(DeviceEvent):
    """
    The MouseInputEvent is an abstract class that is the parent of all MouseInputEvent types
    that are supported in the ioHub. Mouse position is mapped to the coordinate space
    defined in the ioHub configuration file for the Display.
    """
    PARENT_DEVICE=Mouse
    EVENT_TYPE_STRING='MOUSE_INPUT'
    EVENT_TYPE_ID=EventConstants.MOUSE_INPUT
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING

    _newDataTypes = [
                     ('display_id',N.uint8),     # gives the display index that the mouse was over for the event.
                     ('button_state',N.uint8),    # 1 if button is pressed, 0 if button is released
                     ('button_id',N.uint8),       # 1, 2,or 4, representing left, right, and middle buttons
                     ('pressed_buttons',N.uint8), # sum of currently active button int values

                     ('x_position',N.int16),    # x position of the position when the event occurred
                     ('y_position',N.int16),    # y position of the position when the event occurred

                     ('scroll_dx', N.int8),  # horizontal scroll wheel position change when the event occurred (OS X only)
                     ('scroll_x', N.int16),  # horizontal scroll wheel abs. position when the event occurred (OS X only)
                     ('scroll_dy', N.int8),  # vertical scroll wheel position change when the event occurred
                     ('scroll_y', N.int16),  # vertical scroll wheel abs. position when the event occurred

                     ('window_id',N.uint64)      # window ID that the mouse was over when the event occurred
                                                # (window does not need to have focus)
                    ]
    # TODO: Determine real maximum key name string and modifiers string
    # lengths and set appropriately.

    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self,*args,**kwargs):
        # The id of the display that the mouse was over when the event occurred.
        self.display_id=None        
        
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
        
        #: horizontal scroll wheel position change when the event occurred
        self.scroll_dx=None

        #: horizontal scroll wheel absolute position when the event occurred
        self.scroll_x=None

        #: vertical scroll wheel position change when the event occurred
        self.scroll_dy=None

        #: vertical scroll wheel absolute position when the event occurred
        self.scroll_y=None
        
        #: window ID that the mouse was over when the event occurred
        #: (window does not need to have focus)
        self.window_id=None

        DeviceEvent.__init__(self,*args,**kwargs)

class MouseMoveEvent(MouseInputEvent):
    """
    MouseMoveEvents occur when the mouse position changes. Mouse position is
    mapped to the coordinate space defined in the ioHub configuration file 
    for the Display.
    
    Event Type ID: EventConstants.MOUSE_MOVE
    Event Type String: 'MOUSE_MOVE'
    """
    EVENT_TYPE_STRING='MOUSE_MOVE'
    EVENT_TYPE_ID=EventConstants.MOUSE_MOVE
    IOHUB_DATA_TABLE=MouseInputEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        MouseInputEvent.__init__(self, *args, **kwargs)

class MouseDragEvent(MouseMoveEvent):
    """
    MouseDragEvents occur when the mouse position changes and at least one mouse
    button is pressed. Mouse position is mapped to the coordinate space defined
    in the ioHub configuration file for the Display.
    
    Event Type ID: EventConstants.MOUSE_DRAG
    Event Type String: 'MOUSE_DRAG'
    """
    EVENT_TYPE_STRING='MOUSE_DRAG'
    EVENT_TYPE_ID=EventConstants.MOUSE_DRAG
    IOHUB_DATA_TABLE=MouseMoveEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        MouseMoveEvent.__init__(self, *args, **kwargs)

class MouseScrollEvent(MouseInputEvent):
    """
    MouseScrollEvent's are generated when the scroll wheel on the 
    Mouse Device (if it has one) is moved. Vertical scrolling is supported
    on all operating systems, horizontal scrolling is only supported on OS X.
    Each MouseScrollEvent provides the number of units the wheel was turned 
    in each supported dimension, as well as the absolute scroll value for 
    of each supported dimension.

    Event Type ID: EventConstants.MOUSE_SCROLL
    Event Type String: 'MOUSE_SCROLL'
    """
    EVENT_TYPE_STRING='MOUSE_SCROLL'
    EVENT_TYPE_ID=EventConstants.MOUSE_SCROLL
    IOHUB_DATA_TABLE=MouseInputEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        """

        :rtype : MouseScrollEvent
        :param args:
        :param kwargs:
        """
        MouseInputEvent.__init__(self, *args, **kwargs)

class MouseButtonEvent(MouseInputEvent):
    EVENT_TYPE_STRING='MOUSE_BUTTON'
    EVENT_TYPE_ID=EventConstants.MOUSE_BUTTON
    IOHUB_DATA_TABLE=MouseInputEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        """

        :rtype : MouseButtonEvent
        :param args:
        :param kwargs:
        """
        MouseInputEvent.__init__(self, *args, **kwargs)

class MouseButtonPressEvent(MouseButtonEvent):
    """
    MouseButtonPressEvent's are created when a button on the mouse is pressed. 
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

    Event Type ID: EventConstants.MOUSE_BUTTON_PRESS
    Event Type String: 'MOUSE_BUTTON_PRESS'    
    """
    EVENT_TYPE_STRING='MOUSE_BUTTON_PRESS'
    EVENT_TYPE_ID=EventConstants.MOUSE_BUTTON_PRESS
    IOHUB_DATA_TABLE=MouseInputEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        MouseButtonEvent.__init__(self, *args, **kwargs)

class MouseButtonReleaseEvent(MouseButtonEvent):
    """
    MouseButtonUpEvent's are created when a button on the mouse is released. 
    The button_state of the event will equal MouseConstants.MOUSE_BUTTON_STATE_RELEASED,
    and the button that was pressed (button_id) will be MouseConstants.MOUSE_BUTTON_ID_LEFT,
    MouseConstants.MOUSE_BUTTON_ID_RIGHT, or MouseConstants.MOUSE_BUTTON_ID_MIDDLE, 
    assuming you have a 3 button mouse.

    Event Type ID: EventConstants.MOUSE_BUTTON_RELEASE
    Event Type String: 'MOUSE_BUTTON_RELEASE'    
    """
    EVENT_TYPE_STRING='MOUSE_BUTTON_RELEASE'
    EVENT_TYPE_ID=EventConstants.MOUSE_BUTTON_RELEASE
    IOHUB_DATA_TABLE=MouseInputEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        MouseButtonEvent.__init__(self, *args, **kwargs)

class MouseMultiClickEvent(MouseButtonEvent):
    """
    MouseMultiClickEvent's are created when you rapidly press and release a 
    mouse button twice. This event may never get triggered if your OS does not support it.
    The button that was multi clicked (button_id) will be MouseConstants.MOUSE_BUTTON_ID_LEFT,
    MouseConstants.MOUSE_BUTTON_ID_RIGHT, or MouseConstants.MOUSE_BUTTON_ID_MIDDLE, 
    assuming you have a 3 button mouse.

    Event Type ID: EventConstants.MOUSE_MULTI_CLICK
    Event Type String: 'MOUSE_MULTI_CLICK'    
    """
    EVENT_TYPE_STRING='MOUSE_MULTI_CLICK'
    EVENT_TYPE_ID=EventConstants.MOUSE_MULTI_CLICK
    IOHUB_DATA_TABLE=MouseInputEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        MouseButtonEvent.__init__(self, *args, **kwargs)
