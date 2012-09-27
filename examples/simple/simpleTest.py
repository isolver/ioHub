"""
ioHub
.. file: ioHub/examples/simple/simpleTest.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>

------------------------------------------------------------------------------------------------------------------------

simpleTest
++++++++++

Overview:
---------

This script is implemnted by extending the ioHub.psychopyIOHubRuntime.SimpleIOHubRuntime class to a class
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

The main purpose for the simpleTest is to isllustrate the overall structure of the ioHub.psychopyIOHubRuntime.SimpleIOHubRuntime
utility class and how to extend it and use it to run a psycho py program with ioHub / and pyEyeTrackerInterface fucntionality if desired.

To Run:
-------

1. Ensure you have followed the ioHub installation instructions at http://www.github.com/isolver/iohub/wiki
2. Open a command prompt to the directory containing this file.
3. Start the test program by running:
   python.exe simpleTest.py

Any issues or questions, please let me know.
"""

import ioHub
from ioHub.psychopyIOHubRuntime import SimpleIOHubRuntime,EventConstants, visual

class ExperimentRuntime(SimpleIOHubRuntime):
    """
    Create an experiment using psychopy and the ioHub framework by extending the SimpleIOHubRuntime class. At minimum
    all that is needed in the __init__ for the new class, here called ExperimentRuntime, is the a call to the
    SimpleIOHubRuntime __init__ itself.
    """
    def __init__(self,configFileDirectory, configFile):
        SimpleIOHubRuntime.__init__(self,configFileDirectory,configFile)

    def run(self,*args,**kwargs):
        """
        The run method contains your experiment logic. It is equal to what would be in your main psychopy experiment
        script.py file in a standard psychopy experiment setup. That is all there is too it really.

        By running your script within an extension of the SimpleIOHubRuntime class's run method, you automatically
        get access to some nice features:

        #. The ioHub Client class is accessable by calling self.hub . So to get all currently available events from the
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
        #. If you need to pause the execution of your program for a period of time, but want events to be occationally sent from the
        ioHub server process to your experiment process so nothing is lost when the delay returns, you can use self.msecDelay(), which also
        has built in cpu hogging near the end of the delay so it is quite precise (seems to be within 10's of usec on the i5 I have been testing with)
        #. There are lots of other goodies in the SimpleIOHubRuntime utility class, so check out that classes docs, as well as
        the docs for the ioHubClient class, which is what is at the end of self.hub.

        Have fun! Please report any issues you find on the bug tracker at github.com/isolver/iohub. Any suggestions for
        improvement are very welcome too, please email me at sds-git@isolver-software.com .

        Thank you. Sol
        """

        # PLEASE REMEMBER , THE SCREEN ORIGIN IS ALWAYS IN THE CENTER OF THE SCREEN,
        # REGARDLESS OF THE COORDINATE SPACE YOU ARE RUNNING IN. THIS MEANS 0,0 IS SCREEN CENTER,
        # -x_min, -y_min is the screen bottom left
        # +x_max, +y_max is the screen top right
        #
        # RIGHT NOW, ONLY PIXEL COORD SPACE IS SUPPORTED. THIS WILL BE FIXED SOON.

        # Let's make some short-cuts to the devices we will be using in this 'experiment'.
        mouse=self.hub.devices.mouse
        display=self.hub.devices.display
        kb=self.hub.devices.kb

        # Set the mouse position to 0,0, which means the 'center' of the screen.
        mouse.setPosition((0.0,0.0))

        # Read the current mouse position (should be 0,0)  ;)
        currentPosition=mouse.getPosition()

        # Read the current resolution of the monitors screen in pixels.
        # We will set our window size to match the current screen resolution and make it a full screen boarderless window.
        screen_resolution= display.getScreenResolution()

        # Read the coordinate space the script author specified in the config file (right now only pix are supported)
        coord_type=display.getDisplayCoordinateType()

        # Create a psychopy window, full screen resolution, full screen mode, pix units, with no boarder, using the monitor
        # profile name 'test monitor, which is created on the fly right now by the script
        psychoWindow = visual.Window(screen_resolution, monitor="testMonitor", units=coord_type, fullscr=True, allowGUI=False)

        # Hide the 'system mouse cursor' so we can display a cool gaussian mask for a mouse cursor.
        mouse.setSysCursorVisibility(False)

        # Create an ordered dictionary of psychopy stimuli. An ordered dictionary is one that returns keys in the order
        # they are added, you you can use it to reference stim by a name or by 'zorder'
        psychoStim=ioHub.LastUpdatedOrderedDict()
        psychoStim['grating'] = visual.PatchStim(psychoWindow, mask="circle", size=75,pos=[-100,0], sf=.075)
        psychoStim['fixation'] =visual.PatchStim(psychoWindow, size=25, pos=[0,0], sf=0,  color=[-1,-1,-1], colorSpace='rgb')
        psychoStim['mouseDot'] =visual.GratingStim(psychoWindow,tex=None, mask="gauss", pos=currentPosition,size=(50,50),color='purple')

        # Clear all events from the global event buffer, and from the keyboard event buffer.
        self.clearEvents()
        self.clearEvents('kb')

        QUIT_EXP=False
        # Loop until we get a keyboard event with the space, Enter (Return), or Escape key is pressed.
        while QUIT_EXP is False:

            # for each loop, update the grating phase
            psychoStim['grating'].setPhase(0.05, '+')#advance phase by 0.05 of a cycle

            # and update the mouse contingent gaussian based on the current mouse location
            currentPosition=mouse.getPosition()
            psychoStim['mouseDot'].setPos(currentPosition)

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
            flip_time=self.currentUsec()

            # send a message to the iohub with the message text that a flip occurred and what the mouse position was.
            # since we know the ioHub server time the flip occurred on, we can set that directly in the event.
            self.hub.sendMessageEvent("Flip %s"%(str(currentPosition),),usec_time=flip_time)

            kb_events=kb.getEvents()
            if len(kb_events)>0:
                for k in kb_events:
                    # key: the string representation of the key pressed, A-Z if a-zA-Z pressed, 0-9 if 0-9 pressed ect.
                    #      To get the mapping from a key_id to a key string, use
                    #
                    #      key_string=EventConstants.IDToName(key_event['key_id'])
                    #
                    # char: the ascii char for the key pressed. This field factors in if shift was also pressed or not
                    #       when the char was typed, so typing a 's' == char field of 's', while typing SHIFT+s == char
                    #       field of 'S'. This is in contrast to the key field, which always returns upper case values
                    #       regardless of shift value. If the character pressed is not an ascii printable character,
                    #       this filed will print junk, hex, or who knows what else at this point.
                    if k['key'] in ['Space','Return','Escape']:
                        QUIT_EXP=True

        # a key was pressed so the loop was exited. We are clearing the event buffers to avoid an event overflow ( currently known issue)
        self.clearEvents()

        # wait 250 msec before ending the experiment (makes it feel less abrupt after you press the key)
        self.msecDelay(250)

        # _close neccessary files / objects, 'disable high priority.
        psychoWindow._close()

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

