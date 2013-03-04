"""
ioHub
.. file: ioHub/devices/serialIO/__init__.py

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""
import ioHub
from ..import Computer,Device,DeviceEvent
from ioHub.constants import EventConstants, DeviceConstants, SerialConstants
import serial
import numpy as N

currentSec = Computer.currentSec

class SerialIO(Device):
    """
    The SerialIO class .........
    """
    ALL_EVENT_CLASSES=[]

    DEVICE_TYPE_ID=DeviceConstants.SERIAL
    DEVICE_TYPE_STRING=DeviceConstants.getName(DEVICE_TYPE_ID)

    _newDataTypes = [('port', N.uint8),('baud_rate', N.uint16),('parity', N.str,1),('byte_size', N.uint8),('stop_bits', N.float16), ('byte_terminated_read',N.str,1), ('fixed_length_read_size',N.uint16) ]
    __slots__=[e[0] for e in _newDataTypes]+['_connection','_bytesReadBuffer']
    def __init__(self,*args,**kwargs):

        SerialIO.ALL_EVENT_CLASSES=[SerialInputEvent,]

        deviceConfig=kwargs['dconfig']

        deviceConfig['type_id']=deviceConfig.get('type_id',self.DEVICE_TYPE_ID)
        deviceConfig['device_class']=deviceConfig.get('device_class',SerialIO.__name__)
        deviceConfig['port']=deviceConfig.get('port',1)
        deviceConfig['baud_rate']=deviceConfig.get('baud_rate',9600)
        deviceConfig['parity'] = deviceConfig.get('parity', SerialConstants.PARITY_NONE)
        deviceConfig['byte_size'] = deviceConfig.get('byte_size',SerialConstants.EIGHTBITS)
        deviceConfig['stop_bits']=deviceConfig.get('stop_bits',SerialConstants.STOPBITS_ONE)
        deviceConfig['name']=deviceConfig.get('name','com%d'%(deviceConfig['port']))
        deviceConfig['monitor_event_types']=deviceConfig.get('monitor_event_types',SerialIO.ALL_EVENT_CLASSES)
        deviceConfig['os_device_code']=deviceConfig.get('os_device_code','OS_DEV_CODE_NOT_SET')
        deviceConfig['_isReportingEvents']=deviceConfig.get('auto_report_events',False)
        deviceConfig['max_event_buffer_length']=deviceConfig.get('event_buffer_length',512)
        deviceConfig['byte_terminated_read'] = deviceConfig.get('byte_terminated_read','\n')
        deviceConfig['fixed_length_read_size'] = deviceConfig.get('fixed_length_read_size',0)

        self._startupConfiguration=deviceConfig

        Device.__init__(self,*args,**deviceConfig)

        self._bytesReadBuffer='' # temp buffer to hold read data until either fixed_length_read_size is met
                                 # or byte_terminated_read is met
        self._connection=serial.Serial(baudrate=self.baud_rate,parity=self.parity,port=self.port-1,  #ports are indexed starting at 0
                                        bytesize=self.byte_size,stopbits=self.stop_bits)

    def write(self,bytes):
        return self._connection.write(bytes)

    def numberBytesWaitingToRead(self):
        return self._connection.inWaiting()

    def _poll(self):
        pollTime=currentSec()
        triggerEvent=False
        termFound=-1
        postReadTime=None

        bytesAvailableCount=self._connection.inWaiting()
        if bytesAvailableCount>0:
            if self.fixed_length_read_size>0:
                bytesLeftBeforeEvent=self.fixed_length_read_size-len(self._bytesReadBuffer)
                if bytesAvailableCount<bytesLeftBeforeEvent:
                    self._bytesReadBuffer+=self._connection.read(bytesAvailableCount)
                else:
                    self._bytesReadBuffer+=self._connection.read(bytesLeftBeforeEvent)
                    postReadTime=currentSec()
                    triggerEvent=True

            else:
                self._bytesReadBuffer+=self._connection.read(bytesAvailableCount)
                postReadTime=currentSec()
                termFound=self._bytesReadBuffer.find(self.byte_terminated_read)
                if termFound>=0:
                    triggerEvent=True

        if triggerEvent is True:
            eventData=''
            ci = postReadTime-pollTime
            io_time=postReadTime
            dev_time=0
            log_time=pollTime
            delay = (pollTime - self._lastPollTime) / 2.0 # assuming normal distribution, on average delay will be 1/2 the
                                                   # inter poll interval

            if self.fixed_length_read_size>0:
                #TODO Trigger event using full _bytesReadBuffer
                eventData=self._bytesReadBuffer
                self._bytesReadBuffer=''
                pass
            else:
                #TODO Trigger event using eventData
                eventData=self._bytesReadBuffer[0:termFound+1]
                self._bytesReadBuffer=self._bytesReadBuffer[termFound+1:]

            serialEvent=[
                0,                                      # experiment_id filled in by ioHub
                0,                                      # session_id filled in by ioHub
                Computer._getNextEventID(),             # unique event id
                SerialInputEvent.EVENT_TYPE_ID,         # id representation of event type
                dev_time,                               # device Time
                log_time,                               # logged time
                io_time,                                # time (i.e. ioHub Time)
                ci,                                     # confidence Interval
                delay,                                  # delay
                0,                                      #filter_id 0 by default
                self.port,
                len(eventData),
                eventData
                ]
            self._addNativeEventToBuffer(serialEvent)

        self._lastPollTime=pollTime
        return True


    def _getIOHubEventObject(self,event):
        return event # already a SerialInput Event

    def __del__(self):
        self._connection._close()
        self.clearEvents()

class SerialInputEvent(DeviceEvent):
    """
    The MouseEvent is an abstract class that is the parent of all MouseEvent types
    that are supported in the ioHub. Mouse position is mapped to the coordinate space
    defined in the ioHub configuration file for the Display.
    """

    MAX_BYTES_PER_EVENT=256

    PARENT_DEVICE = SerialIO
    EVENT_TYPE_STRING = 'SERIAL_INPUT'
    EVENT_TYPE_ID = EventConstants.SERIAL_INPUT
    IOHUB_DATA_TABLE = EVENT_TYPE_STRING

    _newDataTypes = [
        ('port', N.uint8),
        ('bytes_read', N.uint16),
        ('bytes', N.str_,MAX_BYTES_PER_EVENT)
    ]
    __slots__ = [e[0] for e in _newDataTypes]

    def __init__(self, *args, **kwargs):
        DeviceEvent.__init__(self, *args, **kwargs)