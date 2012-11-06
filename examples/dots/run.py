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

import ioHub
from ioHub.devices import Computer
from ioHub.experiment import ioHubExperimentRuntime, psychopyVisual

class ExperimentRuntime(ioHubExperimentRuntime):
    """
    Create an experiment using psychopy and the ioHub framework by extending the ioHubExperimentRuntime class. At minimum
    all that is needed in the __init__ for the new class, here called ExperimentRuntime, is the a call to the
    ioHubExperimentRuntime __init__ itself.
    """
    DOT_COUNT=2000
    def __init__(self,configFileDirectory, configFile):
        ioHubExperimentRuntime.__init__(self,configFileDirectory,configFile)

    def run(self,*args,**kwargs):
        keyboard = self.devices.kb
        display = self.devices.display

        #create a window to draw in
        myWin =psychopyVisual.Window(display.getStimulusScreenResolution(),
                             screen=display.getStimulusScreenIndex(),
                             allowGUI=False, 
                             bitsMode=None,
                             units='norm',
                             winType='pyglet', 
                             fullscr=True)

        myWin.setRecordFrameIntervals(True)

        #INITIALISE SOME STIMULI
        dotPatch =psychopyVisual.DotStim(myWin, 
                                color=(1.0,1.0,1.0), 
                                dir=270,
                                nDots=self.DOT_COUNT, 
                                fieldShape='circle', 
                                fieldPos=(0.0,0.0),
                                fieldSize=2,
                                dotLife=5, #number of frames for each dot to be drawn
                                signalDots='same', #are the signal dots the 'same' on each frame? (see Scase et al)
                                noiseDots='direction', #do the noise dots follow random- 'walk', 'direction', or 'position'
                                speed=0.01, 
                                coherence=0.9
                                )
                                
        message =psychopyVisual.TextStim(myWin,
                                 text='Hit Q to quit',
                                 pos=(0,-0.5)
                                 )

        Computer.enableHighPriority(disable_gc=False)

        dur=5*60
        endTime=Computer.currentTime()+dur
        fcounter=0
        reportedRefreshInterval=display.getStimulusScreenReportedRetraceInterval()*0.001 # convert to sec.msec
        print 'Screen has a reported refresh interval of ',reportedRefreshInterval
        keyboard.clearEvents()

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
                if event['key'] in ['Escape','Q']:
                    myWin.close()
                    exit=True
                    break
            
            keyboard.clearEvents()
            Computer.disableHighPriority()
            ### End of experiment logic

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

