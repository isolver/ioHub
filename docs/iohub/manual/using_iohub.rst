Using the ioHub Event Framework within a PsychoPy Experiment Script
====================================================================

**THIS PAGE IS NOT COMPLETE AND WILL BE UPDATED WITHIN 48 HOURS**

Initializing ioHub
------------------

Options:
	* iohub.client.quickStartHubServer()
	* iohub.client.ioHubExperimentRuntime() extension.
	

Accessing Device Events and Event Properties
---------------------------------------------

* Distinction between The Device and Event classes that exist on the ioHub Server vs. those that are used by the Experiment Process.

* Reminder that ioHub monitors events on a system wide basis, not just those that occur targeted at the Stimulus Window.

* Global Retrieval
	* ioHubConnection.getEvents()
		* supported arg list of event types to get, as well as arg indicating if the retrieved events should be removed from the ioHub Server event buffer. Default is to get all event types and remove them from the ioHub Global Buffer.

* Device Level Retrieval
	* ioHubConnection.devices.[device_name_of_interest].getEvents()
		* supported arg list of device event types to get, as well as arg indicating if the retrieved events should be removed from the devices event buffer. Default is to get all event types and remove them from the device Buffer.
		
* Event Type level Retrieval

* DeviceConstants and EventConstants

Clearing Device Events
----------------------- 

* Globally
* For a specific Device type
* Considerations regarding when to clear device event buffers and when not to.


Working with the ioHub Time Base
---------------------------------

* Underlying timers based on OS
* Accessing the current time
* Pausing Experiment execution.
* PsychoPy - ioHub timebase Integration
* Example of calculating a manual reaction time.

Working with the Experiment and ioHub Processes
--------------------------------------------------
( Not supported on OS X at this time.)

* Changing either Processes priority
* CHanging either Processes affinity


Shutting Down the ioHub Event Framework
-----------------------------------------

* Explicitly
* Implicitly
* Terminating a rough ioHub Server Process

