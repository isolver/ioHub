# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 18:56:04 2013

@author: isolver
"""

from copy import copy
from Quartz import *
from AppKit import NSEvent

from . import MouseDevice
import ioHub
from ioHub.devices import Computer
from ioHub.constants import EventConstants,MouseConstants

currentSec=Computer.getTime

pressID = [None, kCGEventLeftMouseDown, kCGEventRightMouseDown, kCGEventOtherMouseDown]
releaseID = [None, kCGEventLeftMouseUp, kCGEventRightMouseUp, kCGEventOtherMouseUp]
dragID = [None, kCGEventLeftMouseDragged, kCGEventRightMouseDragged, kCGEventOtherMouseDragged]

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
