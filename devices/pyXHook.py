
# pyxhook -- an extension to emulate some of the PyHook library on linux.
#
#    Copyright (C) 2008 Tim Alexander <dragonfyre13@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    Thanks to Alex Badea <vamposdecampos@gmail.com> for writing the Record
#    demo for the xlib libraries. It helped me immensely working with these
#    in this library.
#
#    Thanks to the python-xlib team. This wouldn't have been possible without
#    your code.
#    
#    This requires: 
#    at least python-xlib 1.4
#    xwindows must have the "record" extension present, and active.
#    
#    This file has now been somewhat extensively modified by 
#    Daniel Folkinshteyn <nanotube@users.sf.net>
#    So if there are any bugs, they are probably my fault. :)
#
#   January 2013: File modified by
#      Sol Simpson (sol@isolver-software.com), with some cleanup done and
#      modifications made so it integrated with the ioHub module more effecively
#     ( but therefore baccking this version not useful for general application usage) 
#

#import sys
import re
import time
import threading

from Xlib import X, XK, display#, error
from Xlib.ext import record
from Xlib.protocol import rq

import ioHub
from ioHub.constants import EventConstants,MouseConstants#,KeyboardConstants

#######################################################################
########################START CLASS DEF################################
#######################################################################

class HookManager(threading.Thread):
    """
    Creates a seperate thread that starts the Xlib Record functionality, 
    capturing keyboard and mouse events and transmitting them
    to the associated callback functions set.
    """
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.finished = threading.Event()
        
        # Give these some initial values
        self.mouse_position_x = 0
        self.mouse_position_y = 0
        self.ison = {"shift":False, "caps":False}
        
        # Compile our regex statements.
        self.isshift = re.compile('^Shift')
        self.iscaps = re.compile('^Caps_Lock')
        self.shiftablechar = re.compile('^[a-z0-9]$|^minus$|^equal$|^bracketleft$|^bracketright$|^semicolon$|^backslash$|^apostrophe$|^comma$|^period$|^slash$|^grave$')
        self.logrelease = re.compile('.*')
        self.isspace = re.compile('^space$')
        
        # Assign default function actions (do nothing).
        self.KeyDown = lambda x: True
        self.KeyUp = lambda x: True
        self.MouseAllButtonsDown = lambda x: True
        self.MouseAllButtonsUp = lambda x: True
        self.MouseAllMotion = lambda x: True
        self.contextEventMask = [X.KeyPress,X.MotionNotify]
        
        # Hook to our display.
        self.local_dpy = display.Display()
        self.record_dpy = display.Display()
        
    def run(self):
        # Check if the extension is present
        if not self.record_dpy.has_extension("RECORD"):
            ioHub.print2err("RECORD extension not found. ioHub can not use python Xlib. Exiting....")
            return False
        #r = self.record_dpy.record_get_version(0, 0)
        #ioHub.print2err("RECORD extension version %d.%d" % (r.major_version, r.minor_version))

        # Create a recording context; we only want key and mouse events
        self.ctx = self.record_dpy.record_create_context(
                0,
                [record.AllClients],
                [{
                        'core_requests': (0, 0),
                        'core_replies': (0, 0),
                        'ext_requests': (0, 0, 0, 0),
                        'ext_replies': (0, 0, 0, 0),
                        'delivered_events': (0, 0),
                        'device_events': tuple(self.contextEventMask), #(X.KeyPress, X.ButtonPress),
                        'errors': (0, 0),
                        'client_started': False,
                        'client_died': False,
                }])

        # Enable the context; this only returns after a call to record_disable_context,
        # while calling the callback function in the meantime
        self.record_dpy.record_enable_context(self.ctx, self.processevents)
        # Finally free the context
        self.record_dpy.record_free_context(self.ctx)

    def cancel(self):
        self.finished.set()
        self.local_dpy.record_disable_context(self.ctx)
        self.local_dpy.flush()
    
    def printevent(self, event):
        ioHub.print2err(event)
    
    def HookKeyboard(self):
        pass
        # We don't need to do anything here anymore, since the default mask 
        # is now set to contain X.KeyPress
        #self.contextEventMask[0] = X.KeyPress
    
    def HookMouse(self):
        pass
        # We don't need to do anything here anymore, since the default mask 
        # is now set to contain X.MotionNotify
        
        # need mouse motion to track pointer position, since ButtonPress events
        # don't carry that info.
        #self.contextEventMask[1] = X.MotionNotify
    
    def processevents(self, reply):
        if reply.category != record.FromServer:
            return
        if reply.client_swapped:
            ioHub.print2err("pyXlib: * received swapped protocol data, cowardly ignored")
            return
        if not len(reply.data) or ord(reply.data[0]) < 2:
            # not an event
            return
        data = reply.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(data, self.record_dpy.display, None, None)
            if event.type == X.KeyPress:
                hookevent = self.keypressevent(event)
                self.KeyDown(hookevent)
            elif event.type == X.KeyRelease:
                hookevent = self.keyreleaseevent(event)
                self.KeyUp(hookevent)
            elif event.type == X.ButtonPress:
                hookevent = self.buttonpressevent(event)
                self.MouseAllButtonsDown(hookevent)
            elif event.type == X.ButtonRelease and event.detail not in (4,5): 
                # 1 mouse wheel scroll event was generating a button press
                # and a button release event for each single scroll, so allow 
                # wheel scroll events through for buttonpressevent, but not for
                # buttonreleaseevent so 1 scroll action causes 1 scroll event.
                hookevent = self.buttonreleaseevent(event)
                self.MouseAllButtonsUp(hookevent)
            elif event.type == X.MotionNotify:
                # use mouse moves to record mouse position, since press and release events
                # do not give mouse position info (event.root_x and event.root_y have 
                # bogus info).
                hookevent=self.mousemoveevent(event)
                self.MouseAllMotion(hookevent)
        
    def keypressevent(self, event):
        matchto = self.lookup_keysym(self.local_dpy.keycode_to_keysym(event.detail, 0))
        if self.shiftablechar.match(self.lookup_keysym(self.local_dpy.keycode_to_keysym(event.detail, 0))): ## This is a character that can be typed.
            if self.ison["shift"] == False:
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
                return self.makekeyhookevent(keysym, event)
            else:
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 1)
                return self.makekeyhookevent(keysym, event)
        else: ## Not a typable character.
            keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
            if self.isshift.match(matchto):
                self.ison["shift"] = self.ison["shift"] + 1
            elif self.iscaps.match(matchto):
                if self.ison["caps"] == False:
                    self.ison["shift"] = self.ison["shift"] + 1
                    self.ison["caps"] = True
                if self.ison["caps"] == True:
                    self.ison["shift"] = self.ison["shift"] - 1
                    self.ison["caps"] = False
            return self.makekeyhookevent(keysym, event)
    
    def keyreleaseevent(self, event):
        if self.shiftablechar.match(self.lookup_keysym(self.local_dpy.keycode_to_keysym(event.detail, 0))):
            if self.ison["shift"] == False:
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
            else:
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 1)
        else:
            keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
        matchto = self.lookup_keysym(keysym)
        if self.isshift.match(matchto):
            self.ison["shift"] = self.ison["shift"] - 1
        return self.makekeyhookevent(keysym, event)

    def buttonpressevent(self, event):
        return self.makemousehookevent(event)

    def buttonreleaseevent(self, event):
        return self.makemousehookevent(event)


    def mousemoveevent(self, event):
        self.mouse_position_x = event.root_x
        self.mouse_position_y = event.root_y
        return self.makemousehookevent(event)
        
    # need the following because XK.keysym_to_string() only does printable chars
    # rather than being the correct inverse of XK.string_to_keysym()
    def lookup_keysym(self, keysym):
        for name in dir(XK):
            if name.startswith("XK_") and getattr(XK, name) == keysym:
                return name.lstrip("XK_")
        return "[%d]" % keysym

    def asciivalue(self, keysym):
        asciinum = XK.string_to_keysym(self.lookup_keysym(keysym))
        if asciinum < 256:
            return asciinum
        else:
            return 0
    
    def makekeyhookevent(self, keysym, event):
        storewm = self.xwindowinfo()
        if event.type == X.KeyPress:
            #MessageName = "key down"
            ioHubEventID=EventConstants.KEYBOARD_PRESS
        elif event.type == X.KeyRelease:
            #MessageName = "key up"
            ioHubEventID =EventConstants.KEYBOARD_RELEASE
        #return pyxhookkeyevent(int(storewm["handle"], base=16), storewm["name"], storewm["class"], self.lookup_keysym(keysym), self.asciivalue(keysym), False, event.detail, MessageName, event.time,ioHubEventID)
        #  Window, Key, Ascii, KeyID, ScanCode, Time,ioHubEventID        
        return pyxhookkeyevent(int(storewm["handle"], base=16),
                                self.lookup_keysym(keysym), 
                                self.asciivalue(keysym), 
                                0, 
                                event.detail, 
                                event.time,
                                ioHubEventID)
    
    def makemousehookevent(self, event):
        ioHubButtonState=MouseConstants.MOUSE_BUTTON_NONE
        wheelChange=0
        storewm = self.xwindowinfo()
        if event.detail == 0 and event.state==0:
            #MessageName = "mouse move"
            ioHubButtonID=MouseConstants.MOUSE_BUTTON_NONE
            ioHubEventID=EventConstants.MOUSE_MOVE
        elif event.detail == 0 and event.state>0:
            #MessageName = "mouse drag"
            ioHubButtonID=MouseConstants.MOUSE_BUTTON_NONE
            ioHubEventID=EventConstants.MOUSE_MOVE
        elif event.detail == 1:
            #MessageName = "mouse left "
            ioHubButtonID=MouseConstants.MOUSE_BUTTON_LEFT
        elif event.detail == 3:
            #MessageName = "mouse right "
            ioHubButtonID=MouseConstants.MOUSE_BUTTON_RIGHT
        elif event.detail == 2:
            #MessageName = "mouse middle "
            ioHubButtonID=MouseConstants.MOUSE_BUTTON_MIDDLE
        elif event.detail == 5:
            #MessageName = "mouse wheel down "
            ioHubButtonID=MouseConstants.MOUSE_BUTTON_NONE
            ioHubEventID=EventConstants.MOUSE_WHEEL_DOWN
            wheelChange=-1
        elif event.detail == 4:
            #MessageName = "mouse wheel up "
            ioHubButtonID=MouseConstants.MOUSE_BUTTON_NONE
            ioHubEventID=EventConstants.MOUSE_WHEEL_UP
            wheelChange=1
        else:
            #Messag        MessageName=''eName = "mouse " + str(event.detail) + " "
            ioHubButtonID=MouseConstants.MOUSE_BUTTON_NONE
            ioHubEventID=EventConstants.MOUSE_INPUT

        if event.type == X.ButtonPress and wheelChange==0:
            #MessageName = MessageName + "down"
            ioHubEventID=EventConstants.MOUSE_BUTTON_PRESS
            ioHubButtonState=MouseConstants.MOUSE_BUTTON_STATE_PRESSED
        elif event.type == X.ButtonRelease  and wheelChange==0:
            #MessageName = MessageName + "up"
            ioHubEventID=EventConstants.MOUSE_BUTTON_RELEASE
            ioHubButtonState=MouseConstants.MOUSE_BUTTON_STATE_RELEASED
        #return pyxhookmouseevent(int(storewm["handle"], base=16), storewm["name"], storewm["class"], (self.mouse_position_x, self.mouse_position_y), MessageName, event.time,ioHubEventID,ioHubButtonID,ioHubButtonState,wheelChange)
        return pyxhookmouseevent(int(storewm["handle"], base=16), 
                                 (self.mouse_position_x, self.mouse_position_y),
                                 event.time,
                                 ioHubEventID,
                                 ioHubButtonID,
                                 ioHubButtonState,
                                 wheelChange)
    
    def xwindowinfo(self):
        try:
            windowvar = self.local_dpy.get_input_focus().focus
            wmname = windowvar.get_wm_name()
            wmclass = windowvar.get_wm_class()
            wmhandle = str(windowvar)[20:30]
        except:
            ## This is to keep things running smoothly. It almost never happens, but still...
            return {"name":None, "class":None, "handle":'0x00'}
        if (wmname == None) and (wmclass == None):
            try:
                windowvar = windowvar.query_tree().parent
                wmname = windowvar.get_wm_name()
                wmclass = windowvar.get_wm_class()
                wmhandle = str(windowvar)[20:30]
            except:
                ## This is to keep things running smoothly. It almost never happens, but still...
                return {"name":None, "class":None, "handle":'0x00'}
        if wmhandle is None:
            wmhandle='0x00'
        if wmclass == None:
            return {"name":wmname, "class":wmclass, "handle":wmhandle}
        else:
            return {"name":wmname, "class":wmclass[0], "handle":wmhandle}

