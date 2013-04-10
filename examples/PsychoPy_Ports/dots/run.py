"""
ioHub
.. file: ioHub/examples/dots/run.py

------------------------------------------------------------------------------------------------------------------------

dots
++++

Overview:
---------

This script is a copy of the PsychoPy 'dots' demo with
ioHub integration.
"""
from psychopy import visual, core
from ioHub import quickStartHubServer
from ioHub.client import Computer
from ioHub.util.experiment import FullScreenWindow
DOT_COUNT=1000

# Example where ioHub does not use yaml config files specified by user.

import random
io=quickStartHubServer("exp_code","sess_%d"%(random.randint(1,10000)))

# By default, keyboard, mouse, and display devices are created if you
# do not pass any config info to the ioHubConnection class above.
display=io.devices.display
keyboard=io.devices.keyboard

# Create a psychopy window, full screen resolution, full screen mode, pix units,
# with no boarder, using the monitor default profile name used by ioHub,
# which is created on the fly right now by the script. (ioHubDefault)
myWin= FullScreenWindow(display)

#INITIALISE SOME STIMULI
dotPatch =visual.DotStim(myWin,
                        color=(1.0,1.0,1.0),
                        dir=270,
                        nDots=DOT_COUNT,
                        fieldShape='circle',
                        fieldPos=(0.0,0.0),
                        fieldSize=display.getPixelResolution(),
                        dotLife=5, #number of frames for each dot to be drawn
                        signalDots='same', #are the signal dots the 'same' on each frame? (see Scase et al)
                        noiseDots='direction', #do the noise dots follow random- 'walk', 'direction', or 'position'
                        speed=3.0,
                        coherence=90.0
                        )

message =visual.TextStim(myWin,
                         text='Hit Q to quit',
                         pos=(0,-0.5)
                         )

Computer.enableHighPriority(disable_gc=False)

io.clearEvents('all')

dur=5*60
endTime=Computer.currentTime()+dur
fcounter=0
reportedRefreshInterval=display.getRetraceInterval()
print 'Screen has a reported refresh interval of ',reportedRefreshInterval

dotPatch.draw()
message.draw()
[myWin.flip() for i in range(10)]
lastFlipTime=Computer.getTime()
myWin.fps()
exit=False

myWin.setRecordFrameIntervals(True)

while not exit and endTime>Computer.currentTime():
    dotPatch.draw()
    message.draw()
    myWin.flip()#redraw the buffer
    flipTime=Computer.getTime()
    IFI=flipTime-lastFlipTime
    lastFlipTime=flipTime
    fcounter+=1

    if IFI > reportedRefreshInterval*1.5:
        print "Frame {0} dropped: IFI of {1}".format(fcounter,IFI)

    #handle key presses each frame
    for event in keyboard.getEvents():
        if event.key in ['ESCAPE','Q','q']:
            exit=True
            break

Computer.disableHighPriority()
myWin.close()

io.quit()### End of experiment logic

core.quit()