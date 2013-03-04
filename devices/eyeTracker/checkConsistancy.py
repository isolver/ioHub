"""
ioHub
pyEyeTracker Interface
.. file: ioHub/devices/eyeTracker/checkConsistancy.py

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

import ioHub
import ioHub.devices.eyeTracker.InterfaceClasses
from ioHub.devices.eyeTracker.InterfaceClasses import EyeTrackerDevice

# Idea here is to have a function that checks each implementation of the EyeTrackerDevice for
# consistency relative to the spec.
# Here, the 'spec' is the EyeTrackerDevice Class, and the 'implementations' are the sub classes
# of EyeTrackerDevice.
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
import collections

if __name__ == '__main__':

    from ioHub.util import describeModule


    attributes,methods,builtins,klasses=describeModule.describe(ioHub.devices.eyeTracker.InterfaceClasses.EyeTrackerDevice,True)

    interfaceAttributes= collections.Counter(attributes.keys())
    interfaceMethods= collections.Counter(methods.keys())
    interfaceBuiltins= collections.Counter(builtins.keys())
    interfaceClasses= collections.Counter(klasses.keys())

    print '\n\n'

    eyeTrackerImplementations=EyeTrackerDevice.__subclasses__()

    for implementation in eyeTrackerImplementations:
        attributes2,methods2,builtins2,klasses2=describeModule.describe(implementation,False)

        a = collections.Counter(attributes2.keys())
        m= collections.Counter(methods2.keys())
        b= collections.Counter(builtins2.keys())
        k= collections.Counter(klasses2.keys())

        onlyInImplementationA=a-interfaceAttributes
        onlyInImplementationM=m-interfaceMethods
        onlyInImplementationB=b-interfaceBuiltins
        onlyInImplementationK=k-interfaceClasses

        missingInImplementationA=interfaceAttributes-a
        missingInImplementationM=interfaceMethods-m
        missingInImplementationB=interfaceBuiltins-b
        missingInImplementationK=interfaceClasses-k

        print "Implementation ",implementation ," contains the following differences from the Interface:"
        print
        print ' + ',list(onlyInImplementationA)
        print ' + ',list(onlyInImplementationM)
        print ' + ',list(onlyInImplementationB)
        print ' + ',list(onlyInImplementationK)
        print
        print ' - ',list(missingInImplementationA)
        print ' - ',list(missingInImplementationM)
        print ' - ',list(missingInImplementationB)
        print ' - ',list(missingInImplementationK)

        print "========================================================================================="
        #c = a - b
        #print list(c.elements())
