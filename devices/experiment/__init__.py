"""
ioHub Python Module

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""

from .. import Device,Computer,DeviceEvent
import ioHub
currentMsec=Computer.currentMsec
import numpy as N

class ExperimentRuntimeDevice(Device):
    dataType = list(Device.dataType)
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames
    categoryTypeString='VIRTUAL'
    deviceTypeString='EXPERIMENT_DEVICE'
    def __init__(self,*args,**kwargs):
        deviceConfig=kwargs['dconfig']
        deviceSettings={'instance_code':deviceConfig['instance_code'],
            'category_id':ioHub.DEVICE_CATERGORY_ID_LABEL[ExperimentRuntimeDevice.categoryTypeString],
            'type_id':ioHub.DEVICE_TYPE_LABEL[ExperimentRuntimeDevice.deviceTypeString],
            'device_class':deviceConfig['device_class'],
            'user_label':deviceConfig['name'],
            'os_device_code':'OS_DEV_CODE_NOT_SET',
            'max_event_buffer_length':deviceConfig['event_buffer_size']
            }          
        Device.__init__(self,**deviceSettings)
 
        print "ExperimentRuntimeDevice class set as ",self.__class__.__name__

    def eventCallback(self,event):
        notifiedTime=int(currentMsec())
        self.I_eventBuffer.append((notifiedTime,event))
        return True
    
    def poll(self):
        pass
 
    @staticmethod
    def getIOHubEventObject(event,device_instance_code):
        print "Exp event:",event
        event_type = event[1][3]
        if event_type==ioHub.EVENT_TYPES['MESSAGE']:
            return MessageEvent.createFromOrderedList(event)
        if event_type==ioHub.EVENT_TYPES['COMMAND']:
            return CommandEvent.createFromOrderedList(event)
            
######### Experiment Events ###########

class ExperimentEvent(DeviceEvent):
    dataType=list(DeviceEvent.dataType)
    attributeNames=[e[0] for e in dataType]
    defaultValueDict={'experiment_id':0,'session_id':0,'event_id':0,'event_type':ioHub.EVENT_TYPES['EXPERIMENT_EVENT'],
                    'device_instance_code':'UNDEFINED','device_time':0,'logged_time':0,'hub_time':0,
                    'confidence_interval': 0.0,'delay':0.0}
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames
    def __init__(self,**kwargs):
        DeviceEvent.__init__(self,**kwargs)

class MessageEvent(ExperimentEvent):
    dataType=ExperimentEvent.dataType+[('msg_offset','i2'),('prefix','a3'),('text','a128')]
    attributeNames=[e[0] for e in dataType]
    defaultValueDict=dict(ExperimentEvent.defaultValueDict,**{'msg_offset':0,'prefix':'','text':'','event_type':ioHub.EVENT_TYPES['MESSAGE']})
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames
    def __init__(self,**kwargs):
        dargs=dict(MessageEvent.defaultValueDict,**kwargs)
        ExperimentEvent.__init__(self,**dargs)

    @staticmethod
    def create(text='',msg_offset=0.0,prefix=''):
        device_time=currentMsec()
        return MessageEvent(device_time=device_time,text=text,msg_offset=msg_offset,prefix=prefix) 
    
class CommandEvent(MessageEvent):
    dataType=MessageEvent.dataType+[('priority','u1'),('command','a32')]
    attributeNames=[e[0] for e in dataType]
    defaultValueDict=dict(MessageEvent.defaultValueDict,**{'priority':255,'command':'','event_type':ioHub.EVENT_TYPES['COMMAND']})
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames
    def __init__(self,**kwargs):
        dargs=dict(CommandEvent.defaultValueDict,**kwargs)
        MessageEvent.__init__(self,**dargs)
        
    @staticmethod
    def create(text='',priority=0,command='',msg_offset=0.0,msg_prefix=''):
        device_time=currentMsec()
        return CommandEvent(device_time=device_time,priority=priority,command=command,text=text,msg_offset=msg_offset,prefix=prefix)
        

'''
######### Meta Deta ##########

class ExperimentMetaData(ioHub.devices.ioObject):
    dataType=ioHub.devices.ioObject.dataType+[('name',N.unicode_,64),('owner_id',N.uint32)]
    attributeNames=[e[0] for e in dataType]
    defaultValueDict={'name':'EXPERIMENT_NAME_NOT_SET','owner_id':0}
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames
    def __init__(self,**kwargs):
        ioHub.devices.ioObject.__init__(self,**kwargs)

########
        
class SessionMetaData(object):
    pass
 

########
        
class ParticipantMetaData(object):
    pass

########
        
class SiteMetaData(object):
    pass

########
        
class LabMetaData(object):
    pass

########
        
class UserMetaData(object):
    pass

########
        
class DeviceMetaData(object):
    pass

########
          
class DeviceConfigurationData(object):
    pass

print "***** TO DO: Update all ExperimentEvents to use new DeviceEvent class structure *****"        
        
class ExperimentIndependentVariable(ExperimentEvent):
    dataType = list(ExperimentEvent.dataType)+[('variable','a16'),('value','a32')]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)
        
class ExperimentDependentVariable(ExperimentIndependentVariable):
    ecode=EVENT_TYPES['EXPERIMENT_DV']
    dataType = list(ExperimentIndependentVariable.dataType)+[('correct_value',N.string_,32),]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class DisplayDrawStart(ExperimentEvent):
    ecode=EVENT_TYPES['DRAW_START']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class DisplayDrawEnd(ExperimentEvent):
    ecode=EVENT_TYPES['DRAW_END']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class DisplaySwapStart(ExperimentEvent):
    ecode=EVENT_TYPES['SWAP_START']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class DisplaySwapEnd(ExperimentEvent):
    ecode=EVENT_TYPES['SWAP_END']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class DisplayVblank(ExperimentEvent):
    ecode=EVENT_TYPES['VBLANK']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class DisplayStart(ExperimentEvent):
    ecode=EVENT_TYPES['DISPLAY_START']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class DisplayEnd(ExperimentEvent):
    ecode=EVENT_TYPES['DISPLAY_END']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class ExperimentEventTrigger(ExperimentEvent):
    ecode=EVENT_TYPES['EVENT_TRIGGER']
    dataType = list(ExperimentEvent.dataType)+[('trigger_event_id',N.uint64),]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]

    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class ExperimentCodeSnippetStart(ExperimentEvent):
    ecode=EVENT_TYPES['FUNCTION_START']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]

    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class ExperimentCodeSnippetEnd(ExperimentEvent):
    ecode=EVENT_TYPES['FUNCTION_END']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]

    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)        
        
class ExperimentStart(ExperimentEvent):
    ecode=EVENT_TYPES['EXPERIMENT_START']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class ExperimentEnd(ExperimentEvent):
    ecode=EVENT_TYPES['EXPERIMENT_END']
    dataType = list(ExperimentEvent.dataType)+[('experiment_duration',N.uint32),]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class SequenceStart(ExperimentEvent):
    ecode=EVENT_TYPES['SEQUENCE_START']
    dataType = list(ExperimentEvent.dataType)+[('id',N.uint16),('label',N.string_,16),('currentIteration',N.uint16),('totalIterations',N.uint16)]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class SequenceEnd(ExperimentEvent):
    ecode=EVENT_TYPES['SEQUENCE_END']
    dataType = list(ExperimentEvent.dataType)+[('id',N.uint16),('label',N.string_,16)]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class BlockStart(SequenceStart):
    ecode=EVENT_TYPES['BLOCK_START']
    dataType = SequenceStart.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        SequenceStart.__init__(**kwargs)

class BlockEnd(SequenceEnd):
    ecode=EVENT_TYPES['BLOCK_END']
    dataType = SequenceEnd.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        SequenceEnd.__init__(**kwargs)

class TrialStart(ExperimentEvent):
    ecode=EVENT_TYPES['TRIAL_START']
    dataType = list(ExperimentEvent.dataType)+[('id',N.uint16),('label',N.string_,16)]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class TrialEnd(TrialStart):
    ecode=EVENT_TYPES['TRIAL_END']
    dataType = TrialStart.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)
'''  