"""
ioHub Python Module

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""

from .. import DeviceEvent
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
    dataType = DeviceEvent.dataType+[('eye', 'u1'), ('gaze_x','f4'),('gaze_y','f4'),('gaze_z','f4'), 
        ('angle_x','f4'),('angle_y','f4'),('raw_x','f4'),('raw_y','f4'),
        ('pupil_measure1','f4'),('pupil_measure2','f4'),('ppd_x','f4'),('ppd_y','f4'),
        ('velocity_x','f4'),('velocity_y','f4'),('velocity_xy','f4'),('status', 'u1')]
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)
        
class BinocularEyeSample(DeviceEvent):
    dataType = DeviceEvent.dataType+[('left_gaze_x','f4'),('left_gaze_y','f4'),('left_gaze_z','f4'), 
        ('left_angle_x','f4'),('left_angle_y','f4'),('left_raw_x','f4'),('left_raw_y','f4'),
        ('left_pupil_measure1','f4'),('left_pupil_measure2','f4'),('left_ppd_x','f4'),('left_ppd_y','f4'),
        ('left_velocity_x','f4'),('left_velocity_y','f4'),('left_velocity_xy','f4'),
        ('right_gaze_x','f4'),('right_gaze_y','f4'),('right_gaze_z','f4'), 
        ('right_angle_x','f4'),('right_angle_y','f4'),('right_raw_x','f4'),('right_raw_y','f4'),
        ('right_pupil_measure1','f4'),('right_pupil_measure2','f4'),('right_ppd_x','f4'),('right_ppd_y','f4'),
        ('right_velocity_x','f4'),('right_velocity_y','f4'),('right_velocity_xy','f4'),('status', 'u1')]
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)
        
######## Eye Tracker basedTTL Input Event Type ############
# 
#class EyeTTLInput(DeviceEvent):
#    dataType = DeviceEvent.dataType+[('port', 'u8'),('value', 'u2')]
#    attributeNames=[e[0] for e in dataType]
#    ndType=N.dtype(dataType)
#    fieldCount=ndType.__len__()
#    __slots__=attributeNames    
#    def __init__(self,*args,**kwargs):
#        DeviceEvent.__init__(self,*args,**kwargs)
         
######## Eye Tracker based Button Box / Response Pad Event Type ############
# 
#class EyeButtonPress(DeviceEvent):
#    dataType = DeviceEvent.dataType+[('button', 'u1')] 
#    ndType=N.dtype(dataType)
#    fieldCount=ndType.__len__()
#    __slots__=[e[0] for e in dataType]    
#    
#    def __init__(self,*args,**kwargs):
#        DeviceEvent.__init__(self,*args,**kwargs)
#
#class EyeButtonRelease(DeviceEvent):
#    dataType = DeviceEvent.dataType+[('button', 'u1')] 
#    ndType=N.dtype(dataType)
#    fieldCount=ndType.__len__()
#    __slots__=[e[0] for e in dataType]  
#    
#    def __init__(self,*args,**kwargs):
#        DeviceEvent.__init__(self,*args,**kwargs)
#
################### Fixation Event Types ##########################
# 
class FixationStartEvent(DeviceEvent):
    dataType = DeviceEvent.dataType+[('eye', 'u1'), ('gaze_x','f4'),('gaze_y','f4'),('gaze_z','f4'),
        ('pupil_measure1','f2'),('pupil_measure2','f2'),('ppd_x','<f2'),('ppd_y','<f2'),
        ('velocity_x','f4'),('velocity_y','f4'),('velocity_xy','f4')]
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)

class FixatonUpdateEvent(FixationStartEvent):
    dataType = FixationStartEvent.dataType+[('peak_velocity_x','f4'),('peak_velocity_y','f4'),('peak_velocity_xy','f4')]
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames    
    def __init__(self,*args,**kwargs):
        FixationStartEvent.__init__(self,*args,**kwargs)
       
class FixationEndEvent(FixatonUpdateEvent):
    dataType = FixatonUpdateEvent.dataType+[('start_event_id', 'u8')]
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames    
    def __init__(self,*args,**kwargs):
        FixatonUpdateEvent.__init__(self,*args,**kwargs)
 

################### Saccade Event Types ##########################
#         
class SaccadeStartEvent(FixationStartEvent):
    dataType = FixationStartEvent.dataType
    ndType=FixationStartEvent.ndType
    fieldCount=FixationStartEvent.fieldCount
    __slots__=[e[0] for e in dataType]   
    
    def __init__(self,*args,**kwargs):
        FixationStartEvent.__init__(self,*args,**kwargs)

#[('experiment_id', 'u8'), ('session_id', 'u4'), ('event_id', 'u8'), ('event_type', 'u1'), 
#('device_instance_code', 'a48'), ('device_time','u8'), ('logged_time', 'u8'), ('hub_time', 'u8'),
#('confidence_interval', 'f4'), ('delay', 'f4'), ('eye', 'u1'), ('gaze', [('x', 'f4'), ('y', 'f4'), ('z', 'f4')]),
#('pupil_measure', [('d1', 'f2'), ('d2', 'f2')]), ('pixels_degree', [('x', '<f2'), ('y', '<f2')]),
#('velocity', [('x', '<f4'), ('y', '<f4')]), ('start_event_id', 'u8'), ('amplitude', 'f32')]
#class SaccadeEndEvent(FixationEndEvent):
#    dataType = FixationEndEvent.dataType+[('amplitude','f32')]
#    print "SaccadeEnd Data Type:",dataType
#    ndType=N.dtype(dataType)
#    fieldCount=FixationEndEvent.fieldCount
#    __slots__=[e[0] for e in dataType]    
#    
#    def __init__(self,*args,**kwargs):
#        FixationEndEvent.__init__(self,*args,**kwargs)    
        
################### Blink Event Types ##########################
# 
class BlinkStartEvent(DeviceEvent):
    dataType = DeviceEvent.dataType+[('eye', 'u1')]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]   
    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)
#
#class BlinkEndEvent(BlinkStartEvent):
##    dataType = BlinkStartEvent.dataType+[('start_event_id', 'u64'),('duration','u16')]
#    ndType=N.dtype(dataType)
#    fieldCount=ndType.__len__()
#    __slots__=[e[0] for e in dataType]    
#    
#    def __init__(self,*args,**kwargs):
#        BlinkStartEvent.__init__(self,*args,**kwargs)   

################### Smooth Pursuit Event Types ##########################
#
# More like place holders at this point. ;)
# 
class PursuitStartEvent(DeviceEvent):
    dataType = DeviceEvent.dataType+[('eye', 'u1')]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]    
    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)

#class PursuitEndEvent(PursuitStartEvent):
#    dataType = PursuitStartEvent.dataType+[('start_event_id', 'u64'),('duration','u16')]
#    ndType=N.dtype(dataType)
#    fieldCount=ndType.__len__()
#    __slots__=[e[0] for e in dataType]   
#    
#    def __init__(self,*args,**kwargs):
#        PursuitStartEvent.__init__(self,*args,**kwargs)
