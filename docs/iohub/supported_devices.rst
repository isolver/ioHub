###################################
Operating System and Device Support
###################################
    

Operating System Support
#########################

ioHub is currently available for use on the following Operating Systems:

#. Windows XP SP3, 7, and 8
#. Linux 2.6 +
#. OSX 10.6 or higher 

.. note:: Regardless of the Operating System being used, Python 2.6 or 2.7 
    **32-bit** is required. Even if a 64 bit OS is being used, install the 32 bit 
    version of Python and any package dependencies.

Current Device Support
#######################
    
The list of available ioHub device types is OS dependent. This is mainly
because of lack of time to port all devices to the different operating systems, 
not because the devices can 'not' be supported. One exception to this is the 
common eye tracking device interface, where OS support for a particular eye tracking
device will always be limited to only the OS's that the underlying eye tracker
hardware interface / API supports itself. 

The current state (April, 2013) of device support for each OS is as follows:

===================== ============= =========== =============== 
Device Type           Windows       Linux       Mac OS X
===================== ============= =========== =============== 
Keyboard              Yes           Yes         Yes
Mouse                 Yes           Yes         yes
Eye Tracker           Yes           H/W Dep.    H/W Dep.
GamePad               Yes (XInput)  No          No
Analog                Yes           No          No
===================== ============= =========== =============== 

Devices *in the works*
#######################

The following devices are on the roadmap for addition to the ioHub by the
end of 2013. Many of the listed devices already have partial 
implementations started. The order of the device listing 
does not imply the priority of the device support implementation.

===================== ============= =========== =============== 
Future Device Type    Windows       Linux       Mac OS X
===================== ============= =========== =============== 
Parrallel Port        Yes           Yes         No
Serial Interface      Yes           Yes         Yes
MBED Microcontroller  Yes           Yes         Yes
Teensy 3 Microcontr.  Yes           Yes         Yes
HID Joystick Support  Yes           Yes         Yes
Cedrus RB BBox's      Yes           Yes         Yes
===================== ============= =========== =============== 
 
If there is a device you think would be useful to add support for in the ioHub,
please let us know as it will help with development prioritization, 
and please consider helping with the implementation by contributing some time to the
project.


