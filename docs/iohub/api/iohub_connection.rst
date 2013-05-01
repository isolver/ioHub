######################################################################
Connecting to the ioHub Event Framework -  The ioHubConnection Class
######################################################################

The ioHub Event Framework runs in a separate process ( called the ioHub Process )
from that of the Python interpreter your PsychoPy experiment is executed within (called the PsychoPy Process).
Therefore the first thing that needs to be done when using the ioHub Event Framework
is to have the experiment script create the ioHub Process and a connection between 
the PsychoPy and ioHub Processes. 

The above functionality is provided in the iohub.client.ioHubConnection class.
The experiment script should **indirectly** create **one instance** of the 
ioHubConnection class using one of the two methods discussed in the next section; 
an instance of ioHubConnection should never be created *directly* by the experiment script.

.. autoclass:: iohub.client.ioHubConnection
	:member-order: 'bysource'

Ways to Create an ioHubConnection Class
#######################################

There are two ways to create an instance of the ioHubConnection class
for use by the experiment script running within the PsychoPy Process:

#. The iohub.client.quickStartHubServer function.
#. By extending the iohub.client.ioHubExperimentRuntime class. 

Each approach to creating the ioHubConnection instance has strengths and weaknesses,
and the most appropriate approach for a given experiment depends
primarily on the ioHub Device types that the experiment is using.
 
quickStartHubServer Function
=============================

Using the quickStartHubServer function to start the ioHub Process and gain access to the ioHub Event Framework
is ideal when only the following ioHub Devices are needed within the experiment script:

* Keyboard
* Mouse
* Display
* Experiment

For details on each of these ioHub device types, please refer to the device's documentation page.

.. autofunction:: iohub.client.quickStartHubServer

ioHubExperimentRuntime Class
=============================

The ioHubExperimentRuntime Class is a core class using in the ioHub Package. If
your experiment contains more than just a keyboard and mouse device, or even if those
are the only devices used, using the ioHubExperimentRuntime class helps make your script mode
modular and helps you control the specific device settings used across sessions of
an experiment during data collection. 

The main features of the ioHubExperimentRuntime class are:
#. Simple addition of the experiment logic by creating your main experiment script in the 'run' method of the ioHubExperimentRuntime class extension.
#. Use of an experiment_config.yaml and ioHub_congif.yaml to represent experiment and device setting to be used during the experiment runtime.
#. Automatic creation of the ioHubConnection class, creation of the ioHub Server process, and initialization of all devices specified in the iohub_config.yaml.
#. Optionally display an "Experiment Details" Dialog at the start of each experiment session, listing some of the experiment details, helping to ensure the correct experiment is being run.
#. Optionally display an Experiment Session Information Dialog, which can be customized within the experiment_config.yaml for each experiment, allowing collection of relevant participant data prior to the start of the experiment itself.
#. Automatic cleanup of ioHub and PsychoPy objects as necessary at the end of the experiment.

.. autoclass:: iohub.client.ioHubExperimentRuntime

Example Usage
##############

The Quickstart section of this manual contains an example of how to use the 
ioHubExperimentRuntime class and create the two .yaml configuration files.

The ioHub examples folder also has many demos of how to use this class, as most
of the demos were written using the ioHubExperimentRuntime class.