class pyxhookkeyevent:
    """This is the class that is returned with each key event.f
    It simply creates the variables below in the class.
    
    Window = The handle of the window.
    WindowName = The name of the window.
    WindowProcName = The backend process for the window.
    Key = The key pressed, shifted to the correct caps value.
    Ascii = An ascii representation of the key. It returns 0 if the ascii value is not between 31 and 256.
    KeyID = This is just 0 for now. Under windows, it is the Virtual Key Code, but that's a windows-only thing.
    ScanCode = Please don't use this. It differs for pretty much every type of keyboard. X11 abstracts this information anyway.
    MessageName = "key down", "key up".
    """
    
    def __init__(self, Window, Key, Ascii, KeyID, ScanCode, Time,ioHubEventID):
#    def __init__(self, Window, WindowName, WindowProcName, Key, Ascii, KeyID, ScanCode, MessageName, Time,ioHubEventID):
        self.Window = Window
        #self.WindowName = WindowName
        #self.WindowProcName = WindowProcName
        self.Key = Key
        self.Ascii = Ascii
        self.KeyID = KeyID
        self.ScanCode = ScanCode
        #self.MessageName = MessageName
        self.Time = Time
        self.ioHubEventID=ioHubEventID
    
    def __str__(self):
#        return "Time: " + str(self.Time) +"\nWindow Handle: " + str(self.Window) + "\nWindow Name: " + str(self.WindowName) + "\nWindow's Process Name: " + str(self.WindowProcName) + "\nKey Pressed: " + str(self.Key) + "\nAscii Value: " + str(self.Ascii) + "\nKeyID: " + str(self.KeyID) + "\nScanCode: " + str(self.ScanCode) + "\nMessageName: " + str(self.MessageName) + "\n"
        return "Type:  {0}\nTime: {1}\nKeyID: {2}\nScanCode: {3}\nAscii: {4}\nKey:{5}\nWindow ID: {6}\n".format(
                EventConstants.getName(self.ioHubEventID), self.Time, self.KeyID,
                self.ScanCode,self.Ascii,self.Key,self.Window)
                
