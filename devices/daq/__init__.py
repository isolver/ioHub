"""
ioHub
.. file: ioHub/devices/daq/__init__.py

Copyright (C)  2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson
"""


from .. import Device, DeviceEvent
from ioHub.constants import DeviceConstants, EventConstants
import numpy as N


class DAQDevice(Device):
    DAQ_CHANNEL_MAPPING=dict()
    DAQ_GAIN_OPTIONS=dict()
    DAQ_CONFIG_OPTIONS=dict()

    DAQ_INPUT_READ_OPTIONS = ['POLL','SCAN'] # either of, or list of selections.
    DAQ_INPUT_READ_TYPE = str # list or str

    DAQ_INPUT_SCAN_FREQ_TYPE = int # list or int
    INPUT_SAMPLE_COUNT_TYPE = int  # always int

    INPUT_POLL_TYPE_OPTIONS = ['ALL','EACH'] #either ALL or EACH str

    ALL_EVENT_CLASSES=[]
    
    DEVICE_MODEL_ID=0 # over write by sub class. Used in multichannel events.
    DEVICE_TYPE_ID=DeviceConstants.DAQ
    DEVICE_TYPE_STRING=DeviceConstants.getName(DEVICE_TYPE_ID)
    __slots__=[]
    def __init__(self, *args, **kwargs):
        Device.__init__(self,*args, **kwargs)

    def _poll(self):
        return self.isReportingEvents()
#
## Event Multichannel input
#

class DAQEvent(DeviceEvent):    
    PARENT_DEVICE=DAQDevice
    
class DAMultiChannelInputEvent(DAQEvent):
    _newDataTypes = [
        ('MODEL_ID',N.uint8),
        ('AI_0',N.float32),
        ('AI_1',N.float32),
        ('AI_2',N.float32),
        ('AI_3',N.float32),
        ('AI_4',N.float32),
        ('AI_5',N.float32),
        ('AI_6',N.float32),
        ('AI_7',N.float32)
    ]
    
    
    EVENT_TYPE_ID=EventConstants.DA_MULTI_CHANNEL_INPUT
    EVENT_TYPE_STRING=EventConstants.getName(EVENT_TYPE_ID)
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING
    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self, *args, **kwargs):
        """

        :rtype : object
        :param args:
        :param kwargs:
        """
        DAQEvent.__init__(self, *args, **kwargs)
#
## Event Multichannel input
#
#
#class DASingleChannelInputEvent(DAQEvent):
#    _newDataTypes = [
#        ('channel_name',N.str,8),
#        ('float_value',N.float32),
#        ('int_value',N.uint32)
#        ]
#
#
#    EVENT_TYPE_ID=EventConstants.DA_SINGLE_CHANNEL_INPUT
#    EVENT_TYPE_STRING=EventConstants.getName(EVENT_TYPE_ID)
#    IOHUB_DATA_TABLE=EVENT_TYPE_STRING
#    __slots__=[e[0] for e in _newDataTypes]
#    def __init__(self, *args, **kwargs):
#        """
#
#        :rtype : object
#        :param args:
#        :param kwargs:
#        """
#        DAQEvent.__init__(self, *args, **kwargs)

import HW