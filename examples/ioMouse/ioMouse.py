# -*- coding: utf-8 -*-
"""
Converted PsychoPy mouse.py demo script to use ioHub package for keyboard and
mouse input.
"""
from psychopy import visual, core,misc,monitors
from ioHub.client import ioHubConnection, EventConstants

# Specify devices you want to use in the ioHub
devices=dict(Keyboard={},Display={},Mouse={})

# Create an ioHub configuration dictionary.
ioConfig=dict(monitor_devices=devices)

# Enable saving of all keyboard and mouse events to the 'ioDataStore'
ioConfig['ioDataStore']=dict(experiment_info=dict(code="mouseExp"),session_info=dict(code="S1"))

# Start the ioHub Server
io=ioHubConnection(ioConfig)

# get 'shortcut' handles to the devices you will be using in the experiment:
myMouse=io.devices.mouse
display=io.devices.display
myKeyboard=io.devices.keyboard

#create a 'fullscreen' window to draw in
screen_resolution=display.getStimulusScreenResolution()

monitor= monitors.Monitor("expMonitor", width=490,distance=500)       
monitor.setSizePix(screen_resolution)
myWin = visual.Window(screen_resolution, allowGUI=False, fullscr=True,monitor=monitor)

#INITIALISE SOME STIMULI
fixSpot = visual.PatchStim(myWin,tex="none", mask="gauss",
        pos=(0,0), size=(0.05,0.05),color='black', autoLog=False)
grating = visual.PatchStim(myWin,pos=(0.5,0),
                           tex="sin",mask="gauss",
                           color=[1.0,0.5,-1.0],
                           size=(1.0,1.0), sf=(3,0),
                           autoLog=False)#this stim changes too much for autologging to be useful

message = visual.TextStim(myWin,pos=(-0.95,-0.9),alignHoriz='left',height=0.08,
    text='left-drag=SF, right-drag=pos, scroll=ori',
    autoLog=False)

last_wheelPosY=0

while True: #continue until keypress
    #handle key presses each frame
    for event in myKeyboard.getEvents(EventConstants.KEYBOARD_PRESS):
        if event.key in ['ESCAPE','q']:
            io.quit()
            core.quit()
            
    # get the 'current' mouse position
    # note that this is 'not' the same as getting mouse motion events
    position, posDelta = myMouse.getPositionAndDelta()
    mouse_dX,mouse_dY=posDelta
    position=misc.pix2deg(position[0],monitor),misc.pix2deg(position[1],monitor)
    # get the 'current' mouse position
    # note that this is 'not' the same as getting mouse button events
    b1, b2, b3 = myMouse.getCurrentButtonStates()
    if (b1):
        grating.setSF( misc.pix2deg(mouse_dX,monitor), '+')
    elif (b3):
        grating.setPos(position)
        
    # Handle the wheel(s):
    # Y is the normal mouse wheel, and is what is supported by ioHub 
    # (until OSX is also supported by ioHub I suppose)
    # ioHub tracks the absolute amount of wheel movement made, so it can be
    # treated like a range or 'position'. Here we track the delta wheel pos
    # delta. 
    # TODO: No reason why ioHub can not track both absolution and delta info. 
    wheelPosY = myMouse.getVerticalScroll()
    wheel_dY=wheelPosY-last_wheelPosY
    last_wheelPosY=wheelPosY
    grating.setOri(wheel_dY*5, '+')
    
    io.clearEvents()#get rid of other, unprocessed events
    
    #do the drawing
    fixSpot.draw()
    grating.setPhase(0.05, '+')#advance 0.05cycles per frame
    grating.draw()
    message.draw()
    myWin.flip()#redraw the buffer
