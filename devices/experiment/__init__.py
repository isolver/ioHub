"""
ioHub
.. file: ioHub/devices/experiment/__init__.py

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

from .. import Device,Computer,DeviceEvent
from ioHub.constants import DeviceConstants, EventConstants

currentSec=Computer.currentSec

class ExperimentDevice(Device):
    """
    The ExperimentDevice class represents a virtual device, being the 
    Experiment / PsychoPy Process that is running the experiment script and 
    has created the ioHub ioServer Process.
    A ExperimentDevice device can generate experiment software related events 
    that are sent to the ioHub to be saved in the ioDataStore along with all 
    other device events being saved.
    """
    ALL_EVENT_CLASSES=[]
    
    DEVICE_TYPE_ID=DeviceConstants.EXPERIMENT
    DEVICE_TYPE_STRING=DeviceConstants.getName(DEVICE_TYPE_ID)
    __slots__=[]
    def __init__(self,*args,**kwargs):
        """

        :rtype : object
        :param args:
        :param kwargs:
        """
        ExperimentDevice.ALL_EVENT_CLASSES=[MessageEvent,]
        self._startupConfiguration=kwargs['dconfig']
        deviceSettings={
            'type_id':self.DEVICE_TYPE_ID,
            'device_class':ExperimentDevice.__name__,
            'name':self._startupConfiguration['name'],
            'monitor_event_types':self._startupConfiguration.get('monitor_event_types',self.ALL_EVENT_CLASSES),
            '_isReportingEvents':self._startupConfiguration.get('auto_report_events',True),
            'os_device_code':'OS_DEV_CODE_NOT_SET',
            'max_event_buffer_length':self._startupConfiguration['event_buffer_length']
            }          
        Device.__init__(self,**deviceSettings)


        
    def _nativeEventCallback(self,event):
        event[DeviceEvent.EVENT_LOGGED_TIME_INDEX]=currentSec() # set logged time of event

        event[DeviceEvent.EVENT_DELAY_INDEX]=event[DeviceEvent.EVENT_LOGGED_TIME_INDEX]-event[DeviceEvent.EVENT_DEVICE_TIME_INDEX]

        # on windows ioHub and experiment process use same timebase, so device time == hub time
        event[DeviceEvent.EVENT_HUB_TIME_INDEX]=event[DeviceEvent.EVENT_DEVICE_TIME_INDEX]

        self._addNativeEventToBuffer(event)
        return True
    
    def _poll(self):
        pass
 

    def _getIOHubEventObject(self,event):
        return event

            
######### Experiment Events ###########

class MessageEvent(DeviceEvent):
    """
    A MessageEvent can be created and sent to the ioHub to record important 
    marker times during the experiment; for example, when key display changes 
    occur, when events related to devices not supported by the ioHub have happened, 
    or simply information about the experiment you want
    to store in the ioDataStore along with all the other event data.

    Since the PsychoPy Process can access the same time base that is used by 
    the ioHub Process, when you create a Message Event you can time stamp it 
    at the time of MessageEvent creation, or with the result of a previous call
    to one of the ioHub time related methods. This makes experiment messages
    extremely accurate temporally when related to other events times saved to
    the ioDataSore.
    
    Event Type ID: EventConstants.MESSAGE
    Event Type String: 'MESSAGE'      
    """
    PARENT_DEVICE=ExperimentDevice
    EVENT_TYPE_ID=EventConstants.MESSAGE
    EVENT_TYPE_STRING=EventConstants.getName(EVENT_TYPE_ID)
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING

    _newDataTypes=[
                ('msg_offset','i2'), # if you want to send the Experiment *before* or *after* the event time occurred
                                     # and you know exactly when relative to the event time you are sending the message
                                     # you can specify an offset that will be applied to the message time to give the
                                     # true event time and not when the message was sent.

                ('prefix','a3'), # A 0 - 3 character prefix code that you can assign to messages and use it to
                                 # do such things as group messages into categories or types when
                                 # retieving them for analysis.

                ('text','a128')  # The actual text of the message. This can be any python string
                                 # up to 128 characters in length.
                ]
    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self, *args, **kwargs):
        DeviceEvent.__init__(self, *args,**kwargs)

    @staticmethod
    def _createAsList(text,prefix='',msg_offset=0.0, sec_time=None):
        csec=currentSec()
        if sec_time is not None:
            csec=sec_time
        return (0,0,Computer._getNextEventID(),MessageEvent.EVENT_TYPE_ID,csec,0,0,0.0,0.0,0,msg_offset,prefix,text)


