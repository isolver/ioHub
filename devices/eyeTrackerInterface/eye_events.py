"""
ioHub
pyEyeTracker Interface
.. file: ioHub/devices/eyeTrackerInterface/eye_events.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

from .. import DeviceEvent, EventConstants
import numpy as N

"""
Eye Tracker Event Types. The Common Eye Tracker Interface supports monocular and binocular eye samples
and four eye event types; note that not all eye trackers support all these event types.  

* Saccades: StartSaccadeEvent, EndSaccadeEvent
* Fixations: StartFixationEvent, FixationUpdateEvent, EndFixationEvent
* Blinks: StartBlinkEvent, EndBlinkEvent
* SmoothPursuit: StartPursuitEvent, EndPursuitEvent

"""
##################### Eye Tracker Sample Stream Types ################################
# 
class MonocularEyeSample(DeviceEvent):
    newDataTypes = [('eye', 'u1'), ('gaze_x','f4'),('gaze_y','f4'),('gaze_z','f4'), 
        ('eye_cam_x','f4'),('eye_cam_y','f4'), ('eye_cam_z','f4'), 
        ('angle_x','f4'),('angle_y','f4'),('raw_x','f4'),('raw_y','f4'),
        ('pupil_measure1','f4'),('pupil_measure2','f4'),('ppd_x','f4'),('ppd_y','f4'),
        ('velocity_x','f4'),('velocity_y','f4'),('velocity_xy','f4'),('status', 'u1')]
    baseDataType=DeviceEvent.dataType
    dataType=baseDataType+newDataTypes
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in newDataTypes]

    EVENT_TYPE_STRING='EYE_SAMPLE'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING

    def __init__(self, *args, **kwargs):
        """

        :rtype : MonocularEyeSample
        :param args:
        :param kwargs:
        """
        DeviceEvent.__init__(self, *args, **kwargs)
        
class BinocularEyeSample(DeviceEvent):
    newDataTypes = [('left_gaze_x','f4'),('left_gaze_y','f4'),('left_gaze_z','f4'), 
        ('left_eye_cam_x','f4'),('left_eye_cam_y','f4'), ('left_eye_cam_z','f4'), 
        ('left_angle_x','f4'),('left_angle_y','f4'),('left_raw_x','f4'),('left_raw_y','f4'),
        ('left_pupil_measure1','f4'),('left_pupil_measure2','f4'),('left_ppd_x','f4'),('left_ppd_y','f4'),
        ('left_velocity_x','f4'),('left_velocity_y','f4'),('left_velocity_xy','f4'),
        ('right_gaze_x','f4'),('right_gaze_y','f4'),('right_gaze_z','f4'), 
        ('right_eye_cam_x','f4'),('right_eye_cam_y','f4'), ('right_eye_cam_z','f4'), 
        ('right_angle_x','f4'),('right_angle_y','f4'),('right_raw_x','f4'),('right_raw_y','f4'),
        ('right_pupil_measure1','f4'),('right_pupil_measure2','f4'),('right_ppd_x','f4'),('right_ppd_y','f4'),
        ('right_velocity_x','f4'),('right_velocity_y','f4'),('right_velocity_xy','f4'),('status', 'u1')]
    baseDataType=DeviceEvent.dataType
    dataType=baseDataType+newDataTypes
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in newDataTypes]

    EVENT_TYPE_STRING='BINOC_EYE_SAMPLE'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING

    def __init__(self,*args,**kwargs):
        """

        :rtype : BinocularEyeSample
        :param args:
        :param kwargs:
        """
        DeviceEvent.__init__(self,*args,**kwargs)

#
################### Fixation Event Types ##########################
# 
class FixationStartEvent(DeviceEvent):
    # 26 fields
    newDataTypes = [('eye', 'u1'), ('gaze_x','f4'),('gaze_y','f4'),('gaze_z','f4'),
        ('angle_x','f4'),('angle_y','f4'),('raw_x','f4'),('raw_y','f4'),
        ('pupil_measure1','f4'),('pupil_measure2','f4'),('ppd_x','f4'),('ppd_y','f4'),
        ('velocity_x','f4'),('velocity_y','f4'),('velocity_xy','f4'),('status','u1')]
    baseDataType=DeviceEvent.dataType
    dataType=baseDataType+newDataTypes
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in newDataTypes]

    EVENT_TYPE_STRING='FIXATION_START'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING

    def __init__(self, *args, **kwargs):
        """

        :rtype : FixationStartEvent
        :param args:
        :param kwargs:
        """
        DeviceEvent.__init__(self, *args, **kwargs)
'''
class FixatonUpdateEvent(FixationStartEvent):
    dataType = FixationStartEvent.dataType+[('peak_velocity_x','f4'),('peak_velocity_y','f4'),('peak_velocity_xy','f4')]
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames    
    def __init__(self,*args,**kwargs):
        FixationStartEvent.__init__(self,*args,**kwargs)
'''
       
class FixationEndEvent(DeviceEvent):
    # 58 fields
    newDataTypes = [('eye', 'u1'), ('duration','u4'),
        ('start_gaze_x','f4'),('start_gaze_y','f4'),('start_gaze_z','f4'),
        ('start_angle_x','f4'),('start_angle_y','f4'),('start_raw_x','f4'),('start_raw_y','f4'),
        ('start_pupil_measure1','f4'),('start_pupil_measure2','f4'), ('start_ppd_x','f4'),('start_ppd_y','f4'),
        ('start_velocity_x','f4'),('start_velocity_y','f4'),('start_velocity_xy','f4'),
        ('end_gaze_x','f4'),('end_gaze_y','f4'),('end_gaze_z','f4'),
        ('end_angle_x','f4'),('end_angle_y','f4'),('end_raw_x','f4'),('end_raw_y','f4'),
        ('end_pupil_measure1','f4'),('end_pupil_measure2','f4'),('end_ppd_x','f4'),('end_ppd_y','f4'),
        ('end_velocity_x','f4'),('end_velocity_y','f4'),('end_velocity_xy','f4'),
        ('average_gaze_x','f4'),('average_gaze_y','f4'),('average_gaze_z','f4'),
        ('average_angle_x','f4'),('average_angle_y','f4'),('average_raw_x','f4'),('average_raw_y','f4'),
        ('average_pupil_measure1','f4'),('average_pupil_measure2','f4'),('average_ppd_x','f4'),('average_ppd_y','f4'),
        ('average_velocity_x','f4'),('average_velocity_y','f4'),('average_velocity_xy','f4'),
        ('peak_velocity_x','f4'),('peak_velocity_y','f4'),('peak_velocity_xy','f4'),
        ('status','u1')]
    baseDataType=DeviceEvent.dataType
    dataType=baseDataType+newDataTypes
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in newDataTypes]

    EVENT_TYPE_STRING='FIXATION_END'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING

    def __init__(self,*args,**kwargs):
        """

        :rtype : FixationEndEvent
        :param args:
        :param kwargs:
        """
        DeviceEvent.__init__(self,*args,**kwargs)
 

################### Saccade Event Types ##########################
#         
class SaccadeStartEvent(FixationStartEvent):
    newDataTypes = []
    baseDataType=FixationStartEvent.dataType
    dataType=baseDataType+newDataTypes
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[]

    EVENT_TYPE_STRING='SACCADE_START'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING

    def __init__(self,*args,**kwargs):
        """

        :rtype : FixationStartEvent
        :param args:
        :param kwargs:
        """
        FixationStartEvent.__init__(self,*args,**kwargs)

class SaccadeEndEvent(DeviceEvent):
    newDataTypes = [('eye', 'u1'), ('duration','u4'), ('amplitude_x','f4'), ('amplitude_y','f4'), ('angle', 'f4'),
        ('start_gaze_x','f4'),('start_gaze_y','f4'),('start_gaze_z','f4'),
        ('start_angle_x','f4'),('start_angle_y','f4'),('start_raw_x','f4'),('start_raw_y','f4'),
        ('start_pupil_measure1','f4'),('start_pupil_measure2','f4'), ('start_ppd_x','f4'),('start_ppd_y','f4'),
        ('start_velocity_x','f4'),('start_velocity_y','f4'),('start_velocity_xy','f4'),
        ('end_gaze_x','f4'),('end_gaze_y','f4'),('end_gaze_z','f4'),
        ('end_angle_x','f4'),('end_angle_y','f4'),('end_raw_x','f4'),('end_raw_y','f4'),
        ('end_pupil_measure1','f4'),('end_pupil_measure2','f4'),('end_ppd_x','f4'),('end_ppd_y','f4'),
        ('end_velocity_x','f4'),('end_velocity_y','f4'),('end_velocity_xy','f4'),
        ('average_velocity_x','f4'),('average_velocity_y','f4'),('average_velocity_xy','f4'),
        ('peak_velocity_x','f4'),('peak_velocity_y','f4'),('peak_velocity_xy','f4'),
        ('status','u1')]
    baseDataType=DeviceEvent.dataType
    dataType=baseDataType+newDataTypes
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in newDataTypes]

    EVENT_TYPE_STRING='SACCADE_END'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING

    def __init__(self,*args,**kwargs):
        """

        :rtype : SaccadeEndEvent
        :param args:
        :param kwargs:
        """
        DeviceEvent.__init__(self,*args,**kwargs)


################### Blink Event Types ##########################
# 
class BlinkStartEvent(DeviceEvent):
    newDataTypes = [('eye', 'u1'),('status', 'u1')]
    baseDataType=DeviceEvent.dataType
    dataType=baseDataType+newDataTypes
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in newDataTypes]

    EVENT_TYPE_STRING='BLINK_START'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING

    def __init__(self,*args,**kwargs):
        """

        :rtype : BlinkStartEvent
        :param args:
        :param kwargs:
        """
        DeviceEvent.__init__(self,*args,**kwargs)

class BlinkEndEvent(DeviceEvent):
    newDataTypes = [('eye', 'u1'),('duration','u4'),('status', 'u1')]
    baseDataType=DeviceEvent.dataType
    dataType=baseDataType+newDataTypes
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in newDataTypes]

    EVENT_TYPE_STRING='BLINK_END'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING

    def __init__(self,*args,**kwargs):
        """

        :rtype : BlinkEndEvent
        :param args:
        :param kwargs:
        """
        DeviceEvent.__init__(self,*args,**kwargs)
