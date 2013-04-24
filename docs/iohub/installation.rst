==================================
Installation
==================================

There are different installation options depending on the target OS.

Windows
==================================

Using the OpenPsycho Distribution
--------------------------------------

The easiest way to get up and running with the ioHub on Windows is to download
the OpenPsycho Portable Software distribution, which includes the following, 
in high level outine form:
    * Python 2.7.3 32 bit
    * PsychoPy and all necessary dependencies, including numpy and scipy
    * ioHub and all necessary dependencies
    * Matplotlib
    * iPython, including the iPython qtConsole and iPython Notebook
    * PyQt, pyqtgraph, and pyqtgui
    * cv2 OpenCV Python wrappers
    * support for cython development out of the box
    * several other useful python packages for scientific applications.
    * Spyder Python IDE
    * Libre Office
    * GIMP
    * Many other python packages preinstalled.
    
Given OpenPsycho is provided in the form of a portable software distribution, 
there is no actual *installation* required. Simply download the latest distribution
from `here <URL_TO_BE_DETERMINED>`_ and unpack the self extracting archive to the 
location of your choosing.

OpenPsycho is based on the `WinPython project <http://www.winpython.org>`_, with extra packages
added and the structure of the distribution changed somewhat.

The OpenPsycho file you download is a self extracting '7zip <www.7zip.org>`_ archive.
7zip is **not** required to be installed on your computer to run the self extracting file. 
Simply double click on the downloaded OpenPsycho.exe and select where you want
the OpenPsycho directory placed in your file system. Avoiding paths with the ' '
space character in them may be a safe idea. Placing the extracted OpenPsycho 
directory in the root C:\ folder is often easiest; or the root of another partition, or
USB drive. No changes to your Windows registry or environment variables are made
during installation.

Once extracted, open the OpenPsycho folder and a set of bat files 
(soon to be exe files) can be found and used to start the main tools
of the OpenPsycho distribution. 

.. note:: It is very important to always launch a tool packaged in the OpenPsycho
    distribution using the provided launch .bat file or exe in the openPsycho 
    folder root folder. These launchers temporarily configure the environment 
    variables for that process so that the application and associated APIs will 
    run correctly. 
    
    Starting a tool by directly running the tools exe or similar file will not 
    work correctly and will cause unexpected issues and perhaps application crashes.
    Nothing will happen that would effect your computer overall or result
    in long standing issues though, don't worry.

Manually Installing ioHub
----------------------------

The following software must be installed on the computer before proceeding with 
the ioHub dependency installation list and installation of ioHub itself: 

    #. Python 2.6.8 or 2.7.3 32 bit is required as the Python interpreter. The 32 bit version of Python can be installed on a supported 64 bit OS.

    #. Psychopy 1.74.03 or higher and all of it's dependencies. See the `PsychoPy installation <http://www.psychopy.org/installation.html>`_ page for details. 

    #. For the NumPy package, please ensure 1.6.2 or greater is installed.

Dependency List Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once Python and PsychoPy are installed, the following extra Python packages must
be installed for the ioHub:

