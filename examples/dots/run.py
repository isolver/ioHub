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

To Run:
-------

1. Ensure you have followed the ioHub installation instructions
   at http://www.github.com/isolver/iohub/wiki
2. Open a command prompt to the directory containing this file.
3. Start the test program by running:
   python.exe run.py

Any issues or questions, please let me know.
"""
from psychopy import visual, core
from ioHub.client import ioHubConnection, Computer, EventConstants

DOT_COUNT=2000

# Example where ioHub does not use yaml config files specified by user.
# Each device you want enabled is a key, value pair in a dict, where
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

# If you want to enable the ioDataStore, and simply use default parameter
# settings, then just add a'ioDataStore' key to your ioConfig with dict
# containing the experiment_code and session_code to associate all events
# with. Experiment codes are unique within an ioDataStore file, for using
# the same experiment_code multiple times, adds multiple sessions to the
# experiment. Session_codes are 'not' unique, so if you provide the same
# session code across different runs of your experiment script, each run
# will use a different 'session_id' to tag events with.

ioConfig['ioDataStore']=dict(experiment_info=dict(code="IOR_V1.1"),session_info=dict(code="S101-F-R"))

# This creates an ioHub server process and a connection interface for it.
# using the ioConfig defined above.
io=ioHubConnection(ioConfig)

# By default, keyboard, mouse, and display devices are created if you
# do not pass any config info to the ioHubConnection class above.
display=io.devices.display
keyboard=io.devices.keyboard

# set the Screen to use for stimulus presentation (if > one screen is available)
display.setStimulusScreenIndex(0)

# Lets switch to high priority on the experiment process.
Computer.enableHighPriority()

# Create a psychopy window, full screen resolution, full screen mode, pix units,
# with no boarder, using the monitor default profile name used by ioHub,
# which is created on the fly right now by the script. (ioHubDefault)
myWin = visual.Window(display.getStimulusScreenResolution(),
                        monitor=display.getPsychoPyMonitorSettingsName(),
                        units=display.getDisplayCoordinateType(),
                        fullscr=True,
                        allowGUI=False,
                        screen=display.getStimulusScreenIndex())

myWin.setRecordFrameIntervals(True)

#INITIALISE SOME STIMULI
dotPatch =visual.DotStim(myWin,
                        color=(1.0,1.0,1.0),
                        dir=270,
                        nDots=DOT_COUNT,
                        fieldShape='circle',
                        fieldPos=(0.0,0.0),
                        fieldSize=display.getStimulusScreenResolution(),
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
reportedRefreshInterval=display.getStimulusScreenReportedRetraceInterval()*0.001 # convert to sec.msec
print 'Screen has a reported refresh interval of ',reportedRefreshInterval

dotPatch.draw()
message.draw()
[myWin.flip() for i in range(10)]
lastFlipTime=Computer.getTime()
myWin.fps()
exit=False

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
core.quit()
io.quit()### End of experiment logic

