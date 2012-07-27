"""
XioHub Linux Keyboard Class and Event Generator

Part of the XioHub Module
Copyright (C) 2012 Sol Simpson 
Distributed under the terms of the GNU General Public License 
(GPL version 3 or any later version). 

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors,
   please see credits section of documentation.
"""
"""
import sys
import os

from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq

local_dpy = display.Display()
record_dpy = display.Display()

def record_callback(reply):
    if reply.category != record.FromServer:
        print '>> RETURN: reply.category != record.FromServer'
        return
    if reply.client_swapped:
        print ">> RETURN: received swapped protocol data, cowardly ignored"
        return
    if not len(reply.data) or ord(reply.data[0]) < 2:
        print ">> RETURN: Not an event", reply.data
        return

    data = reply.data
    clients=local_dpy.screen().root.query_tree().children
    while len(data):
        event, data = rq.EventField(None).parse_binary_value(data, record_dpy.display, None, None)
        if event.type == X.ButtonRelease:
            printEvent('ButtonRelease',event,clients)
        elif event.type == X.ButtonPress:
            printEvent('ButtonPress',event,clients)
        elif event.type in [X.KeyPress, X.KeyRelease]:
            pr = event.type == X.KeyPress and "Press" or "Release"
            printEvent("KEY_"+pr,event,clients)
         else:
            print '*********************************'
            print 'Type: [not specifically handled]', event.type
            print "Event.time: ",event.time
            print "Event.detail: ",event.detail
            print "Event.root_x: ",event.root_x
            print "Event.root_y: ",event.root_y
            print "Event.state: ",event.state
            print 'Data.root: ', event.root
            print 'Data.window: ', event.window

#-----------------------------------------------------------------------

def printEvent(typeName, event,clients):
        print '*********************************'
        print 'Type:',typeName, event.type
        print "Event.time: ",event.time
        print "Event.detail: ",event.detail
        print "Event.root_x: ",event.root_x
        print "Event.root_y: ",event.root_y
        print "Event.state: ",event.state
        print 'Data.root: ', event.root
        print 'Data.window: ', event.window
        for win in clients:
            if win==local_dpy.screen().root.query_pointer().child:
                print '** Hit: ', win
    
# Check if the extension is present
if not record_dpy.has_extension("RECORD"):
    print "RECORD extension not found"
    sys.exit(1)
r = record_dpy.record_get_version(0, 0)
print "RECORD extension version %d.%d" % (r.major_version, r.minor_version)

ctx = record_dpy.record_create_context(
        0,
        [record.CurrentClients],
        [{
                'core_requests': (0, 0),
                'core_replies': (0, 0),
                'ext_requests': (0, 0, 0, 0),
                'ext_replies': (0, 0, 0, 0),
                'delivered_events': (0, 0),
                'device_events': (X.KeyPress, X.MotionNotify),
                'errors': (0, 0),
                'client_started': False,
                'client_died': False,
        }])

record_dpy.record_enable_context(ctx, record_callback)
record_dpy.record_free_context(ctx)
"""
