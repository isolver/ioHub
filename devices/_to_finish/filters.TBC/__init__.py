# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 03:55:27 2012

@author: Sol
"""
import ioHub
import ioHub.devices
from ioHub.devices import Device, DeviceEvent,EventConstants, DeviceConstants, Computer
import collections
from copy import deepcopy

class EventFilter(Device):
    __slots__=['_internalEventQueDict','_inputEventFilterParameters','_outputEventFilterParameters','_outputEventFilterIDs']

    DEVICE_TYPE_ID=DeviceConstants.FILTER
    DEVICE_TYPE_STRING=DeviceConstants.getName(DEVICE_TYPE_ID)
    def __init__(self,*args,**kwargs):
        deviceConfig=kwargs['dconfig']

        deviceConfig['type_id']=deviceConfig.get('type_id',self.DEVICE_TYPE_ID)
        deviceConfig['device_class']=deviceConfig.get('device_class',EventFilter.__name__)
        deviceConfig['name']=deviceConfig.get('name',EventFilter.__name__.lower())
        deviceConfig['monitor_event_types']=deviceConfig.get('monitor_event_types',self.ALL_EVENT_CLASSES)
        deviceConfig['os_device_code']=deviceConfig.get('os_device_code','eventFilter')
        deviceConfig['_isReportingEvents']=deviceConfig.get('auto_report_events',True)
        deviceConfig['max_event_buffer_length']=deviceConfig.get('event_buffer_length',512)

        self._internalEventQueDict={}
        self._outputEventFilterIDs={}

        self._inputEventFilterParameters={}
        temp=deviceConfig.get('input_events',[])
        for l in temp:
            for k,v in l.iteritems():
                self._inputEventFilterParameters[k]=v

        for input_event_class, input_event_filter_params in self._inputEventFilterParameters.iteritems():
            window_size=input_event_filter_params.get('window_size',0)
            if window_size>0:
                self._internalEventQueDict[input_event_class]=collections.deque(maxlen=window_size)


        self._outputEventFilterParameters={}
        temp=deviceConfig.get('output_events',[])
        for l in temp:
            for k,v in l.iteritems():
                self._outputEventFilterParameters[k]=v

        for output_event_class, output_event_filter_params in self._outputEventFilterParameters.iteritems():
            filter_id=output_event_filter_params.get('filter_id',None)
            if filter_id:
                self._outputEventFilterIDs[output_event_class]=filter_id
            else:
                raise ioHub.devices.ioDeviceError('Filter Devices must provide an output event filter_id for pre-existsing each output event type',output_event_class,self.__class__.__name__)


        self._startupConfiguration=deviceConfig

        Device.__init__(self,*args,**deviceConfig)


    def _applyFilter(self,eventToFilter):
        #no op filter
        #
        ecls=EventConstants.getClass(eventToFilter[DeviceEvent.EVENT_TYPE_ID_INDEX]).__name__
        if ecls in self._internalEventQueDict:
            self._internalEventQueDict[ecls].append(eventToFilter)

            if self._internalEventQueDict[ecls].maxlen == len(self._internalEventQueDict[ecls]):
                self._applyQueFilter(ecls, self._internalEventQueDict[ecls],eventToFilter)
                return (self._internalEventQueDict[ecls][0],)

        elif eventToFilter:
            eventToFilter=self._applySolitaryFilter(ecls,eventToFilter)
            filteredEvent=eventToFilter
            return (filteredEvent,)

        # return no events to send out
        return ()

    def _applyQueFilter(self,eventToFilterClass,eventToFilterQue,eventToFilter):
        # apply filter to contents of window
        #
        # ......
        #
        pass

    def _applySolitaryFilter(self,eventToFilterClass,eventToFilter):
        # apply filter to scalar event
        #
        # ......
        #
        return eventToFilter

    def _handleEvent(self,e):
        notifiedTime=Computer.currentTime()
        eventToFilter=deepcopy(e)
        e=None
        eventToFilter[DeviceEvent.EVENT_LOGGED_TIME_INDEX]=notifiedTime

        filteredEvents=self._applyFilter(eventToFilter)

        sendTime=Computer.currentTime()
        for evt in filteredEvents:
            timeToAdd=sendTime-evt[DeviceEvent.EVENT_LOGGED_TIME_INDEX]
            evt[DeviceEvent.EVENT_DELAY_INDEX]=evt[DeviceEvent.EVENT_DELAY_INDEX]+timeToAdd
            evt[DeviceEvent.EVENT_HUB_TIME_INDEX]=evt[DeviceEvent.EVENT_HUB_TIME_INDEX]+timeToAdd
            evt[DeviceEvent.EVENT_ID_INDEX]=Computer._getNextEventID()
            cls_name=EventConstants.getClass(evt[DeviceEvent.EVENT_TYPE_ID_INDEX]).__name__
            #ioHub.print2err('>>>> evt[DeviceEvent.EVENT_ID_INDEX]:',evt[DeviceEvent.EVENT_ID_INDEX],EventConstants.getClass(evt[DeviceEvent.EVENT_ID_INDEX]))
            evt[DeviceEvent.EVENT_FILTER_ID_INDEX]=self._outputEventFilterIDs[cls_name]
            #ioHub.print2err('>>>> evt[DeviceEvent.EVENT_FILTER_ID_INDEX]: ',evt[DeviceEvent.EVENT_FILTER_ID_INDEX])
            Device._handleEvent(self,evt)
            self._addNativeEventToBuffer(evt)

    def _getIOHubEventObject(self,evt):
        """

                :param evt:
                :type evt:
                :return:
                :rtype:
                """
        return evt


#
## Class for generic Filter events. Contains standard Device Event fields, as well as a Python object for data
#

class GenericFilterEvent(DeviceEvent):
    EVENT_TYPE_STRING='FILTER_EVENT'
    EVENT_TYPE_ID=EventConstants.FILTER_EVENT
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING

    __slots__=['_filterEventDataDictionary']
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)
        self._filterEventDataDictionary={}

#####################################################################################################################
class StampeFilter(EventFilter):

    ALL_EVENT_CLASSES=[]
    DEVICE_TYPE_ID=DeviceConstants.STAMPE_FILTER
    DEVICE_TYPE_STRING=DeviceConstants.getName(DEVICE_TYPE_ID)

    def __init__(self,*arg,**kwargs):
        """

        :param arg:
        :type arg:
        :param kwargs:
        :type kwargs:
        """

        deviceConfig = kwargs['dconfig']

        deviceConfig['type_id'] = deviceConfig.get('type_id', self.DEVICE_TYPE_ID)
        deviceConfig['device_class'] = deviceConfig.get('device_class', StampeFilter.__name__)
        deviceConfig['name'] = deviceConfig.get('name', StampeFilter.__name__.lower())
        deviceConfig['monitor_event_types'] = deviceConfig.get('monitor_event_types', self.ALL_EVENT_CLASSES)
        deviceConfig['os_device_code'] = deviceConfig.get('os_device_code', 'eventFilter')
        deviceConfig['_isReportingEvents'] = deviceConfig.get('auto_report_events', True)
        deviceConfig['max_event_buffer_length'] = deviceConfig.get('event_buffer_length', 512)


        EventFilter.__init__(self,*arg,**kwargs )

        self._startupConfiguration = deviceConfig

        tmp=[]
        for class_name in self._outputEventFilterIDs.keys():
            EventKlass = getattr(ioHub.devices,class_name)
            tmp.append(EventKlass)
        StampeFilter.ALL_EVENT_CLASSES=tmp
        self.monitor_event_types=tmp


    def _applyQueFilter(self,eventToFilterClass,eventsToFilterQue,eventToFilter):
        # apply filter to contents of window
        #
        # ......
        #
        """

        Apply filter to contents of window

        :param eventToFilterClass:
        :type eventToFilterClass:
        :param eventToFilterQue:
        :type eventToFilterQue:
        :param eventToFilter:
        :type eventToFilter:
        """
        filter_level=self._startupConfiguration.get('filter_level',2)

        que=eventsToFilterQue

        if filter_level==0:
            pass
        elif eventToFilterClass != 'MonocularEyeSample':
            pass
        else: # nust be monocular
            if filter_level>0:
                gx0=que[0][11] #gx
                gy0=que[0][12] #gx
                gx1 = que[1][11] #gx
                gy1 = que[1][12] #gx
                gx2 = que[2][11] #gx
                gy2 = que[2][12] #gx
                gx3 = que[3][11] #gx
                gy3 = que[3][12] #gx
                #ioHub.print2err(que[0][11],':',que[0][12],':',que[1][11],':',que[1][12],':',que[2][11],':',que[2][12],':',que[3][11],':',que[3][12])

                if gx0<gx1<gx2:
                    pass
                elif gx0>gx1>gx2:
                    pass
                else:
                     que[1][11]=(que[0][11]+que[2][11])/2.0

                if gy0<gy1<gy2:
                    pass
                elif gy0>gy1>gy2:
                    pass
                else:
                    que[1][12]=(que[0][12]+que[2][12])/2.0

            if filter_level==2:
                gx0=que[1][11] #gx
                gy0=que[1][12] #gx
                gx1 = que[2][11] #gx
                gy1 = que[2][12] #gx
                gx2 = que[3][11] #gx
                gy2 = que[3][12] #gx

                if gx0<gx1<gx2:
                    pass
                elif gx0>gx1>gx2:
                    pass
                else:
                    que[2][11]=(que[1][11]+que[3][11])/2.0

                if gy0<gy1<gy2:
                    pass
                elif gy0>gy1>gy2:
                    pass
                else:
                    que[2][12]=(que[1][12]+que[3][12])/2.0

                #ioHub.print2err(que[0][11],':',que[0][12],':',que[1][11],':',que[1][12],':',que[2][11],':',que[2][12],':',que[3][11],':',que[3][12])
                #ioHub.print2err('-------------')