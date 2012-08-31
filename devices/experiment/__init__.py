"""
ioHub Python Module

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""

from .. import Device,Computer,DeviceEvent
import ioHub
currentUsec=Computer.currentUsec
import numpy as N

class ExperimentDevice(Device):
    dataType = Device.dataType+[]
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames
    categoryTypeString='VIRTUAL'
    deviceTypeString='EXPERIMENT_DEVICE'
    
    STAT_COLLECTION_COUNT=200
    
    runningTimebaseOffset=0
    eventCount=0
    
    def __init__(self,*args,**kwargs):
        deviceConfig=kwargs['dconfig']
        deviceSettings={'instance_code':deviceConfig['instance_code'],
            'category_id':ioHub.DEVICE_CATERGORY_ID_LABEL[ExperimentDevice.categoryTypeString],
            'type_id':ioHub.DEVICE_TYPE_LABEL[ExperimentDevice.deviceTypeString],
            'device_class':deviceConfig['device_class'],
            'user_label':deviceConfig['name'],
            'os_device_code':'OS_DEV_CODE_NOT_SET',
            'max_event_buffer_length':deviceConfig['event_buffer_length']
            }          
        Device.__init__(self,**deviceSettings)
        
    def _nativeEventCallback(self,event):
        event[6]=int(currentUsec()) # set logged time of event
        
        ExperimentDevice.eventCount+=1
        
        if self.eventCount<self.STAT_COLLECTION_COUNT:
            ExperimentDevice.runningTimebaseOffset+=(event[6]-event[5])
            event[9]=1000.0 # for first 100 events, assume 1 msec (1000 usec) delay while stats are being gathered
        elif self.eventCount == self.STAT_COLLECTION_COUNT:
            ExperimentDevice.runningTimebaseOffset=ExperimentDevice.runningTimebaseOffset/float(self.STAT_COLLECTION_COUNT)
            event[9]=1000.0 # for first 100 events, assume 1 msec (1000 usec) delay while stats are being gathered
        else:
            ExperimentDevice.runningTimebaseOffset=(ExperimentDevice.runningTimebaseOffset*0.99)+((event[6]-event[5])*0.01)
            event[9]=(event[6]-self.runningTimebaseOffset)-event[5] # calc delay based on running avg. of timebase offsets
        
        event[7]=int(event[6]-event[9]) # hub time
        
        self.I_nativeEventBuffer.append(event)
        return True
    
    def _poll(self):
        pass
 
    @staticmethod
    def _getIOHubEventObject(event,device_instance_code):
        #print "Exp event:",event
        event_type = event[3]
        if event_type==ioHub.EVENT_TYPES['MESSAGE']:
            return MessageEvent.createFromOrderedList(event)
        if event_type==ioHub.EVENT_TYPES['COMMAND']:
            return CommandEvent.createFromOrderedList(event)
            
######### Experiment Events ###########

class MessageEvent(DeviceEvent):
    dataType=DeviceEvent.dataType+[('msg_offset','i2'),('prefix','a3'),('text','a128')]
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames
    def __init__(self,**kwargs):
        DeviceEvent.__init__(self,**kwargs)

    @staticmethod
    def createAsList(text,prefix='',msg_offset=0.0):
        cusec=int(currentUsec())
        return (0,0,Computer.getNextEventID(),ioHub.EVENT_TYPES['MESSAGE'],'psychopy',cusec,0,0,0.0,0.0,msg_offset,prefix,text)
    
class CommandEvent(MessageEvent):
    dataType=MessageEvent.dataType+[('priority','u1'),('command','a32')]
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames
    def __init__(self,**kwargs):
        MessageEvent.__init__(self,**kwargs)
        
    @staticmethod
    def createAsList(command,text,priority=0,prefix='',msg_offset=0.0):
        cusec=int(currentUsec())
        return (0,0,Computer.getNextEventID(),ioHub.EVENT_TYPES['COMMAND'],'psychopy',cusec,0,0,0.0,0.0,msg_offset,prefix,text,priority,command)
        

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