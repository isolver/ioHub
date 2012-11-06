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
from ioHub.experiment import ioHubExperimentRuntime

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

        print "Hello World"

        ### End of experiment logic

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

if __name__ == "__main__":
    # This code only gets called when the python file is executed, not if it is loaded as a module by another python file
    #
    # The module_directory function determines what the current directory is of the function that is passed to it. It is
    # more reliable when running scripts via IDEs etc in terms of reporting the true file location.
    configurationDirectory=ioHub.module_directory(main)

    # run the main function, which starts the experiment runtime
    main(configurationDirectory)

