# -*- coding: utf-8 -*-
"""
Created on Sat Nov 03 19:03:04 2012

@author: Sol
"""

from psychopy import visual as psychopyVisual
import ioHub
from ioHub.devices import Computer
from . import pumpLocalMessageQueue
import time
import weakref

 
# Device EventTrigger Class ---------------------------------------------------

class DeviceEventTrigger(object):
    """
    DeviceEventTrigger are used by SCreenState objects. A DeviceEventTrigger
    associates a set of conditions for a DeviceEvent that must be met before
    the classes triggered() method returns True. 
    """
    _lastEventsByDevice=dict()
    __slots__=['device','event_type','event_attribute_conditions','triggerFunction','_triggeringEvent']
    def __init__(self, device, event_type, event_attribute_conditions, triggerFunction = lambda a: True==True):
        self.device=device
        self.event_type=event_type
        self.event_attribute_conditions=event_attribute_conditions
        self.triggerFunction=triggerFunction
        self._triggeringEvent=None

    def triggered(self):
        events=self.device.getEvents()

        if events is None:
            events=[]
        newEventCount=len(events)

        unhandledEvents=[]

        if newEventCount > 0:
            if self.device in self._lastEventsByDevice:
                self._lastEventsByDevice[self.device].extend(events)
            else:
                self._lastEventsByDevice[self.device]=events
            unhandledEvents=self._lastEventsByDevice[self.device]

        elif self.device in self._lastEventsByDevice:
            unhandledEvents=self._lastEventsByDevice[self.device]


        for event in unhandledEvents:
            foundEvent=True

            if event['type'] != self.event_type:
                foundEvent=False

            else:
                for attrib_name,the_conditions in self.event_attribute_conditions.iteritems():
                    if isinstance(the_conditions,(list,tuple)) and event[attrib_name] in the_conditions:
                        # event_value is a list or tuple of possible values that are OK
                        pass
                    elif event[attrib_name] is the_conditions or event[attrib_name] == the_conditions:
                        # event_value is a single value
                        pass
                    else:
                        foundEvent=False
                        break

            if foundEvent is True:
                self._triggeringEvent=event
                return True

    def getTriggeringEvent(self):
        return self._triggeringEvent

    def getTriggeredStateCallback(self):
        return self.triggerFunction

    @staticmethod
    def clearEventHistory():
        DeviceEventTrigger._lastEventsByDevice.clear()

    def reset(self):
        self._triggeringEvent=None
        if self.device in self._lastEventsByDevice:
            self._lastEventsByDevice[self.device]=None
            del self._lastEventsByDevice[self.device]

