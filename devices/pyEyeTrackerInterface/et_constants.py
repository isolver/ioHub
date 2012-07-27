"""
et_constants

Part of the pyEyeTracker library 
Copyright (C) 2012 Sol Simpson 
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version). 

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""


from collections import deque,namedtuple
import logging
from et_base_types import *

Point2D = namedtuple('Point2D', 'x y')
Point3D = namedtuple('Point3D', 'x y z')
ColorRGBA= namedtuple('ColorRGBA', 'r g b a')

class EYE_IMAGE_GRAPHICS_COLORS:
    PUPIL_HAIR_COLOR = ColorRGBA(255,255,255,255)
    CR_HAIR_COLOR = ColorRGBA(255,255,255,255)
    PUPIL_BOX_COLOR = ColorRGBA(0,255,0,255)
    SEARCH_LIMIT_BOX_COLOR = ColorRGBA(255,0,0,255)
    MOUSE_CURSOR_COLOR = ColorRGBA(255,255,255,255)
    def __init__(self):
        pass
        
class etReturnCodes(etEnum):
        pass
ET_RTN_CODES=etReturnCodes(["ET_OK", "ET_WARNING", "ET_ERROR", "ET_RTN_VALUE", "ET_RESULT_UNKNOWN", "ET_NOT_IMPLEMENTED"])
        
class etEyes(etEnum):
        pass
ET_EYE_CODES=etEyes(['NO_EYE','LEFT','RIGHT','BINOCULAR','LEFT_RIGHT_AVERAGED'])        

class etPupilSizeTypes(etEnum):
        pass
ET_PUPIL_SIZE_MEASURES=etPupilSizeTypes(['AREA','DIAMETER','WIDTH','HEIGHT','MAJOR_AXIS_LENGTH','MINOR_AXIS_LENGTH'])

class etDataTypes(etEnum):
        pass    
ET_DATA_TYPES=etDataTypes(['SAMPLE','FIXATION','FIXATION_START','FIXATION_UPDATE','FIXATION_END','SACCADE','SACCADE_START','SACCADE_END','BLINK','BLINK_START','BLINK_END','MESSAGE','BUTTON','INPUT'])

class etSoftwareModes(etEnum):
        pass  
ET_MODES = etSoftwareModes(["OFFLINE","NO_TRACKER"])
    
class etCalibrationTypes(etEnum):
        pass  
ET_CALIBRATION_TYPES = etCalibrationTypes(["DC","HV3","HV5","HV9","HV13"])

class etCalibrationModes(etEnum):
        pass  
ET_CALIBRATION_MODES = etCalibrationModes(["AUTO","MANUAL"])

class etEyeTrackerDataStreams(etEnum):
        pass  
ET_DATA_STREAMS = etEyeTrackerDataStreams(["ALL","FILE","LINK","ANALOG"])

class etOnlineFilterLevel(etEnum):
        pass
ET_REALTIME_FILTERS= etOnlineFilterLevel([0,1,2,3,4,5])
