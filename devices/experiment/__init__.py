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

class Experiment(Device):
    """
    The Experiment class represents a *virtual* device ( the 
    Experiment / PsychoPy Process that is running the experiment script ), and is unique
    in that it is the *client* of the ioHub Server, but can also generate events
    itself that are registered with the ioHub Server. Currently the Experiment
    supports the creation of general purpose MessageEvent's, which can effectively
    hold any string up to 128 characters in length. Experiment Message events can be
    sent to the ioHub Server at any time, and are useful for creating stimulus onset or offset
    notifications, or other experiment events of interest that should be associated 
    with events from other devices for post hoc analysis of the experiments event steam using
    the ioDataStore.
    """
    EVENT_CLASS_NAMES=['MessageEvent']
    
    DEVICE_TYPE_ID=DeviceConstants.EXPERIMENT
    DEVICE_TYPE_STRING='EXPERIMENT'
    __slots__=[]
    def __init__(self,*args,**kwargs):
        Device.__init__(self,*args,**kwargs['dconfig'])

        
    def _nativeEventCallback(self,native_event_data):
        if self.isReportingEvents():
            notifiedTime=currentSec()
            
            native_event_data[DeviceEvent.EVENT_LOGGED_TIME_INDEX]=notifiedTime # set logged time of event
    
            native_event_data[DeviceEvent.EVENT_DELAY_INDEX]=native_event_data[DeviceEvent.EVENT_LOGGED_TIME_INDEX]-native_event_data[DeviceEvent.EVENT_DEVICE_TIME_INDEX]
    
            # on windows ioHub and experiment process use same timebase, so device time == hub time
            native_event_data[DeviceEvent.EVENT_HUB_TIME_INDEX]=native_event_data[DeviceEvent.EVENT_DEVICE_TIME_INDEX]
    
            self._addNativeEventToBuffer(native_event_data)
            
            self._last_callback_time=notifiedTime

    def _close(self):
        Device._close(self)
            
######### Experiment Events ###########

class MessageEvent(DeviceEvent):
    """
    A MessageEvent can be created and sent to the ioHub to record important 
    marker times during the experiment; for example, when key display changes 
    occur, or when events related to devices not supported by the ioHub have happened, 
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
    PARENT_DEVICE=Experiment
    EVENT_TYPE_ID=EventConstants.MESSAGE
    EVENT_TYPE_STRING='MESSAGE'
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING

    _newDataTypes=[
                ('msg_offset','float32'), 
                ('prefix','a3'), 
                ('text','a128')  
                ]
    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self, *args, **kwargs):
        """
        """
        
        #: The text attribute is used to hold the actual 'content' of the message.
        #: The text attribute string can not be more than 128 characters in length.
        #: String type
        self.text=None
        
        #: The prefix attribute is a 0 - 3 long string used as a 'group' or 'category' 
        #: code that can be assigned to messages. The prefix attribute may be useful
        #: for grouping messages into categories or types when retieving them for analysis
        #: by assigning the same prix string to related Message Event types.
        #: String type.
        self.prefix=None
        
        #: The msg_offset attribute can be used in cases where the Experiment Message
        #: Evenet needs to be sent *before* or *after* the time the actual event occurred.
        #: msg offset should be in sec.msec format and in general can be calculated as:
        #:
        #: msg_offset=actual_event_iohub_time - iohub_message_time
        #: 
        #: where actual_event_iohub_time is the time the event occured that is being
        #: represented by the Message event; and iohub_message_time is either the
        #: time provided to the Experiment Message creation methods to be used as the 
        #: Message time stamp, or is the time that the Message Event actually requested the
        #: current time if no message time was provided.
        #: Both times must be read from Computer.getTime() or one of it's method aliases. 
        #: Float type.
        self.msg_offset=None         

        DeviceEvent.__init__(self, *args,**kwargs)

    @staticmethod
    def _createAsList(text,prefix='',msg_offset=0.0, sec_time=None):
        csec=currentSec()
        if sec_time is not None:
            csec=sec_time
        return (0,0,0,Computer._getNextEventID(),MessageEvent.EVENT_TYPE_ID,
                csec,0,0,0.0,0.0,0,msg_offset,prefix,text)


