"""
ioHub
pyEyeTracker Interface
.. file: ioHub/devices/eyeTrackerInterface/checkConsistancy.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

import ioHub
import ioHub.devices.eyeTrackerInterface.InterfaceClasses
from ioHub.devices.eyeTrackerInterface.InterfaceClasses import EyeTrackerInterface

# Idea here is to have a function that checks each implementation of the EyeTrackerInterface for
# consistency relative to the spec.
# Here, the 'spec' is the EyeTrackerInterface Class, and the 'implementations' are the sub classes
# of EyeTrackerInterface.
#
# Things that can be checked for consistency:
#    - the class name follows the HW.[company_name].[tracker_model_or_family].EyeTracker
#    - that the implementation has no public methods that are in in the Interface.
#    - for each method that is implemented, check that the parameters matches the Interface.
#    - that no public attributes exist in the Implementation that are not in the Interface
#    - are there some methods that 'must' be defined in the Implementation????
#           - maybe ones like connection related, recording related, that either the _poll is used or the
#              _event_callback is used., others??
#
# Result should be a report (to stdout or file?) for each Implementation that notes:
#   - Implementation class Name
#   - Comments at top of file.
#   - if any non standard public methods or attributes have been defined, and what they are, on what line numbers too?
#   - if any standard methods do not have the same parameter set as in the Interface, what they are, line numbers
#   - if any standard methods == the Interface base (by comparing code lines??). if so, should they be removed or
#     has implementer forgotten to override base method? Q for developer of interface.

import inspect

def checkImplementation(implementation):
    print implementation

def printSpec(aclass):
    print aclass
    print ''
    print 'Methods:'
    cdir=dir(aclass)

    for a in cdir:
        if callable(a):
            print '\t',a

if __name__ == '__main__':

    from ioHub.util import describeModule


    describeModule.describe(ioHub.devices.eyeTrackerInterface.InterfaceClasses)

    print '\n\n'

    eyeTrackerImplementations=EyeTrackerInterface.__subclasses__()

    for implementation in eyeTrackerImplementations:
            checkImplementation(implementation)



