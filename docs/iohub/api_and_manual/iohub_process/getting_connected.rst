########################################
Connecting to the ioHub Event Framework 
########################################

Running an experiment using the ioHub Event Framework utilizes two Python processes.
The first is for running the traditional PsychoPy coder experiment logic called the PsychoPy 
Process. The second is a separate process for device monitoring, event bundling, 
and data storage called the ioHub Process.

The PsychoPy Process is established by the Python interpreter executing
the experiment script. Therefore, the first thing that needs to be done when using
the ioHub Event Framework is to have the PsychoPy Process establish and connect
to a new ioHub Server process. 

The functionality for establishing and connecting to a new ioHub Process
is provided in the iohub.client.ioHubConnection class.
The experiment script should **indirectly** create **one instance** of the 
ioHubConnection class using one of the two methods discussed in the next section.
That is, an instance of ioHubConnection should never be created *directly* by the 
experiment script.

Ways to Create an ioHubConnection Class
#######################################

There are two ways to create an instance of the ioHubConnection class
to use with a PsychoPy experiment:

<<<<<<< HEAD:docs/iohub/api_and_manual/getting_connected/getting_connected.rst
#. The iohub.client.launchHubProcess function.
#. By extending the iohub.client.ioHubExperimentRuntime class. 

Each approach to creating the ioHubConnection instance has strengths and weaknesses,
and the most appropriate approach for a given experiment depends
primarily on the ioHub Device types that the experiment is using.
After Reviewing the ioHubConnection Class, we will go into more detail about
each approach to working with ioHub. 
=======
#. Calling the iohub.client.quickStartHubServer function.
#. Extending the iohub.client.ioHubExperimentRuntime class. 

Each approach to creating the ioHubConnection instance has strengths and weaknesses,
and the most appropriate approach for a given experiment depends
primarily on the ioHub Device types used in the experiment.
 
quickStartHubServer Function
=============================

Using the quickStartHubServer function to start the ioHub Process and gain access to the ioHub Event Framework
is ideal when only the following ioHub Devices are needed in an experiment:
>>>>>>> new_docs:docs/iohub/api/iohub_connection.rst

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

<<<<<<< HEAD:docs/iohub/api_and_manual/getting_connected/getting_connected.rst
=======
The Quickstart section of this manual contains an example of how to 
extend the ioHubExperimentRuntime class and create the two .yaml configuration files
used to gain access to the ioHub Event Framework.
>>>>>>> new_docs:docs/iohub/api/iohub_connection.rst