Python 2.7 Package List
~~~~~~~~~~~~~~~~~~~~~~~~~~

    #. `psutil: <http://code.google.com/p/psutil/downloads/detail?name=psutil-0.6.1.win32-py2.7.exe>`_ A cross-platform process and system utilities module for Python
    #. `msgpack: <http://pypi.python.org/packages/2.7/m/msgpack-python/msgpack_python-0.2.0-py2.7-win32.egg#md5=d52bd856ca8c8d9a6ee86937e1b4c644>`_ It's like JSON. but fast and small.
    #. `greenlet: <http://pypi.python.org/packages/2.7/g/greenlet/greenlet-0.4.0.win32-py2.7.exe#md5=910896116b1e4fd527b8afaadc7132f3>`_ The greenlet package is a spin-off of Stackless, a version of CPython that supports micro-threads called "tasklets".
    #. `gevent: <https://github.com/downloads/SiteSupport/gevent/gevent-1.0rc2.win32-py2.7.exe>`_ A coroutine-based Python networking library that uses greenlet to provide a high-level synchronous API on top of the libevent event loop.
    #. `numexpr: <http://code.google.com/p/numexpr/downloads/detail?name=numexpr-1.4.2.win32-py2.7.exe&can=2&q=>`_ Fast numerical array expression evaluator for Python and NumPy.
    #. `pytables: <http://www.lfd.uci.edu/~gohlke/pythonlibs/#pytables>`_ PyTables is a package for managing hierarchical datasets and designed to efficiently and easily cope with extremely large amounts of data.
    #. `pyYAML: <http://pyyaml.org/download/pyyaml/PyYAML-3.10.win32-py2.7.exe>`_ PyYAML is a YAML parser and emitter for Python.
    #. `pywin32: <http://sourceforge.net/projects/pywin32/files/pywin32/Build%20217/pywin32-217.win32-py2.7.exe/download>`_ Python Extensions for Windows
    #. `pyHook: <http://sourceforge.net/projects/pyhook/files/pyhook/1.5.1/pyHook-1.5.1.win32-py2.7.exe/download>`_ Python wrapper for global input hooks in Windows.

Python 2.6 Package List
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #. `psutil: <https://code.google.com/p/psutil/downloads/detail?name=psutil-0.6.1.win32-py2.6.exe>`_ A cross-platform process and system utilities module for Python
    #. `msgpack: <http://www.lfd.uci.edu/~gohlke/pythonlibs/#msgpack>`_ It's like JSON. but fast and small.
    #. `greenlet: <https://pypi.python.org/packages/2.6/g/greenlet/greenlet-0.4.0.win32-py2.6.exe>`_ The greenlet package is a spin-off of Stackless, a version of CPython that supports micro-threads called "tasklets".
    #. `gevent: <https://code.google.com/p/gevent/downloads/detail?name=gevent-1.0b4.win32-py2.6.exe&can=2&q=>`_ A coroutine-based Python networking library that uses greenlet to provide a high-level synchronous API on top of the libevent event loop.
    #. `numexpr: <http://code.google.com/p/numexpr/downloads/detail?name=numexpr-1.4.2.win32-py2.6.exe&can=2&q=>`_ Fast numerical array expression evaluator for Python and NumPy.
    #. `pytables: <http://www.lfd.uci.edu/~gohlke/pythonlibs/#pytables>`_ PyTables is a package for managing hierarchical datasets and designed to efficiently and easily cope with extremely large amounts of data.
    #. `pyYAML: <http://pyyaml.org/download/pyyaml/PyYAML-3.10.win32-py2.6.exe>`_ PyYAML is a YAML parser and emitter for Python.
    #. `pyHook: <http://sourceforge.net/projects/pyhook/files/pyhook/1.5.1/pyHook-1.5.1.win32-py2.6.exe/download>`_ Python wrapper for global input hooks in Windows.
    #. `pywin32: <http://sourceforge.net/projects/pywin32/files/pywin32/Build%20217/pywin32-217.win32-py2.6.exe/download>`_ Python Extensions for Windows

Several of the devices supported by ioHub require the installation of an OS driver
for the device that can not be included with the ioHub package due to licensing 
considerations. Please refer to the documentation page for each device to ensure that
any device specific driver required is known about and is installed.

ioHub Package Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install the ioHub package itself, currently no python package installer exists. 
Therefore the ioHub source is simply copied to your Python site-packages folder, 
putting the ioHub directory in the site-packages directory of your Python installation.
To do so:

#. Get a `zip download <https://github.com/isolver/ioHub/zipball/master/>`_ of the `ioHub project source <https://www.github.com/isolver/ioHub/>`_
#. Open the zip file.
#. Copy the folder in the zip file to your python site-packages directory. (likely something like C:\Python27\Lib\site-packages, or C:\Python27\Lib\site-packages)
#. Rename the folder you copied to the site-packages directory from ioHub-master to just ioHub .


