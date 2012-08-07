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
'''
('raw_pupil_only', [('x', '<f4'), ('y', '<f4')]),('raw_pupil_size',[('v1','f2'),('v2','f2')]),
        ('raw_cr1_only', [('x', '<f4'), ('y', '<f4')]), ('raw_cr1_size',[('v1','f2'),('v2','f2')]),
        ('raw_cr2_only', [('x', '<f4'), ('y', '<f4')]), ('raw_cr2_size',[('v1','f2'),('v2','f2')]),
'''
##################### Eye Tracker Sample Stream Types ################################
# 
class MonocularEyeSample(DeviceEvent):
    dataType = DeviceEvent.dataType+[('eye', 'u1'), ('gaze', [('x','f4'), ('y','f4'),('z','f4')]), 
        ('angle', [('x','f4'), ('y','f4')]),('raw', [('x','f4'), ('y','f4')]),
        ('pupil_measure',[('v1','f2'),('v2','f2')]),('pixels_degree', [('x', '<f2'), ('y', '<f2')]),
        ('status', 'u1')]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,**kwargs)
        
class BinocularEyeSample(DeviceEvent):
    dataType = DeviceEvent.dataType+[('gaze', [('x','f4',2), ('y','f4',2),('z','f4',2)]), 
        ('angle', [('x','f4',2), ('y','f4',2),('z','f4',2)]), 
        ('raw', [('x','f4',2), ('y','f4',2),('z','f4',2)]),('pupil_measure',[('v1','f2',2),('v2','f2',2)]),  
        ('raw_pupil_only', [('x', '<f4',2), ('y', '<f4',2)]),('raw_pupil_size',[('d1','f2',2),('d2','f2',2)]),
        ('raw_cr1_only', [('x', '<f4',2), ('y', '<f4',2)]), ('raw_cr1_size',[('v1','f2',2),('v2','f2',2)]),
        ('raw_cr2_only', [('x', '<f4',2), ('y', '<f4',2)]), ('raw_cr2_size',[('v1','f2',2),('v2','f2',2)]),
        ('pixels_degree', [('x', '<f2',2), ('y', '<f2',2)]),('status', 'u1',2)]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]   
    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,**kwargs)
        
######## Eye Tracker basedTTL Input Event Type ############
# 
class EyeTTLInput(DeviceEvent):
    dataType = DeviceEvent.dataType+[('port', 'u8'),('value', 'u2')]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]   
    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)
        
######## Eye Tracker based Button Box / Response Pad Event Type ############
# 
class EyeButtonPress(DeviceEvent):
    dataType = DeviceEvent.dataType+[('button', 'u1')] 
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]    
    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)

class EyeButtonRelease(DeviceEvent):
    dataType = DeviceEvent.dataType+[('button', 'u1')] 
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]  
    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)

################### Fixation Event Types ##########################
# 
class FixationStartEvent(DeviceEvent):
    dataType = DeviceEvent.dataType+[('eye', 'u1'),('gaze', [('x','f4'), ('y','f4'),('z','f4')]), 
                ('pupil_measure',[('v1','f2'),('v2','f2')]),('pixels_degree', [('x', 'f4'), ('y', 'f4')]),
                ('velocity', [('x', 'f4'), ('y', 'f4'),('xy', 'f4')])]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]    
    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)

#class FixatonUpdateEvent(DeviceEvent):
##    dataType = DeviceEvent.dataType+[('eye', 'u1'),('duration','u16'),('average_gaze', [('x', 'f4'), ('y', 'f4')]),\
#               ('average_pupil_measure',[('v1','f4'),('v2','f4')]),('average_pixels_degree', [('x', '<f4'), ('y', 'f4')]),\
#                ('average_velocity', [('x', 'f4'), ('y', 'f4'),('xy', 'f4')]),('peak_velocity', [('x', 'f4'), ('y', 'f4'),('xy', 'f4')])]
#    print 'FixatonUpdateEvent:',dataType
#    ndType=N.dtype(dataType)
#    fieldCount=ndType.__len__()
#    __slots__=[e[0] for e in dataType]    
#    
##    def __init__(self,*args,**kwargs):
#        DeviceEvent.__init__(self,*args,**kwargs)    
       
class FixationEndEvent(FixationStartEvent):
    dataType = FixationStartEvent.dataType+[('start_event_id', 'u8')]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]    
    
    def __init__(self,*args,**kwargs):
        FixationStartEvent.__init__(self,*args,**kwargs) 

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
