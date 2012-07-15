# ioHub

# Project Status

The ioHub is actively in development, but is very new. It is therefore
at a point where it is very likely that downloading the code and trying
to run it will fail. Please bear with us as we get the ioHub to a stable
'alpha' state.

#Overview

The ioHub module is intended to be a standalone Python service that runs
in parallel to psycopy ( http://www.psychopy.org ) during experiment 
runtime / data collection. The ioHub can also be used by any other
application that is interested in the 'service' it offers.

The ioHub effectively acts as a proxy between the experiment logic 
and the input and output devices used by the experiment, centralizing 
a large portion of the I/O bound tasks an application may have into a
common asynchronous non-blocking architecture that runs in a seperate
independent process than the application itself (not a child process).

The **main features / goals** of the ioHub are:

1. **Integrate data collection from multiple devices**, including keyboard, 
   mouse, parallel port, eye trackers ( using the Common Eye Tracker 
   Interface project ), etc.
   
2. **Time Base Syncronization.**

2a.For devices that provide data streams and / or events that are time
   stamped, the ioHub will convert the various "Device Time"s to a common
   "Application Time" base. The exact mechanism for determining the 'offset' 
   between the two time bases is device dependent, please see the full 
   documentation for details. The base offset that is determined is applied
   to convert the Device Time to Application Time prior to further corrections.

2b.For devices that do not provide time stamped data streams or events, the ioHub
   will time stampe them in Application Time when the ioHub receives the event.
   An important goal of the ioHub is to keep its core IOLoop as fast as possible, 
   following a non-blocking asyncronous methodology whenever possible. 
   This has the effect of it being able to check for polled device updates 
   quickly ( currently several times a msec ). This also means time stampes
   for this type of devices whould be sub millisecond *realative to when 
   the event was received by the hub*. 

2c.The accuracy and precision of time stamping is
   important to the ioHub, so it does what it can, when it can:*  

     i)  The offset between time bases is corrected for, when an existing 
         time stamp is present.

     ii) Delay that is measurable, or a known average, can be applied to
         each device data stream and event type to correct for the delay
         in the time stamp.

     iii)Drift between the Application Time base and each Device's timebase
         can be actively monitored and also corrected for in the Application
         time stamping. This is necessary when the Application Time base and
         the Device Time are derived from difference clocks / crystals.

     *It is important to note that the ability for the ioHub to correct 
      for the above factors is 100% device and OS dependent. If a device
      has not been designed with proper time base interfacing in mind, and
      there are therefore limited, coarse, or no ways to determine one or more
      of these factors, then the ioHub can only do so much in this area.
      The documentation will have a section outlining what is in place for
      each device, what the level of expected accuracy and precision should be, 
      and what (if any) tests have been done to date to validate the 
      time base corrections.

3.**Common Data Stream / Event Access and Data Types**, regardless of device. 
   The ioHub, while normalizing the time stamps of all input events to a 
   common experiment / application level timebase, also provides the 
   convenience of a single interface to device data, and common device
   sample and event definition standards. Furthermore devices within
   the same device category will have their sample data and events mapped
   to a single set of vendor independent structures as much as possible.

4. **Low Overhead Design.** The ioHub runs as a seperate process from your
   application, while at the same time doing work that your application
   once needed spend CPU time on and perhaps dead I/O blocking time on
   (depending on your application design of course). The ioHub allows 
   for this work to be done truely in parallel with your application on 
   any multiprocessor / multicore base computer. Multicore CPUs are now
   standard for laptop and desktop computers. These advantages are provided 
   with a simple and fast request / response IPC architechure using standard 
   Python UDP sockets / packets, making it very cross platform to boot.
   The request / response pattern also hels ensure that, if a UDP packet
   is dropped, the ioHub Client, or the ioHub itself will know about
   it and can handle it. Current performance tests on Windows 7, using an
   i5 mobile chipset connecting with 127.0.0.1, show base request / response 
   round trip times through the core ioHub infrastructure taking under 
   100 usec ( 0.1 msec, 0.001 sec ) with packet loads of about 1400 bytes. 
   In all tests preformed to date, no dropped packets have occurred.

5. **Data Storage.** Given all the data stgream / event based processing that
   the ioHub is doing, it seems to only make sense to offer the option for
   it to also save all this data from the ioHub process, further reducing
   the overhead and processing required by your application if it is not 
   needed. The experiment runtime can therefore request certain events to
   be available over the UDP connection, while all data be saved to disk.
   The experiment itself can in effect act as an input device in this case,
   sending Experiment Events to the ioHub to be integrated with the rest 
   of the device data and saved for future analysis. pyTables will be used
   as the API / storage mechanism for the ioHub. This feature is completely
   optional, may not be of use in all situations, and requires further 
   definition refinement befine implementation of an alpha stage of 
   functionality can occur.      

# Installing

TBC

# Dependencies

TBC

# Known Issues / Black Holes

TBC

# Getting Help

email: sds-git _AT_ isolver-solftware.coP (change the P to an m)