Linux
=================

For Linux the OpenPsycho distribution can not be used. Instead the necessary
packages must be installed using the OS's package manager and the Python pip 
and / or easy_install utilities.

Manually Installing ioHub
----------------------------

The following software must be installed on the computer before proceeding with 
the ioHub dependency installation list and installation of ioHub itself: 

    #. Python 2.6.8 or 2.7.3 32 bit is required as the Python interpreter. The 32 bit version of Python can be installed on a supported 64 bit OS.

    #. Psychopy 1.74.03 or higher and all of it's dependencies. See the `PsychoPy installation <http://www.psychopy.org/installation.html>`_ page for details. 

    #. For the NumPy package, please ensure 1.6.2 or greater is installed.

ioHub Dependency List Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following Python packages need to be installed on the system you plan to run
ioHub on. Some apckages can be installed using *pip*, while other should be installed 
by downloading the package from the provided URL, unpacking the tarball, and 
installing the package by typing::

    > python setup.py install

in a terminal session where you have cd to the location of the uncompressed 
python package source that contrains the setup.py script.

Some packages downloaded via a URL are a .deb file, in which case you just download
the file and install it by dowble clicking the .deb file once downloaded. 

Note that for both 'pip' and manual 'python setup.py install', depending on your
Linux distribution and system configuration, you may need to run pip or 
'python setup.py install' with root priveledges.

If your user had admin rights, this can be done by running the command with 'sudo'
at the start of the command and entering your password when prompted. For example::

    > sudo pip install package_name

where package_name is the name of one of the required python packages.

Installing pip if it is not Already on the System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you type:: 

    > pip

in a console and are told the program does not exist, then you can install pip using::

    > sudo apt-get install pip

Packages To Download
~~~~~~~~~~~~~~~~~~~~~~~~~~

#. `psutil: <http://code.google.com/p/psutil/downloads/detail?name=psutil-0.6.1.tar.gz&can=2&q=>`_ A cross-platform process and system utilities module for Python
#. `gevent: <https://github.com/downloads/SiteSupport/gevent/python-gevent_1.0rc2_i386.deb>`_ A coroutine-based Python networking library that uses greenlet to provide a high-level synchronous API on top of the libevent event loop.
#. `numexpr: <http://code.google.com/p/numexpr/downloads/detail?name=numexpr-2.0.1.tar.gz&can=2&q=>`_ Fast numerical array expression evaluator for Python and NumPy.
#. `pyYAML: <http://pyyaml.org/wiki/PyYAMLDocumentation>`_ Following install instructions on the page. PyYAML is a YAML parser and emitter for Python. For faster processing, also download and install `LibYAML <http://pyyaml.org/wiki/LibYAML>`_; following install instructions on the page.
#. `python-xlib: <http://sourceforge.net/projects/python-xlib/>`_ The Python X Library is a complete X11R6 client-side implementation, written in pure Python.


Packages to install using pip
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. msgpack: It's like JSON. but fast and small. ( pip install msgpack-python )
#. greenlet: The greenlet package is a spin-off of Stackless, a version of CPython that supports micro-threads called "tasklets". ( pip install greenlet )
#. pytables: PyTables is a package for managing hierarchical datasets and designed to efficiently and easily cope with extremely large amounts of data. ( pip install tables )

ioHub Package Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install the ioHub package itself the source should be downloaded from github, 
as currently no python package installer exists. 

To do so:

#. Get a `zip download <https://github.com/isolver/ioHub/zipball/master/>`_ of the `ioHub project source <https://www.github.com/isolver/ioHub/>`_
#. Open the zip file
#. Rename the folder in the zip, which is likely called something like 'iohub-master', to just 'ioHub'.
#. Copy the 'ioHub' folder to a directory in your Python path. sudo access may be needed.


OSX 10.6 - 10.8
====================

