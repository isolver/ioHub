# -*- coding: utf-8 -*-
"""
ioHub Python Module
.. file: ioHub/devices/xinput/__init__.py

fileauthor: Sol Simpson <sol@isolver-software.com>

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License 
(GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + 
contributors, please see credits section of documentation.
"""
 
import xinput
import numpy as N
import gevent
from .. import Computer, Device, DeviceEvent, ioDeviceError
from ioHub.constants import XInputGamePadConstants, DeviceConstants,EventConstants
from ioHub import  print2err


def enableXInput():
    # Enables xinput on the system 
    if not hasattr(xinput,'xinput_dll'):
        xinput.loadDLL()    
    xinput._xinput_dll.XInputEnable(True)

def disableXInput():
    # Disables xinput on the system 
    if not hasattr(xinput,'xinput_dll'):
        xinput.loadDLL()    
    xinput._xinput_dll.XInputEnable(False)
    
class XInputDevice(Device):
    _ASSIGNED_USER_IDS=[]
    _USER2DEVICE=dict()
    
    DEVICE_TYPE_ID=DeviceConstants.XINPUT
    DEVICE_LABEL = DeviceConstants.getName(DEVICE_TYPE_ID)
    __slots__=['_user_id','_device_state','_device_state_buffer','_state_time','_time_ci']    
    def __init__(self, *args,**kwargs):
        user_id=self._startupConfiguration.get('user_id',-1)
        self._startupConfiguration['_user_id']=user_id
        self._user_id=user_id
        
        type_id=self._startupConfiguration.get('type_id',self.DEVICE_TYPE_ID)
        self._startupConfiguration['type_id']=type_id

        device_class=self._startupConfiguration.get('device_class',self.__class__.__name__)
        self._startupConfiguration['device_class']=device_class

        name=self._startupConfiguration.get('name',self.__class__.__name__)
        self._startupConfiguration['name']=name

        os_device_code=self._startupConfiguration.get('os_device_code','OS_DEV_CODE_NOT_SET')
        self._startupConfiguration['os_device_code']=os_device_code

        auto_report_events=self._startupConfiguration.get('auto_report_events',True)
        self._startupConfiguration['_isReportingEvents']=auto_report_events
        self._isReportingEvents=auto_report_events
        
        max_event_buffer_length=self._startupConfiguration.get('event_buffer_length',256)
        self._startupConfiguration['max_event_buffer_length']=max_event_buffer_length

        monitor_event_types=self._startupConfiguration.get('monitor_event_types',self.ALL_EVENT_CLASSES)
        self._startupConfiguration['monitor_event_types']=monitor_event_types

        if not hasattr(xinput,'xinput_dll'):
            xinput.loadDLL()
                       
        Device.__init__(self,*args,**self._startupConfiguration)
        
                
