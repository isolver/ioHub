# ioHub

ioHub is a [Python](http://www.python.org) package providing a cross-platform computer device event monitoring and storage framework. ioHub is free to use and is GLP version 3 licensed. 

ioHub is not a complete experiment design and runtime API, but is instead intended to be used with existing Python experiment runtime packages,primarily [the most excellent PsychoPy](http://www.psychopy.org). 

ioHub supports the following high level functionality:

*  Monitoring of events from computer devices such as the keyboard, mouse, analog to digital converters, XInput compatible gamepads, and eye trackers via a Common Eye Tracking Interface that provides the same user level API regardless of the eye tracking hardware used.
*  The Common Eye Tracking Interface currently supports the following eye tracking systems:
    *  [LC Technologies](http://www.eyegaze.com/) EyeGaze and EyeFollower models
    *  [SensoMotoric Instruments](http://www.smivision.com/) iViewX models
    *  [SR Research](http://www.sr-research.com) EyeLink models
    *  [Tobii Technologies](http://www.tobii.com) Tobii models
*  Support for Windows XP and 7, Apple OS X 10.6, 10.7, and Linux 2.6+  
*  Device event monitoring is done completely independently from the experiment runtime graphics environment and allows for device inputs to be captured system wide, not just for events targeted to the stimulus presentation / forground application window. In fact, no graphical window in needed at all to collect inputs from supported devices.
*  The ioHub Server, responsible for the monitoring, translation, storage, and online transmission of device events,  runs in a seperate OS process from the main application / experiment runtime process. This allows for event monitoring and device event callback processing to occur very quickly, regardless of what state the experiment runtime process is in (i.e. even when the experiment runtime process is blocked and would not be able to monitor for new events itself).
*  Device inputs can be saved by the ioHub Server Process for post hoc analysis. Assuming a multicore CPU is being used, in general *all* device events can be saved during the experiment without effecting the performance of the experiment runtime logic itself. Event data is saved in a structured format using the HDF5 standard. Event data retrieved from a data file is provided as numpy ndarray's, providing the ability to directly use retrieved data in several scientific Python models such as [Scipy](http://scipy.org/) and [MatPlotLib](http://matplotlib.org/).   
*  Events can be accessed by the experiment script during runtime either in a global, chronologically ordered, device independent manner or for a specific device type alone. 
*  Text Messages can be sent to ioHub Server as Experiment Runtime Events, allowing the easy integration of important experiment information (such as stimulus onsets, etc.), each timestamped with microsecond level precision with the ioHub timebase.
*  A common time base is provided for all device events, making it easy to syncronize data from multiple physical devices and virtual devices, such as the Experiment Runtime itself. Events are time stamped by ioHub when it is not done by the source device itself, or existing device event time stamps are converted to the common ioHub time base. 
*  Device inputs are converted into common event types based on device type, regardless of the underlying supported hardware. 

    
## Download

**Note that the provided setup.py file is currently broken, and will be fixed ASAP. For now simply download the source distribution and copy the internal 'iohub' folder (all lower case folder name) to your python path; for example your site-packages folder. Sorry for the inconvience.**

ioHub source is hosted on GitHub [here](https://www.github.com/isolver/ioHub/).

Download the source, uncompress the file downloaded, open a terminal or console in the 
uncompressed directory location, and run::

    >> python setup.py install
    
A package installers will also be made available soon.


## Documentation

The ioHub source contains a documentation folder that has been written using Sphinx.
If the ioHub source is downloaded, open a console or terminal window in the
iohub/doc/ directory and build the documentation using::

    >> make html

[Sphinx](http://sphinx-doc.org/#) must be installed.

Pre-built documentation will be available online shortly.


## Installation


Please refer to the Installation section of the documentation.


## Support

A [user forum / mailing list](https://groups.google.com/forum/?hl=en&fromgroups#!forum/iohub-users) 
and [developer forum / mailing list](https://groups.google.com/forum/?hl=en&fromgroups#!forum/iohub-dev)
are available on Google Groups for support questions and development discussion topics respectively.


## License

ioHub and the Python Common Eye Tracker Interface are Copyright (C) 2012-2013 iSolver Software Solutions, except for files or modules where otherwise noted.

ioHub is distributed under the terms of the GNU General Public License (GPL version 3 or any later version). See the LICENSE file for details. 

Python module dependancies and other 3rd party libraries are copyright their respective copyright holders. Any trademarked names used are owned by their trademark owners and use of any such names is not an endorsement of ioHub by the trademark owner.
