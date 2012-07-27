"""
ioHub.devices.parallelPort module __init__

Part of the Eye Movement Research Toolkit
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
        defaultValueDict=dict(Device.defaultValueDict,**{'base_address':888,'address_offset':0,'category_id':ioHub.DEVICE_CATERGORY_ID_LABEL['DIGITAL_IO'],'type_id':ioHub.DEVICE_TYPE_LABEL['PARALLEL_PORT_DEVICE'],'max_event_buffer_length':1024}) #base_address 0x378 = 888 dec
        ndType=N.dtype(dataType)
        fieldCount=ndType.__len__()
        __slots__=attributeNames
        def __init__(self,*args,**kwargs):
            dargs=dict(ParallelPort.defaultValueDict)
            for k,v in kwargs.iteritems():
                if k in dargs:
                    dargs[k]=v
             
            Device.__init__(self,**dargs)
            ParallelPortWin32.__init__(self,**dargs)           
            print "ParallelPort class set as ",self.__class__.__name__
   
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

 
		