class GamePad(XInputDevice): 
    DEVICE_TYPE_ID=DeviceConstants.GAMEPAD
    DEVICE_LABEL = DeviceConstants.getName(DEVICE_TYPE_ID)
    
    ALL_EVENT_CLASSES=[]
    
    __slots__=['_capabilities','_battery_information','_keystroke','_rumble']    
    def __init__(self, *args,**kwargs):
        self._startupConfiguration=kwargs.get('dconfig',{})
        GamePad.ALL_EVENT_CLASSES=GamePadStateChangeEvent,GamePadDisconnectEvent,GamePadButtonEvent,GamePadTriggerEvent,GamePadThumbStickEvent

        self._startupConfiguration['monitor_event_types']=self._startupConfiguration.get('monitor_event_types',GamePad.ALL_EVENT_CLASSES)
        self._startupConfiguration['device_class']=self._startupConfiguration.get('device_class',self.__class__.__name__)
        self._startupConfiguration['name']=self._startupConfiguration.get('name',self.__class__.__name__.lower())

        XInputDevice.__init__(self,*args,**self._startupConfiguration)
        
        if self._user_id in self._ASSIGNED_USER_IDS:
            raise ioDeviceError("XInputDevice with user_id %d already in use."%(self._user_id))

        if len(self._ASSIGNED_USER_IDS) == xinput.XUSER_MAX_COUNT:
            raise ioDeviceError("XInputDevice max user count reached: %d."%(xinput.XUSER_MAX_COUNT))
            
        if self._user_id >= 0 and self._user_id < xinput.XUSER_MAX_COUNT:   
            connectedOK=_initializeGamePad(self,self._user_id)
            if not connectedOK:
                raise ioDeviceError("XInputDevice with user_id %d is not connected."%(self._user_id))
        else:
            self._user_id=-1
            for i in [i for i in range(xinput.XUSER_MAX_COUNT) if i not in self._ASSIGNED_USER_IDS]:
                connectedOK=_initializeGamePad(self,i)
                if connectedOK:
                    break
                else:
                    raise ioDeviceError("No XInputDevice is Available for Use. Please check Connections.")


        self._rumble=xinput.XINPUT_VIBRATION(0,0)
        self._battery_information=xinput.XINPUT_BATTERY_INFORMATION(0,0)
        self._capabilities=xinput.XINPUT_CAPABILITIES(0,0,0,
                                        xinput.XINPUT_GAMEPAD(0,0,0,0,0,0,0),
                                        xinput.XINPUT_VIBRATION(0,0))
        self.setRumble(0,0)

    def getButtons(self,gamepad_state=None):
        if gamepad_state == None:
            gamepad_state=self._device_state.Gamepad

        buttonStates=self._getButtonNameList(gamepad_state.wButtons)
        buttonStates['time']=self._state_time,
        buttonStates['confidence_interval']=self._time_ci
        return buttonStates

    @staticmethod
    def _getButtonNameList(wbuttons=0):
        buttonStates=dict()
        if wbuttons!=0:
            for k in XInputGamePadConstants._keys:
                if wbuttons&k == k:
                    buttonStates[XInputGamePadConstants._names[k]]=True
                else:
                    buttonStates[XInputGamePadConstants._names[k]]=False
        return buttonStates

    def getTriggers(self,gamepad_state=None):
        if gamepad_state == None:
            gamepad_state=self._device_state.Gamepad
        return dict(time=self._state_time, confidence_interval=self._time_ci,LeftTrigger=gamepad_state.bLeftTrigger/255.0,RightTrigger=gamepad_state.bRightTrigger/255.0)

    def getPressedButtons(self):
        return self._device_state.Gamepad.wButtons
        
    def getPressedButtonList(self):
        bdict=self._getButtonNameList(self._device_state.Gamepad.wButtons)
        blist=[]
        for k,v in bdict.iteritems():
            if v:
                blist.append(k)
        return blist
        
    def getThumbSticks(self,gamepad_state=None):
        if gamepad_state == None:
            gamepad_state=self._device_state.Gamepad
        leftStick=xinput.normalizeThumbStickValues(gamepad_state.sThumbLX,gamepad_state.sThumbLY,xinput.XINPUT_GAMEPAD_LEFT_THUMB_DEADZONE)
        rightStick=xinput.normalizeThumbStickValues(gamepad_state.sThumbRX,gamepad_state.sThumbRY,xinput.XINPUT_GAMEPAD_RIGHT_THUMB_DEADZONE)
        return dict(time=self._state_time, confidence_interval=self._time_ci,LeftStick=leftStick,RightStick=rightStick)

    def _poll(self):
        t=Computer.getTime()
        result = xinput._xinput_dll.XInputGetState(self._user_id, xinput.pointer(self._device_state_buffer))
        t2=Computer.getTime()


        if result == xinput.ERROR_SUCCESS:
            changed = self._checkForStateChange()
            if len(changed) > 0:
                temp=self._device_state
                self._device_state = self._device_state_buffer
                self._state_time=t2
                self._time_ci=t2-t
                self._device_state_buffer=temp

                delay=(t-self._lastPollTime)/2.0 # assuming normal distribution, on average delay will be 1/2 the
                                                 # inter poll interval
                buttons=0
                if len(changed.get('Buttons',[])) > 0:
                    buttons=self._device_state.Gamepad.wButtons

                gpe= [
                    0,                                      # experiment_id filled in by ioHub
                    0,                                      # session_id filled in by ioHub
                    Computer._getNextEventID(),             # unique event id
                    GamePadStateChangeEvent.EVENT_TYPE_ID,  # id representation of event type
                    self._state_time,                       # device Time
                    t,                                      # logged time
                    self._state_time,                       # time (i.e. ioHub Time)
                    self._time_ci,                          # confidence Interval
                    delay,                                  # delay
                    0,
                    self._user_id,                          # number 0-3 representing which controller event is from.
                    buttons,                                # buttons id's that were pressed at the time of the state change.
                    'B',                                    # buttons 1 char placeholder
                    changed.get('LeftThumbStick',(0.0,0.0,0.0)),   # normalized x,y, and magnitude value for left thumb stick
                    changed.get('RightThumbStick',(0.0,0.0,0.0)),  # normalized x,y, and magnitude value for right thumb stick
                    changed.get('LeftTrigger',0.0),      # normalized degree pressed for left trigger button
                    changed.get('RightTrigger',0.0)     # normalized degree pressed for left trigger button
                    ]
                self._addNativeEventToBuffer(gpe)
        else:
            # TODO: device has disconnected, create a special event.....
            temp=self._device_state
            self._device_state = self._device_state_buffer
            self._state_time=t
            self._time_ci=t2-t
            self._device_state_buffer=temp

            delay=(t-self._lastPollTime)/2.0 # assuming normal distribution, on average delay will be 1/2 the
                                             # inter poll interval
            gpe= [
                0,                                      # experiment_id filled in by ioHub
                0,                                      # session_id filled in by ioHub
                Computer._getNextEventID(),             # unique event id
                GamePadDisconnectEvent.EVENT_TYPE_ID,  # id representation of event type
                self._state_time,                       # device Time
                t,                                      # logged time
                self._state_time,                       # time (i.e. ioHub Time)
                self._time_ci,                          # confidence Interval
                delay,                                  # delay
                0,                                      #filter_id 0 by default
                self._user_id,                          # number 0-3 representing which controller event is from.
                0,                                      # buttons id's that were pressed at the time of the state change.
                'B',                                      # buttons 1 char placeholder
                0,                                      # normalized x,y, and magnitude value for left thumb stick
                0,                                      # normalized x,y, and magnitude value for right thumb stick
                0,                                      # normalized degree pressed for left trigger button
                0                                       # normalized degree pressed for left trigger button
                ]

            self._addNativeEventToBuffer(gpe)
            self._close()

        self._lastPollTime=t
        return True


    def _getIOHubEventObject(self,event):
        return event # already a Gamepad Event

    def _checkForStateChange(self):
        g1=self._device_state.Gamepad
        g2=self._device_state_buffer.Gamepad
        changed={}      
            
        if g1.wButtons!=g2.wButtons:
            buttonNameList=[]
            if g2.wButtons!=0:
                for k in XInputGamePadConstants._keys:
                    if g2.wButtons&k == k:
                        buttonNameList.append(XInputGamePadConstants._names[k])
            changed['Buttons']=buttonNameList
            

        if g1.bLeftTrigger!=g2.bLeftTrigger:
            changed['LeftTrigger']=g2.bLeftTrigger/255.0
        if g1.bRightTrigger!=g2.bRightTrigger:
            changed['RightTrigger']=g2.bRightTrigger/255.0


        if g1.sThumbLX!=g2.sThumbLX or g1.sThumbLY!=g2.sThumbLY:        
            nl1=xinput.normalizeThumbStickValues(g1.sThumbLX,g1.sThumbLY,xinput.XINPUT_GAMEPAD_LEFT_THUMB_DEADZONE)
            nl2=xinput.normalizeThumbStickValues(g2.sThumbLX,g2.sThumbLY,xinput.XINPUT_GAMEPAD_LEFT_THUMB_DEADZONE)
            if (nl1 != nl2):
                changed['LeftThumbStick']=nl2            
        if g1.sThumbRX!=g2.sThumbRX or g1.sThumbRY!=g2.sThumbRY:            
            nr1=xinput.normalizeThumbStickValues(g1.sThumbRX,g1.sThumbRY,xinput.XINPUT_GAMEPAD_RIGHT_THUMB_DEADZONE)
            nr2=xinput.normalizeThumbStickValues(g2.sThumbRX,g2.sThumbRY,xinput.XINPUT_GAMEPAD_RIGHT_THUMB_DEADZONE)
            if (nr1 != nr2):
                changed['RightThumbStick']=nr2
            
        return changed
    
    def setRumble(self,lowFrequencyValue=0,highFrequencyValue=0,duration=1.0):

        DeNormalizedLowFrequencyValue= int(65535.0*(lowFrequencyValue/100.0))
        DeNormalizedHighFrequencyValue= int(65535.0*(highFrequencyValue/100.0))
        
        if DeNormalizedLowFrequencyValue < 0:
            self._rumble.wLeftMotorSpeed=0
        elif DeNormalizedLowFrequencyValue > 65535:
            self._rumble.wLeftMotorSpeed=65535
        else:
            self._rumble.wLeftMotorSpeed=DeNormalizedLowFrequencyValue
            
        if DeNormalizedHighFrequencyValue < 0:
            self._rumble.wRightMotorSpeed=0
        elif DeNormalizedHighFrequencyValue > 65535:
            self._rumble.wRightMotorSpeed=65535
        else:
            self._rumble.wRightMotorSpeed=DeNormalizedHighFrequencyValue

        t1=Computer.getTime()
        xinput._xinput_dll.XInputSetState(self._user_id, xinput.pointer(self._rumble))
        t2=Computer.getTime()

        gevent.spawn(self._delayedRumble,delay=duration)
        return t2, t2-t1
    
    def _delayedRumble(self,lowFrequencyValue=0,highFrequencyValue=0,delay=0):
        gevent.sleep(delay)
        self._rumble.wLeftMotorSpeed=0
        self._rumble.wRightMotorSpeed=0
        xinput._xinput_dll.XInputSetState(self._user_id, xinput.pointer(self._rumble))

    def getRumbleState(self):
        NormalizedLowFrequencyValue= 100.0*(self._rumble.wLeftMotorSpeed/65535.0)
        NormalizedHighFrequencyValue= 100.0*(self._rumble.wRightMotorSpeed/65535.0)
        return NormalizedLowFrequencyValue, NormalizedHighFrequencyValue
        
    def updateBatteryInformation(self):
        resultCode=xinput._xinput_dll.XInputGetBatteryInformation(
            self._user_id, # Index of the gamer associated with the device
            xinput.BATTERY_DEVTYPE_GAMEPAD,# Which device on this user index
            xinput.pointer(self._battery_information)) # Contains the level 
                                                       # and types of batteries

        bl=XInputGamePadConstants._batteryLevels.getName(self._battery_information.BatteryLevel)
        bt=XInputGamePadConstants._batteryTypes.getName(self._battery_information.BatteryType)
        return bl,bt
        
    def getLastReadBatteryInfo(self):
        bl=XInputGamePadConstants._batteryLevels.getName(self._battery_information.BatteryLevel)
        bt=XInputGamePadConstants._batteryTypes.getName(self._battery_information.BatteryType)
        return bl,bt
       
    def updateCapabilitiesInformation(self):
        resultCode=xinput._xinput_dll.XInputGetCapabilities(
            self._user_id,
            xinput.XINPUT_FLAG_GAMEPAD,
            xinput.pointer(self._capabilities))
            
        t=self._capabilities.Type
        s=self._capabilities.SubType
        f=self._capabilities.Flags

        g=self._capabilities.Gamepad
        b=g.wButtons
        blt=g.bLeftTrigger
        brt=g.bRightTrigger
        lxt=g.sThumbLX
        lyt=g.sThumbLY
        rxt=g.sThumbRX
        ryt=g.sThumbRY
        
        v=self._capabilities.Vibration
        lf=v.wLeftMotorSpeed
        hf=v.wRightMotorSpeed
        
        return (t,s,f),b,(blt,brt),((lxt,lyt),(rxt,ryt)),(lf,hf)

    def getLastReadCapabilitiesInfo(self):
        t=self._capabilities.Type
        s=self._capabilities.SubType
        f=self._capabilities.Flags

        g=self._capabilities.Gamepad
        b=g.wButtons
        blt=g.bLeftTrigger
        brt=g.bRightTrigger
        lxt=g.sThumbLX
        lyt=g.sThumbLY
        rxt=g.sThumbRX
        ryt=g.sThumbRY
        
        v=self._capabilities.Vibration
        lf=v.wLeftMotorSpeed
        hf=v.wRightMotorSpeed
        
        return (t,s,f),b,(blt,brt),((lxt,lyt),(rxt,ryt)),(lf,hf)
            
    def _close(self):
        self.setRumble(0,0)
        XInputDevice._ASSIGNED_USER_IDS.remove(self._user_id)
        del XInputDevice._USER2DEVICE[self._user_id]
        self._user_id=None
        self._device_state=None
    
    def __del__(self):
        self._close()
        self.clearEvents()


