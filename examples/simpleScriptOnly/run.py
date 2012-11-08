"""
ioHub
.. file: ioHub/examples/simpleScriptOnly/run.py

-------------------------------------------------------------------------------

simpleScriptOnly
++++++++++++++++

Overview:
---------

This script is implemented using psychopy and the core ioHubConnection class 
only. It shows how to integrate the ioHub into a PsychoPy script in a minimal
was, without using any of the ioHub's extra features such as automatic 
event storage.

To Run:
-------

1. Ensure you have followed the ioHub installation instructions 
   at http://www.github.com/isolver/iohub/wiki
2. Open a command prompt to the directory containing this file.
3. Start the test program by running:
   python.exe run.py

"""

from collections import OrderedDict

from psychopy import visual, core

import ioHub
from ioHub.client import ioHubConnection, Computer, EventConstants

# PLEASE REMEMBER , THE SCREEN ORIGIN IS ALWAYS IN THE CENTER OF THE SCREEN,
# REGARDLESS OF THE COORDINATE SPACE YOU ARE RUNNING IN. THIS MEANS 0,0 IS SCREEN CENTER,
# -x_min, -y_min is the screen bottom left
# +x_max, +y_max is the screen top right
#
# *** RIGHT NOW, ONLY PIXEL COORD SPACE IS SUPPORTED. THIS WILL BE FIXED SOON. ***

# create the ioHub Config

# each device you want enabled is a key, value pair in a dict, where 
# the key is the Class name of the device you want enabled, and the value
# is a dict of configuration properties for that device. If you provide 
# an empty dict() as a device key's value, the default properties for that
# device will be loaded.
# This will enable streaming of data for each device to the experiment 
# process, but will not enable saving of device events by the ioHub in 
# the ioDataStore.
devices=dict(Keyboard={},Display={},Mouse={})

# The dict of devices is assigned to the ioConfigs 'monitor_devices' key
ioConfig=dict(monitor_devices=devices)

# 'If' you want to enable the ioDataStore, and simply use default parameter
# settings, then just add a'ioDataStore' key to your ioConfig with dict 
# containing the experiment_code and session_code to associate all events
# with. Experiment codes are unique within an ioDataStore file, for using
# the same experiment_code multiple times, adds multiple sessions to the 
# experiment. Session_codes are 'not' unique, so if you provide the same
# session code across different runs of your experiment script, each run
# will use a different 'session_id' to tag events with.

#ioConfig['ioDataStore']=dict(experiment_info=dict(code="IOR_V1.1"),session_info=dict(code="S101-F-R"))

# This creates an ioHub server process and a connection interface for it. 
# using the ioConfig defined above. 
io=ioHubConnection(ioConfig)
        
# By default, keyboard, mouse, and display devices are created if you 
# do not pass any config info to the ioHubConnection class above.        
mouse=io.devices.mouse
display=io.devices.display
keyboard=io.devices.keyboard

# set the Screen to use for stimulus presentation (if > one screen is contented)
display.setStimulusScreenIndex(0)

# Lets switch to high priority on the psychopy process.
Computer.enableHighPriority()

# Create a psychopy window, full screen resolution, full screen mode, pix units,
# with no boarder, using the monitor default profile name used by ioHub, 
# which is created on the fly right now by the script. (ioHubDefault)
psychoWindow = visual.Window(display.getStimulusScreenResolution(), 
                             monitor=display.getPsychoPyMonitorSettingsName(), 
                             units=display.getDisplayCoordinateType(), 
                             fullscr=True, 
                             allowGUI=False,
                             screen=display.getStimulusScreenIndex())

# Hide the 'system mouse cursor' so we can display a cool gaussian mask for a mouse cursor.
mouse.setSystemCursorVisibility(False)

# Set the mouse position to 0,0, which means the 'center' of the screen.
mouse.setPosition((0.0,0.0))

# Create an ordered dictionary of psychopy stimuli. An ordered dictionary is 
# one that returns keys in the order they are added, you you can use it to 
# reference stim by a name or by 'zorder'

psychoStim=OrderedDict()

