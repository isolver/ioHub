================================
ioHub Event Monitoring Framework
================================

ioHub is a Python package providing a cross-platform computer device event monitoring and storage framework. ioHub is free to use and is GLP version 3 licensed.

ioHub is not a complete experiment design and runtime API, but is instead intended to be used with existing Python experiment runtime packages, primarily the most excellent `PsychoPy <http://www.psychopy.org>`_.

ioHub supports the following high level functionality:

* Monitoring of events from computer devices such as:
	#. Keyboard
	#. Mouse
	#. Analog to Digital Converter
	#. XInput compatible gamepad
	#. Eye Tracker, via a Common Eye Tracking Interface
.. note::
    The Common Eye Tracking Interface provides the same user level API for all supported hardwares, so the same eye tracking experiment script can be run with any eye tracker. Moreover, the same data analysis script can be used to interpret eye sample data saved in the ioDataStore recorded from any eye tracker.
    
    The Common Eye Tracking Interface currently supports the following eye tracking systems:
        #. `LC Technologies <http://www.eyegaze.com>`_ EyeGaze and EyeFollower models.
        #. `SensoMotoric Instruments <http://www.smivision.com>`_ iViewX models.
        #. `SR Research <http://www.sr-research.com>`_ EyeLink models.
        #. `Tobii <http://www.tobii.com>`_ Technologies Tobii models.
        
* Support for the following operating Systems:
	#. Windows XP SP3, 7, 8
	#. Apple OS X 10.6+
	#. Linux 2.6+

ioHub Features
==============

* Independent device event monitoring:
    The ioHub Server, responsible for the monitoring, translation, storage, and online transmission of device events, runs in a separate OS process from the main application / experiment runtime process. Device events are therefore monitored completely independently from the experiment runtime graphics environment, allowing events to be captured system wide, not just for events targeted to the stimulus presentation / foreground application window. In fact, no graphical window in needed at all to collect inputs from supported devices (An example of using this *headless* event tracking mode is provided in the examples folder). This process independence allows for event monitoring and device event callback processing to occur very quickly, regardless of what state the experiment runtime process is in (i.e. even when the experiment runtime process is blocked and would not be able to monitor for new events itself).
* Easy data storage and retrival:
    Device event data are saved in the *ioDataStore*, a structured event definition using the `HDF5 <http://www.hdfgroup.org/HDF5/>`_ standard, for post hoc analysis. Events saved in the ioDataStore have the same event attributes as events accessed in real-time within the experiment script. Events can be accessed by the experiment script at runtime in a number of ways: (1) By event time (chronologically and device independent), (2) by device (e.g., mouse events), and (3) by device event type (e.g., fixation events).
    Event data retrieved from a data file is provided as numpy ndarray's, providing the ability to directly use retrieved data in several scientific Python models such as Scipy and MatPlotLib. With a multicore CPU, all device events can be saved during the experiment without affecting the performance of the experiment runtime logic itself.
* Smooth integration with PsychoPy:
    When used with `PsychoPy <http://www.psychopy.org>`_, ioHub can save debugging messages to PsychoPy log files, and a PsychoPy script can create *LogEvents* that are saved to the PsychoPy logging system as well as being saved in the ioDataStore. Furthermore, ioHub and PsychoPy share a common time base, so times read from the PsychoPy process are directly comparable to times read from ioHub-monitored events (The PsychoPy time must be based on the core.getTime or default logging.defaultClock mechanisms.)
* High-precision synchronization:
    Descriptive messages can be sent to ioHub Server as Experiment Runtime Events, allowing important experiment information (such as stimulus onsets, etc.) to be timestamped with microsecond level precision. A common time base is provided for all device events, making it easy to syncronize data from multiple physical and virtual devices, such as the Experiment Runtime itself. Device inputs are converted to common event types with ioHub regulated time stamps regardless of the underlying hardware.

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
