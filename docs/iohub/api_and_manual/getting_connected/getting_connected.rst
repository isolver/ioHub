########################################
Connecting to the ioHub Event Framework 
########################################

The ioHub Event Framework runs in a separate process ( called the ioHub Process )
from that of the Python interpreter your PsychoPy experiment is executed within (called the PsychoPy Process).
Therefore the first thing that needs to be done when using the ioHub Event Framework
is to have the experiment script create the ioHub Process and a connection between 
the PsychoPy and ioHub Processes. 

The above functionality is provided in the iohub.client.ioHubConnection class.
The experiment script should **indirectly** create **one instance** of the 
ioHubConnection class using one of the two methods discussed in the next section; 
an instance of ioHubConnection should never be created *directly* by the experiment script.

Ways to Create an ioHubConnection Class
#######################################

There are two ways to create an instance of the ioHubConnection class
for use by the experiment script running within the PsychoPy Process:

#. The iohub.client.launchHubProcess function.
#. By extending the iohub.client.ioHubExperimentRuntime class. 

Each approach to creating the ioHubConnection instance has strengths and weaknesses,
and the most appropriate approach for a given experiment depends
primarily on the ioHub Device types that the experiment is using.
After Reviewing the ioHubConnection Class, we will go into more detail about
each approach to working with ioHub. 

The ioHubConnection Class
##############################
 
.. autoclass:: iohub.client.ioHubConnection
	:member-order: bysource


Connection Type Details
#########################

.. toctree::
    :maxdepth: 2
    
    * The launchHubProcess Function <launchHubServer>
    * ioHubExperimentRuntime Class <ioHubExperimentRuntime>
    * Configuration Files and Dictionaries <config_files_explained>


