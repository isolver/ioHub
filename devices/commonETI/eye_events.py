from .. import DeviceEvent
import numpy as N

"""
Eye Tracker Event Types. The Common Eye Tracker Interface supports monocular and binocular eye samples
and four eye event types; note that not all eye tracker support all these event types.  

* Saccades: StartSaccadeEvent, EndSaccadeEvent, SaccadeEvent
* Fixations: StartFixationEvent, FixationUpdateEvent, EndFixationEvent, FixationEvent
* Blinks: StartBlinkEvent, EndBlinkEvent, BlinkEvent
* SmoothPursuit: StartPursuitEvent, EndPursuitEvent, PursuitEvent



"""
class MonocularEyeSample(DeviceEvent):
    dataType = DeviceEvent.dataType+[('eye', 'u1'), ('gaze', [('x','f4'), ('y','f4'),('z','f4')]), 
        ('angle', [('x','f4'), ('y','f4'),('z','f4')]), 
        ('raw', [('x','f4'), ('y','f4'),('z','f4')]),('pupil_measure',[('d1','f2'),('d2','f2')]),  
        ('raw_pupil_only', [('x', '<f4'), ('y', '<f4')]),('raw_pupil_size',[('d1','f2'),('d2','f2')]),
        ('raw_cr1_only', [('x', '<f4'), ('y', '<f4')]), ('raw_cr1_size',[('d1','f2'),('d2','f2')]),
        ('raw_cr2_only', [('x', '<f4'), ('y', '<f4')]), ('raw_cr2_size',[('d1','f2'),('d2','f2')]),
        ('pixels_degree', [('x', '<f2'), ('y', '<f2')]),('status', 'u1')]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]+['np_array','transport_dict','tablesRow']    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)
        
class BinocularEyeSample(DeviceEvent):
    dataType = DeviceEvent.dataType+[('gaze', [('x','f4',2), ('y','f4',2),('z','f4',2)]), 
        ('angle', [('x','f4',2), ('y','f4',2),('z','f4',2)]), 
        ('raw', [('x','f4',2), ('y','f4',2),('z','f4',2)]),('pupil_measure',[('d1','f2',2),('d2','f2',2)]),  
        ('raw_pupil_only', [('x', '<f4',2), ('y', '<f4',2)]),('raw_pupil_size',[('d1','f2',2),('d2','f2',2)]),
        ('raw_cr1_only', [('x', '<f4',2), ('y', '<f4',2)]), ('raw_cr1_size',[('d1','f2',2),('d2','f2',2)]),
        ('raw_cr2_only', [('x', '<f4',2), ('y', '<f4',2)]), ('raw_cr2_size',[('d1','f2',2),('d2','f2',2)]),
        ('pixels_degree', [('x', '<f2',2), ('y', '<f2',2)]),('status', 'u1',2)]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]+['np_array','transport_dict','tablesRow']    
    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)
        
######## Eye Tracker basedTTL Input Event Type ############
# 
class EyeTTLInput(DeviceEvent):
    dataType = DeviceEvent.dataType+[('port', 'u8'),('value', 'u2') 
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]+['np_array','transport_dict','tablesRow']    
    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)
        
######## Eye Tracker based Button Box / Response Pad Event Type ############
# 
class EyeButtons(DeviceEvent):
    dataType = DeviceEvent.dataType+[('button', 'u1'),('state', 'b') 
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]+['np_array','transport_dict','tablesRow']    
    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)

################### Fixation Event Types ##########################
# 
class FixationStartEvent(DeviceEvent):
    dataType = DeviceEvent.dataType+[('eye', 'u1')('gaze', [('x','f4'), ('y','f4'),('z','f4')]), 
                ('pupil_measure',[('d1','f2'),('d2','f2')]),('pixels_degree', [('x', '<f2'), ('y', '<f2')]),
                ('velocity', [('x', '<f4'), ('y', '<f4')])]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]+['np_array','transport_dict','tablesRow']    
    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)

