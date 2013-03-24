##############################
ioHub Known Issues
##############################

Section TBC.

**Some point form notes for now**:

PsychoPy Integration Considerations
====================================

These items are things I am not happy with in terms of the current state of psychopy integration.
Better can be done. 
#. Poor, perhaps inproper, psychopy Monitor and ioHub Display integration.
#. Using PsychoPy Timers with the ioHub ( don't ).

ioHub Functionality Issues
============================
 
#. Support for only pixel display coordinates type. *Angle* and *Normalized* types need to be added at minimum.
#. ioHub currently only supports visual angle calculation where it is assumed that all points on the monitor are the same distance from the eye. THis is not strictly true and Josh Borah has provided input on calculating visual angles using several of the common ways; each of which makes different assumptions and has a different degree of accuracy (mathematically at least). ioHub should allow the experiment designer to choose which visual angle algorithm will be used.
#. Limited API for accessing data from the ioDataStore hdf5 file in a user friendly way.
#. Error handling within the ioHub Server could be greatly improved in terms of providing a consistant, reliable way for exceptions raised on the ioHub Server to be reported to the Experiment Process, and thus to the experiment designer.
#. See the project `issue tracker <https://github.com/isolver/ioHub/issues?state=open>`_ as well.

Missing Functionality
=======================

#. ioHub should have an eye tracking module that makes it very easy to associate eye data with PsychoPy visual stim, support the creation of *Interest Areas* in the Distplay's coordinate space and event generation based on eye behavior and the Interest Area characteristics, etc.
#. Built in support for device event *Filters*, which can both create new ioHub event types based on the input from other device events, to be able to create new event type streams; as well as modify the values of existing device event attributes to perform filtering , etc. The architecture should support runtime event processing as well as feeding an event stream in from a saved ioDataStore file.