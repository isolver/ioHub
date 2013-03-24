###############
ioHub Overview
###############

Relationship to Experiment Design and Runtime Packages
#######################################################

The **ioHub** is a `Python <http://www.python.org/>`_ framework that runs in parallel 
to the most excellent `PsychoPy <http://www.psychopy.org/>`_ during experiment run-time
and data collection. While ioHub can be used with other experiment runtime packages or
windowing / graphics rendering packages, the use of PsychoPy is highly encouraged
and is what 95% of the ioHub development, testing, and examples has been based on.

The **ioHub** effectively acts as a proxy between the experiment script that is 
responsible for defining the paradigm logic and stimuli presentation and several input
devices that are often used for collecting participant reponses (manual, oculomotor, etc).

High Level Software Design
###########################
 
Implementation wise, **ioHub** has been designed to run in a seperate process than the
Experiment Run-time Process (i.e PsychoPy), meaning that while PsychoPy is focusing on 
presenting stimuli and controlling the experiment logic, the **ioHub** is **in parallel**
focusing on monitoring the devices being used for the experiment, quickly time 
stamping events that have no native time stamp (regardless of what the PsychoPy
script is doing at that time). ioHub can be used to access device events via a
consistant API from the PsychoPy process script, as well as saving all device
events to the ioDataStore, which is based on pytables and uses a HDF5 file format.

Both the Experiment Process and ioHub Process go about there business largely 
unaffected by each other since they are actually running in completely separate 
Python interpreters, ideally on completely separate processing units of your PC, that are
*really* operating in *parallel*. This is assuming you are running your experiment
on a multicore or multi-cpu computer (not just hyperthreaded),
and that the Experiment Process and ioHub Process are running on separate cores.
Often it seems the OS runs each process on a separate core by default, by you
can enforce this by setting each process to only be allowed to run on a different
processor (set) than the other.

Benifits of Usage
##################

When ioHub and PsychoPy modules are used together within an experiment script,
the devloper gains the following benifits:

1. A design goal of ioHub is to provide a constent device representation for 
   each device type, regardless of the underlying hardware or device model being used.
   This is done already by the operating system for common input devices such 
   keyboards and mice for example; i.e. the experiment developer does not need
   to use a different API to access keyboard events from a keyboard made
   by vendor A or vendor B. Similarly, ioHub provides standard device APIs for 
   less common devices such as eye trackers and analog to digital input devices.

2. Device events are all accessed via a simple and consistent event interface 
   during experiment runtime. Events can be accessed sequentially for all devices
   that are being monitored, or for a specific device and device event type only.

3. All events processed by the ioHub are also saved in an experiment event file, 
   using the pytables package and saved in the hdf5 file format. Events can be 
   retrieved for post hoc analysis very quickly, even with very large data sets,
   in the form of 2D numpy arrays, or tables. The retieved events can therefore
   be easily and directly used in most common python scientific packages like
   scipy and matplotlib. This event audit log, while optional, has no inpact on 
   the processing capabilities in the Experiment Process script, 
   and is therefore recommended. 

4. Experiment Process events, in the form of arbitrary string messages, can be 
   sent to the ioHub, time stamped with the same precision as the underlying 
   ioHub clock and saved in the experiment event file, allowing the ioHub event
   file to aften be used as 'the' results file for an experiment.
   This can reduce the complexity and amount of processing required by the 
   Experiment Process greatly.

5. A special form of an experiment messaging, called an Experiment Variable Condition Set,
   can be defined by the experiment script to represent the Independent and 
   Dependent variables of interest for each 'trial' of the experiment. The state
   of all variables defined in the Condition Set can be sent to the ioHub and 
   saved with all event information. This allows for selective retrieval of 
   event data that occurred during specific experiment conditions or dependent 
   variable result states.  
   
6. ioHub runs in a seperate process from the Experiment Process (PsychoPy script),
   allowing devices to be polled (when required) at a high frequency regardless
   of what the Experiment Process script is doing, and even when the Experiment
   Process script is blocked waiting for an operation to complete. This provides
   more accurate event time stamping, particulary for device inputs that must be
   time stamped by the receiving API, such as serial and TTL data.

7. ioHub uses a multiprocessing model, therefore distributing the experiment CPU
   load accross two processing units in a multicore / multi cpu based computer. 
   This alows for much more 'work' to be done than in the standard single process
   experiment package design.

8. ioHub has no dependence on the device event capabilities or representation 
   of the Experiment Process, or underlying visual stimulus package used by the 
   Experiment Process, exists. Therefore ioHub can be used in in place of or in 
   parallel to the Experiment Processes existing device input API(s). Furthermore,
   ioHub can be used with different python experiment packages or Windowing / 
   Graphics packages. For example, while it is prefered to use PsychoPy as the 
   Experiment Process runtime package, a user could also use pygame or pyglet 
   directly, or pyOpenGL if so desired. In fact, ioHub can be used as the event
   system in python programs that do not even create a graphics Window if so desired,
   and can capture device events as a user interacts with the standard 
   OS desktop or other applications running on the OS.    

Operating System Support
#########################

ioHub is currently available for use on Windows and Linux Operating systems, with
OS X supported planned for a future release. 

The list of available ioHub device types is OS dependent. This is mainly
because of lack of time to port all devices to the different operating systems, 
not because the devices can 'not' be supported. One exception to this is the 
common eye tracking device interface, where OS support for a particular eye tracking
device will always be limited to only the OS's that the underlying eye tracker
hardware interface / API supports itself. 

Device Support
###############

The current state (March, 2013) of device support for each OS is as follows:

===================== ============= =========== =============== 
Device Type           Windows       Linux       Mac OS X
===================== ============= =========== =============== 
Keyboard              Yes           Yes         No
Mouse                 Yes           Yes         No
Eye Tracker           Yes           H/W Dep.    No
GamePad               Yes (XInput)  No          No
Analog                Yes           No          No
===================== ============= =========== =============== 


More devices will be tested and ported on Linux and OS X as time permits. If 
you want a device supported on a particular OS, or want a new device type or
device hardware supported in ioHub, please let us know as it will help prioritizing,
and please consider helping with the implementation by contributing some time to the
project.


