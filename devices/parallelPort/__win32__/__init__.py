"""
ioHub Python Module

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""

import os
import ioHub

def _nofunc():
    pass

_HERE= ioHub.module_directory(_nofunc)
if _HERE not in os.environ['PATH']:
    os.environ['PATH'] = os.environ['PATH'] + ';' +_HERE
    #ioHub.print2err("os.environ['PATH']",os.environ['PATH'])

from ctypes import windll,c_short
io=windll.inpout32
PortOut=io.Out32
PortIn=io.Inp32

from ... import Computer
currentSec=Computer.currentSec

class ParallelPortWin32(object):
    def __init__(self,*args,**kwargs):
        """
        
        :rtype : object
        :param args: 
        :param kwargs: 
        """
        self.base_address=c_short(kwargs['base_address'])
        #ioHub.print2err(' self.base_address', self.base_address)
        self.lastReadTime=None
        self.lastReadValue=None


    def read(self):
        """
        
        :rtype : object
        :return:
        """
        return c_short(PortIn(self.base_address)).value

    def write(self, word):
        """
        
        :type word: object
        :param word: 
        """
        PortOut(self.base_address, c_short(word))

    def isDriverOpen(self):
        r=io.IsInpOutDriverOpen()
        return bool(r)

    def isOS64bit(self):
        r= io.IsXP64Bit()
        return bool(r)
        
    def _poll(self):
        """
        
        :rtype : object
        """
        currentTime=currentSec()
        currentValue=self.read()
        
        if currentValue == self.lastReadValue:
            pass
        else:
            from .. import ParallelPortEvent
            #ioHub.print2err('pport event c_short(PortIn(self.base_address)).value:',c_short(PortIn(self.base_address)).value)

            ci=0.0
            lrv=self.lastReadValue
            if self.lastReadTime is not None:
                ci=currentTime-self.lastReadTime
            else:
                lrv=0

            pdelay=ci/2.0 # on average, actual port state change will be the confidence interval / 2

            device_time=currentTime
            logged_time=currentTime
            iohub_time=currentTime-int(pdelay)

            ppe= [0,0,Computer.getNextEventID(),ParallelPortEvent.EVENT_TYPE_ID,self.instance_code,
                  device_time, logged_time, iohub_time, ci,pdelay,self.base_address,currentValue,lrv]

            self._addNativeEventToBuffer(ppe)

        self.lastReadTime=currentTime
        self.lastReadValue=currentValue

    @staticmethod    
    def _getIOHubEventObject(event,device_instance_code):
        return event # already a ParallelPort Event
