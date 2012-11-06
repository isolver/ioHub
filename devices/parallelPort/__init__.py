"""
ioHub Python Module

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""


import binascii
from .. import Computer,Device,EventConstants
import numpy as N

currentSec=Computer.currentSec

#----------------------------

if Computer.system == 'Windows':
    global ParallelPort
    from __win32__ import ParallelPortWin32
    
    class ParallelPort(Device,ParallelPortWin32):
        _newDataTypes=[('base_address',N.uint32),]
        CATEGORY_LABEL='DIGITAL_IO'
        DEVICE_LABEL='PARALLEL_PORT_DEVICE'
        __slots__=[e[0] for e in _newDataTypes]
        def __init__(self,*args,**kwargs):
            """
            
            :rtype : ParallelPort
            :param args: 
            :param kwargs: 
            """
            deviceConfig=kwargs['dconfig']
            deviceSettings={
                'category_id':EventConstants.DEVICE_CATERGORIES[ParallelPort.CATEGORY_LABEL],
                'type_id':EventConstants.DEVICE_TYPES[ParallelPort.DEVICE_LABEL],
                'device_class':ParallelPort.__name__,
                'name':deviceConfig['name'],
                'base_address':deviceConfig['base_address'],
                'os_device_code':'OS_DEV_CODE_NOT_SET',
                'max_event_buffer_length':deviceConfig['event_buffer_length'],
                '_isReportingEvents':deviceConfig.get('auto_report_events',True)
                }          
            Device.__init__(self,*args,**deviceSettings)
            ParallelPortWin32.__init__(self,*args,**deviceSettings)

        def byte2hex(self, v):
            """
            
            :rtype : object
            :param v: 
            :return:
            """
            return "0x%s" % (binascii.b2a_hex(v).upper())

else:
    print "Parallel Port is not implemented for your OS yet"
    
############# OS independent TTL Event classes ####################

from .. import DeviceEvent

class ParallelPortEvent(DeviceEvent):
    _newDataTypes = [('base_address',N.uint32),('current_value',N.uint8),('last_value', N.uint8)]
    EVENT_TYPE_STRING='TTL_INPUT'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING
    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self, *args, **kwargs):
        """
        
        :rtype : object
        :param args: 
        :param kwargs: 
        """
        DeviceEvent.__init__(self, *args, **kwargs)
