"""
ioHub
.. file: ioHub/examples/simple/simpleTrackerTest.py
"""

from psychopy import visual

import ioHub
from ioHub import OrderedDict
from ioHub.devices import Computer
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
        """

        # PLEASE REMEMBER , THE SCREEN ORIGIN IS ALWAYS IN THE CENTER OF THE SCREEN,
        # REGARDLESS OF THE COORDINATE SPACE YOU ARE RUNNING IN. THIS MEANS 0,0 IS SCREEN CENTER,
        # -x_min, -y_min is the screen bottom left
        # +x_max, +y_max is the screen top right
        #
        # RIGHT NOW, ONLY PIXEL COORD SPACE IS SUPPORTED. THIS WILL BE FIXED SOON.

        # Let's make some short-cuts to the devices we will be using in this 'experiment'.


        tracker=self.hub.devices.tracker
        display=self.hub.devices.display
        kb=self.hub.devices.kb
        mouse=self.hub.devices.mouse

        
        tracker.runSetupProcedure()
        self.hub.clearEvents('all')
        self.hub.delay(0.050)

        current_gaze=[0,0]

        # get the index of the screen to create the PsychoPy window in.
        screen_index=display.getStimulusScreenIndex()

        #if screen_index == 0:
        #    screen_index=1
        #else:
        #    screen_index=0 


        # Create a psychopy window, full screen resolution, full screen mode, pix units, with no boarder, using the monitor
        # profile name 'test monitor, which is created on the fly right now by the script
        psychoWindow = visual.Window(display.getStimulusScreenResolution(), monitor="testMonitor",
                                                units=display.getDisplayCoordinateType(),
                                                fullscr=True, allowGUI=False, screen=screen_index)

        # Hide the 'system mouse cursor' so we can display a cool gaussian mask for a mouse cursor.
        mouse.setSystemCursorVisibility(False)

        # Create an ordered dictionary of psychopy stimuli. An ordered dictionary is one that returns keys in the order
        # they are added, you you can use it to reference stim by a name or by 'zorder'
        psychoStim=OrderedDict()
        psychoStim['grating'] = visual.PatchStim(psychoWindow, mask="circle", size=75,pos=[-100,0], sf=.075)
        psychoStim['fixation'] =visual.PatchStim(psychoWindow, size=25, pos=[0,0], sf=0,  color=[-1,-1,-1], colorSpace='rgb')
        psychoStim['gazePosText'] =visual.TextStim(psychoWindow, text=str(current_gaze), pos = [100,0], height=48, color=[-1,-1,-1], colorSpace='rgb',alignHoriz='left',wrapWidth=300)
        psychoStim['gazePos'] =visual.GratingStim(psychoWindow,tex=None, mask="gauss", pos=current_gaze,size=(50,50),color='purple')

        [psychoStim[stimName].draw() for stimName in psychoStim]

        Computer.enableHighPriority(True)
        #self.setProcessAffinities([0,1],[2,3])

        tracker.setRecordingState(True)
        self.hub.delay(0.050)

        # Clear all events from the ioHub event buffers.
        self.hub.clearEvents('all')


        # Loop until we get a keyboard event
        while len(kb.getEvents())==0:

            # for each loop, update the grating phase
            psychoStim['grating'].setPhase(0.05, '+')#advance phase by 0.05 of a cycle

            # and update the gaze contingent gaussian based on the current gaze location

            current_gaze=tracker.getLatestGazePosition()
            current_gaze=int(current_gaze[0]),int(current_gaze[1])
               
            psychoStim['gazePos'].setPos(current_gaze)
            psychoStim['gazePosText'].setText(str(current_gaze))

            # this is short hand for looping through the psychopy stim list and redrawing each one
            # it is also efficient, may not be as user friendly as:
            # for stimName, stim in psychoStim.itervalues():
            #    stim.draw()
            # which does the same thing if you like and is probably just as efficent.
            [psychoStim[stimName].draw() for stimName in psychoStim]

            # flip the psychopy window buffers, so the stim changes you just made get displayed.
            psychoWindow.flip()
            # it is on this side of the call that you know the changes have been displayed, so you can
            # make a call to one of the built-in time methods and get the event time of the flip, as the built in
            # time methods represent both experiment process and ioHub server process time.
            # Most times in ioHub are represented as unsigned 64 bit integers when they are saved, so using usec
            # as a timescale is appropriate.
            flip_time=Computer.currentSec()

            # send a message to the iohub with the message text that a flip occurred and what the mouse position was.
            # since we know the ioHub server time the flip occurred on, we can set that directly in the event.
            self.hub.sendMessageEvent("Flip %s"%(str(current_gaze),),sec_time=flip_time)

        # a key was pressed so the loop was exited. We are clearing the event buffers to avoid an event overflow ( currently known issue)
        self.hub.clearEvents('all')

        tracker.setRecordingState(False)

        # wait 250 msec before ending the experiment (makes it feel less abrupt after you press the key)
        self.hub.delay(0.250)
        tracker.setConnectionState(False)

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

