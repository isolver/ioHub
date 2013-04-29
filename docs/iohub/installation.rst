#############
Installation
#############

.. important:: Exciting news: ioHub is in the process of merging with the PsychoPy Package, so these Installation instructions will be changing drastically over the short term as the PsychoPy Package and PsychoPy Python Distributions are updated to include ioHub as a submodule.
 
There are different installation options depending on the target OS.

Windows
########

Using the WinPythonPlus Distribution
=====================================

The easiest way to get up and running with the ioHub and PychoPy on Windows (as of end of April, 2013)
is to download the WinPythonPlus Portable Software distribution, which includes everything you need plus
several other very useful and cool tools.

Download the WinPythonPlus self-extracting archive from ** `here <https://docs.google.com/file/d/0B-qFhchxISOSUHpfS3dvN2hXU00/edit?usp=sharing>`_ **

What's Included
++++++++++++++++

* Python 2.7.3 32 bit.
* `PsychoPy <http://www.psychopy.org>`_ and all necessary dependencies.
* ioHub and all necessary dependencies.
* `NumPy <http://www.numpy.org>`_.
* `SciPy <http://www.scipy.org>`_.
* `Matplotlib <http://matplotlib.org/>`_.
* `iPython 0.13 <http://ipython.org/install.html>`_ , including the iPython qtConsole and iPython Notebook.
* `PyQt <http://wiki.python.org/moin/PyQt>`_.
* `PyGraphQt <http://www.pyqtgraph.org/>`_.
* `GuiQwt <https://code.google.com/p/guiqwt/>`_.
* `GuiData <http://pythonhosted.org/guidata/>`_.
* `OpenCV (including the cv2 Python interface) <http://opencv.org/>`_.
* `cython <http://www.cython.org/>`_, using the provided minggw / gnuwin32 / gcc tool chain.
* `Spyder <https://code.google.com/p/spyderlib/>`_.
* `HDFView <http://www.hdfgroup.org/hdf-java-html/hdfview/>`_, a HDF5 file viewer written by The HDF Group.
* Several other useful python packages for scientific applications.

Installation of WinPythonPlus
++++++++++++++++++++++++++++++

Given WinPythonPlus is provided in the form of a portable software distribution, 
there is no actual *installation* required. Simply downloaded the WinPythonPlus archive from the link above, 
run the self extracting archive, and select where you want the WinPythonPlus distribution to go. **That is it.**
Once extracted, open the WinPythonPlus folder and you will see a set of .bat files in the top level directory
(a poor mans version of an executable ;) ). The .bat file are what need to be used to start any of the 
provided applications, and even when you wish to just start a python interpreter in the Windows console.


.. note:: WinPythonPlus is based on the `great WinPython project <http://www.winpython.org>`_, with extra packages added and the structure of the distribution changed somewhat. WinPython makes no permanent changes to your Windows registry or environment settings. Only temporary changes are made to the shell environment that is launched to run which ever application you run.

.. warning:: It is important to always launch a tool packaged in the WinPythonPlus distribution using the provided launcher .bat file or exe in the WinPythonPlus root folder. These launchers temporarily configure the environment variables for that process so that the application and associated APIs will run correctly. Starting one of the provided tools by directly running the tools exe or similar file will not work correctly and will cause unexpected issues and perhaps application crashes.
	
.. note:: **Nothing can happen to your computer that would affect your computer overall or result in long standing issues though, don't worry.**

Manually Installing ioHub
===========================

The following software must be installed on the computer before proceeding with 
the ioHub dependency installation list and installation of ioHub itself: 

    #. Python 2.6.8 or 2.7.3 32 bit is required as the Python interpreter. The 32 bit version of Python can be installed on a supported 64 bit OS.

    #. Psychopy 1.74.03 or higher and all of it's dependencies. See the `PsychoPy installation <http://www.psychopy.org/installation.html>`_ page for details. 

    #. For the NumPy package, please ensure 1.6.2 or greater is installed.

Dependency Installation List 
+++++++++++++++++++++++++++++

Once Python and PsychoPy (including all the stated PsychoPy dependencies) are installed, the following extra Python packages must be installed for the ioHub:

