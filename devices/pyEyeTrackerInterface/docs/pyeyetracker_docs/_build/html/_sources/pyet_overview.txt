.. pyEyeTracker Overview

*********
Overview
*********

.. _design-goals:

Design Goals
============

pyEyeTracker is a new, in progress, python module that provides an 
eye tracking interface and specification with the following high level goals:

* Simple python interface that addresses common eye tracker functionality used in many research and HCI applications. 
* Designed for use with multiple eye tracking models; several eye tracking manufacturers have already provided the information and / or resources necessary to implement the interface for some of their eye tracker models,and more are on the way.
* Single set of funtion / method calls used for the core interface, regardless of eye tracker model.  
* Built-in support for use with the mature and popular `PsychoPy Psychology software <http://http://www.psychopy.org/>`_ ; coder support is provided to start, with the plan to add designer support in the future.
* pyEyeTracker inncludes built in pussport for PsychoPy, although support for any python environrmnt that can generate your stimuli and non eye tracker events should be possible; but why would you when there is Psychopy? 
* Cross platform support for Windows &, Mac OS X, and Linux (assuming support exists for each OS by the particular eye tracker implementation)
* Recognition that not all eye tracking system will be able to support the core set of pyEyeTracker features, so inclusion of a common method for providing 'function not supported' feadback to the user of the interface is provided.
* Common Extension mechanism allowing functionaily that is not part of the pyEyeTracker core functionality set, but is critical to a particular eye tracker model, to be accessed. 
* Community and industry based support and input on the improvement and evolution of the pyEyeTracker project
* Planned to be an Open Source based project with GPL version 3 license ASAP.
* Lead by the COGAIN committee on eye tracker data quality standardization, and administered by Sol Simpson / iSolver Software Solutions.

In general, the pyEyeTracker module design should be as flexible and powerful
as possible, while also being non-overwhelmming and as simple as possible, 
reflecting the common standard functionaily found in many of the eye tracking 
systems used for computer based experimental and usability testing, or HCI applications. 
These requirements are competing, so the pyEyeTracker design needs to balance the
two appropriately.

.. _areas-of-functionality:

Areas of Functionality Supported
================================

The pyEyeTracker interface is intended to provide a common interface to the following high levels of eye tracker functionality:

#. Connection and Initalization 

#. Setting Eye Tracker Settings and Variable States

#. Presenting Eye Tracker Driven Graphics for Calibration, Validation, or Drift Correction Type Processes

#. Creating and Closing of Eye Tracker Data Files

#. Starting and Stopping of Eye Data Recording

#. Sending Syncronization Messages to the Eye Tracker

#. Receiving Data from the Eye Tracker ( Eye Samples and Eye Events, Perhaps Other ) During the Recording Session

#. Providing an Accurate Experiment PC Time Stamp for any Data Received From the Eye Tracker ( defined as accurate to within 1 msec )

#. Providing a Single Event Queue for Experiment PC Events and Eye Tracker Based Events of Interest, Streamed Chronologically.

#. Transfering an Eye Tracker File from a Remote Eye Tracker to the Experiment PC.

#. Closing and Uninitializing the Eye Tracker.

#. Providing a Common Extension Base Class for use when Functionality Not supported in pyEyeTracker Needs to be Added.

#. Providing Documented, Common Default Behaviour for Any Base pyEyeTracker Functionality that a Specific Implementation can NOT Support.

.. _project-status:

Project Status
==============    


May 11th, 2012
++++++++++++++

* The initial design specification is basically complete for pyEyeTracker.
* The design spec will be sent out for review and input to relevent parties.
* A meeting will (hopefully) be held sometime the week of May 13 to review the specification.
* Once there is general agreement on the phase 1 specification, implementation of the interface to some eye trackers wil begin.
* Intial eye trackers to integrate will likely be: SMI high Speed 1250, LC Technologies (model not known by Sol at time of writting), SR Research EyeLink 1000, ASL series 6000, and others.
* Inital experiment requirements are being refined in parrallel to pyEyeTracker design speficiation
* Sol has been learning PychoPy API while working on pyEyeTracker spec, by no means a master of it yet. ;)
* We are meeting in Lund on May 19th to work on the eye tracker integration and experiment program.
* Denis Engemann has been brought into the discussion by Michael MacAskill (see below). Denis is a very talented software developer and seems possibly interested in looking at the project. Hopefully we find mutual goals and he ends up being onboad with helping out on implementation moving forward.
* My (Sol's) hope is that the pyEyeTracker spec is stable enough, that we have enough example eye tracker interfaces done, and some sample experiments, etc. by end of June so that we can release the pyEyeTracker publicly and start the process of treating it as an open source community driven project from that point on.
* Obviously, momentum will need to build up before there is any significant input and help from others in the eye tracking comunity, but the sooner we start, the sooner this will hopefully happen.
 
In terms of eye tracker integration status:

* Many eye tracking companies have been very helpful and supportive of this effort. This is really nice to see.
* No eye trackers have actually been implemented in the interface yet, until this is done, it means the pyEyeTracker spec is just that, a spec as far as I am conserned. ;)
* We have the information needed to integrate SMI system quite easly (hopefully) thanks to an existing python implementation done by Michael R. MacAskill and Dr Daniel Myall, both of the New Zealand Brain Research Institute. It uses the SMI UDP ascii protocol so is cross platform from the get go. This is a major win. We owe them a big big beer.
* SR Research integration is not an issue given pyLink already exists, the question is what priority does this have. Although pyLink relies on the SR Research core libraries, they are available for Windows, OS X and Linux, and therefore so is pyLink.
* LC Technologies we have provided the documentation and you have their developers kit. I have not looked at it in detail yet but from discussion it sounds like we will be able to do do what we need to, however it will be via calls to external libraries / DLLs, like with SR Research. I am not sure what OSs are supported.
* ASL iontergation is not so clear right now; from emails with Josh, we should be able to start / stop recording, send sync messages, and receive data at runtime. However we will not be able to do integrated calibtartion, so an extrenal program will we run for the calibration prior to running the experiment. I is not clear what the interface is, but my sense is that it is a  C library, perhaps windows only.
* Cambridge Research Systems (CRS) has shown great interest in integrating their new system with the pyEyeTracker interface. I have had lengthy discusions with them about their new system and it should not be a problem. It uses a USB HID interface. 
* Others, like Tobii, are unclear to me at this point.
  

General Thoughts Moving Forward
+++++++++++++++++++++++++++++++

There are a large number of eye trackers available 
today, each with their own strengths and unique aspects of functionality. 
Therefore it should be expected that during the initial phase of develoment, 
particualrly prior to version 1.0 being released. The module's API will likely 
change as input is received and modifications are made to improve overall design as more detailed 
insight is learned about each eye tracking systems programming interface.
Is is very likely that some of these changes will not be backwards compatible with the 
current API spec, so before upgrading to a newer version of the module, be sure to check the
pyEyeTracker change log to review any incompatible changes that have been made and how your
experiment may need to be modified to reflect the changes. 

