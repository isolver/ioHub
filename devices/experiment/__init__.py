"""
ioHub
.. file: ioHub/devices/experiment/__init__.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

from .. import Device,Computer,DeviceEvent,EventConstants
currentUsec=Computer.currentUsec
import numpy as N

class ExperimentDevice(Device):
    CATEGORY_LABEL='VIRTUAL'
    DEVICE_LABEL='EXPERIMENT_DEVICE'
    __slots__=[]
    def __init__(self,*args,**kwargs):
        """

        :rtype : object
        :param args:
        :param kwargs:
        """
        deviceConfig=kwargs['dconfig']
        deviceSettings={'instance_code':deviceConfig['instance_code'],
            'category_id':EventConstants.DEVICE_CATERGORIES[ExperimentDevice.CATEGORY_LABEL],
            'type_id':EventConstants.DEVICE_TYPES[ExperimentDevice.DEVICE_LABEL],
            'device_class':deviceConfig['device_class'],
            'name':deviceConfig['name'],
            'os_device_code':'OS_DEV_CODE_NOT_SET',
            'max_event_buffer_length':deviceConfig['event_buffer_length']
            }          
        Device.__init__(self,**deviceSettings)
        
    def _nativeEventCallback(self,event):
        event[DeviceEvent.EVENT_LOGGED_TIME_INDEX]=int(currentUsec()) # set logged time of event

        event[DeviceEvent.EVENT_DELAY_INDEX]=event[DeviceEvent.EVENT_LOGGED_TIME_INDEX]-event[DeviceEvent.EVENT_DEVICE_TIME_INDEX]

        # on windows ioHub and experiment process use same timebase, so device time == hub time
        event[DeviceEvent.EVENT_HUB_TIME_INDEX]=event[DeviceEvent.EVENT_DEVICE_TIME_INDEX]

        self._nativeEventBuffer.append(event)
        return True
    
    def _poll(self):
        pass
 
    @staticmethod
    def _getIOHubEventObject(event,device_instance_code):
        return event

            
######### Experiment Events ###########

class MessageEvent(DeviceEvent):
    EVENT_TYPE_STRING='MESSAGE'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE='MESSAGE'

    _newDataTypes=[('msg_offset','i2'),('prefix','a3'),('text','a128')]
    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self, **kwargs):
        """

        :rtype : object
        :param kwargs:
        """
        DeviceEvent.__init__(self, *args,**kwargs)

    @staticmethod
    def createAsList(text,prefix='',msg_offset=0.0, usec_time=None):
        """

        :rtype : object
        :param text:
        :param prefix:
        :param msg_offset:
        :param usec_time:
        :return:
        """
        cusec=int(currentUsec())
        if usec_time is not None:
            cusec=usec_time
        return (0,0,Computer.getNextEventID(),MessageEvent.EVENT_TYPE_ID,'psychopy',cusec,0,0,0.0,0.0,msg_offset,prefix,text)


