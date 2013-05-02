##################################
ioHub Event Monitoring Framework
##################################

ioHub is a Python package providing a cross-platform computer device event monitoring 
and storage framework. ioHub is free to use and is GPL version 3 licensed.

ioHub is not a complete experiment design and runtime API. It's main focus is 
on device event monitoring, real-time reporting, and persistent storage of 
input device events on a system wide basis. When ioHub is used for experiment 
device monitoring during a psychology or neuroscience type study, 
ioHub is designed to be used with the most excellent `PsychoPy <http://www.psychopy.org>`_. 

.. note:: In the near future ioHub will be merging with PsychoPy, so it can be 
    used out of the box with a PsychoPy installation.
    This will mean many **positive changes** over the short term
    as the psychopy.iohub project is put in place. We will keep this
    page updated with the latest news and status on this exciting development. 

OS and Device Support
#####################

* Support for the following operating Systems:
	#. Windows XP SP3, 7, 8
	#. Apple OS X 10.6+
	#. Linux 2.6+
	
* Monitoring of events from computer devices such as:
	#. Keyboard
	#. Mouse
	#. Analog to Digital Converter
	#. XInput compatible gamepad
	#. Eye Tracker, via a Common Eye Tracking Interface
	
.. note::
    The Common Eye Tracking Interface provides the same user level API for all supported hardwares, meaning the same experiment script can be run with any supported eye tracker and the same data analyses can be performed on any eye tracking data saved via ioHub in the ioDataStore. The Common Eye Tracking Interface currently supports the following eye tracking systems:
	
        #. `LC Technologies <http://www.eyegaze.com>`_ EyeGaze and EyeFollower models.
        #. `SensoMotoric Instruments <http://www.smivision.com>`_ iViewX models.
        #. `SR Research <http://www.sr-research.com>`_ EyeLink models.
        #. `Tobii <http://www.tobii.com>`_ Technologies Tobii models.

ioHub Features
###############

* Independent device event monitoring:
    The ioHub Server, responsible for the monitoring, bundling, and storage of device events, runs in a separate OS process from the main PsychoPy Experiment. Device events are monitored continuously system-wide rather than intermittently or relative to the PsychoPy window. In fact, no graphical window is needed to monitor supported devices (An example of using this *headless* event tracking mode is provided in the examples folder). Device event monitoring and callback processing occurs very quickly in parallel, regardless of what state the PsychoPy Experiment process is in (i.e. even when it is performing a blocking operation and would not be able to monitor new events itself).
* Easy data storage and retrieval:
    Device event data are saved in the *ioDataStore*, a structured event definition using the `HDF5 <http://www.hdfgroup.org/HDF5/>`_ standard. With a multicore CPU, all device events during an experiment can be automatically saved for post hoc analyses without impairing performance of the PsychoPy Experiment process. The same device events saved to the ioDataStore can be accessed during an experiment as numpy ndarray's, affording direct use in powerful scientific Python models such as Scipy and MatPlotLib. These events can be retrieved during the PsychoPy Experiment and from the ioDataStore very flexibly: for example, by event time (chronologically and device independent), by device (e.g., mouse events), and by event type (e.g., fixation events).
* Smooth integration with PsychoPy:
    When used with full `PsychoPy <http://www.psychopy.org>`_ functionality, ioHub can save debugging messages to PsychoPy log files, and PsychoPy *LogEvents* can be saved in the ioDataStore (as well as the PsychoPy logging system). Furthermore, ioHub and PsychoPy share a common time base, so times read from the PsychoPy Experiment process are directly comparable to times read from ioHub Device Events (if the PsychoPy time is based on psychopy.core.getTime or default psychopy.logging.defaultClock mechanisms).
* High-precision synchronization:
    The ioHub Server provides a common time base to automatically synchronize device events from multiple physical and virtual devices. In fact, the ioHub Server interacts with the PsychoPy Experiment process 'as if' it were another virtual device: descriptive MessageEvents can be sent from within the PsychoPy Experiment to the ioHub Server, allowing important information in the course of the experiment (such as stimulus onsets, etc.) to be time stamped with microsecond-level precision and saved in the ioDataStore alongside similarly time-stamped device events.


Github Hosted
##############

The ioHub project source is available on GitHub `here <https://www.github.com/isolver/ioHub>`_.

Support
########

A `user forum / mailing list <https://groups.google.com/forum/?hl=en&fromgroups#!forum/iohub-users>`_ 
and `developer forum / mailing list <https://groups.google.com/forum/?hl=en&fromgroups#!forum/iohub-dev>`_
are available on Google Groups for support questions and development discussion topics respectively.


Documentation Contents
########################

.. toctree::
   :maxdepth: 4
   
   Installation <iohub/installation>
   Supported Device Types for Your OS <iohub/supported_devices>
   Quick Start Guide <iohub/quickstart>
   User Manual / API Review <iohub/api_and_manual/start_here>
   Performance <iohub/performance>
   Credits <iohub/credits>
   License <iohub/license>
   Change Log <iohub/change_log>
