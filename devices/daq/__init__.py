"""
ioHub
.. file: ioHub/devices/eyeTrackerInterface/HW/devices/daq/__init__.py

Copyright (C)  Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson
"""


from .. import Device, EventConstants, DeviceEvent
import numpy as N


class DAQDevice(Device):
    CATEGORY_LABEL='DIGITAL_ANALOG_IO'
    DEVICE_LABEL='GPIO_DEVICE'

    DAQ_CHANNEL_MAPPING=dict()
    DAQ_GAIN_OPTIONS=dict()
    DAQ_CONFIG_OPTIONS=dict()

    DAQ_INPUT_READ_OPTIONS = ['POLL','SCAN'] # either of, or list of selections.
    DAQ_INPUT_READ_TYPE = str # list or str

    DAQ_INPUT_SCAN_FREQ_TYPE = int # list or int
    INPUT_SAMPLE_COUNT_TYPE = int  # always int

    INPUT_POLL_TYPE_OPTIONS = ['ALL','EACH'] #either ALL or EACH str

    __slots__=[]
    def __init__(self, *args, **kwargs):
        Device.__init__(self,*args, **kwargs)


    def _poll(self):
        if self.isReportingEvents():
            return True
        return False

class DAQMultiChannelInputEvent(DeviceEvent):
    _newDataTypes = [
        ('AI_0',N.float32),
        ('AI_1',N.float32),
        ('AI_2',N.float32),
        ('AI_3',N.float32),
        ('AI_4',N.float32),
        ('AI_5',N.float32),
        ('AI_6',N.float32),
        ('AI_7',N.float32),
        ('DI_0',N.uint8),
        ('DI_1',N.uint8),
        ('DI_2',N.uint8),
        ('DI_3',N.uint8),
        ('DI_4',N.uint8),
        ('DI_5',N.uint8),
        ('DI_6',N.uint8),
        ('DI_7',N.uint8),
        ('CT_0',N.uint32),
        ('CT_1',N.uint32)
    ]
    EVENT_TYPE_STRING='DAQ_MULTI_CHANNEL_INPUT'
    EVENT_TYPE_ID=EventConstants.DAQ_MULTI_CHANNEL_INPUT_EVENT
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING
    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self, *args, **kwargs):
        """

        :rtype : object
        :param args:
        :param kwargs:
        """
        DeviceEvent.__init__(self, *args, **kwargs)


class DAQSingleChannelInputEvent(DeviceEvent):
    _newDataTypes = [
        ('channel_name',N.str,8),
        ('float_value',N.float32),
        ('int_value',N.uint32)
        ]

    EVENT_TYPE_STRING='DAQ_SINGLE_CHANNEL_INPUT'
    EVENT_TYPE_ID=EventConstants.DAQ_SINGLE_CHANNEL_INPUT_EVENT
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING
    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self, *args, **kwargs):
        """

        :rtype : object
        :param args:
        :param kwargs:
        """
        DeviceEvent.__init__(self, *args, **kwargs)

import HW