"""
ioHub
.. file: ioHub/devices/experiment/__init__.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

from .. import Device,Computer,DeviceEvent
import ioHub
currentUsec=Computer.currentUsec
import numpy as N

class ExperimentDevice(Device):
    newDataTypes=[]
    baseDataType=Device.dataType
    dataType=baseDataType+newDataTypes
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    categoryTypeString='VIRTUAL'
    deviceTypeString='EXPERIMENT_DEVICE'
    def __init__(self,*args,**kwargs):
        deviceConfig=kwargs['dconfig']
        deviceSettings={'instance_code':deviceConfig['instance_code'],
            'category_id':ioHub.devices.EventConstants.DEVICE_CATERGORIES[ExperimentDevice.categoryTypeString],
            'type_id':ioHub.devices.EventConstants.DEVICE_TYPES[ExperimentDevice.deviceTypeString],
            'device_class':deviceConfig['device_class'],
            'user_label':deviceConfig['name'],
            'os_device_code':'OS_DEV_CODE_NOT_SET',
            'max_event_buffer_length':deviceConfig['event_buffer_length']
            }          
        Device.__init__(self,**deviceSettings)
        
    def _nativeEventCallback(self,event):
        event[DeviceEvent.EVENT_LOGGED_TIME_INDEX]=int(currentUsec()) # set logged time of event

        event[DeviceEvent.EVENT_DELAY_INDEX]=event[DeviceEvent.EVENT_LOGGED_TIME_INDEX]-event[DeviceEvent.EVENT_DEVICE_TIME_INDEX]

        # on windows ioHub and experiment process use same timebase, so device time == hub time
        event[DeviceEvent.EVENT_HUB_TIME_INDEX]=event[DeviceEvent.EVENT_DEVICE_TIME_INDEX]

        self.I_nativeEventBuffer.append(event)
        return True
    
    def _poll(self):
        pass
 
    @staticmethod
    def _getIOHubEventObject(event,device_instance_code):
        return event

            
######### Experiment Events ###########

class MessageEvent(DeviceEvent):
    newDataTypes=[('msg_offset','i2'),('prefix','a3'),('text','a128')]
    baseDataType=DeviceEvent.dataType
    dataType=baseDataType+newDataTypes
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in newDataTypes]
    def __init__(self,**kwargs):
        DeviceEvent.__init__(self,**kwargs)

    @staticmethod
    def createAsList(text,prefix='',msg_offset=0.0, usec_time=None):
        cusec=int(currentUsec())
        if usec_time is not None:
            cusec=usec_time
        return (0,0,Computer.getNextEventID(),ioHub.devices.EventConstants.EVENT_TYPES['MESSAGE'],'psychopy',cusec,0,0,0.0,0.0,msg_offset,prefix,text)
    
#class CommandEvent(MessageEvent):
#    newDataTypes=[('priority','u1'),('command','a32')]
#    baseDataType=MessageEvent.dataType
#    dataType=baseDataType+newDataTypes
#    attributeNames=[e[0] for e in dataType]
#    ndType=N.dtype(dataType)
#    fieldCount=ndType.__len__()
#    __slots__=[e[0] for e in newDataTypes]
#    def __init__(self,**kwargs):
#        MessageEvent.__init__(self,**kwargs)
#
#    @staticmethod
#    def createAsList(command,text,priority=0,prefix='',msg_offset=0.0):
#        cusec=int(currentUsec())
#        return (0,0,Computer.getNextEventID(),ioHub.devices.EventConstants.EVENT_TYPES['COMMAND'],'psychopy',cusec,0,0,0.0,0.0,msg_offset,prefix,text,priority,command)
        

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
        
class ExperimentIndependentVariable(ExperimentEvent):
    dataType = list(ExperimentEvent.dataType)+[('variable','a16'),('value','a32')]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)
        
class ExperimentDependentVariable(ExperimentIndependentVariable):
    ecode=EventConstants.EVENT_TYPES['EXPERIMENT_DV']
    dataType = list(ExperimentIndependentVariable.dataType)+[('correct_value',N.string_,32),]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class DisplayDrawStart(ExperimentEvent):
    ecode=EventConstants.EVENT_TYPES['DRAW_START']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class DisplayDrawEnd(ExperimentEvent):
    ecode=EventConstants.EVENT_TYPES['DRAW_END']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class DisplaySwapStart(ExperimentEvent):
    ecode=EventConstants.EVENT_TYPES['SWAP_START']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class DisplaySwapEnd(ExperimentEvent):
    ecode=EventConstants.EVENT_TYPES['SWAP_END']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class DisplayVblank(ExperimentEvent):
    ecode=EventConstants.EVENT_TYPES['VBLANK']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class DisplayStart(ExperimentEvent):
    ecode=EventConstants.EVENT_TYPES['DISPLAY_START']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class DisplayEnd(ExperimentEvent):
    ecode=EventConstants.EVENT_TYPES['DISPLAY_END']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class ExperimentEventTrigger(ExperimentEvent):
    ecode=EventConstants.EVENT_TYPES['EVENT_TRIGGER']
    dataType = list(ExperimentEvent.dataType)+[('trigger_event_id',N.uint64),]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]

    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class ExperimentCodeSnippetStart(ExperimentEvent):
    ecode=EventConstants.EVENT_TYPES['FUNCTION_START']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]

    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class ExperimentCodeSnippetEnd(ExperimentEvent):
    ecode=EventConstants.EVENT_TYPES['FUNCTION_END']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]

    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)        
        
class ExperimentStart(ExperimentEvent):
    ecode=EventConstants.EVENT_TYPES['EXPERIMENT_START']
    dataType = ExperimentEvent.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class ExperimentEnd(ExperimentEvent):
    ecode=EventConstants.EVENT_TYPES['EXPERIMENT_END']
    dataType = list(ExperimentEvent.dataType)+[('experiment_duration',N.uint32),]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class SequenceStart(ExperimentEvent):
    ecode=EventConstants.EVENT_TYPES['SEQUENCE_START']
    dataType = list(ExperimentEvent.dataType)+[('id',N.uint16),('label',N.string_,16),('currentIteration',N.uint16),('totalIterations',N.uint16)]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class SequenceEnd(ExperimentEvent):
    ecode=EventConstants.EVENT_TYPES['SEQUENCE_END']
    dataType = list(ExperimentEvent.dataType)+[('id',N.uint16),('label',N.string_,16)]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class BlockStart(SequenceStart):
    ecode=EventConstants.EVENT_TYPES['BLOCK_START']
    dataType = SequenceStart.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        SequenceStart.__init__(**kwargs)

class BlockEnd(SequenceEnd):
    ecode=EventConstants.EVENT_TYPES['BLOCK_END']
    dataType = SequenceEnd.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        SequenceEnd.__init__(**kwargs)

class TrialStart(ExperimentEvent):
    ecode=EventConstants.EVENT_TYPES['TRIAL_START']
    dataType = list(ExperimentEvent.dataType)+[('id',N.uint16),('label',N.string_,16)]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)

class TrialEnd(TrialStart):
    ecode=EventConstants.EVENT_TYPES['TRIAL_END']
    dataType = TrialStart.dataType
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=[e[0] for e in dataType]
    def __init__(self,**kwargs):
        ExperimentEvent.__init__(**kwargs)
'''  