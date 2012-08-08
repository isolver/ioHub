"""
ioHub Python Module

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""

from .. import Device,Computer
import ioHub
currentMsec=Computer.currentMsec
import numpy as N

class Display(Device):
    dataType = list(Device.dataType)
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames
    categoryTypeString='VISUAL_STIMULUS_PRESENTER'
    deviceTypeString='DISPLAY_DEVICE'
    def __init__(self,*args,**kwargs):
        deviceConfig=kwargs['dconfig']
        deviceSettings={'instance_code':deviceConfig['instance_code'],
            'category_id':ioHub.DEVICE_CATERGORY_ID_LABEL[Display.categoryTypeString],
            'type_id':ioHub.DEVICE_TYPE_LABEL[Display.deviceTypeString],
            'device_class':deviceConfig['device_class'],
            'user_label':deviceConfig['name'],
            'os_device_code':'OS_DEV_CODE_NOT_SET',
            'max_event_buffer_length':16
            }          
        Device.__init__(self,**deviceSettings)
    
    def _poll(self):
        pass
 
            
######### Display Events ###########