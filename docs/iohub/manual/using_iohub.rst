Using the ioHub Event Framework within a PsychoPy Experiment Script
====================================================================

Initialized ioHub
------------------

Interacting with ioHub Device objects
--------------------------------------

- Device wide methods and properties
- Device specific properties

Accessing Device Events and Event Properties
---------------------------------------------

- Distinction between The Device and Event classes that exist on the ioHub Server vs. those that are used by the Experiment Process.
- Reminder that ioHub monitors events on a system wide basis, not just those that occur targeted at the Stimulus Window.
- Global Retrieval
- Device Level Retrieval
- Event Type level Retrieval
- DeviceConstants and EventConstants

Clearing Device Events
----------------------- 

- Globally
- For a specific Device type
- Considerations regarding when to clear device event buffers and when not to.


Working with the ioHub Time Base
---------------------------------

- Underlying timers based on OS
- Accessing the current time
- Pausing Experiment execution.
- PsychoPy - ioHub timebase Integration
- Example of calculating a manual reaction time.

Working with the Experiment and ioHub Processes
--------------------------------------------------

Changing Process priority
CHanging Process affinity

Shutting Down the ioHub Event Framework
-----------------------------------------

-Explicitly
-Implicitly
-Terminating a rough ioHub Server Process