def _initializeGamePad(gamepad,user_id):
    dwResult, gamepadState, stime, ci=xinput.createXInputGamePadState(user_id)
    if dwResult == xinput.ERROR_SUCCESS:
        gamepad._user_id=user_id
        gamepad._device_state=gamepadState
        gamepad._state_time=stime
        gamepad._time_ci=ci
        XInputDevice._ASSIGNED_USER_IDS.append(user_id)
        dwResult2, gamepadState2, stime2, ci2=xinput.createXInputGamePadState(user_id)
        gamepad._device_state_buffer=gamepadState2
        XInputDevice._USER2DEVICE[user_id]=gamepad
        return True
    return False

class GamePadStateChangeEvent(DeviceEvent):
    PARENT_DEVICE=GamePad
    EVENT_TYPE_ID=EventConstants.GAMEPAD_EVENT
    EVENT_TYPE_STRING=EventConstants.getName(EVENT_TYPE_ID)
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING
    _newDataTypes = [ ('controller_id',N.uint8),  #number 0-3 representing which controller event is for.
                                                  # On xbox360 controller, the id of the controller can be
                                                  # visually determined by the quadrant that is illuminated
                                                  # on the center 'red circle of light'.
                                                  # Top Left = XINPUT_USER_0 == 0
                                                  # Top Right = XINPUT_USER_1 == 1
                                                  # Bottom Right = XINPUT_USER_2 == 2
                                                  # Bottom Left = XINPUT_USER_3 == 3


                      ('buttonIDs',N.uint32),     # the buttons that were pressed at the time of the state change.
                                                  # All buttons that are pressed are & together into this field.
                                                  # Use buttons to get a list of the text representation for
                                                  # each button that was pressed in list form
                      ('buttons',N.str,1),        # placeholder for button name list when event is viewed as NamedTuple

                      # Thumbsticks are represented in normalized units between 0.0 and 1.0 for x direction, y direction
                      # and magnitude of the thumbstick. x and y are the horizontal and vertical position of the stick
                      # around the center point. Magnitude is how far from the center point the stick location is: 0.0
                      # would equal the stick being in the center position, not moved. 1.0 would indicate the stick
                      # is pushed all the way to the outer rail of the thumbstick movement circle. The resolution of
                      # each thumbstick is about 16 bits for each measure.
                      ('leftThumbStick',N.dtype([('x',N.float32),('y',N.float32),('magnitude',N.float32)])),
                      ('rightThumbStick',N.dtype([('x',N.float32),('y',N.float32),('magnitude',N.float32)])),

                      ('leftTrigger',N.float32),   # the triggers are the two pistol finger analog buttons on the
                                                   # XInput gamepad. The value is normalized to between 0.0 (not pressed)
                                                   # and 1.0 (fully depressed). The resolution of the triggers are 8 bits.
                      ('rightTrigger',N.float32)
                    ]
    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self,*args,**kwargs):
        DeviceEvent.__init__(self,*args,**kwargs)

    @classmethod
    def createEventAsDict(cls,values):
        ed=super(DeviceEvent,cls).createEventAsDict(values)
        if ed['buttonIDs'] == 0:
            ed['buttons']={}
            return ed
        ed['buttons']=GamePad._getButtonNameList(ed['buttonIDs'])
        return ed

    #noinspection PyUnresolvedReferences
    @classmethod
    def createEventAsNamedTuple(cls,valueList):
        if valueList[-6] == 0:
            valueList[-5]={}
            return cls.namedTupleClass(*valueList)

        valueList[-5]=GamePad._getButtonNameList(valueList[-6])
        return cls.namedTupleClass(*valueList)

