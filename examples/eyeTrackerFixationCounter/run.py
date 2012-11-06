"""
ioHub
.. file: ioHub/examples/eyeTrackerFixationCounter/run.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. fileauthor:: Sol Simpson <sol@isolver-software.com>

------------------------------------------------------------------------------------------------------------------------

eyeTrackerFixationCounter
+++++++++++++++++++++++++

Overview:
---------

This script is implemnted by extending the ioHub.experiment.ioHubExperimentRuntime class to a class
called ExperimentRuntime. The ExperimentRuntime class provides a utility object to run a psychopy script and
also launches the ioHub server process so the script has access to the ioHub service and associated devices.

The program loads many configuration values for the experiment process by using the experiment_Config.yaml file that
is located in the same directory as this script. Configuration settings for the ioHub server process are defined in
the ioHub_configuration.yaml file.

The __main__ of this script file simply calls the start() method of the ExperimentRuntime object,
that calls the run() method for the instance which is what contains the actual 'program / experiment execution code'
that has been added to this file. When run() completes, the ioHubServer process is closed and the local program ends.

Desciption:
-----------

The main purpose for the eyeTrackerFixationCounter is to illustrate how to monitor for a specific eye event type
 (FixationEndEvents), and gather some stats about the events being monitored.

To Run:
-------

1. Ensure you have followed the ioHub installation instructions at http://www.github.com/isolver/iohub/wiki
2. Open a command prompt to the directory containing this file.
3. Start the test program by running:
   python.exe run.py

Any issues or questions, please let me know.
"""


import ioHub
from ioHub.devices import Computer
from ioHub.experiment import ioHubExperimentRuntime, EventConstants, psychopyVisual, pumpLocalMessageQueue

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
        psychoWindow = psychopyVisual.Window(screen_resolution, monitor="testMonitor", units=coord_type, fullscr=True, allowGUI=False, screen=screen_index)

        # Hide the 'system mouse cursor' so we can display a cool gaussian mask for a mouse cursor.
        mouse.setSystemCursorVisibility(False)

        # Create an ordered dictionary of psychopy stimuli. An ordered dictionary is one that returns keys in the order
        # they are added, you you can use it to reference stim by a name or by 'zorder'
        image_name='./images/party.png'
        imageStim = psychopyVisual.ImageStim(psychoWindow, image=image_name, name='image_stim')

        imageStim.draw()

        tracker.setRecordingState(True)
        self.hub.delay(0.050)

        psychoWindow.flip()
        flip_time=Computer.currentSec()
        self.hub.clearEvents()
        self.hub.sendMessageEvent("SYNCTIME %s"%(image_name,),sec_time=flip_time)

        # Clear all events from the global event buffer, and from the keyboard and eyetracker event buffer.
        # This 'mess' of calls is needed right now because clearing the global event buffer does not
        # clear device level event buffers, and each device buffer is independent. Not sure this is a 'good'
        # thing as it stands, but until there is feedback, it will stay as is.

        self.hub.clearEvents('all')

        fixationCount=0
        dwellTime=0.0
        # Loop until we get a keyboard event
        while len(kb.getEvents())==0:
            eye_events=tracker.getEvents()
            for ee in eye_events:
                if ee['type']==EventConstants.FIXATION_END_EVENT:
                    etime=ee['hub_time']
                    eeye=ee['eye']
                    ex=ee['average_gaze_x']
                    ey=ee['average_gaze_y']
                    edur=ee['duration']
                    ert=etime-flip_time
                    print 'FIX %.3f\t%d\t%.3f\t%.3f\t%.3f\t%.3f'%(etime,eeye,ex,ey,edur,ert)
                    fixationCount+=1
                    dwellTime+=edur

            # pump local processes message queue so that Windows thinks the psychopy Window is still 'alive'.
            # This is not necessary, right now atleast, if you are flipping the window frequently, as that
            # causes a message pump to occur during the flip call in psychopy.
            pumpLocalMessageQueue()

        print "-------------"
        print " Number Fixations Made: ",fixationCount
        print " Total Dwell Time: ",dwellTime
        if fixationCount:
            print " Average Dwell Time / Fixation: ",dwellTime/fixationCount

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

