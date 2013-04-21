################################
ioHubExperimentRuntime Class
################################

The ioHubExperimentRuntime Class is a core class using in the ioHub Package. If
your experiment contains more than just a keyboard and mouse device, or even if those
are the only devices used, using the ioHubExperimentRuntime class helps make your script mode
modular and helps you control the specific device settings used across sessions of
an experiment during data collection. 

The main features of the ioHubExperimentRuntime classs are:
#. Simple addition of the experiment logic by simply creating your main experiment script in the runmethod of the ioHubExperimentRuntime class extension.
#. Use of an experiment_config.yaml and ioHub_congif.yaml to represent experiment and device setting to be used during the experiment runtime.
#. Automatic creation of the ioHubCOnnection class, creation of the ioHub Server process, and initialization of all devices specified in the iohub_config.yaml.
#. Automatic display of an "Experiment Details" Dialog at the start of each experiment session, listing some of the experiment details, helping to ensure the correct experiment is being run.
#. Automatic display of an Experiment Session information dialog, which can be customized within the experiment_config.yaml for each experiment, allowing collection of relevent participant data prior to the start of the experiment itself.
#. Automatic cleanup of ioHub and PsychoPy objects as necessary at the end of the experiment.

ioHubExperimentRuntime Class Definition
#########################################

.. autoclass:: iohub.util.experiment.ioHubExperimentRuntime
    :members:

Example Usage
##############

The Quickstart section of this manual contains an example of how to use the 
ioHubExperimentRuntime class and create the two .yaml configuration files.

The ioHub examples folder also has many demos of how to use this class, as most
of the demos were written using it.