Python 2.7 Package List with URLs
++++++++++++++++++++++++++++++++++

    #. `psutil <http://code.google.com/p/psutil/downloads/detail?name=psutil-0.6.1.win32-py2.7.exe>`_ A cross-platform process and system utilities module for Python
    #. `msgpack <http://pypi.python.org/packages/2.7/m/msgpack-python/msgpack_python-0.2.0-py2.7-win32.egg#md5=d52bd856ca8c8d9a6ee86937e1b4c644>`_ It's like JSON. but fast and small.
    #. `greenlet <http://pypi.python.org/packages/2.7/g/greenlet/greenlet-0.4.0.win32-py2.7.exe#md5=910896116b1e4fd527b8afaadc7132f3>`_ The greenlet package is a spin-off of Stackless, a version of CPython that supports micro-threads called "tasklets".
    #. `gevent <https://github.com/downloads/SiteSupport/gevent/gevent-1.0rc2.win32-py2.7.exe>`_ A coroutine-based Python networking library that uses greenlet to provide a high-level synchronous API on top of the libevent event loop.
    #. `numexpr <http://code.google.com/p/numexpr/downloads/detail?name=numexpr-1.4.2.win32-py2.7.exe&can=2&q=>`_ Fast numerical array expression evaluator for Python and NumPy.
    #. `pytables <http://www.lfd.uci.edu/~gohlke/pythonlibs/#pytables>`_ PyTables is a package for managing hierarchical datasets and designed to efficiently and easily cope with extremely large amounts of data.
    #. `pyYAML <http://pyyaml.org/download/pyyaml/PyYAML-3.10.win32-py2.7.exe>`_ PyYAML is a YAML parser and emitter for Python.
    #. `pywin32 <http://sourceforge.net/projects/pywin32/files/pywin32/Build%20217/pywin32-217.win32-py2.7.exe/download>`_ Python Extensions for Windows
    #. `pyHook <http://sourceforge.net/projects/pyhook/files/pyhook/1.5.1/pyHook-1.5.1.win32-py2.7.exe/download>`_ Python wrapper for global input hooks in Windows.

Python 2.6 Package List with URLs
+++++++++++++++++++++++++++++++++++

    #. `psutil <https://code.google.com/p/psutil/downloads/detail?name=psutil-0.6.1.win32-py2.6.exe>`_ A cross-platform process and system utilities module for Python
    #. `msgpack <http://www.lfd.uci.edu/~gohlke/pythonlibs/#msgpack>`_ It's like JSON. but fast and small.
    #. `greenlet <https://pypi.python.org/packages/2.6/g/greenlet/greenlet-0.4.0.win32-py2.6.exe>`_ The greenlet package is a spin-off of Stackless, a version of CPython that supports micro-threads called "tasklets".
    #. `gevent <https://code.google.com/p/gevent/downloads/detail?name=gevent-1.0b4.win32-py2.6.exe&can=2&q=>`_ A coroutine-based Python networking library that uses greenlet to provide a high-level synchronous API on top of the libevent event loop.
    #. `numexpr <http://code.google.com/p/numexpr/downloads/detail?name=numexpr-1.4.2.win32-py2.6.exe&can=2&q=>`_ Fast numerical array expression evaluator for Python and NumPy.
    #. `pytables <http://www.lfd.uci.edu/~gohlke/pythonlibs/#pytables>`_ PyTables is a package for managing hierarchical datasets and designed to efficiently and easily cope with extremely large amounts of data.
    #. `pyYAML <http://pyyaml.org/download/pyyaml/PyYAML-3.10.win32-py2.6.exe>`_ PyYAML is a YAML parser and emitter for Python.
    #. `pyHook <http://sourceforge.net/projects/pyhook/files/pyhook/1.5.1/pyHook-1.5.1.win32-py2.6.exe/download>`_ Python wrapper for global input hooks in Windows.
    #. `pywin32 <http://sourceforge.net/projects/pywin32/files/pywin32/Build%20217/pywin32-217.win32-py2.6.exe/download>`_ Python Extensions for Windows

Several of the devices supported by ioHub require the installation of a binary OS driver
for the device that can not be included with the ioHub package due to licensing 
considerations. Please refer to the documentation page for each device you will be using to ensure that
any device specific driver required is known about and is installed.

ioHub Package Installation
++++++++++++++++++++++++++++++

There is currently no python package installer for ioHub, so to install the ioHub package itself, the iohub source directory can simply be copied to a location in your Python Path. 
The site-packages directory of your Python installation is a guaranteed place that will work. 

To do so:

