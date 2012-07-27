"""
ioHub.devices.eyetracker.interface module __init__

Part of the Eye Movement Research Toolkit
Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""

class Enum:
    def __init__(self,enum_list,starting_value=0):
        self._build(enum_list,starting_value)
        self.current=starting_value
        
    @classmethod
    def _build(_class,enum_list,starting_value):
        _class.ENUM_LIST=enum_list
        _class.ENUM_DICT=dict()
 
        _class.BASE_VALUE=starting_value
        
        for i,a in enumerate(enum_list):
            _class.ENUM_DICT[a]=i+_class.BASE_VALUE
            _class.__dict__[a]=i+_class.BASE_VALUE
    
    @classmethod
    def add(_class,item):
        if item not in _class.ENUM_DICT:
            i=len(_class.ENUM_LIST)
            _class.ENUM_DICT[item]=i+_class.BASE_VALUE
        
    def __iter__(self):
        return self
        
    def next(self):
        if self.current< len(self.ENUM_LIST):
            self.current+=1
            return self.current-1
        else:
            self.current=0
            raise StopIteration
            
    def __str__(self):
        return str(self.__class__.ENUM_LIST)

from collections import namedtuple

Point2D = namedtuple('Point2D', 'x y')
Point3D = namedtuple('Point3D', 'x y z')
ColorRGBA= namedtuple('ColorRGBA', 'r g b a')
        
class etReturnCodes(Enum):
        pass
ET_RTN_CODES=etReturnCodes(["ET_OK", "ET_WARNING", "ET_ERROR", "ET_RTN_VALUE", "ET_RESULT_UNKNOWN", "ET_NOT_IMPLEMENTED"])
        
class etEyes(Enum):
        pass
ET_EYE_CODES=etEyes(['LEFT','RIGHT','BINOCULAR','LEFT_RIGHT_AVERAGED','NO_EYE'])        

class etPupilSizeTypes(Enum):
        pass
ET_PUPIL_SIZE_MEASURES=etPupilSizeTypes(['AREA','DIAMETER','WIDTH','HEIGHT','MAJOR_AXIS_LENGTH','MINOR_AXIS_LENGTH'])

class etDataTypes(Enum):
        pass    
ET_DATA_TYPES=etDataTypes(['SAMPLE','FIXATION','FIXATION_START','FIXATION_UPDATE','FIXATION_END','SACCADE','SACCADE_START','SACCADE_END','SMOOTH_PURSUIT','SMOOTH_PURSUIT_START','SMOOTH_PURSUIT_END','BLINK','BLINK_START','BLINK_END','MESSAGE','BUTTON','INPUT'])

class etSoftwareModes(Enum):
        pass  
ET_MODES = etSoftwareModes(["OFFLINE","NO_TRACKER"])

class etInitialUserSetupState(Enum):
        pass  
ET_USER_SETUP_STATES = etInitialUserSetupState(["DEFAULT","CAMERA_SETUP","PARTICIPANT_SETUP","CALIBRATE","VALIDATE", "DRIFT_CORRECT", ,"CUSTOM_MODE_A","CUSTOM_MODE_B","CUSTOM_MODE_C","CUSTOM_MODE_D","CUSTOM_MODE_E","CUSTOM_MODE_F","CUSTOM_MODE_G","CUSTOM_MODE_H"])
    
class etCalibrationTypes(Enum):
        pass  
ET_CALIBRATION_TYPES = etCalibrationTypes(["DC","HV3","HV5","HV9","HV13"])

class etCalibrationModes(Enum):
        pass  
ET_CALIBRATION_MODES = etCalibrationModes(["AUTO","MANUAL"])

class etEyeTrackerDataStreams(Enum):
        pass  
ET_DATA_STREAMS = etEyeTrackerDataStreams(["ALL","FILE","LINK","ANALOG"])

class etOnlineFilterLevel(Enum):
        pass
ET_REALTIME_FILTERS= etOnlineFilterLevel([0,1,2,3,4,5])

from InterfaceClasses import EyeTracker,EyeTrackerEventHandler,EyeTrackerVendorExtension
from eye_events import *

import HW
SUPPORTED_EYE_TRACKER_INTERFACES={"SMI":[HW.SMI.iViewXEyeTracker,"SMI.iVieweyeTracker interface for pyEyeTracker supports the SMI iViewX High Speed 1250 Hz system."],
                                  "LC_TECH":[HW.LC_Technologies.LCTechEyeTracker,"LC Technologies interface for pyEyeTracker, supports the LC Technologies eye trackers in single computer mode only at this time."],
                                  "SR_RESEARCH":[HW.SR_Research.EyeLinkEyeTracker,"SR Research EyeLink interface for pyEyeTracker, supports the EyeLink II and EyeLink 1000 systems."]}
