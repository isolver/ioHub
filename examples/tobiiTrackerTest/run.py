"""
ioHub
.. file: ioHub/examples/tobiiTrackerTest/run.py
"""

from psychopy import visual
from ioHub.devices import Computer,EventConstants
from ioHub.util import getCurrentDateTimeString
from ioHub.util.experiment import (ioHubExperimentRuntime, DeviceEventTrigger, 
                                   ClearScreen, InstructionScreen, 
                                   pumpLocalMessageQueue)

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

        # Read the current resolution of the monitors screen in pixels.
        # We will set our window size to match the current screen resolution and make it a full screen boarderless window.
        screen_resolution= display.getStimulusScreenResolution()
        # get the index of the screen to create the PsychoPy window in.
        screen_index=display.getStimulusScreenIndex()
        # Read the coordinate space the script author specified in the config file (right now only pix are supported)
        coord_type=display.getDisplayCoordinateType()

        # Create a psychopy window, full screen resolution, full screen mode, pix units, with no boarder, using the monitor
        # profile name 'test monitor, which is created on the fly right now by the script
        self.window = visual.Window(screen_resolution, monitor="testMonitor", units=coord_type, fullscr=True, allowGUI=False, screen=screen_index)
        # Hide the 'system mouse cursor' so we can display a cool gaussian mask for a mouse cursor.
        mouse.setSystemCursorVisibility(False)

        # Create an ordered dictionary of psychopy stimuli. An ordered dictionary is one that returns keys in the order
        # they are added, you you can use it to reference stim by a name or by 'zorder'
        image_name='./images/party.png'
        imageStim = visual.ImageStim(self.window, image=image_name, name='image_stim')
        gaze_dot =visual.GratingStim(self.window,tex=None, mask="gauss", pos=(-2000,-2000),size=(100,100),color='green')

        # create screen states

        # screen state that can be used to just clear the screen to blank.
        self.clearScreen=ClearScreen(self)
        self.clearScreen.setScreenColor((128,128,128))

        self.clearScreen.flip(text='EXPERIMENT_INIT')

        self.clearScreen.sendMessage("IO_HUB EXPERIMENT_INFO START")
        self.clearScreen.sendMessage("ioHub Experiment started {0}".format(getCurrentDateTimeString()))
        self.clearScreen.sendMessage("Experiment ID: {0}, Session ID: {1}".format(self.hub.experimentID,self.hub.experimentSessionID))
        self.clearScreen.sendMessage("Stimulus Screen ID: {0}, Size (pixels): {1}, CoordType: {2}".format(display.getStimulusScreenIndex(),display.getStimulusScreenResolution(),display.getDisplayCoordinateType()))
        self.clearScreen.sendMessage("Calculated Pixels Per Degree: {0} x, {1} y".format(*display.getPPD()))        
        self.clearScreen.sendMessage("IO_HUB EXPERIMENT_INFO END")

        # Sscreen for showing text and waiting for a keyboard response or something
        instuction_text="Press Space Key".center(32)+'\n'+"to Start Experiment.".center(32)
        dtrigger=DeviceEventTrigger(kb,EventConstants.KEYBOARD_CHAR,{'key':'SPACE'})
        timeout=5*60.0
        self.instructionScreen=InstructionScreen(self,instuction_text,dtrigger,timeout)
        self.instructionScreen.setScreenColor((128,128,128))
        #flip_time,time_since_flip,event=self.instructionScreen.switchTo("CALIBRATION_WAIT")

        self.instructionScreen.setText(instuction_text)        
        self.instructionScreen.switchTo("START_EXPERIMENT_WAIT")
                
        tracker.setRecordingState(True)
        self.clearScreen.flip()
        self.hub.delay(0.050)

        # Clear all events from the global event buffer,
        # and from the all device level event buffers.
        self.hub.clearEvents('all')

        # Loop until we get a keyboard event
        while not kb.getEvents():
            gpos=tracker.getLatestGazePosition()
            if gpos:
                gaze_dot.setPos(gpos)
                imageStim.draw()
                gaze_dot.draw()
            else:
                imageStim.draw()
                
            self.window.flip()
            flip_time=Computer.currentSec()            
            self.hub.sendMessageEvent("SYNCTIME %s"%(image_name,),sec_time=flip_time)
        
        self.hub.clearEvents('all')

        # A key was pressed so exit experiment.
        # Wait 250 msec before ending the experiment 
        # (makes it feel less abrupt after you press the key to quit IMO)
        self.hub.delay(0.250)

        tracker.setRecordingState(False)
        tracker.setConnectionState(False)

        self.clearScreen.flip(text='EXPERIMENT_COMPLETE')
        instuction_text="Experiment Finished".center(32)+'\n'+"Press 'SPACE' to Quit.".center(32)+'\n'+"Thank You.".center(32)
        self.instructionScreen.setText(instuction_text)        
        self.instructionScreen.switchTo("EXPERIMENT_COMPLETE_WAIT")

        ### End of experiment logic

##################################################################

def main():
    """
    Creates an instance of the ExperimentRuntime class, checks for an experiment config file name parameter passed in via
    command line, and launches the experiment logic.
    """
    import sys
    import ioHub

    # The module_directory function determines what the current directory is of the function that is passed to it. It is
    # (supposedly) more reliable when running scripts via IDEs etc in terms of reporting the true file location.
    configurationDirectory=ioHub.module_directory(main)

    if len(sys.argv)>1:
        configFile=unicode(sys.argv[1])
        runtime=ExperimentRuntime(configurationDirectory, configFile)
    else:
        runtime=ExperimentRuntime(configurationDirectory, "experiment_config.yaml")

    runtime.start()

if __name__ == "__main__":
    # This code only gets called when the python file is executed, not if it is loaded as a module by another python file

    # run the main function, which starts the experiment runtime
    main()