#. Get a `zip download <https://github.com/isolver/ioHub/zipball/master/>`_ of the `ioHub project source <https://www.github.com/isolver/ioHub/>`_
#. Open the zip file.
#. Copy the **inner** iohub (all lower case) folder that is located in the top level directory of the zip file downloaded to your python site-packages directory. (likely something like C:\Python27\Lib\site-packages, or C:\Python26\Lib\site-packages).


Linux
#######

For Linux the WinPythonPlus distribution can not be used. Instead the necessary
packages must be installed using the OS's package manager and the Python pip 
and / or easy_install utilities. Fortunately, on Linux, this is a very easy 
process that almost anyone can do.

Manually Installing ioHub
===========================

The following software must be installed on the computer before proceeding with 
the ioHub dependency installation list and installation of ioHub itself: 

    #. Python 2.6.8 or 2.7.3 32 bit is required as the Python interpreter. The 32 bit version of Python can be installed on a supported 64 bit OS.

    #. Psychopy 1.74.03 or higher and all of it's dependencies. See the `PsychoPy installation <http://www.psychopy.org/installation.html>`_ page for details. 

    #. For the NumPy package, please ensure 1.6.2 or greater is installed.

ioHub Dependency List Installation
+++++++++++++++++++++++++++++++++++

The following Python packages need to be installed on the system you plan to run
ioHub on. Some packages can be installed using *pip*, while other should be installed 
by downloading the package from the provided URL, unpacking the tarball, and 
installing the package by typing::

    > python setup.py install

in a terminal session where you have changed directories to the location of the uncompressed 
python package source that contains the setup.py script.

Some packages downloaded via a URL are a .deb file, in which case you just download
the file and install it by double clicking the .deb file once downloaded. 

Note that for both 'pip' and manual 'python setup.py install', depending on your
Linux distribution and system configuration, you may need to run pip or 
'python setup.py install' with root privileges by placing 'sudo ' in front of the
command line text to be run.

For example::

    > sudo pip install package_name

where package_name is the name of one of the required python packages.

Installing pip if it is not Already on the System
+++++++++++++++++++++++++++++++++++++++++++++++++++

If you type:: 

    > pip

in a console and are told the program does not exist, then you can install pip using::

    > sudo apt-get install pip

Packages To Download with URLs
++++++++++++++++++++++++++++++

#. `psutil <http://code.google.com/p/psutil/downloads/detail?name=psutil-0.6.1.tar.gz&can=2&q=>`_ A cross-platform process and system utilities module for Python
#. `gevent <https://github.com/downloads/SiteSupport/gevent/python-gevent_1.0rc2_i386.deb>`_ A coroutine-based Python networking library that uses greenlet to provide a high-level synchronous API on top of the libevent event loop.
#. `numexpr <http://code.google.com/p/numexpr/downloads/detail?name=numexpr-2.0.1.tar.gz&can=2&q=>`_ Fast numerical array expression evaluator for Python and NumPy.
#. `pyYAML <http://pyyaml.org/wiki/PyYAMLDocumentation>`_ Following install instructions on the page. PyYAML is a YAML parser and emitter for Python. For faster processing, also download and install `LibYAML <http://pyyaml.org/wiki/LibYAML>`_; following install instructions on the page.
#. `python-xlib <http://sourceforge.net/projects/python-xlib/>`_ The Python X Library is a complete X11R6 client-side implementation, written in pure Python.


Packages to install using pip
++++++++++++++++++++++++++++++

#. msgpack: It's like JSON. but fast and small. ( pip install msgpack-python )
#. greenlet: The greenlet package is a spin-off of Stackless, a version of CPython that supports micro-threads called "tasklets". ( pip install greenlet )
#. pytables: PyTables is a package for managing hierarchical datasets and designed to efficiently and easily cope with extremely large amounts of data. ( pip install tables )

ioHub Package Installation
++++++++++++++++++++++++++++++

There is currently no python package installer for ioHub, so to install the ioHub package itself, the iohub source directory can simply be copied to a location in your Python Path. 
The site-packages directory of your Python installation is a guarenteed place that will work. 

To do so:

#. Get a `zip download <https://github.com/isolver/ioHub/zipball/master/>`_ of the `ioHub project source <https://www.github.com/isolver/ioHub/>`_
#. Open the zip file.
#. Copy the **inner** iohub (all lower case) folder that is located in the top level directory of the compressed file downloaded to a directory in your Python path. sudo access may be needed.


OSX 10.6 - 10.8
################

