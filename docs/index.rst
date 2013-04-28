================================
ioHub Event Monitoring Framework
================================

ioHub is a Python package providing a cross-platform computer device event monitoring and storage framework. ioHub is free to use and is GLP version 3 licensed.

ioHub is not a complete experiment design and runtime API, but is instead intended to be used with existing Python experiment runtime packages,primarily the most excellent `PsychoPy <http://www.psychopy.org>`_.

ioHub supports the following high level functionality:

* Monitoring of events from computer devices such as a:
	#. Keyboard
	#. Mouse
	#. Analog to Digital Converter.
	#. XInput compatible gamepad.
	#. Eye Tracker, via a Common Eye Tracking Interface. The Common Eye Tracking Interface provides the same user level API regardless of the eye tracking hardware being used. Easily write an experiment script one and run it using any of the supported eye tracking hardware. Write a data analysis script based on eye sample data saved in the ioDataStore and use to for analysis of data collected from any of the supported eye tracking platforms as well.
* The Common Eye Tracking Interface currently supports the following eye tracking systems:
	#. `LC Technologies <http://www.eyegaze.com>`_ EyeGaze and EyeFollower models.
	#. `SensoMotoric Instruments <http://www.smivision.com>`_ iViewX models.
	#. `SR Research <http://www.sr-research.com>`_ EyeLink models.
	#. `Tobii <http://www.tobii.com>`_ Technologies Tobii models.
* Support for the following operating Systems:
	#. Windows XP SP3, 7, 8
	#. Apple OS X 10.6+
	#. Linux 2.6+
* Device event monitoring is done completely independently from the experiment runtime graphics environment and allows for device inputs to be captured system wide, not just for events targeted to the stimulus presentation / forground application window. In fact, no graphical window in needed at all to collect inputs from supported devices. An example of using this *headless* event tracking mode is provided in the examples folder. 
* The ioHub Server, responsible for the monitoring, translation, storage, and online transmission of device events, runs in a seperate OS process from the main application / experiment runtime process. This allows for event monitoring and device event callback processing to occur very quickly, regardless of what state the experiment runtime process is in (i.e. even when the experiment runtime process is blocked and would not be able to monitor for new events itself).
* Device inputs can be saved by the ioHub Server Process for post hoc analysis. Assuming a multicore CPU is being used, in general all device events can be saved during the experiment without effecting the performance of the experiment runtime logic itself. Event data is saved in the *ioDataStore*, which is a structured event definition using the HDF5 standard. Events saved in the ioDataStore have the same event attributes, using the same attribyte names, as when events are accessing in real-time within your experiment script. Event data retrieved from a data file is provided as numpy ndarray's, providing the ability to directly use retrieved data in several scientific Python models such as Scipy and MatPlotLib.
* When used with `PsychoPy <http://www.psychopy.org>`_, ioHub can save debugging messages to PsychoPy log files, and a PsychoPy script can create *LogEvents* that are saved to the PsychoPy logging system as well as being saved in the ioHub DataStore. Furthermore, ioHub and PsychoPy share a common time base, so times read from your experiment and those provided for any of the ioHub event types can be used together without any time base transaltions being required. (The PsychoPy time must be based on the core.getTime or default logging.defaultClock mechanisms.)
* Events can be accessed by the experiment script at runtime either in a chronologically ordered, device independent manner, for a specific device type only, or for specific Device Events types only.
* Text Messages can be sent to ioHub Server as Experiment Runtime Events, allowing the easy integration of important experiment information (such as stimulus onsets, etc.), each timestamped with microsecond level precision with the ioHub timebase.
* A common time base is provided for all device events, making it easy to syncronize data from multiple physical devices and virtual devices, such as the Experiment Runtime itself. Events are time stamped by ioHub when it is not done by the source device itself, or existing device event time stamps are converted to the common ioHub time base.
* Device inputs are converted into common event types based on device type, regardless of the underlying supported hardware.



Contents
============

.. toctree::
   :maxdepth: 5
   
   Installation <iohub/installation>
   Quick Start Guide <iohub/quickstart>
   User Manual <iohub/manual/user_manual>
   API Specification <iohub/api/api_home>
   Credits <iohub/credits>
   License <iohub/license>
   Change Log <iohub/change_log>
