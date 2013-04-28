==========================================
Connecting to the ioHub Event Framework
==========================================

The Experiment / PsychoPy script runs in a seperate Process than that of the 
ioHub Server. A UDP message protocal is used by the two processes to communicate
back and forth. All communication with the ioHub server is initiated by the 
PsychoPy runtime script via the iohub.client.ioHubConnection class. Each request
made by the PsychoPy experiment script receives a response from the ioHub Server
which includes either the data / information requested, or an acknowedgement from
the ioServer that the request was received and processed. On an Intel i5 type of CPU,
the round trip time for a request to be sent to the ioHub server and the response be
received by the PsychoPy script is typically around 0.25 msec on avaergae, with a maximum
round trip delay of 1.0 msec or less. The round trip time it is taking to request 
and receive back event information can be tested by running the ioHubAccessDelayTest
which can be found in the ioHub examples folder. This test script requests and receives 
1000 responses from the ioHub server that contain *at least* one event that has occurred
since the last request. Requests that receive a response with no events are not included
in the delay calculation to ensure that the delay represents requests where the ioHub
Server process needed to send at minimum on event object back to the experiment
script process.

If you run the ioHubAccessDelayTest script and find that the ioHub delays are 
significantly longer than stated above, please check the following:
    * Are you running the test on a multicore CPU? Using the the ioHub and PychoPy packages together on an old single core or single CPU computer will likely cause increased delays.
    * Are other background processes running that can interfer with the experiment or ioHub process and cause poor reduced performance? Examples of such programs or services are file backup software, cloud based file syncronization programs such as Dropbox, Google Drive, bloated antivirus software such as Norton, etc. If any of these types of serverices or programs are running in the background, turn them off while you run your experiment sessions. This is important even if using PsychoPy alone, but is even more important when using ioHub and PsychoPy together. 
 
ioHubConnection Class
=======================

.. autoclass:: iohub.client.ioHubConnection
    :members:
	

quickStartHubServer Function
==============================

.. autofunction:: iohub.client.quickStartHubServer

    
ioHubExperimentRuntime Class
=============================

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

.. autoclass:: iohub.client.ioHubExperimentRuntime
    :members:

Example Usage
##############

The Quickstart section of this manual contains an example of how to use the 
ioHubExperimentRuntime class and create the two .yaml configuration files.

The ioHub examples folder also has many demos of how to use this class, as most
of the demos were written using it.