class FixatonUpdateEvent(DeviceEvent):
    dataType = DeviceEvent.dataType+[('duration','u16'),('average_gaze', [('x', '<f4'), ('y', '<f4')]),
                ('averagePupilSize','f32'),('average_pixels_degree', [('x', '<f2'), ('y', '<f2')]), 
                ('average_velocity', [('x', '<f4'), ('y', '<f4')]),('peak_velocity', [('x', '<f4'), ('y', '<f4')])
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]+['np_array','transport_dict','tablesRow']    
    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)    
       
class FixationEndEvent(FixationStartEvent):
    dataType = FixationStartEvent.dataType+[('start_event_id', 'u8')]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]+['np_array','transport_dict','tablesRow']    
    
    def __init__(self,*args,**kwargs):
        FixationStartEvent.__init__(self,*args,**kwargs) 
        
class FixationEvent(DeviceEvent):
    dataType = DeviceEvent.dataType+[('end_event_id', 'u64'),
                ('duration','u16'),('average_gaze', [('x', '<f4'), ('y', '<f4')]),('averagePupilSize','f32'),
                ('average_pixels_degree', [('x', '<f2'), ('y', '<f2')]), 
                ('average_velocity', [('x', '<f4'), ('y', '<f4')]),('peak_velocity', [('x', '<f4'), ('y', '<f4')])
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]+['np_array','transport_dict','tablesRow']    
    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)    

################### Saccade Event Types ##########################
#         
class SaccadeStartEvent(FixationStartEvent):
    dataType = FixationStartEvent.dataType
    ndType=FixationStartEvent.ndtype
    fieldCount=FixationStartEvent.fieldCount
    __slots__=[e[0] for e in dataType]+['np_array','transport_dict','tablesRow']    
    
    def __init__(self,*args,**kwargs):
        FixationStartEvent.__init__(self,*args,**kwargs)

class SaccadeEndEvent(FixationEndEvent):
    dataType = FixationEndEvent.dataType+[('amplitude','f32')]
    ndType=N.dtype(dataType)
    fieldCount=FixationEndEvent.fieldCount
    __slots__=[e[0] for e in dataType]+['np_array','transport_dict','tablesRow']    
    
    def __init__(self,*args,**kwargs):
        FixationEndEvent.__init__(self,*args,**kwargs) 

class SaccadeEvent(FixationEvent):
    dataType = FixationEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=FixationEvent.__len__()
    __slots__=[e[0] for e in dataType]+['np_array','transport_dict','tablesRow']    
    
    def __init__(self,*args,**kwargs):
        FixationEvent.__init__(self,*args,**kwargs)    
        
################### Blink Event Types ##########################
# 
class BlinkStartEvent(DeviceEvent):
    dataType = DeviceEvent.dataType+[('eye', 'u1')]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]+['np_array','transport_dict','tablesRow']    
    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)

class BlinkEndEvent(BlinkStartEvent):
    dataType = BlinkStartEvent.dataType+[('start_event_id', 'u64'),('duration','u16'),]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]+['np_array','transport_dict','tablesRow']    
    
    def __init__(self,*args,**kwargs):
        BlinkStartEvent.__init__(self,*args,**kwargs)

class BlinkEvent(DeviceEvent):
    dataType = DeviceEvent.dataType+[('end_event_id', 'u64')]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]+['np_array','transport_dict','tablesRow']    
    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)    

################### Smooth Pursuit Event Types ##########################
#
# More like place holders at this point. ;)
# 
class PursuitStartEvent(DeviceEvent):
    dataType = DeviceEvent.dataType+[('eye', 'u1')]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]+['np_array','transport_dict','tablesRow']    
    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)

class PursuitEndEvent(PursuitStartEvent):
    dataType = PursuitStartEvent.dataType++[('start_event_id', 'u64'),('duration','u16'),]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]+['np_array','transport_dict','tablesRow']    
    
    def __init__(self,*args,**kwargs):
        PursuitStartEvent.__init__(self,*args,**kwargs)

class PursuitEvent(DeviceEvent):
    dataType = DeviceEvent.dataType+[('end_event_id', 'u64')]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]+['np_array','transport_dict','tablesRow']    
    
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)    
StartPursuitEvent, EndPursuitEvent, PursuitEvent
