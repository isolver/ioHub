"""
ioHub
.. file: ioHub/ioDataStore/log.py

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

from tables import *
import ioHub

class ExperimentLog(IsDescription):
    experiment_id = UInt32Col() # Unique site experiment ID
    session_id = UInt32Col()    # Unique Experiment level session ID
    sec_time = Float64Col()     # Sec time since timer init as start of experiment
    level = UInt8Col()          # log level
    caller = StringCol(32)      # name for method / function that log was called from
    text = StringCol(128)       # log line text

class BaseLogLevels(object):
    __slots__ = ('DATA','CODE','INFO','DEBUG','WARNING','EXCEPTION','ERROR')

    def __init__(self):
        for i,a in enumerate(BaseLogLevels.__slots__):
            setattr(self,a,i)



