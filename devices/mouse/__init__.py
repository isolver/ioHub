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
    three buttons and an optional vertical scroll wheel. Mouse position data is 
    mapped to the coordinate space defined in the ioHub configuration file for the Display.
    """
    EVENT_CLASS_NAMES=['MouseInputEvent','MouseButtonEvent','MouseWheelEvent',
                       'MouseMoveEvent', 'MouseWheelUpEvent', 'MouseWheelDownEvent',
                       'MouseButtonPressEvent','MouseButtonReleaseEvent',
                       'MouseDoubleClickEvent']
                       
    DEVICE_TYPE_ID=DeviceConstants.MOUSE
    DEVICE_TYPE_STRING='MOUSE'

    __slots__=['_lock_mouse_to_display_id','_scrollPositionY','_position',
               '_lastPosition','_display_index','_last_display_index','_isVisible','activeButtons'
               ]
    def __init__(self,*args,**kwargs):     
        Device.__init__(self,*args,**kwargs)
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
        
    def getCurrentButtonStates(self):
        return (self.activeButtons[MouseConstants.MOUSE_BUTTON_LEFT]!=0,
                self.activeButtons[MouseConstants.MOUSE_BUTTON_MIDDLE]!=0,
                self.activeButtons[MouseConstants.MOUSE_BUTTON_RIGHT]!=0)
                
    def lockMouseToDisplayID(self,display_id):
        self._lock_mouse_to_display_id=display_id    

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
        
    def getDisplayIndexForMousePosition(self,system_mouse_pos):
        return self._display_device.getDisplayIndexForNativePixelPosition(system_mouse_pos)


if Computer.system == 'Windows':
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
            WM_RBUTTONDBLCLK : [MouseConstants.MOUSE_BUTTON_STATE_DOUBLE_CLICK, EventConstants.MOUSE_DOUBLE_CLICK, MouseConstants.MOUSE_BUTTON_RIGHT],
            WM_MBUTTONDBLCLK : [MouseConstants.MOUSE_BUTTON_STATE_DOUBLE_CLICK, EventConstants.MOUSE_DOUBLE_CLICK, MouseConstants.MOUSE_BUTTON_MIDDLE],
            WM_LBUTTONDBLCLK : [MouseConstants.MOUSE_BUTTON_STATE_DOUBLE_CLICK, EventConstants.MOUSE_DOUBLE_CLICK, MouseConstants.MOUSE_BUTTON_LEFT],
            WM_MOUSEWHEEL : [0, EventConstants.MOUSE_WHEEL_DOWN, MouseConstants.MOUSE_BUTTON_NONE]
        }
    
        slots=['_user32','_original_system_cursor_clipping_rect','_clipRectsForDisplayID']
        def __init__(self,*args,**kwargs):          
            MouseDevice.__init__(self,*args,**kwargs['dconfig'])
    
            self._user32=ctypes.windll.user32
    
            self.getSystemCursorVisibility()
            self._clipRectsForDisplayID={}
            self._original_system_cursor_clipping_rect=RECT()
            self._user32.GetClipCursor(ctypes.byref(self._original_system_cursor_clipping_rect))

        def lockMouseToDisplayID(self,display_id):
            MouseDevice.lockMouseToDisplayID(self,display_id)
            if display_id is not None:
                if display_id not in self._clipRectsForDisplayID:
                    screen=self._display_device.getConfiguration()['runtime_info']              
                    if screen:
                        left,top,right,bottom=screen['bounds']
                        right=ctypes.c_long(right)
                        bottom=ctypes.c_long(bottom)
                        left=ctypes.c_long(left)
                        top=ctypes.c_long(top)
                        clip_rect=RECT(left,top,right,bottom)
                    self._clipRectsForDisplayID[display_id]=clip_rect,ioHub.RectangleBorder(clip_rect.left,clip_rect.top,clip_rect.right,clip_rect.bottom)

                clip_rect=self._clipRectsForDisplayID[display_id][0]    
                self._user32.ClipCursor(ctypes.byref(clip_rect))
            else:
                #ioHub.print2err("Setting Mouse ClipRect: None")
                self._user32.ClipCursor(None)
                if None not in self._clipRectsForDisplayID:
                    clip_rect=RECT()
                    self._user32.GetClipCursor(ctypes.byref(clip_rect))
                    self._clipRectsForDisplayID[None]=clip_rect,ioHub.RectangleBorder(clip_rect.left,clip_rect.top,clip_rect.right,clip_rect.bottom)
            return self._clipRectsForDisplayID[display_id][1]
            
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
                
                    self._user32.SetCursorPos(int(px),int(py))
                    #ioHub.print2err(" mouse.setPos updated to {0}".format((px,py)))
                    
            return self._position
    
        def getSystemCursorVisibility(self):
            """
            Returns whether the system cursor is visible on the currently active Window.
            
            Args: 
                None
                
            Returns: 
                bool: True if system cursor is visible on currently active Window. False otherwise.
            """
            #  >> WIN32_ONLY
            self._user32.ShowCursor(False)    
            self._isVisible = self._user32.ShowCursor(True)
            #  << WIN32_ONLY
            return self._isVisible >= 0
     
        def setSystemCursorVisibility(self,v):
            """
            Set whether the system cursor is visible on the currently active Window.
            
            Args:
                v (bool): True = make system cursor visible. False = Hide system cursor
            
            Returns:
                (bool): True if system cursor is visible on currently active Window. False otherwise.
    
            """
            #  >> WIN32_ONLY
            self._isVisible=self._user32.ShowCursor(v)
            #  << WIN32_ONLY
            return self._isVisible >= 0


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
            
        def _nativeEventCallback(self,event):
            if self.isReportingEvents():
                logged_time=currentSec()

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
                
                if result != True:
                    #ioHub.print2err("!!! _validateMousePosition made ajustment: {0} to {1}".format(
                    #                                    event.Position,result))
                    self._user32.SetCursorPos(*result)   
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
    
            if event.Message == self.WM_MOUSEWHEEL:
                if event.Wheel > 0:
                    etype=EventConstants.MOUSE_WHEEL_UP
    
            confidence_interval=0.0
            delay=0.0
    
            # From MSDN: http://msdn.microsoft.com/en-us/library/windows/desktop/ms644939(v=vs.85).aspx
            # The time is a long integer that specifies the elapsed time, in milliseconds, from the time the system was started to the time the message was 
            # created (that is, placed in the thread's message queue).REMARKS: The return value from the GetMessageTime function does not necessarily increase
            # between subsequent messages, because the value wraps to zero if the timer count exceeds the maximum value for a long integer. To calculate time
            # delays between messages, verify that the time of the second message is greater than the time of the first message; then, subtract the time of the
            # first message from the time of the second message.
            device_time = event.Time/1000.0 # convert to sec
            
            hubTime = logged_time #TODO correct mouse times to factor in offset.
    
            r= [0,0,Computer._getNextEventID(),etype,device_time,logged_time,hubTime,
                        confidence_interval, delay,0, event.DisplayIndex, bstate, bnum,event.ActiveButtons,
                        px, py,event.Wheel,event.WheelAbsolute, event.Window]    
            return r

        def __del__(self):
            self._user32.ClipCursor(ctypes.byref(self._original_system_cursor_clipping_rect))
            MouseDevice.__del__(self)
            
elif Computer.system == 'Linux':
#    global Mouse
    class Mouse(MouseDevice):
        """
        The Mouse class and related events represent a standard computer mouse device
        and the events a standard mouse can produce. Mouse position data is mapped to
        the coordinate space defined in the ioHub configuration file for the Display.
        """
        
        def __init__(self,*args,**kwargs):          
            MouseDevice.__init__(self,*args,**kwargs['dconfig'])
            
            #self.getSystemCursorVisibility()
            

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
                self._lastPosition=self._position
                self._position=pos[0],pos[1]
    
            ioHub.print2err('Mouse.setPosition not implemented on Linux yet.')
            return self._position
            
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
        
                    ioHub.print2err("UPDATE Linux _getIOHubEventObject to include event.DisplayIndex logic.")            
                    event.DisplayIndex=0
    
                    p=self._display_device.pixel2DisplayCoord(event.Position[0],event.Position[1])
                    event.Position=p
    
                    self._lastPosition=self._position
                    self._position=event.Position
    
                    self._last_display_index=self._display_index
                    self._display_index=event.DisplayIndex
     
                    if event.ioHubButtonID is not MouseConstants.MOUSE_BUTTON_NONE:
                        self.activeButtons[event.ioHubButtonID]= int(event.ioHubButtonState==MouseConstants.MOUSE_BUTTON_STATE_PRESSED)
        
                    abuttonSum=0
                    for k,v in self.activeButtons.iteritems():
                        abuttonSum+=k*v
        
                    event.ActiveButtons=abuttonSum
        
                    self._addNativeEventToBuffer((logged_time,event))
        
                    self._last_callback_time=logged_time
        
    
        def _getIOHubEventObject(self,native_event_data):
            logged_time, event=native_event_data
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
                event.DisplayIndex,
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

else: # assume OS X
    import _osx
    print 'Mouse not implemented on OS X yet.'

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

                     ('wheel_change', N.int8),  # vertical scroll wheel position change when the event occurred
                     ('wheel_value', N.int16),  # vertical scroll wheel abs. position when the event occurred

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
        
        #: vertical scroll wheel position change when the event occurred
        self.wheel_change=None

        #: vertical scroll wheel absolute position when the event occurred
        self.wheel_value=None

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

class MouseWheelEvent(MouseInputEvent):
    EVENT_TYPE_STRING='MOUSE_WHEEL'
    EVENT_TYPE_ID=EventConstants.MOUSE_WHEEL
    IOHUB_DATA_TABLE=MouseInputEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        """

        :rtype : MouseWheelEvent
        :param args:
        :param kwargs:
        """
        MouseInputEvent.__init__(self, *args, **kwargs)

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
    IOHUB_DATA_TABLE=MouseInputEvent.IOHUB_DATA_TABLE
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
    IOHUB_DATA_TABLE=MouseInputEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        """

        :rtype : MouseWheelDownEvent
        :param args:
        :param kwargs:
        """
        MouseWheelEvent.__init__(self, *args, **kwargs)

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
    IOHUB_DATA_TABLE=MouseInputEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self, *args, **kwargs):
        MouseButtonEvent.__init__(self, *args, **kwargs)
