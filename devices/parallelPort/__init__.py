"""
ioHub Python Module

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""


import binascii
from .. import computer,Device
import numpy as N
currentMsec=computer.currentMsec
import ioHub

#----------------------------

if computer.system == 'Windows':
    global ParallelPort
    from __win32__ import ParallelPortWin32
    
    class ParallelPort(Device,ParallelPortWin32):
        dataType = Device.dataType+[('base_address',N.uint32),('address_offset',N.uint32)]
        attributeNames=[e[0] for e in dataType]
        ndType=N.dtype(dataType)
        fieldCount=ndType.__len__()
        __slots__=attributeNames
        categoryTypeString='DIGITAL_IO'
        deviceTypeString='PARALLEL_PORT_DEVICE'
        def __init__(self,*args,**kwargs):
            deviceConfig=kwargs['dconfig']
            deviceSettings={'instance_code':deviceConfig['instance_code'],
                'category_id':ioHub.DEVICE_CATERGORY_ID_LABEL[ParallelPort.categoryTypeString],
                'type_id':ioHub.DEVICE_TYPE_LABEL[ParallelPort.deviceTypeString],
                'device_class':deviceConfig['device_class'],
                'user_label':deviceConfig['name'],
                'base_address':deviceConfig['base_address'],
                'address_offset':0,
                'os_device_code':'OS_DEV_CODE_NOT_SET',
                'max_event_buffer_length':deviceConfig['event_buffer_length']
                }          
            Device.__init__(self,**deviceSettings)
            ParallelPortWin32.__init__(self,**deviceSettings)
   
        def byte2hex(self,v):
            return "0x%s"%(binascii.b2a_hex(v).upper())

else:
    print "Parallel Port is not implemented for your OS yet"
    
############# OS independent TTL Event classes ####################

from .. import DeviceEvent

class ParallelPortEvent(DeviceEvent):
    dataType = DeviceEvent.dataType+[('base_address',N.uint32),('address_offset',N.uint32),
                                    ('current_value',N.uint8),('last_value', N.uint8)]
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames   
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)

 
		