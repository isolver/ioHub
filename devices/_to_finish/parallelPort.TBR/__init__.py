"""
ioHub Python Module

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""


import binascii
from .. import Computer,Device
from ioHub.constants import EventConstants, DeviceConstants
import numpy as N

currentSec=Computer.currentSec

#----------------------------

if Computer.system == 'Windows':
    global ParallelPort
    from __win32__ import ParallelPortWin32
    
    class ParallelPort(Device,ParallelPortWin32):
        _newDataTypes=[('base_address',N.uint32),]

        ALL_EVENT_CLASSES=[]

        DEVICE_TYPE_ID=DeviceConstants.PARALLEL_PORT
        DEVICE_TYPE_STRING=DeviceConstants.getName(DEVICE_TYPE_ID)
        __slots__=[e[0] for e in _newDataTypes]
        def __init__(self,*args,**kwargs):
            """
            
            :rtype : ParallelPort
            :param args: 
            :param kwargs: 
            """
            ParallelPort.ALL_EVENT_CLASSES=[ParallelPortEvent,]
            deviceConfig=kwargs['dconfig']
            deviceSettings={
                'type_id':self.DEVICE_TYPE_ID,
                'device_class':ParallelPort.__name__,
                'name':deviceConfig['name'],
                'monitor_event_types':deviceConfig.get('monitor_event_types',self.ALL_EVENT_CLASSES),
                'base_address':deviceConfig['base_address'],
                'max_event_buffer_length':deviceConfig['event_buffer_length'],
                '_isReportingEvents':deviceConfig.get('auto_report_events',True)
                }          
            Device.__init__(self,*args,**deviceSettings)
                        
            ParallelPortWin32.__init__(self,*args,**deviceSettings)
            self._startupConfiguration=deviceConfig



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
    PARENT_DEVICE=ParallelPort
    EVENT_TYPE_ID=EventConstants.PARALLEL_PORT_INPUT
    EVENT_TYPE_STRING=EventConstants.getName(EVENT_TYPE_ID)
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING
    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self, *args, **kwargs):
        """
        
        :rtype : object
        :param args: 
        :param kwargs: 
        """
        DeviceEvent.__init__(self, *args, **kwargs)