#
# ScreenState Class------------------------------------------------------------
#
class ScreenState(object):
    _currentState=None
    DEFAULT_BACKGROUND_COLOR=(255,255,255)
    def __init__(self,experimentRuntime,  deviceEventTriggers=None, timeout=None):
                                     
        self.experimentRuntime=weakref.ref(experimentRuntime)
        self.window=weakref.ref(experimentRuntime.window)

        screenbackground=psychopyVisual.Rect(self.window(), 
                                     self.experimentRuntime().SCREEN_WIDTH, 
                                     self.experimentRuntime().SCREEN_HEIGHT,
                                     units='pix',name='BACKGROUND', 
                                     opacity=1.0, interpolate=False)
        screenbackground.setFillColor(self.DEFAULT_BACKGROUND_COLOR,'rgb255')
        screenbackground.setLineColor(self.DEFAULT_BACKGROUND_COLOR,'rgb255')

        self.stim=dict(BACKGROUND=screenbackground)
        self.stimNames=['BACKGROUND',]

        if isinstance(deviceEventTriggers,DeviceEventTrigger):
            deviceEventTriggers=[deviceEventTriggers,]
        self.deviceEventTriggers=deviceEventTriggers
        self.timeout=timeout
        self.dirty=True

    def setScreenColor(self,rgbColor):
        self.window().setColor(rgbColor,'rgb255')
        self.stim['BACKGROUND'].setFillColor(rgbColor,'rgb255')
        self.stim['BACKGROUND'].setLineColor(rgbColor,'rgb255')
        self.dirty=True

    def setDeviceEventTriggers(self,triggers):
        self.deviceEventTriggers=[]
        if isinstance(triggers,DeviceEventTrigger):
            triggers=[triggers,]
        self.deviceEventTriggers=triggers

    def addDeviceEventTrigger(self,trigger):
        if isinstance(trigger,DeviceEventTrigger):
            self.deviceEventTriggers.append(trigger)
        else:
            raise ioHub.ioHubError("Triggers added to a screen state object must be of type DeviceEventTrigger.")

    def getDeviceEventTriggers(self):
        return self.deviceEventTriggers
        
    def setTimeout(self,timeout):
        self.timeout=timeout

    # switches to screen state (draws and flips)
    # records flip time as start time for timer if timeout has been specified.
    # monitors the device.getEvents function ptrs that are available and if any events are returned,
    # checks the events against the event masks dict provided. If an event matches, it causes method to return
    # then, if no event masks are provided and an event is received, it will cause the method to return regardless
    # of event type for that device.
    # Otherwise method does not reurn until timeout seconds has passed.
    # Returns: [flip_time, time_since_flip, event]
    #          all elements but flip_time may be None. All times are in sec.msec
    def switchTo(self,clearEvents=True,msg=None):
        """
        Switches to the screen state defined by the class instance. The screen
        stim and built and a flip occurs. 
        
        Three conditions can cause the switchTo method to then return, 
        based on whether a timeout and / or DeviceEventTriggers
        have been set with the Screen state when switchTo is called. In all cases 
        a tuple of three values is returned, some elements of which may be None
        depending on what resulted in the state exit. The three conditions are:
            1) If no timeout or DeviceEventTriggers have been specified with
            the ScreenState, switchto() returns after the window.flip() with:
                (stateStartTime, None, None)
                where stateStartTime is the time the call to flip() returned.
            2) If a timeout has been specified, and that amount of time
            elapses from the startStartTime, then switchTo() returns with:
                (stateStartTime, stateDuration, None)
                where stateStartTime is the time the call to flip() returned.
                      stateDuration is the time switchTo() returned minus
                      stateStartTime; so it should be close to the timeout
                      specified. It may be rounded to the next flip() time 
                      interval if something in the state is causing the screen
                      to be updated each frame.
            3) If 1 - N DeviceEventTriggers have been set with the ScreenState, 
            they are monitored to determine if any have triggered. 
            If a DeviceEventTrigger has triggered, the triggering event and 
            the triggers callback function are retrieved. 
            The deviceEventTrigger is then reset, and the callback is called.
            
            If a callback returns True, the ScreenState is exited, returning: 
            (stateStartTime, stateDuration, exitTriggeringEvent).
                where -stateStartTime is the time the call to flip() returned.
                      -stateDuration is the time switchTo() returned minus
                      stateStartTime; so it should be close to the timeout
                      specified. It may be rounded to the next flip() time 
                      interval if something in the state is causing the screen
                      to be updated each frame.
                      -exitTriggeringEvent is the Device event (in dict form)
                      that caused the ScreenState to exit.
            
            If the callback returns False, the ScreenState is not exited, and
            the the timeout period and DeviceEventTriggers cintinue to be
            checked.
         """       
        ER=self.experimentRuntime()
        localClearEvents=ER.hub.clearEvents
        if clearEvents is False:
            localClearEvents = lambda clearEvents: clearEvents==None
        
        deviceEventTriggers=self.deviceEventTriggers
        currentSec=Computer.currentSec        
        lastMsgPumpTime=0
        stime=self.flip(text=msg)
        endTime=stime+self.timeout
        localClearEvents('all')

        if deviceEventTriggers and len(deviceEventTriggers)>0:
            while currentSec()+0.002<endTime:
                for trigger in deviceEventTriggers:
                    if trigger.triggered() is True:

                        event=trigger.getTriggeringEvent()
                        functionToCall=trigger.getTriggeredStateCallback()

                        trigger.reset()

                        if functionToCall:
                            exitState=functionToCall(event)
                            if exitState is True:
                                localClearEvents('all')
                                DeviceEventTrigger.clearEventHistory()
                                return stime, currentSec()-stime, event
                        break

                DeviceEventTrigger.clearEventHistory()

                tempTime=currentSec()
                if tempTime+0.002<endTime:
                    time.sleep(0.001)

                    if tempTime-lastMsgPumpTime>0.5:
                        pumpLocalMessageQueue()
                        lastMsgPumpTime=tempTime

            localClearEvents('all')
            while currentSec()<endTime:
                pass
            return stime, currentSec()-stime, None

        elif self.timeout is not None:
            ER.delay(self.timeout-0.002), None
            localClearEvents('all')

            while currentSec()<endTime:
                pass

            return stime,currentSec()-stime,None

        return stime, None, None

    def build(self):
        for stimName in self.stimNames:
            self.stim[stimName].draw()
        self.dirty=False

    def flip(self,text=None):
        if self.dirty:
            self.build()
        self.window().flip()
        ftime=Computer.currentSec()
        ScreenState._currentState=self
        if text is not None:
            flipText="%s : flip_time [%.6f]"%(text,ftime)
            self.sendMessage(flipText,ftime)
        return ftime

    def sendMessage(self, text, mtime=None):
        if mtime is None:
            mtime=Computer.currentSec()
        mtext=text
        try:
            tracker=self.experimentRuntime().devices.tracker
            if tracker is not None:
                mtext="%s : tracker_time [%.6f]"%(mtext, tracker.trackerTime())
                tracker.sendMessage(mtext)
        except:
            pass
        self.experimentRuntime().hub.sendMessageEvent(mtext,sec_time=mtime)

    @classmethod
    def getCurrentScreenState(cls):
        return cls._currentState

