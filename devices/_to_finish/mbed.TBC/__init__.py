__author__ = 'Sol'

import serial
import numpy as N
from .. import Computer, Device, DeviceEvent, ioDeviceError
from ioHub.constants import DeviceConstants,EventConstants,SerialConstants
from ioHub import  print2err

class MBED1768(Device):
    ALL_EVENT_CLASSES=[]

    # Supported mbed commands

    # Onboard LED:
    # LED [id] [on/off/toggle] [duration] [repeat_interval]
    #
    # DO [id] [on/off/toggle] [duration] [repeat_interval]
    #
    # DI [id] [read_frequency]
    #
    # AI [id] [read_frequency]
    #
    # AO [value1] [value2] [value1_duration] [value_2_duration]

    DEVICE_TYPE_ID=DeviceConstants.MBED
    DEVICE_TYPE_STRING=DeviceConstants.getName(DEVICE_TYPE_ID)
    _newDataTypes = [('port', N.uint8),('baud_rate', N.uint16),('parity', N.str,1),('byte_size', N.uint8),('stop_bits', N.float16) ]
    __slots__=[e[0] for e in _newDataTypes]+['_connection','_bytesReadBuffer','_streaming']
    def __init__(self, *args,**kwargs):
        self._startupConfiguration=kwargs['dconfig']
        port=self._startupConfiguration.get('port',15)
        self._startupConfiguration['port']=port
        self._streaming=False
        baud_rate = self._startupConfiguration.get('baud_rate', 921600)
        self._startupConfiguration['baud_rate'] = baud_rate

        parity = self._startupConfiguration.get('parity', SerialConstants.PARITY_NONE)
        self._startupConfiguration['parity'] = parity

        byte_size = self._startupConfiguration.get('byte_size', SerialConstants.EIGHTBITS)
        self._startupConfiguration['byte_size'] = byte_size

        stop_bits = self._startupConfiguration.get('stop_bits', SerialConstants.STOPBITS_ONE)
        self._startupConfiguration['stop_bits'] = stop_bits

        type_id=self._startupConfiguration.get('type_id',self.DEVICE_TYPE_ID)
        self._startupConfiguration['type_id']=type_id

        device_class=self._startupConfiguration.get('device_class',self.__class__.__name__)
        self._startupConfiguration['device_class']=device_class

        name=self._startupConfiguration.get('name',self.__class__.__name__)
        self._startupConfiguration['name']=name

        auto_report_events=self._startupConfiguration.get('auto_report_events',True)
        self._startupConfiguration['_isReportingEvents']=auto_report_events
        self._isReportingEvents=auto_report_events

        max_event_buffer_length=self._startupConfiguration.get('event_buffer_length',64)
        self._startupConfiguration['max_event_buffer_length']=max_event_buffer_length

        monitor_event_types=self._startupConfiguration.get('monitor_event_types',self.ALL_EVENT_CLASSES)
        self._startupConfiguration['monitor_event_types']=monitor_event_types

        Device.__init__(self,*args,**self._startupConfiguration)

        self._bytesReadBuffer='' # temp buffer to hold read data until either fixed_length_read_size is met
                                 # or byte_terminated_read is met
        self._connection=serial.Serial(baudrate=self.baud_rate,parity=self.parity,port=self.port-1,  #ports are indexed starting at 0
                                        bytesize=self.byte_size,stopbits=self.stop_bits)

    def _poll(self):
        try:
            if self._streaming is True:
                t=Computer.getTime()
                cmd1 = "AI R "
                self._connection.write(cmd1)

                sampleCount=self._connection.readline()
               # print2err("SAMPLE COUNT: ",sampleCount)
                sampleCount=sampleCount.split(' ')
               # print2err("SAMPLE COUNT: ",sampleCount)
                sampleCount=int( sampleCount[1])
                print2err("SAMPLE COUNT: ",sampleCount)

                for i in xrange(sampleCount):
                    sample_scan=self._connection.readline()
                    print2err(sample_scan)
                    tokens=sample_scan.strip(' \n').split()
                    print2err(tokens)
                    #print2err('---')

                t2=Computer.getTime()
            return True
        except:
            import ioHub
            ioHub.printExceptionDetailsToStdErr()

    def _getIOHubEventObject(self,event):
        return event

    def setInputLinesToMonitor(self, analog, digital):
        # used to set which analog inputs and digital input lines should be read
        # and monitored for state changes.
        pass

    def setOutputPins(self, analogOutputValue=None, digitalOutputPins=None, digitalOutputStates=None):
        # used to set the analog out channel value, and / or a set of digital outputs to high / low based on
        # digitalOutputStates.
        pass

    def setLEDStates(self,led1=None,led2=None,led3=None,led4=None):
        # used to set the state of the 4 on board leds.
        # each led can have the following values:
        #    - None: do not change the led
        #    - True or false : set the LED to On or Off and leave it in that state
        #    - [state, blink_cycle_time, repeat]
        #           - blink_cycle_time = how long between the start of each blink of the led
        #           - repeat = should the blink repeat. 0 = no, +n = number of times to blink, -1 = keep blinking
        # command is sent in format:
        #   LED-S ncount ledid_a [1/0]_a .....  # command to have an LED (n) set to on (1) or off(0)
        #   LED-B n [1/0] [dur1] [dur2] [repeat]
        setLedList=[]
        blinkLedList=[]
        if isinstance(led1,(int,bool)):
            setLedList.append((0,led1))
        elif isinstance(led1,(tuple,list)) and len(led1) == 3:
            blinkLedList.append((0,led1[0],led1[1],led1[2]))

        if isinstance(led2, (int, bool)):
            setLedList.append((1, led2))
        elif isinstance(led2,(tuple,list)) and len(led2) == 3:
            blinkLedList.append((1,led2[0],led2[1],led2[2]))

        if isinstance(led3, (int, bool)):
            setLedList.append((2, led3))
        elif isinstance(led3,(tuple,list)) and len(led3) == 3:
            blinkLedList.append((2,led3[0],led3[1],led3[2]))

        if isinstance(led4, (int, bool)):
            setLedList.append((3, led4))
        elif isinstance(led4,(tuple,list)) and len(led4) == 3:
            blinkLedList.append((3,led4[0],led4[1],led4[2]))

        if len(setLedList)>0:
            cmd1="LED-S {0} ".format(len(setLedList))
            for l in setLedList:
                cmd1+="{0} {1} ".format(l[0],l[1])
            print2err(cmd1)
            self._connection.write(cmd1)
            self._connection.flush()

        if len(blinkLedList)>0:
            cmd2 = "LED-B {0} ".format(len(blinkLedList))
            for l in blinkLedList:
                cmd2 += "{0} {1} {2} {3} ".format(l[0], l[1], l[2], l[3])
            print2err(cmd2)
            self._connection.write(cmd2)
            self._connection.flush()

    def setAnalogOutputChannel(self,value = 1.0):
        """
        Value provided needs to be a float between 0.0 and 1.0; such that you are setting the proportion of
        the AO range to be used for the value set. The MBED can output 0 to 3.3 V, for providing a value of 0.0
        will map to an output of 0.0 volts. Specifying 1.0 will output 3.3 V
        :param value:
        :type value:
        :return:
        :rtype:
        """
        cmd2 = "AO W {0} ".format(value)
        self._connection.write(cmd2)
        self._connection.flush()

        # mbed is set to return the value set on the channel:

        aoValue=self._connection.readline()
        return aoValue


    def getAnalogOutputValue(self):
        cmd2 = "AO R\n"
        print2err(cmd2)
        self._connection.write(cmd2)
        self._connection.flush()

        # mbed is set to return the value set on the channel:

        aoValue = self._connection.readline()
        return aoValue

    def setDigitalPins(self,d1,d2,d3,d4,d5,d6,d7,d8):
        """
        :param d1: Maps to pin 8 on the MBEDrddwwdww
        :type d1: int, 0 or 1
        :param d2: Maps to pin 11 on the MBED
        :type d2: int, 0 or 1
        :param d3: Maps to pin 12 on the MBED
        :type d3: int, 0 or 1
        :param d4: Maps to pin 13 on the MBED
        :type d4: int, 0 or 1
        :param d5: Maps to pin 14 on the MBED
        :type d5: int, 0 or 1
        :param d6: Maps to pin 21 on the MBED
        :type d6: int, 0 or 1
        :param d7: Maps to pin 22 on the MBED
        :type d7: int, 0 or 1
        :param d8: Maps to pin 23 on the MBED
        :type d8: int, 0 or 1
        :return:
        :rtype:
        """

        cmd2 = "DO {0} {1} {2} {3} {4} {5} {6} {7}\n".format(d1,d2,d3,d4,d5,d6,d7,d8)

        print2err(cmd2)
        self._connection.write(cmd2)
        self._connection.flush()


    def getDigitalPins(self):
        """

        """

        cmd2 = "DI "

        print2err(cmd2)
        self._connection.write(cmd2)
        self._connection.flush()
        dioValue = self._connection.readline()
        return dioValue

    def enableEventReporting(self, enable):
        try:
            print2err("---------------------------------------------")
            print2err("DAQ.enableEventReporting: ", enable)
            current = self.isReportingEvents()
            if enable is False and current == enable:
                return current
            if enable is True and current is True and self._streaming is True:
                return True

            if Device.enableEventReporting(self, enable) is True:
                print2err("enabling streaming....")

                if self._streaming is False:
                    cmd1="AI S "
                    self._connection.write(cmd1)
                    self._connection.flush()

                    self._streaming = True
                    print2err("Streaming started...")

            else:
                #ioHub.print2err("disabling streaming....")
                if self._streaming is True:
                    self._streaming = False
                    cmd1="AI E "
                    self._connection.write(cmd1)
                    self._connection.flush()
                    print2err("---------------------------------------------")
        except:
            import ioHub
            ioHub.printExceptionDetailsToStdErr()

    def __del__(self):
        self._connection._close()
        self.clearEvents()