class pyxhookmouseevent:
    """This is the class that is returned with each key event.f
    It simply creates the variables below in the class.
    
    Window = The handle of the window.
    WindowName = The name of the window.
    WindowProcName = The backend process for the window.
    Position = 2-tuple (x,y) coordinates of the mouse click
    MessageName = "mouse left|right|middle down", "mouse left|right|middle up".
    """
    
    def __init__(self, Window, Position,Time,ioHubEventID,ioHubButtonID,ioHubButtonState,wheelChange):
#    def __init__(self, Window, WindowName, WindowProcName, Position, MessageName,Time,ioHubEventID,ioHubButtonID,ioHubButtonState,wheelChange):
        self.Window = Window
        #self.WindowName = WindowName
        #self.WindowProcName = WindowProcName
        self.Position = Position
        #self.MessageName = MessageName
        self.Time=Time
        self.ioHubEventID=ioHubEventID
        self.ioHubButtonID=ioHubButtonID
        self.ioHubButtonState=ioHubButtonState
        self.Wheel=wheelChange
    def __str__(self):
#        return "Time: "+str(self.Time)+"\nWindow Handle: " + str(self.Window) + "\nWindow Name: " + str(self.WindowName) + "\nWindow's Process Name: " + str(self.WindowProcName) + "\nPosition: " + str(self.Position) + "\nMessageName: " + str(self.MessageName) + "\n"
        return "Type:  {0}\nTime: {1}\nButton: {2}\nButton State: {3}\nScroll Wheel Change: {4}\nWindow ID: {5}\n".format(
                EventConstants.getName(self.ioHubEventID), self.Time, MouseConstants.getName(self.ioHubButtonID),
                MouseConstants.getName(self.ioHubButtonState),self.Wheel,self.Window)

#######################################################################
#########################END CLASS DEF#################################
#######################################################################

def handle_key_press_event(event):
    print 'handle_key_press_event:\n',event

def handle_key_release_event(event):
    print 'handle_key_release_event:\n',event
    
def handle_mouse_press_event(event):
    print 'handle_mouse_press_event:\n',event

def handle_mouse_release_event(event):
    print 'handle_mouse_release_event:\n',event
    
def handle_mouse_movement_event(event):
    print 'handle_mouse_movement_event:\n',event
    
if __name__ == '__main__':
    hm = HookManager()
    hm.HookKeyboard()
    hm.HookMouse()
    hm.KeyDown = handle_key_press_event
    hm.KeyUp = handle_key_release_event
    hm.MouseAllButtonsDown = handle_mouse_press_event
    hm.MouseAllButtonsUp = handle_mouse_release_event
    hm.MouseAllMotion = handle_mouse_movement_event
    hm.start()
    while 1:
        time.sleep(0.1)
    print 'Exiting.....'
    hm.cancel()
    