class ClearScreen(ScreenState):
    def __init__(self,experimentRuntime, deviceEventTriggers=None, timeout=None):
        ScreenState.__init__(self,experimentRuntime, deviceEventTriggers, timeout)

    def flip(self, text=None):
        if text is not None:
            text="CLR_SCREEN SYNC: [%s] "%(text)
        return ScreenState.flip(self,text)

class InstructionScreen(ScreenState):
    TEXT_POS=[0,0]
    TEXT_COLOR=[0,0,0]
    TEXT_HEIGHT=48
    def __init__(self,experimentRuntime, text, deviceEventTriggers=None, timeout=None):
        ScreenState.__init__(self,experimentRuntime, deviceEventTriggers, timeout)
        self.stim['TEXTLINE']=psychopyVisual.TextStim(self.window(), text=text, pos = self.TEXT_POS, height=self.TEXT_HEIGHT, color=self.TEXT_COLOR, colorSpace='rgb255',alignHoriz='center',alignVert='center',wrapWidth=self.experimentRuntime().SCREEN_WIDTH/2)
        self.stimNames.append('TEXTLINE')

    def setText(self,text):
        self.stim['TEXTLINE'].setText(text)
        self.dirty=True

    def setTextColor(self,rgbColor):
        self.stim['TEXTLINE'].setColor(rgbColor,'rgb255')
        self.dirty=True

    def setTextSize(self,size):
        self.stim['TEXTLINE'].setSize(size)

    def setTextPosition(self,pos):
        self.stim['TEXTLINE'].setPos(pos)

    def flip(self, text=''):
        if text is not None:
            text="INSTRUCT_SCREEN SYNC: [%s] [%s] "%(self.stim['TEXTLINE'].text[0:30],text)
        return ScreenState.flip(self,text)