For OS X 10.6 + the WinPythonPlus distribution can not be used. Instead the necessary
packages must be installed. Unfortunately, on OS X, this can be a frustrating task. If you are
based at a university, then I would suggest that you get a free copy of the Enthought Canopy Python distribution. 
The link to apply for one is: https://www.enthought.com/products/canopy/academic/
The Enthought Canopy Python distribution includes many of the packages needed by PsychoPy and ioHub.
You will find that some packages are still missing and must be installed manually.

Manual Installation
====================

The following software must be installed on the computer before proceeding with 
the ioHub dependency installation list and installation of ioHub itself: 

    #. Python 2.6.8 or 2.7.3 32 bit is required as the Python interpreter. The 32 bit version of Python can be installed on a supported 64 bit OS.

    #. Psychopy 1.74.03 or higher and all of it's dependencies. See the `PsychoPy installation <http://www.psychopy.org/installation.html>`_ page for details. 

    #. For the NumPy package, please ensure 1.6.2 or greater is installed.

Dependency List Installation
++++++++++++++++++++++++++++++

The following Python packages need to be installed on the system you plan to run
ioHub on. Some packages can be installed using *pip*, while other should be installed 
by downloading the package from the provided URL, unpacking the tarball, and 
installing the package by typing::

    > python setup.py install

in a terminal session where you have changed directories to the location of the uncompressed 
python package source that contains the setup.py script.

Note that for both 'pip' and manual 'python setup.py install', depending on your
OS X settings and python configuration, you may need to run pip or 
'python setup.py install' with root priveledges.

If your user has admin rights, this can be done by running the command with 'sudo'
at the start of the command and entering your password when prompted. For example::

    > sudo pip install package_name

where package_name is the name of one of the required python packages.

Installing pip if it is not Already on the System
++++++++++++++++++++++++++++++++++++++++++++++++++

If you type:: 

    > pip

in a console and are told the program does not exist, then you can install pip or easy_install before proceeding.


Packages to install using pip or easy_install
++++++++++++++++++++++++++++++++++++++++++++++

#. **msgpack** It's like JSON. but fast and small. ( pip install msgpack-python )
#. **greenlet** The greenlet package is a spin-off of Stackless, a version of CPython that supports micro-threads called "tasklets". ( pip install greenlet )
#. **pytables** PyTables is a package for managing hierarchical datasets and designed to efficiently and easily cope with extremely large amounts of data. ( pip install tables ). FIRST INSTALL 'numexpr' from the list below, as it is a dependency of tables) 

Packages To Download
++++++++++++++++++++

#. `pyobjc <https://pypi.python.org/packages/source/p/pyobjc/pyobjc-2.5.1.tar.gz#md5=f242cff4a25ce397bb381c21a35db885>`_ : A  Python ObjectiveC binding.    
#. **gevent**: A coroutine-based Python networking library that uses greenlet to provide a high-level synchronous API on top of the libevent event loop::

		pip install cython -e git://github.com/surfly/gevent.git@1.0rc2#egg=gevent

#. `numexpr <http://code.google.com/p/numexpr/downloads/detail?name=numexpr-2.0.1.tar.gz&can=2&q=>`_ Fast numerical array expression evaluator for Python and NumPy.    
#. `pyYAML <http://pyyaml.org/download/pyyaml/PyYAML-3.10.tar.gz>`_ PyYAML is a YAML parser and emitter for Python. First install the C side package `LibYAML <http://pyyaml.org/wiki/LibYAML>`_, before installing ptYAML.

ioHub Package Installation
+++++++++++++++++++++++++++

There is currently no python package installer for ioHub, so to install the ioHub package itself, the iohub source directory can simply be copied to a location in your Python Path. 
The site-packages directory of your Python installation is a guarenteed place that will work. 

To do so:

#. Get a `zip download <https://github.com/isolver/ioHub/zipball/master/>`_ of the `ioHub project source <https://www.github.com/isolver/ioHub/>`_
#. Open the zip file.
#. Copy the **inner** iohub (all lower case) folder that is located in the top level directory of the compressed file downloaded to a directory in your Python path. sudo access may be needed.


Running Example Scripts
#########################

Running example scripts using ioHub should now work. All examples are in the *examples* folder of the iohub distribution. To run a demo, open a console and cd to the **Example dir** (relative to the iohub root folder): examples\ioHubAccessDelayTest         

**Run with**: python run.py

or cd to **Demo dir** (relative to the ioHub root folder):  examples\PsychoPy_Ports\ioMouse

**Run with**: python ioMouse.py

