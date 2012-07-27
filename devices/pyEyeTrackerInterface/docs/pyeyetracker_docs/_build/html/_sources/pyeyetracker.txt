pyeyetracker Package
====================

The pyEyeTracker package is brocken into several
modules that try to group related items together.
Overall, the EyeTracker class is the main class ghe 
you will work with. As an end user, you will take the
class that extendes pyEyeTracker that supports the eye 
tracker you wish to use and create one instance of it.

:mod:`eyetracker` Module
------------------------

.. automodule:: pyeyetracker.eyetracker
    :members:
    :undoc-members:
    :show-inheritance:

The et_grapphics module contains the callback stubs sused by an ete tracker 
that supports calibration within an exoerment and can be used to creating the
graphics to display during calibration in what ever graphics env. upi use.      

:mod:`et_graphics` Module
-------------------------

.. automodule:: pyeyetracker.et_graphics
    :members:
    :undoc-members:
    :show-inheritance:

The et_events module conntains the enumerations and other constants 
used in PyEyeTracker. 

:mod:`et_events` Module
-----------------------

.. automodule:: pyeyetracker.et_events
    :members:
    :undoc-members:
    :show-inheritance:

The even_handlers module holds the EyeTrackerEventHandler and UserEvent Handlers that are
responsible for converting eye tracking data into the expeiment time base amoung other things.
   
:mod:`et_event_handlers` Module
-------------------------------

.. automodule:: pyeyetracker.et_event_handlers
    :members:
    :undoc-members:
    :show-inheritance:

base_types module si another utility module holding some many of the fundatental
ojects that are used throught the experujmenr  script.
     
:mod:`et_base_types` Module
---------------------------

.. automodule:: pyeyetracker.et_base_types
    :members:
    :undoc-members:
    :show-inheritance:
    
:mod:`et_constants` Module
--------------------------

.. automodule:: pyeyetracker.et_constants
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`et_vendor_extension` Module
---------------------------------

.. automodule:: pyeyetracker.et_vendor_extension
    :members:
    :undoc-members:
    :show-inheritance:

    
Subpackages
-----------

.. toctree::

    pyeyetracker.HW

