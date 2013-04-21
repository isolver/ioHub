"""
ioHub
.. file: ioHub/devices/daq/__init__.py

Copyright (C)  2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson
"""


from .. import Device, DeviceEvent
from ...constants import DeviceConstants, EventConstants
import numpy as N


class AnalogInputDevice(Device):
    DAQ_CHANNEL_MAPPING=dict()
    DAQ_GAIN_OPTIONS=dict()
    DAQ_CONFIG_OPTIONS=dict()

    _newDataTypes = [('input_channel_count', N.uint8), 
                     ('channel_sampling_rate', N.uint16)]

    EVENT_CLASS_NAMES=['MultiChannelAnalogInputEvent']
    DEVICE_TYPE_ID=DeviceConstants.ANALOGINPUT
    DEVICE_TYPE_STRING="ANALOGINPUT"

    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self, *args, **kwargs):
        Device.__init__(self,*args, **kwargs['dconfig'])

    def _poll(self):
        return self.isReportingEvents()
#
## Event Multichannel input
#

class AnalogInputEvent(DeviceEvent):    
    PARENT_DEVICE=AnalogInputDevice
    
class MultiChannelAnalogInputEvent(AnalogInputEvent):
    _newDataTypes = [
        ('AI_0',N.float32),
        ('AI_1',N.float32),
        ('AI_2',N.float32),
        ('AI_3',N.float32),
        ('AI_4',N.float32),
        ('AI_5',N.float32),
        ('AI_6',N.float32),
        ('AI_7',N.float32)
    ]
    EVENT_TYPE_ID=EventConstants.MULTI_CHANNEL_ANALOG_INPUT
    EVENT_TYPE_STRING='MULTI_CHANNEL_ANALOG_INPUT'
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING
    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self, *args, **kwargs):
        AnalogInputEvent.__init__(self, *args, **kwargs)
