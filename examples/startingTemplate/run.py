"""
ioHub
.. file: ioHub/examples/startingTemplate/run.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>

------------------------------------------------------------------------------------------------------------------------

startingTemplate
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

The main purpose for the startingTemplate is to act as a blank starting template that can be copied and then used as a
starting point to create a new experiment by writing your psychopy / ioHub code in the run method and editing the two .yaml
config files as needed.

To Run:
-------

1. Ensure you have followed the ioHub installation instructions at http://www.github.com/isolver/iohub/wiki
2. Open a command prompt to the directory containing this file.
3. Start the test program by running:
   python.exe run.py

Any issues or questions, please let me know.
"""

import ioHub
from ioHub.psychopyIOHubRuntime import SimpleIOHubRuntime, visual

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

		print "HELLO WORLD"
		
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

