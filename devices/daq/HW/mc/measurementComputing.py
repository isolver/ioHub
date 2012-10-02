"""
ioHub
.. file: ioHub/devices/eyeTrackerInterface/HW/devices/daq/mc/measurementComputing.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson
"""

import numpy as N
import ioHub
from ioHub.devices import Device, Computer
			  
from ctypes import *

from constants import *

ctime=Computer.currentMsec
 
class MQ1616FS(Device):
    """
    """
    CATEGORY_LABEL="AD_CONVERTER"
    DEVICE_LABEL="ANALOG_OUTPUT_DEVICE"
    # <<<<<    
    lastPollTime=0.0        

    # >>> implementation specific private class attributes
    _DLL=None
    # <<<

    _newDataTypes=[('board_number','u1'),('channel_numbers','a32'),('gain','u1'),('offset','u4'),('options','u1')]
    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self,*args,**kwargs):
        """
        """
        deviceConfig=dict()
        deviceConfig['name']='daq'
        deviceConfig['device_class']='daq.mc.measurementComputing.MQ1616FS'
        deviceConfig['event_buffer_length']=2048
        deviceConfig['instance_code']='mc_daq_serial#'
        deviceConfig['board_number']=0
        deviceConfig['channel_numbers']='02'  
        deviceConfig['gain']=BIP10VOLTS
        deviceConfig['offset']=0.0
        deviceConfig['options']=DEFAULTOPTION
        
        if len(kwargs)>0:
                deviceConfig=kwargs['dconfig']
        

        deviceSettings={'instance_code': deviceConfig['instance_code'],
            'category_id':ioHub.devices.EventConstants.DEVICE_CATERGORIES[MQ1616FS.CATEGORY_LABEL],
            'type_id':ioHub.devices.EventConstants.DEVICE_TYPES[MQ1616FS.DEVICE_LABEL],
            'device_class':deviceConfig['device_class'],
            'name':deviceConfig['name'],
            'os_device_code':'OS_DEV_CODE_NOT_SET',
            'max_event_buffer_length':deviceConfig['event_buffer_length'],
            'board_number':0,
            'channel_numbers':'02' , 
            'gain':BIP10VOLTS,
            'offset':0.0,
            'options':DEFAULTOPTION
             }          
 
        Device.__init__(self,*args,**deviceSettings)


        self.board_number=deviceConfig['board_number']  
        self.channel_numbers=tuple(deviceConfig['channel_numbers']) 

        ichannels=[]        
        for c in self.channel_numbers:
            c=int(c)
            ichannels.append(c)
        self.channel_numbers=ichannels
        
        ioHub.print2err('ichannels:',ichannels)
        
        self.gain=deviceConfig['gain']  
        self.offset=deviceConfig['offset']  
        self.options=deviceConfig['options']
        
  
        MQ1616FS._DLL = windll.LoadLibrary("cbw32.dll")
        ioHub.print2err("DLL: ",MQ1616FS._DLL)

       # Initiate error handling
       # Parameters: 
       #    PRINTALL :all warnings and errors encountered will be printed
       #    DONTSTOP :program will continue even if error occurs.
       #              Note that STOPALL and STOPFATAL are only effective in 
       #              Windows applications, not Console applications. 

        self._DLL.cbErrHandling (c_int(PRINTALL), c_int(DONTSTOP));

        ioHub.print2err("Init done")

        

    def _poll(self,channel,*args,**kwargs):
        #/*Parameters:
        #BoardNum    :number used by CB.CFG to describe this board
        #Chan        :input channel number
        #Gain        :gain for the board in BoardNum
        #DataValue   :value collected from Chan */
        dataValue = c_float(0)
        udStat = c_int(NOERRORS)
        chan=c_int(channel)
        
        udStat = self._DLL.cbVIn (self.board_number, chan, self.gain, byref(dataValue), self.options);
        if udStat == NOERRORS:
            print "%d %f %f"%(channel, dataValue.value,ctime())
        else:
            print "ERROR: ", udStat,dataValue ,dataValue.value

    
if __name__ == "__main__":
    import time
    
    daq=MQ1616FS()

   

    tstart=ctime()

    while ctime()-tstart<10000:
        daq._poll(0)
        daq._poll(2)
