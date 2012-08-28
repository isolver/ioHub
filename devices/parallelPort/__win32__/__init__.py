"""
ioHub Python Module

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""

import os

os.environ['PATH'] = os.environ['PATH'] + ';' + os.path.abspath(os.path.dirname(__file__))
import ioHub
import time
from ctypes import windll,c_ushort,c_ubyte
import binascii
io=windll.io
PortOut=io.PortOut
PortIn=io.PortIn
from collections import deque
from ... import Device, Computer
currentMsec=Computer.currentMsec
import numpy as N

# note real starting address of MY pCIx card is 0xEF00 = 61184
# and I have put that into the io.ini file in this directory.    

class ParallelPortWin32(object):
    def __init__(self,*args,**kwargs):
        self.base_address=kwargs['base_address']
        self.address_offset=kwargs['address_offset']

        self.lastReadTime=None
        self.lastReadValue=None

    def read(self):
        return PortIn(self.base_address)
        
    def write(self, word):
        PortOut(self.base_address,word)
        
    def _poll(self):
        currentTime=int(currentMsec())
        currentValue=self.read()
        
        if currentValue == self.lastReadValue:
            pass
        else:    
            from .. import ParallelPortEvent
            
            print 'PPort event VALUES:',currentValue, self.lastReadValue
            ci=0
            lrv=self.lastReadValue
            if self.lastReadTime is not None:
                ci=currentTime-self.lastReadTime
            else:
                lrv=0
                
            ppe= ParallelPortEvent(experiment_id=0,session_id=0,event_id=Computer.getNextEventID(),event_type=ioHub.EVENT_TYPES['PARALLEL_PORT_INPUT'],
                                    device_type=ioHub.DEVICE_TYPE_LABEL['PARALLEL_PORT_DEVICE'],
                                    device_instance_code=self.instance_code,device_time=currentTime,
                                    logged_time=currentTime,hub_time=currentTime,confidence_interval=ci,
                                    delay=0.025,base_address=self.base_address,address_offset=self.address_offset,current_value=currentValue,
                                    last_value=lrv)

            self.I_nativeEventBuffer.append(ppe)

        self.lastReadTime=currentTime
        self.lastReadValue=currentValue

    @staticmethod    
    def _getIOHubEventObject(event,device_instance_code):
        return event # already a ParallelPort Event
