"""
"""

from psychopy import visual

import ioHub
from ioHub import OrderedDict
from ioHub.devices import Computer,Keyboard
from ioHub.constants import KeyboardConstants, EventConstants
from ioHub.util.experiment import ioHubExperimentRuntime

class ExperimentRuntime(ioHubExperimentRuntime):
    """
    Create an experiment using psychopy and the ioHub framework by extending the ioHubExperimentRuntime class. At minimum
    all that is needed in the __init__ for the new class, here called ExperimentRuntime, is the a call to the
    ioHubExperimentRuntime __init__ itself.
    """
    def __init__(self,configFileDirectory, configFile):
        ioHubExperimentRuntime.__init__(self,configFileDirectory,configFile)

    def run(self,*args,**kwargs):
        """
        The run method contains your experiment logic. It is equal to what would be in your main psychopy experiment
        script.py file in a standard psychopy experiment setup. That is all there is too it really.

        By running your script within an extension of the ioHubExperimentRuntime class's run method, you automatically
        get access to some nice features:

        #. The ioHub Client class is accessible by calling self.hub . So to get all currently available events from the
         ioHub event buffer, simply call events = self.hub.getEvents(). There is also a shortcut method, so you can simply call self.getEvents()
         to achieve the same thing, or self.getEvents('kb') to get keyboard events if you named your keyboard device 'kb'.
        #. To clear an event buffer, call getEvents(), as it also clears the buffer, or call self.clearEvents() to clear the global
        event buffer, or self.clearEvents('kb') to clear the keyboard devices event buffer only, assuming you named your keyboard 'kb'.
        #. All devices that have been specified in the iohub .yaml config file are available via self.hub.devices.[device_name]
        where [device_name] is the name of the device you sepified in the config file. So to get all keyboard events since
        the last call to the keyboard device event buffer, you can call kb_events=self.hub.devices.keyboard.getEvents(),
        assuming you named the keyboard device 'keyboard'
        #. As long as the ioHub server is running on the same computer as your experiment, you can access a shared timebase that
        is common between the two processes. self.getSec(), self.getMsec(), or self.getUsec() all will do that.
        #. If you need to pause the execution of your program for a period of time, but want events to be occasionally sent from the
        ioHub server process to your experiment process so nothing is lost when the delay returns, you can use self.msecDelay(), which also
        has built in cpu hogging near the end of the delay so it is quite precise (seems to be within 10's of usec on the i5 I have been testing with)
        #. There are lots of other goodies in the ioHubExperimentRuntime utility class, so check out that classes docs, as well as
        the docs for the ioHubConnection class, which is what is at the end of self.hub.

        Have fun! Please report any issues you find on the bug tracker at github.com/isolver/iohub. Any suggestions for
        improvement are very welcome too, please email me at sds-git@isolver-software.com .

        Thank you. Sol
        """

        # PLEASE REMEMBER , THE SCREEN ORIGIN IS ALWAYS IN THE CENTER OF THE SCREEN,
        # REGARDLESS OF THE COORDINATE SPACE YOU ARE RUNNING IN. THIS MEANS 0,0 IS SCREEN CENTER,
        # -x_min, -y_min is the screen bottom left
        # +x_max, +y_max is the screen top right
        #
        # *** RIGHT NOW, ONLY PIXEL COORD SPACE IS SUPPORTED. THIS WILL BE FIXED SOON. ***

        # Let's make some short-cuts to the devices we will be using in this 'experiment'.
        mouse=self.devices.mouse
        display=self.devices.display
        kb=self.devices.kb
        mbed=self.devices.mbed

        #Computer.enableHighPriority()

        # Set the mouse position to 0,0, which means the 'center' of the screen.
        mouse.setPosition((0.0,0.0))

        # Read the current mouse position (should be 0,0)  ;)
        currentPosition=mouse.getPosition()

        # Read the current resolution of the monitors screen in pixels.
        # We will set our window size to match the current screen resolution and make it a full screen boarderless window.
        screen_resolution= display.getStimulusScreenResolution()

        # Read the coordinate space the script author specified in the config file (right now only pix are supported)
        coord_type=display.getDisplayCoordinateType()

        # get the index of the screen to create the PsychoPy window in.
        screen_index=display.getStimulusScreenIndex()

        # Create a psychopy window, full screen resolution, full screen mode, pix units, with no boarder, using the monitor
        # profile name 'test monitor, which is created on the fly right now by the script
        psychoWindow = visual.Window(screen_resolution, monitor="testMonitor", units=coord_type, fullscr=True, allowGUI=False,screen=screen_index)

        # Hide the 'system mouse cursor' so we can display a cool gaussian mask for a mouse cursor.
        mouse.setSystemCursorVisibility(False)

        # Create an ordered dictionary of psychopy stimuli. An ordered dictionary is one that returns keys in the order
        # they are added, you you can use it to reference stim by a name or by 'zorder'
        psychoStim=OrderedDict()
        psychoStim['grating'] = visual.PatchStim(psychoWindow, mask="circle", size=75,pos=[-100,0], sf=.075)
        psychoStim['fixation'] =visual.PatchStim(psychoWindow, size=25, pos=[0,0], sf=0,  color=[-1,-1,-1], colorSpace='rgb')
        psychoStim['mouseDot'] =visual.GratingStim(psychoWindow,tex=None, mask="gauss", pos=currentPosition,size=(50,50),color='purple')
        psychoStim['mbedReply'] = visual.TextStim(win=psychoWindow, text='', pos = [0,300], height=48, color=[-1,-1,-1], colorSpace='rgb',alignHoriz='left',wrapWidth=800.0)

        # Clear all events from the global event buffer, and from the keyboard event buffer.
        self.hub.clearEvents()
        self.hub.clearEvents('kb')

        QUIT_EXP=False
        # Loop until we get a keyboard event with the space, Enter (Return), or Escape key is pressed.
        while QUIT_EXP is False:

            # for each loop, update the grating phase
            psychoStim['grating'].setPhase(0.05, '+')#advance phase by 0.05 of a cycle

            # and update the mouse contingent gaussian based on the current mouse location
            currentPosition=mouse.getPosition()
            psychoStim['mouseDot'].setPos(currentPosition)


            # redraw the stim
            [psychoStim[stimName].draw() for stimName in psychoStim]

            # flip the psychopy window buffers, so the stim changes you just made get displayed.
            psychoWindow.flip()
            # it is on this side of the call that you know the changes have been displayed, so you can
            # make a call to the ioHub time method and get the time of the flip, as the built in
            # time methods represent both experiment process and ioHub server process time.
            # Most times in ioHub are represented sec.msec format to match that of Psychopy.
            flip_time=Computer.currentSec()

            # send a message to the iohub with the message text that a flip occurred and what the mouse position was.
            # since we know the ioHub server time the flip occurred on, we can set that directly in the event.
            self.hub.sendMessageEvent("Flip %s"%(str(currentPosition),), sec_time=flip_time)

            # get any new keyboard char events from the keyboard device


            #char_events=kb.getEvents(event_type_id=EventConstants.KEYBOARD_CHAR)
            # for each new keyboard character event, check if it matches one of the end example keys.
            for k in kb.getEvents(EventConstants.KEYBOARD_CHAR):
                print 'KeyboardCharEvent: ',k
                if k.key in ['ESCAPE', ]:
                    print 'Quit key pressed: ',k.key,' for ',k.duration,' sec.'
                    QUIT_EXP=True
                elif k.key == 'SPACE':
                    mbed.setLEDStates(0,0,0,0)
                elif k.key in ['ENTER', 'RETURN']:
                    mbed.setLEDStates(1,0,1,0)
                elif k.key in ['b', 'B']:
                    mbed.setLEDStates([0,.500,-1],[1,.500,-1],[1,1.5,0],[1,1.500,5])
                elif k.key in ['s', 'S']:
                    mbed.enableEventReporting(True)
                elif k.key in ['e', 'E']:
                    mbed.enableEventReporting(False)
                elif k.key in ['g', 'G']:
                    print "Current Analog Output value is: ", mbed.getAnalogOutputValue()
                elif k.key in ['a', 'A']:
                    print "set Analog Output value to 50 percent: ", mbed.setAnalogOutputChannel(0.5)
                elif k.key in ['d', 'D']:
                    print "get digital inputs values: ", mbed.getDigitalPins()
                elif k.key in ['w', 'W']:
                    print "set digital inputs values: ", mbed.setDigitalPins(1,0,1,0,1,0,1,0)

        # wait 250 msec before ending the experiment (makes it feel less abrupt after you press the key)
        actualDelay=self.hub.delay(0.250)
        print "Delay requested %.6f, actual delay %.6f, Diff: %.6f"%(0.250,actualDelay,actualDelay-0.250)

        # for fun, test getting a bunch of events at once, likely causing a mutlipacket getEvents()
        stime = Computer.currentSec()
        events=self.hub.getEvents()
        etime=Computer.currentSec()
        print 'event count: ', len(events),' delay (msec): ',(etime-stime)*1000.0

        # _close neccessary files / objects, 'disable high priority.
        psychoWindow.close()

        ### End of experiment logic

##################################################################

def main(configurationDirectory):
    """
    Creates an instance of the ExperimentRuntime class, checks for an experiment config file name parameter passed in via
    command line, and launches the experiment logic.
    """
    import sys
    if len(sys.argv)>1:
        configFile=unicode(sys.argv[1])
        runtime=ExperimentRuntime(configurationDirectory, configFile)
    else:
        runtime=ExperimentRuntime(configurationDirectory, "experiment_config.yaml")

    runtime.start()

if __name__ == "__main__":
    # This code only gets called when the python file is executed, not if it is loaded as a module by another python file
    #
    # The module_directory function determines what the current directory is of the function that is passed to it. It is
    # more reliable when running scripts via IDEs etc in terms of reporting the true file location.
    configurationDirectory=ioHub.module_directory(main)

    # run the main function, which starts the experiment runtime
    main(configurationDirectory)