psychoStim['grating'] = visual.PatchStim(psychoWindow, mask="circle", 
                                        size=75,pos=[-100,0], sf=.075)

psychoStim['fixation'] =visual.PatchStim(psychoWindow, size=25, 
                                        pos=[0,0], sf=0,  
                                        color=[-1,-1,-1], 
                                        colorSpace='rgb')
                                        
psychoStim['mouseDot'] =visual.GratingStim(psychoWindow,tex=None,
                                            mask="gauss", 
                                            pos=mouse.getPosition(),
                                            size=(50,50),color='purple')

# Clear all events from the global event buffer, 
# and from the device level event buffers.
io.clearEvents('all')

[psychoStim[stimName].draw() for stimName in psychoStim]
psychoWindow.flip()
first_flip_time=Computer.currentSec()

QUIT_EXP=False
# Loop until we get a keyboard event with the space, Enter (Return), 
# or Escape key is pressed.
while QUIT_EXP is False:

    # for each loop, update the grating phase
    # advance phase by 0.05 of a cycle
    psychoStim['grating'].setPhase(0.05, '+')

    # and update the mouse contingent gaussian based on the 
    # current mouse location
    psychoStim['mouseDot'].setPos(mouse.getPosition())

    #draw all the stim
    [psychoStim[stimName].draw() for stimName in psychoStim]

    # flip the psychopy window buffers, so the 
    # stim changes you just made get displayed.
    psychoWindow.flip()
    # It is on this side of the call that you know the changes have 
    # been displayed, so you can make a call to one of the built-in time 
    # methods and get the event time of the flip, as the built in
    # time methods represent both experiment process and ioHub server
    # process time. NOTE: Integration between the ioHub times and 
    # psychopy clock times needs to be done, so for now when using ioHub
    # you should use the ioHub times so that the event hub_time fields
    # can be related to Computer.getTime() current time readings.
    flip_time=Computer.currentSec()

    # get any new keyboard events from the keyboard device
    # This gets key press and key release events, right now, there is 
    # no way to get events on only 1 type from a device, you have to filter
    # them 
    kb_events=keyboard.getEvents()
    if len(kb_events)>0:
        # for each new keyboard event, check if it matches one 
        # of the end example keys.
        for k in kb_events:
            # key: the string representation of the key pressed, 
            #      A-Z if a-zA-Z pressed, 0-9 if 0-9 pressed ect.
            #      To get the mapping from a key_id to a key string, use
            #
            #      key=EventConstants.IDToName(key_event['key_id']) BTW
            #
            # char: the ascii char for the key pressed. This field factors
            #       in if shift was also pressed or not
            #       when the char was typed, so typing a 's' == char 
            #       field of 's', while typing SHIFT+s == char
            #       field of 'S'. This is in contrast to the key field, 
            #       which always returns upper case values
            #       regardless of shift value. If the character pressed 
            #       is not an ascii printable character,
            #       this field will print junk, hex, or who knows what 
            #       else at this point.
            if k['type'] == EventConstants.KEYBOARD_PRESS_EVENT \
            and k['key'] in ['Space','Return','Escape']:
                print 'Quit key pressed: ',k['key']
                QUIT_EXP=True

print "You played around with the mouse cursor for {0} seconds.".format(
                                            k['hub_time']-first_flip_time)
print ''

# wait 250 msec before ending the experiment 
# (makes it feel less abrupt after you press the key)
actualDelay=io.delay(0.250)
print "Delay requested %.6f, actual delay %.6f, Diff: %.6f"%(
                                        0.250,actualDelay,actualDelay-0.250)
print ''

# for fun, test getting a bunch of events at once, 
# likely causing a mutlipacket getEvents() since we have not cleared the
# event buffer or retrieved events from anything but the keyboard since
# the start.
stime = Computer.currentSec()
events=io.getEvents()
etime=Computer.currentSec()
print 'event count: ', len(events),' delay (msec): ',(etime-stime)*1000.0

# close neccessary files / objects, 'disable high priority.
Computer.disableHighPriority()
 
psychoWindow.close()

# be sure to shutdown your ioHub server!
io.shutdown()
core.quit()
### End of experiment logic

