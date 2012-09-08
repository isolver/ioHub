"""
ioHub
.. file: ioHub/ioDataStore/stats.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

import numpy as N
import util as dsUtil

class StatsStruct(object):
    def __init__(self,label,x=None,y=None):
        self.label=label
        if x is not None:
            self.x=x
        if y is not None:
            self.y=y

def calculateStatsOnArray(a):
    stats = StatsStruct('Sample Delays')
    stats.ncount=len(a)
    stats.min=N.amin(a)
    stats.range=N.ptp(a)
    stats.max=stats.min+stats.range
    stats.mean=N.mean(a,dtype=N.float64)
    stats.median=N.median(a)
    stats.std=N.std(a)
    stats.var=N.var(a)
    return stats

def calculateStatsOnColumn(hfile,table,columnName):
    if isinstance(table,'str') or isinstance(table,'unicode'):
        table=dsUtil.getTableFromHubFile(hfile,table)
    a=table.col(columnName)    
    stats = StatsStruct(columnName)
    stats.ncount=len(a)
    stats.min=N.amin(a)
    stats.range=N.ptp(a)
    stats.max=stats.min+stats.range
    stats.mean=N.mean(a,dtype=N.float64)
    stats.median=N.median(a)
    stats.std=N.std(a)
    stats.var=N.var(a)
    return stats
