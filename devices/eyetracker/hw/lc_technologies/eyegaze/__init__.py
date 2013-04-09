# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 06:49:45 2013

@author: isolver
"""

from ioHub import addDirectoryToPythonPath

addDirectoryToPythonPath('devices/eyetracker/hw/lc_technologies/eyegaze','bin')


from eyetracker import (EyeTracker, MonocularEyeSampleEvent, BinocularEyeSampleEvent,
                        FixationStartEvent,FixationEndEvent,SaccadeStartEvent,
                        SaccadeEndEvent,BlinkStartEvent,BlinkEndEvent)