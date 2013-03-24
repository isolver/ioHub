# -*- coding: utf-8 -*-
"""
Converted PsychoPy mouse.py demo script to use ioHub package for keyboard and
mouse input.
"""
from psychopy import visual, core
from ioHub import quickStartHubServer
from ioHub.constants import EventConstants
from ioHub.util.experiment import FullScreenWindow

import random
io=quickStartHubServer("exp_code","sess_%d"%(random.randint(1,10000)))

# get 'shortcut' handles to the devices you will be using in the experiment:
myMouse=io.devices.mouse
display=io.devices.display
myKeyboard=io.devices.keyboard

myMouse.setSystemCursorVisibility(False)

myWin = FullScreenWindow(display)

screen_resolution=display.getPixelResolution()

display_index=display.getIndex()

#INITIALISE SOME STIMULI
fixSpot = visual.PatchStim(myWin,tex="none", mask="gauss",
        pos=(0,0), size=(30,30),color='black', autoLog=False)
grating = visual.PatchStim(myWin,pos=(300,0),
                           tex="sin",mask="gauss",
                           color=[1.0,0.5,-1.0],
                           size=(150.0,150.0), sf=(0.01,0.0),
                           autoLog=False)#this stim changes too much for autologging to be useful

message = visual.TextStim(myWin,pos=(0.0,-250),alignHoriz='center',
                          alignVert='center',height=40,
                          text='move=mv-spot, left-drag=SF, right-drag=mv-grating, scroll=ori',
                          autoLog=False,wrapWidth=screen_resolution[0]*.9)

last_wheelPosY=0

while True: #continue until keypress
    #handle key presses each frame
    for event in myKeyboard.getEvents(EventConstants.KEYBOARD_PRESS):
        if event.key in ['ESCAPE','q']:
            io.quit()
            core.quit()

    # get the 'current' mouse position
    # note that this is 'not' the same as getting mouse motion events
    position, posDelta , current_display_index= myMouse.getPositionAndDelta(return_display_index=True)
    
    if current_display_index == display_index:
        mouse_dX,mouse_dY=posDelta
    
        # get the 'current' mouse position
        # note that this is 'not' the same as getting mouse button events
        b1, b2, b3 = myMouse.getCurrentButtonStates()
        if (b1):
            grating.setSF(mouse_dX/display.getPixelsPerDegree()[0]/20.0, '+')
        elif (b3):
            grating.setPos(position)
            
        if not b1 and not b2 and not b3:
            fixSpot.setPos(position)
            
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
