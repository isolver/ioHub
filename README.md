# ioHub Framework, including the pyEyeTrackerInterface

## Project Status

Please see the project webpage http://isolver.github.com/ioHub for current status details.

## Overview

The ioHub is a Python framework that runs in a seperate system process in parallel
to psycopy ( http://www.psychopy.org ) during experiment runtime / data collection.

The ioHub could  also be used by any other python application that is interested in the 'services' it offers,
however all development and testing has been done with psychopy as the application / experiment runtime.

The ioHub effectively acts as a proxy between the experiment logic and the input and output devices
used by the experiment, centralizing a large portion of the I/O bound tasks an application may have into a
common asynchronous, non-blocking, architecture that runs in a seperate independent process.

The **main features / goals** of the ioHub are:

1. **Integrate data collection from multiple devices**, including keyboard, 
   mouse, parallel port, eye trackers ( using the Common Eye Tracker 
   Interface project ), etc.
   
2. **Time Base Syncronization** and normalization across different devices.

3. **Common Data Stream / Event Access and Data Types**, regardless of device. 
   The ioHub, while normalizing the time stamps of all input events to a 
   common experiment / application level timebase, also provides the 
   convenience of a single interface to device data, and common device
   sample and event definition standards. Furthermore devices within
   the same device category will have their sample data and events mapped
   to a single set of vendor independent structures as much as possible.

4. **Low Overhead Design.** The ioHub runs as a seperate process from your
   experiment / psychopy, while at the same time doing work that your application
   once needed to spend CPU time on and perhaps dead I/O blocking time on
   (depending on your application design of course). The ioHub allows 
   for this work to be done truely in parallel with your application on 
   any multiprocessor / multicore based computer. Multicore CPUs are now
   standard for laptop and desktop computers. These advantages are provided 
   with a simple and fast request / response IPC architechure using standard 
   Python UDP sockets / packets, making it very cross platform to boot.
   The request / response pattern also hels ensure that, if a UDP packet
   is dropped, the ioHub Client, or the ioHub itself will know about
   it and can handle it. Current performance tests on Windows 7, using an
   i5 mobile chipset connecting with 127.0.0.1, show base request / response 
   round trip times through the core ioHub infrastructure taking under 
   300 usec on average ( 0.3 msec, 0.003 sec ) with packet loads of about 1400 bytes. 
   In all tests preformed to date, no dropped packets have occurred.

5. **Data Storage.** Given all the data stream / event based processing that
   the ioHub is doing, it seems to only make sense to offer the option for
   it to also save all this data from the ioHub process, further reducing
   the overhead and processing required by your application if it is not 
   needed. The experiment runtime can therefore request certain events to
   be available over the UDP connection, while all data be saved to disk.
   The experiment itself can in effect act as an input device in this case,
   sending Experiment Events to the ioHub to be integrated with the rest 
   of the device data and saved for future analysis. pyTables ( www.pytables.org ) is used
   as the API / storage mechanism for the ioHub. This functionality is packaged in
   the ioHub.ioDataStore directory. The use of this functionality is completely optional,
   may not be of use in all situations, and requires further requirements refinement refinement
   to move implementation beyond an alpha stage of functionality. With that said, it also has a huge 
   amount of potential.

## Installing

  Currently only Windows is supported. This will change to Linux and Mac OS X as well
  as time permits.
  
  Python 2.7.3 32 bit for Windows is required as the python interpreter (not Python 3.0, 
  and not Python 2.6 due to a couple bugs, that could be worked around, but have yet to be)
  (can be installed on 32 or 64 bit version of OS)

  You then need to install psychopy and all of it's dependencies. Note that the 'all in one' Windows
  installer installs 2.6 at this time, so it can not be used. You must install psychopy as a 
  package and all the psychopy dependencies seperately.
  
   psychopy 1.74.01 for Python 2.7 - http://code.google.com/p/psychopy/downloads/

  And all dependencies for it, which are listed at:

   http://www.psychopy.org/installation.html#dependencies

  You will want to get with python 2.7 win32 version of each dependency.
 
  **For numpy, please get 1.6.2 or higher.**

  OK, once you have all that installed, you will want to get the following extra 
  dependencies for ioHub and ioDataStore:
  
   psutil: http://code.google.com/p/psutil/downloads/detail?name=psutil-0.5.1.win32-py2.7.exe
 
   ujson: http://pypi.python.org/packages/2.7/u/ujson/ujson-1.19.win32-py2.7.exe#md5=a5eda15e99f6091e9e550887b35e7fd4

   msgpack: http://pypi.python.org/packages/2.7/m/msgpack-python/msgpack_python-0.2.0-py2.7-win32.egg#md5=d52bd856ca8c8d9a6ee86937e1b4c644

   gevent: http://code.google.com/p/gevent/downloads/detail?name=gevent-1.0b3.win32-py2.7.exe&can=2&q=
   
   greenlet: http://pypi.python.org/packages/2.7/g/greenlet/greenlet-0.4.0.win32-py2.7.exe#md5=910896116b1e4fd527b8afaadc7132f3

   pytables: http://www.lfd.uci.edu/~gohlke/pythonlibs/#pytables 
    
   numexpr: http://code.google.com/p/numexpr/downloads/detail?name=numexpr-1.4.2.win32-py2.7.exe&can=2&q=

   pywin32: http://sourceforge.net/projects/pywin32/files/pywin32/Build%20217/pywin32-217.win32-py2.7.exe/download
    
   pyHook: http://sourceforge.net/projects/pyhook/files/pyhook/1.5.1/pyHook-1.5.1.win32-py2.7.exe/download
   
   pyYAML: http://pyyaml.org/download/pyyaml/PyYAML-3.10.win32-py2.7.exe

   For parallel port access in Windows, you also need to download and install the following driver (free for personal use):

   http://www.entechtaiwan.com/dev/port/index.shtm

   'Finally', the ioHub source to your site-packages folder, putting the ioHub directory in the site-packages directory 
   of your Python 2.7 installation. 

## Known Issues / Black Holes

See the Bug Tracker.

## Examples

See the examples directory (https://github.com/isolver/ioHub/tree/master/examples) in the ioHub folder. Also see the project webpage for details on which examples are
currently running.

## Getting Help

email: sds-git _AT_ isolver-software.coT (change _AT_ to an @ and the T to an m)

## License

ioHub and ioDataStore are Copyright (C) 2012 Sol Simpson, except for files where otherwise noted.

ioHub and ioDataStore are distributed under the terms of the GNU General Public License (GPL version 3 or any later version).
See the LICENSE file for details.

