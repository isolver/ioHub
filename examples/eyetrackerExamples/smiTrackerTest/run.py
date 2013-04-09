"""
ioHub
.. file: ioHub/examples/smiTrackerTest/run.py
"""

from psychopy import visual
import ioHub
from ioHub.devices import Computer
from ioHub.constants import EventConstants, EyeTrackerConstants
from ioHub.util import getCurrentDateTimeString
from ioHub.util.experiment import (ioHubExperimentRuntime, DeviceEventTrigger, 
                                   ClearScreen, InstructionScreen, 
                                   FullScreenWindow)

class ExperimentRuntime(ioHubExperimentRuntime):
    """
    Create an experiment using psychopy and the ioHub framework by extending the ioHubExperimentRuntime class. At minimum
    all that is needed in the __init__ for the new class, here called ExperimentRuntime, is the a call to the
    ioHubExperimentRuntime __init__ itself.
    """
    def run(self,*args,**kwargs):
        """
        The run method contains your experiment logic. It is equal to what would be in your main psychopy experiment
        script.py file in a standard psychopy experiment setup. That is all there is too it really.
        """

        # Let's make some short-cuts to the devices we will be using in this 'experiment'.
        tracker=self.hub.devices.tracker
        display=self.hub.devices.display
        kb=self.hub.devices.kb
        mouse=self.hub.devices.mouse

        result=tracker.runSetupProcedure()
        if isinstance(result,dict):
            print "Validation Accuracy Results: ", result
        elif result != EyeTrackerConstants.EYETRACKER_OK:
            print "An error occurred during eye tracker user setup: ",EyeTrackerConstants.getName(result)
            
        # Create a psychopy window, full screen resolution, full screen mode...
        self.window = FullScreenWindow(display)

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
        self.clearScreen.sendMessage("Stimulus Screen ID: {0}, Size (pixels): {1}, CoordType: {2}".format(display.getIndex(),display.getPixelResolution(),display.getCoordinateType()))
        self.clearScreen.sendMessage("Calculated Pixels Per Degree: {0} x, {1} y".format(*display.getPixelsPerDegree()))        
        self.clearScreen.sendMessage("IO_HUB EXPERIMENT_INFO END")

        # Screen for showing text and waiting for a keyboard response or something
        instuction_text="Press Space Key".center(32)+'\n'+"to Start Experiment.".center(32)
        dtrigger=DeviceEventTrigger(kb,EventConstants.KEYBOARD_CHAR,{'key':'SPACE'})
        timeout=5*60.0
        self.instructionScreen=InstructionScreen(self,instuction_text,dtrigger,timeout)
        self.instructionScreen.setScreenColor((128,128,128))
        #flip_time,time_since_flip,event=self.instructionScreen.switchTo("CALIBRATION_WAIT")

        self.instructionScreen.setText(instuction_text)        
        self.instructionScreen.switchTo("START_EXPERIMENT_WAIT")
        
        for t in range(5): 
            self.hub.clearEvents('all')
            instuction_text="Press Space Key To Start Trial %d"%t
            self.instructionScreen.setText(instuction_text)        
            self.instructionScreen.switchTo("START_TRIAL")

            tracker.setRecordingState(True)
            self.clearScreen.flip()
            self.hub.clearEvents('all')
    
            # Loop until we get a keyboard event
            runtrial=True
            while runtrial:
                gpos=tracker.getLastGazePosition()
                if gpos:
                    gaze_dot.setPos(gpos)
                    imageStim.draw()
                    gaze_dot.draw()
                else:
                    imageStim.draw()
                    
                flip_time=self.window.flip()          
                self.hub.sendMessageEvent("SYNCTIME %s"%(image_name,),sec_time=flip_time)
                
                keys=kb.getEvents(EventConstants.KEYBOARD_CHAR)
                for key in keys:
                    if key.key == 'SPACE':
                       runtrial=False
                       break
                   
            self.clearScreen.flip(text='TRIAL_%d_DONE'%t)
            tracker.setRecordingState(False)

        self.clearScreen.flip(text='EXPERIMENT_COMPLETE')
        instuction_text="Experiment Finished".center(32)+'\n'+"Press 'SPACE' to Quit.".center(32)+'\n'+"Thank You.".center(32)
        self.instructionScreen.setText(instuction_text)        
        self.instructionScreen.switchTo("EXPERIMENT_COMPLETE_WAIT")

        # A key was pressed so exit experiment.
        # Wait 250 msec before ending the experiment 
        # (makes it feel less abrupt after you press the key to quit IMO)
        self.hub.wait(0.250)

        tracker.setConnectionState(False)

        ### End of experiment logic

# The below code should never need to be changed, unless you want to get command
# line arguements or something.
##################################################################

if __name__ == "__main__":
    def main(configurationDirectory):
        """
        Creates an instance of the ExperimentRuntime class, checks for an experiment config file name parameter passed in via
        command line, and launches the experiment logic.
        """
        import sys
        if len(sys.argv)>1:
            configFile=sys.argv[1]
            runtime=ExperimentRuntime(configurationDirectory, configFile)
        else:
            runtime=ExperimentRuntime(configurationDirectory, "experiment_config.yaml")
    
        runtime.start()

    # The ioHub.module_directory function determines what the current directory is of
    # the function that is passed to it. It is more reliable when running scripts
    # via IDEs etc in terms of reporting the true file location. That is the claim
    # of the original function author at least. ;) It works, which is what matters.
    configurationDirectory=ioHub.module_directory(main)

    # run the main function, which starts the experiment runtime
    main(configurationDirectory)