class GamePadDisconnectEvent(GamePadStateChangeEvent):
    EVENT_TYPE_ID=EventConstants.GAMEPAD_DISCONNECT_EVENT
    EVENT_TYPE_STRING=EventConstants.getName(EVENT_TYPE_ID)
    IOHUB_DATA_TABLE=GamePadStateChangeEvent.EVENT_TYPE_STRING
    __slots__=[]
    def __init__(self,*args,**kwargs):
        GamePadStateChangeEvent.__init__(self,*args,**kwargs)

class GamePadButtonEvent(GamePadStateChangeEvent):
    EVENT_TYPE_ID=EventConstants.GAMEPAD_BUTTON_EVENT
    EVENT_TYPE_STRING=EventConstants.getName(EVENT_TYPE_ID)
    IOHUB_DATA_TABLE=GamePadStateChangeEvent.EVENT_TYPE_STRING
    __slots__=[]
    def __init__(self,*args,**kwargs):
        GamePadStateChangeEvent.__init__(self,*args,**kwargs)

class GamePadThumbStickEvent(GamePadStateChangeEvent):
    EVENT_TYPE_ID=EventConstants.GAMEPAD_THUMBSTICK_EVENT
    EVENT_TYPE_STRING=EventConstants.getName(EVENT_TYPE_ID)
    IOHUB_DATA_TABLE=GamePadStateChangeEvent.EVENT_TYPE_STRING
    __slots__=[]
    def __init__(self,*args,**kwargs):
        GamePadStateChangeEvent.__init__(self,*args,**kwargs)

class GamePadTriggerEvent(GamePadStateChangeEvent):
    EVENT_TYPE_ID=EventConstants.GAMEPAD_TRIGGER_EVENT
    EVENT_TYPE_STRING=EventConstants.getName(EVENT_TYPE_ID)
    IOHUB_DATA_TABLE=GamePadStateChangeEvent.EVENT_TYPE_STRING
    __slots__=[]
    def __init__(self,*args,**kwargs):
        GamePadStateChangeEvent.__init__(self,*args,**kwargs)


