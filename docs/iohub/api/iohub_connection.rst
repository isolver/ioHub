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

.. autoclass:: iohub.client.ioHubExperimentRuntime
    :exclude-members: start
	
Example Usage
##############

The Quickstart section of this manual contains an example of how to use the 
ioHubExperimentRuntime class and create the two .yaml configuration files.

The ioHub examples folder also has many demos of how to use this class, as most
of the demos were written using the ioHubExperimentRuntime class.
