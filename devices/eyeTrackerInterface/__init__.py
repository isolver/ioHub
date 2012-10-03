"""
ioHub
pyEyeTracker Interface
.. file: ioHub/devices/eyeTrackerInterface/__init__.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

import cStringIO

class Enum(object):
    __slots__=[]
    def __init__(self):
        for i,n in enumerate(self.__class__.__slots__):
            setattr(self,n,2**i)

    def __str__(self):
        output = cStringIO.StringIO()
        output.write("%s Enum:\n"%self.__class__.__name__)
        
        for n in self.__class__.__slots__:
            v=getattr(self,n)
            output.write("%s : %s\n",n,str(v))
            
        r=output.getvalue()
        output.close()
        return r
    
    def __repr__(self):
        output = cStringIO.StringIO()
        output.write("<%s("%self.__class__.__name__)
        
        for n in self.__class__.__slots__:
            v=getattr(self,n)
            output.write("%s:%s, "%(n,str(v)))
        output.write('\n')
  
        r=output.getvalue()
        output.close()
        return r  
        
class ReturnCodes(Enum):
    __slots__=["ET_OK", "ET_RESULT_UNKNOWN", "ET_NOT_IMPLEMENTED"]
    def __init__(self):
        Enum.__init__(self)        
RTN_CODES=ReturnCodes()

class DataTypes(Enum):
    __slots__=['MONO_SAMPLE','BINOC_SAMPLE','FIXATION_START','FIXATION_UPDATE','FIXATION_END','SACCADE_START','SACCADE_END','BLINK_START','BLINK_END','PURSUIT_START', 'PURSUIT_END','MESSAGE','BUTTON','TTL_INPUT']
    def __init__(self):
        Enum.__init__(self)
DATA_TYPES=DataTypes()

class SoftwareModes(Enum):
    __slots__=["NO_TRACKER","IDLE","SYSTEM_SETUP","RECORDING","FILE_TRANSFER"]
    def __init__(self):
        Enum.__init__(self)
ET_MODES = SoftwareModes()

class InitialUserSetupState(Enum):
    __slots__=["DEFAULT","CAMERA_SETUP","PARTICIPANT_SETUP","CALIBRATE","VALIDATE", "DRIFT_CORRECT", "CUSTOM_MODE_A","CUSTOM_MODE_B","CUSTOM_MODE_C","CUSTOM_MODE_D","CUSTOM_MODE_E","CUSTOM_MODE_F"]
    def __init__(self):
        Enum.__init__(self)
USER_SETUP_STATES = InitialUserSetupState()
    
class CalibrationTypes(Enum):
    __slots__=["DC","H3","HV3","HV5","HV9","HV13"]
    def __init__(self):
        Enum.__init__(self)
CALIBRATION_TYPES = CalibrationTypes()

class CalibrationModes(Enum):
    __slots__=["AUTO","MANUAL"]
    def __init__(self):
        Enum.__init__(self)
CALIBRATION_MODES = CalibrationModes()

class EyeTrackerDataStreams(Enum):
    __slots__=["ALL","FILE","NET","SERIAL","ANALOG"]
    def __init__(self):
        Enum.__init__(self)
DATA_STREAMS = EyeTrackerDataStreams()

class FilterLevel(Enum):
    __slots__=['OFF','LEVEL_1','LEVEL_2','LEVEL_3','LEVEL_4','LEVEL_5']
    def __init__(self):
        Enum.__init__(self)
DATA_FILTER = FilterLevel()

import eye_events
import InterfaceClasses
from InterfaceClasses import EyeTrackerInterface
import HW
