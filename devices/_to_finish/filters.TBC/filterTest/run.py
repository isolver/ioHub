"""

"""

from psychopy import core, visual

import ioHub
from ioHub.devices import Computer
from ioHub.constants import EventConstants
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
        # PLEASE REMEMBER , THE SCREEN ORIGIN IS ALWAYS IN THE CENTER OF THE SCREEN,
        # REGARDLESS OF THE COORDINATE SPACE YOU ARE RUNNING IN. THIS MEANS 0,0 IS SCREEN CENTER,
        # -x_min, -y_min is the screen bottom left
        # +x_max, +y_max is the screen top right
        #
        # *** RIGHT NOW, ONLY PIXEL COORD SPACE IS SUPPORTED. THIS WILL BE FIXED SOON. ***
        """

        # Let's make some short-cuts to the devices we will be using in this 'experiment'.
        mouse=self.devices.mouse
        display=self.devices.display
        kb=self.devices.kb
        tracker=self.devices.tracker

        tracker.runSetupProcedure()
        self.hub.clearEvents('all')
        self.hub.delay(0.050)

        tracker.setRecordingState(True)

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


        # Set the mouse position to 0,0, which means the 'center' of the screen.
        mouse.setPosition((0.0,0.0))

        # Read the current mouse position (should be 0,0)  ;)
        currentPosition=mouse.getPosition()

        # Hide the 'system mouse cursor' so we can display a cool gaussian mask for a mouse cursor.
        mouse.setSystemCursorVisibility(False)

        # Create an ordered dictionary of psychopy stimuli. An ordered dictionary is one that returns keys in the order
        # they are added, you you can use it to reference stim by a name or by 'zorder'
        psychoStim=dict()
        psychoStim['grating'] =  visual.PatchStim(psychoWindow, mask="circle", size=75,pos=[-100,0], sf=.075)
        psychoStim['fixation'] = visual.PatchStim(psychoWindow, size=25, pos=[0,0], sf=0,  color=[-1,-1,-1], colorSpace='rgb')
        psychoStim['mouseDot'] = visual.GratingStim(psychoWindow,tex=None, mask="gauss", pos=currentPosition,size=(50,50),color='purple')

        psychoWindow.flip()

        # Clear all events from the global event buffer, and from the keyboard event buffer.
        self.hub.clearEvents('all')

        QUIT_EXP=False
        # Loop until we get a keyboard event with the space, Enter (Return), or Escape key is pressed.
        while QUIT_EXP is False:

            # for each loop, update the grating phase
            psychoStim['grating'].setPhase(0.05, '+')#advance phase by 0.05 of a cycle

            # and update the mouse contingent gaussian based on the current mouse location
            currentPosition=mouse.getPosition()
            psychoStim['mouseDot'].setPos(currentPosition)


            # redraw the stim
            for stimObj in psychoStim.values():
                stimObj.draw()

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

            # for each new keyboard event, check if it matches one of the end example keys.
            for k in kb.getEvents(EventConstants.KEYBOARD_PRESS):
                #print 'keyevent namedtuple: ',k
                #print 'KEY: ',k.key
                if k.key in ['ESCAPE', ]:
                    print 'Quit key pressed: ',k.key
                    QUIT_EXP=True
                    break

        tracker.setRecordingState(False)
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

