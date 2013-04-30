================================
ioHub Event Monitoring Framework
================================

ioHub is a Python package providing a cross-platform computer device event monitoring 
and storage framework. ioHub is free to use and is GLP version 3 licensed.

ioHub is not a complete experiment design and runtime API. It's main focus is 
on device event monitoring, real-time reporting, and persistant storage of 
input device events on a system wide basis. When ioHub is used for experiment 
device monitoring during a psychopolgy or neuroscience type study, 
ioHub is designed to be used with the most excellent `PsychoPy <http://www.psychopy.org>`_. 

.. note:: In the near future ioHub will be merging with PsychoPy, so it can be 
    used out of the box with a PsychoPy installation.
    This will mean many **positive changes** over the short term
    as the psychopy.iohub project is put in place. We will keep this
    page updated with the latest news and status on this exciting development. 

OS and Device Support
=====================

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
    The Common Eye Tracking Interface provides the same user level API for all supported hardwares, so the same eye tracking experiment script can be run with any eye tracker. Moreover, the same data analysis script can be used to interpret eye sample data saved in the ioDataStore recorded from any eye tracker. The Common Eye Tracking Interface currently supports the following eye tracking systems:
	
        #. `LC Technologies <http://www.eyegaze.com>`_ EyeGaze and EyeFollower models.
        #. `SensoMotoric Instruments <http://www.smivision.com>`_ iViewX models.
        #. `SR Research <http://www.sr-research.com>`_ EyeLink models.
        #. `Tobii <http://www.tobii.com>`_ Technologies Tobii models.

ioHub Features
==============

* Independent device event monitoring:
    The ioHub Server, responsible for the monitoring, translation, storage, and online transmission of device events, runs in a separate OS process from the main PsychoPy Process. Device events are therefore monitored completelyindependently from the PsychoPy environment, allowing events to be captured system wide, not just for events targeted to the stimulus presentation / foreground PsychoPy window. In fact, no graphical window in needed at all to collect inputs from supported devices (An example of using this *headless* event tracking mode is provided in the examples folder). This process independence allows for event monitoring and device event callback processing to occur very quickly, regardless of what state the PsychoPy Process is in (i.e. even when it is performing a blocking operation and would not be able to monitor for new events itself).
* Easy data storage and retrival:
    Device event data are saved in the *ioDataStore*, a structured event definition using the `HDF5 <http://www.hdfgroup.org/HDF5/>`_ standard, for post hoc analysis. Events saved in the ioDataStore have the same event attributes as events accessed in real-time within the experiment script. Events can be accessed by the experiment script at runtime in a number of ways: (1) By event time (chronologically and device independent), (2) by device (e.g., mouse events), and (3) by device event type (e.g., fixation events).
    Event data retrieved from a data file is provided as numpy ndarray's, providing the ability to directly use retrieved data in several scientific Python models such as Scipy and MatPlotLib. With a multicore CPU, all device events can be saved during the experiment without affecting the performance of the PsychoPy runtime logic itself.
* Smooth integration with PsychoPy:
    When used with `PsychoPy <http://www.psychopy.org>`_, ioHub can save debugging messages to PsychoPy log files, and a PsychoPy script can create *LogEvents* that are saved to the PsychoPy logging system as well as being saved in the ioDataStore. Furthermore, ioHub and PsychoPy share a common time base, so times read from the PsychoPy process are directly comparable to times read from ioHub-monitored events (The PsychoPy time must be based on the psychopy.core.getTime or default psychopy.logging.defaultClock mechanisms.)
* High-precision synchronization:
    Descriptive messages can be sent to ioHub Server as Experiment Runtime Events, allowing important experiment information (such as stimulus onsets, etc.) to be time stamped with microsecond level precision. A common time base is provided for all device events, making it easy to syncronize data from multiple physical and virtual devices, such as the PsychoPy runtime itself. Device inputs are converted to common event types with ioHub regulated time stamps regardless of the underlying hardware.


Github Hosted
==============

The ioHub project source is available on GitHub `here <https://www.github.com/isolver/ioHub>`_.

Support
========

A `user forum / mailing list <https://groups.google.com/forum/?hl=en&fromgroups#!forum/iohub-users>`_ 
and `developer forum / mailing list <https://groups.google.com/forum/?hl=en&fromgroups#!forum/iohub-dev>`_
are available on Google Groups for support questions and development discussion topics respectively.


Manual Contents
================

.. toctree::
   :maxdepth: 4
   
   Installation <iohub/installation>
   Quick Start Guide <iohub/quickstart>
   User Manual / API Overview <iohub/api/api_home>
   Performance <iohub/performance>
   Credits <iohub/credits>
   License <iohub/license>
   Change Log <iohub/change_log>
