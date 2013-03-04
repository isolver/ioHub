import ioHub
from ...import DAQDevice, DAMultiChannelInputEvent#, DASingleChannelInputEvent
from ....import Computer, EventConstants, DeviceConstants, ioDeviceError
import pylabjack
import numpy as N

class DAQ(DAQDevice):
    """
    """
    NUM_CHANNELS=8
    CHANNEL_NUMBERS = range(NUM_CHANNELS)
    CHANNEL_OPTIONS = [0, 0, 0, 0, 0, 0, 0, 0]
    DAQ_CHANNEL_MAPPING = dict()
    DAQ_CHANNEL_MAPPING['AIN0'] = 0
    DAQ_CHANNEL_MAPPING['AIN1'] = 1
    DAQ_CHANNEL_MAPPING['AIN2'] = 2
    DAQ_CHANNEL_MAPPING['AIN3'] = 3
    DAQ_CHANNEL_MAPPING['AIN4'] = 4
    DAQ_CHANNEL_MAPPING['AIN5'] = 5
    DAQ_CHANNEL_MAPPING['AIN6'] = 6
    DAQ_CHANNEL_MAPPING['AIN7'] = 7


    DAQ_CONFIG_OPTIONS = dict()
    DAQ_CONFIG_OPTIONS['DEFAULTOPTION'] = 0

    DAQ_MODEL_OPTIONS = dict()
    DAQ_MODEL_OPTIONS['U6'] = 'U6'

    ANALOG_TO_DIGITAL_RANGE=2**16
    ANALOG_RANGE=22.0
    ALL_EVENT_CLASSES = []
    # <<<<<
    lastPollTime = 0.0

    # >>> implementation specific private class attributes
    _DLL = None
    # <<<

    DEVICE_MODEL_ID=2
    DEVICE_TYPE_ID = DeviceConstants.DAQ
    DEVICE_TYPE_STRING = DeviceConstants.getName(DEVICE_TYPE_ID)

    _newDataTypes = [('board_id', N.uint8), ('daq_model',N.str_,32), ('resolution_index',N.uint8), ('settling_factor',N.uint8),
                     ('channel_sample_rate', N.uint16)]

    __slots__=[e[0] for e in _newDataTypes]+['_device','_scanBuffer','_sampleCount','_missedCount','_lastStartStreamingTimePre','_lastStartStreamingTimePost','_streaming','_feedbackArguments']
    def __init__(self, *args, **kwargs):
        """
        """
        deviceConfig = kwargs['dconfig']

        self._startupConfiguration = deviceConfig

        DAQ.ALL_EVENT_CLASSES = [DAMultiChannelInputEvent, ]

        deviceConfig['name'] = deviceConfig.get('name', 'daq')
        deviceConfig['device_class'] = DAQ.__name__
        deviceConfig['monitor_event_types'] = deviceConfig.get('monitor_event_types', DAQ.ALL_EVENT_CLASSES)
        deviceConfig['max_event_buffer_length'] = deviceConfig.get('event_buffer_length', 1024)
        deviceConfig['type_id'] = self.DEVICE_TYPE_ID
        deviceConfig['_isReportingEvents'] = deviceConfig.get('auto_report_events', False)
        deviceConfig['os_device_code'] = 'OS_DEV_CODE_NOT_SET'

        deviceConfig['board_id'] = deviceConfig.get('board_id', 0)
        deviceConfig['daq_model']=deviceConfig.get('daq_model','U6')
        deviceConfig['resolution_index'] = deviceConfig.get('resolution_index', 0)
        deviceConfig['settling_factor'] = deviceConfig.get('settling_factor', 0)
        deviceConfig['channel_sample_rate']=deviceConfig.get('channel_sample_rate',1000)

        DAQDevice.__init__(self, *args, **deviceConfig)

        self._device=None

        if self.daq_model == 'U6':
            from pylabjack import u6 # Import the u6 class
            self._device = u6.U6()
            self._device.getCalibrationData()

        self._lastStartStreamingTimePre=0.0
        self._lastStartStreamingTimePost=0.0
        self._missedCount=0
        self._scanBuffer=[0] * self.NUM_CHANNELS
        self._streaming=False




    def enableEventReporting(self, enable):
        try:
            #ioHub.print2err("---------------------------------------------")
            #ioHub.print2err("DAQ.enableEventReporting: ", enable)
            current = self.isReportingEvents()
            if enable is False and current == enable:
                return current
            if enable is True and current is True and self._streaming is True:
                return True

            if DAQDevice.enableEventReporting(self, enable) is True:
                #ioHub.print2err("enabling streaming....")

                self._missedCount=0
                self._sampleCount=0
                self._lastStartStreamingTimePre = 0.0
                self._lastStartStreamingTimePost = 0.0
                self._scanBuffer=[0]*self.NUM_CHANNELS

                #self._lastStartStreamingTimePre=Computer.getTime()
                #self._device.streamConfig(NumChannels=self.NUM_CHANNELS, ChannelNumbers=self.CHANNEL_NUMBERS,
                #    ChannelOptions=self.CHANNEL_OPTIONS, SettlingFactor=self.settling_factor,
                #    ResolutionIndex=self.resolution_index, ScanFrequency=self.channel_sample_rate)
                FIOEIOAnalog = ( 2 ** self.NUM_CHANNELS ) - 1;
                fios = FIOEIOAnalog & (0xFF)
                eios = FIOEIOAnalog/256

                from pylabjack import u6
                self._device.getFeedback(u6.PortDirWrite(Direction = [0, 0, 0], WriteMask = [0, 0, 15]))


                self._feedbackArguments = []

                self._feedbackArguments.append(u6.DAC0_8(Value = 125))
                self._feedbackArguments.append(u6.PortStateRead())

                gain_index=0
                differential=False
                for i in range(self.NUM_CHANNELS):
                    self._feedbackArguments.append( u6.AIN24(i,self.resolution_index, gain_index, self.settling_factor, differential) )

                #ioHub.print2err(self.NUM_CHANNELS, "ChannelNumbers=",self.CHANNEL_NUMBERS,
                #    "ChannelOptions=",self.CHANNEL_OPTIONS, "SettlingFactor=",self.settling_factor,
                #    "ResolutionIndex=",self.resolution_index, "ScanFrequency=",self.channel_sample_rate)

                #self._lastStartStreamingTimePost=Computer.getTime()

                if self._streaming is False:
                    #self._device.streamStart()
                    self._streaming=True
                    #ioHub.print2err("Streaming started...")

            else:
                #ioHub.print2err("disabling streaming....")
                if self._streaming is True:
                    self._streaming=False
                    #self._device.streamStop()
            #ioHub.print2err("---------------------------------------------")
        except:
            ioHub.printExceptionDetailsToStdErr()

    def _poll(self):
        try:
            pollTime=Computer.currentSec()
            rend=pollTime
            if self.isReportingEvents() is True and self._streaming is True:
                rstart=Computer.currentTime()
                results = self._device.getFeedback(self._feedbackArguments )
                rend=Computer.currentTime()
                ci=rend-rstart
                event =[
                
                    0, # exp id
                    0, # session id
                    Computer._getNextEventID(), # event id
                    DAMultiChannelInputEvent.EVENT_TYPE_ID, # event type
                    0, # device time
                    pollTime, # logged time
                    rend, # hub time
                    ci, # confidence interval
                    rend-self._lastPollTime, # delay
                    0, # filter_id
                    self.DEVICE_MODEL_ID
                    ]
                for j in range(self.NUM_CHANNELS):
                    ain = self._device.binaryToCalibratedAnalogVoltage(0, results[ 2 + j ])
                    event.append(ain)
                self._addNativeEventToBuffer(event)
        except:
            ioHub.printExceptionDetailsToStdErr()
        self._lastPollTime=rend
        return True

                #self._device.nextStreamData(convert=False)


