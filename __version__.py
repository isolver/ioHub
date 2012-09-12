"""
ioHub Python Module
.. file: ioHub/__version__.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""
from verlib import suggest_normalized_version, NormalizedVersion
import warnings
def validate_version(version):
    rversion = suggest_normalized_version(version)
    if rversion is None:
        raise ValueError('Cannot work with "%s"' % version)
    if rversion != version:
        warnings.warn('"%s" is not a normalized version.\n'
                        'It has been transformed into "%s" '
                        'for interoperability.' % (version, rversion))
    return NormalizedVersion(rversion)

iohub_version=validate_version("0.1a5")
print 'Current ioHub Version:',iohub_version