================================
ioHub Event Monitoring Framwork
================================

ioHub is a Python package providing a cross-platform computer device event monitoring and
storage framework. ioHub is not a complete experiment design and runtime API,
but is instead intended to be used with existing Python experiment runtime packages,
primarily `the most excellent PsychoPy <http://www.psychopy.org>`_ . 

High Level Features
=====================

ioHub includes the following high level functionality:

#.  Monitoring of input events from experiment input devices such as the keyboard,
    mouse, analog to digital converters, XInput compatible gamepads, and eye trackers
    via a common eye tracking interface that provides the same user level API 
    regardless of the eye tracking hardware used.
#.  Device event monitoring is done completely independently from the experiment runtime
    graphics environment and allows for device inputs to be captured system wide, not just for
    events targeted to the stimulus presentation window. In fact, no graphical window 
    in needed at all to collect inputs from the majority of supported devices.
#.  Device input monitoring is run as a seperate process from the experiment runtime
    itself, called the ioHub Server Process. This allows for input event monitoring and 
    device event callback processing to occur very quickly and regardless of what state
    the experiment runtime process is in (i.e. even when the experiment runtime process
    is blocked and would not be able to monitor for new events itself).
#.  Device inputs can be saved by the ioHub Server Process for post hoc analysis. 
    Assuming a multicore CPU is being used, in general *all* device events can be saved during
    the experiment without effecting the performance of the experiment runtime logic
    itself.
#.  Events can be accessed by the experiment script during runtime either at a global,
    device independent manner, or for a specific device type alone. 
#.  Text Messages can be registered with ioHub Server, allowing easy integration of experiment
    runtime events (such as important stimuli onsets, etc.)
#.  A common time base is provided for all device input events, and between the 
    experiment runtime and ioHub Server processes, making it easy to syncronize experiment and
    device input events. Events are time stamped when it is not done by the source 
    device itself, or existing device event time stamps are converted to the common 
    ioHub time base. 
#.  Device inputs are converted into common event types based on device type, 
    regardless of the underlying supported hardware. 

Project Website and User Groups
================================

ioHub source is hosted on GitHub `here <https://www.github.com/isolver/iohub/>`_.

A `user forum / mailing list <https://groups.google.com/forum/?hl=en&fromgroups#!forum/iohub-users>`_ 
and `developer forum / mailing list <https://groups.google.com/forum/?hl=en&fromgroups#!forum/iohub-dev>`_
are available on Google Groups for support questions and development discussion topics respectively.

Contents
============

.. toctree::
   :maxdepth: 2
   
   Installation <iohub/installation>
   Supported OS and Device Overview <iohub/overview>
   Quick Start <iohub/quickstart>
   API Specification <iohub/api/api_home>
   API Index <iohub/api/indices>
   Performance Considerations<iohub/performance>
   Known Issues <iohub/known_issues>
   Change Log <iohub/change_log>
   Credits <iohub/credits>
   License <iohub/iohub_license>