#                if ljData is not None:
#                    dataReadTime=Computer.currentSec()
#
#                    if ljData['errors'] != 0:
#                        print "Error: %s ; " % ljData['errors'], Computer.getTime()
#
#                    if ljData['numPackets'] != self._device.packetsPerRequest:
#                        print "----- UNDERFLOW : %s : " % ljData['numPackets'], ()
#
#                    if ljData['missed'] != 0:
#                        self._missedCount += ljData['missed']
#                        print "+++ Missed ", ljData['missed']
#
#                    receivedSamples=[]
#                    eventSamples=[]
#                    analogChannelName='AIN{0}'
#                    minSampleLength=100000000
#                    for k in xrange(8):
#                        channelName=analogChannelName.format(k)
#                        nSamples=len(ljData[channelName])
#                        if  nSamples<minSampleLength:
#                            minSampleLength=nSamples
#                        receivedSamples.append(ljData[channelName])
#
#                    # put extra samples in buffer for use in next scan
#                    for k in xrange(8):
#                        eventSamples.append(self._scanBuffer[k])
#                        eventSamples[k].extend(receivedSamples[k][:minSampleLength])
#                        self._scanBuffer[k]=receivedSamples[k][minSampleLength:]
#                        #print "CHANNEL {0}: EVENT LENGTH: {1}".format(k,len(eventSamples[k]))
#
#                    # createEvents
#                    events=[]
#                    nsamples=len(eventSamples[0])
#                    for si in xrange(nsamples):
#                        time = (1000.0/self.channel_sample_rate)*self._sampleCount+self._lastStartStreamingTimePost
#                        self._sampleCount+=1
#                        event =[
#                            0, # exp id
#                            0, # session id
#                            Computer._getNextEventID(), # event id
#                            DAMultiChannelInputEvent.EVENT_TYPE_ID, # event type
#                            0, # device time
#                            pollTime, # logged time
#                            time, # hub time
#                            self._lastStartStreamingTimePost - self._lastStartStreamingTimePre, # confidence interval
#                            dataReadTime - time, # delay
#                            0 # filter_id
#                            ]
#                        for k in xrange(8):
#                            event.append(eventSamples[k][si])
#
#
#                        self._addNativeEventToBuffer(event)
#        except:
#            ioHub.printExceptionDetailsToStdErr()
#        pollCompetedTime=Computer.currentSec()
#        return True

    def _getIOHubEventObject(self,event):
        return event # already a Gamepad Event




    def _close(self):
        #self._device.streamStop()
        self._device.close()


    def __del__(self):
        try:
            self._close()
        except:
            pass