For OS X 10.6 + the OpenPsycho distribution can not be used. Instead the necessary
packages must be installed using the OS's package manager and the Python pip utility
as well as manually building packages

Manual Installation
----------------------------

The following software must be installed on the computer before proceeding with 
the ioHub dependency installation list and installation of ioHub itself: 

    #. Python 2.6.8 or 2.7.3 32 bit is required as the Python interpreter. The 32 bit version of Python can be installed on a supported 64 bit OS.

    #. Psychopy 1.74.03 or higher and all of it's dependencies. See the `PsychoPy installation <http://www.psychopy.org/installation.html>`_ page for details. 

    #. For the NumPy package, please ensure 1.6.2 or greater is installed.

Dependency List Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following Python packages need to be installed on the system you plan to run
ioHub on. Some apckages can be installed using *pip*, while other should be installed 
by downloading the package from the provided URL, unpacking the tarball, and 
installing the package by typing::

    > python setup.py install

in a terminal session where you have cd to the location of the uncompressed 
python package source that contains the setup.py script.

Note that for both 'pip' and manual 'python setup.py install', depending on your
OS X settings and system configuration, you may need to run pip or 
'python setup.py install' with root priveledges.

If your user has admin rights, this can be done by running the command with 'sudo'
at the start of the command and entering your password when prompted. For example::

    > sudo pip install package_name

where package_name is the name of one of the required python packages.

Installing pip if it is not Already on the System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you type:: 

    > pip

in a console and are told the program does not exist, then you can install pip using::

    > sudo apt-get install pip


Packages to install using pip
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. **msgpack**: It’s like JSON. but fast and small. ( pip install msgpack-python )
#. **greenlet**: The greenlet package is a spin-off of Stackless, a version of CPython that supports micro-threads called “tasklets”. ( pip install greenlet )
#. **pytables**: PyTables is a package for managing hierarchical datasets and designed to efficiently and easily cope with extremely large amounts of data. ( pip install tables ). FIRST ENSURE TO INSTALL 'numexpr' from the list below, as it is a dependency of tables) 

Packages To Download
~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. `pyobjc <https://pypi.python.org/packages/source/p/pyobjc/pyobjc-2.5.1.tar.gz#md5=f242cff4a25ce397bb381c21a35db885>`_ : A  Python ObjectiveC binding.    
#. **gevent**: A coroutine-based Python networking library that uses greenlet to provide a high-level synchronous API on top of the libevent event loop::

    pip install cython -e git://github.com/surfly/gevent.git@1.0rc2#egg=gevent

#. `numexpr: <http://code.google.com/p/numexpr/downloads/detail?name=numexpr-2.0.1.tar.gz&can=2&q=>`_ Fast numerical array expression evaluator for Python and NumPy.    
#. `pyYAML: <http://pyyaml.org/download/pyyaml/PyYAML-3.10.tar.gz>`_ PyYAML is a YAML parser and emitter for Python::

    First install the C side package `LibYAML <http://pyyaml.org/wiki/LibYAML>`_, before installing ptYAML.

ioHub Package Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install the ioHub package itself the source should be downloaded from github, 
as currently no python package installer exists. 

To do so:

#. Get a `zip download <https://github.com/isolver/ioHub/zipball/master/>`_ of the `ioHub project source <https://www.github.com/isolver/ioHub/>`_    
#. Open the zip file    
#. Rename the folder in the zip, which is likely called something like 'iohub-master', to just 'ioHub'.    
#. Copy the 'ioHub' folder to a directory in your Python path. sudo access may be needed.    


Running Example Scripts
#########################

Running example scripts using ioHub should now work. All examples are in the *examples* folder of the ioHub distribution. For example

**Demo dir** (relative to the ioHub root folder): ioHub\examples\ioHubAccessDelayTest         

**Run with**: python run.py

or

**Demo dir** (relative to the ioHub root folder):  examples\PsychoPy_Ports\ioMouse

**Run with**: python ioMouse.py

