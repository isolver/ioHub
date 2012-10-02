"""
ioHub
.. file: ioHub/devices/joystick/__init__.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

JOYSTICK_1=0
JOYSTICK_2=1
JOYSTICK_3=2
JOYSTICK_4=3
JOYSTICK_5=4
JOYSTICK_6=5
JOYSTICK_7=6
JOYSTICK_8=7

import glfw
import numpy as N
from ioHub.devices import Device, DeviceEvent, Computer, EventConstants,ioDeviceError

currentUsec= Computer.currentUsec

class Joystick(Device):

    DEVICE_LABEL='JOYSTICK_DEVICE'
    CATEGORY_LABEL='JOYSTICK'
    _joystickGLFWInitialized=False
    _detectedJoysticks=[]
    __slots__=['_joystickButtonStates','_joystickPositionStates','_lastPollTime','_jid']
    def __init__(self,*args,**kwargs):
        deviceConfig=kwargs['dconfig']
        deviceSettings={'instance_code':deviceConfig['instance_code'],
                        'category_id':EventConstants.DEVICE_CATERGORIES[Joystick.CATEGORY_LABEL],
                        'type_id':EventConstants.DEVICE_TYPES[Joystick.DEVICE_LABEL],
                        'device_class':deviceConfig['device_class'],
                        'name':deviceConfig['name'],
                        'os_device_code':'OS_DEV_CODE_NOT_SET',
                        'max_event_buffer_length':deviceConfig['event_buffer_length']
                        }
        Device.__init__(self,*args,**deviceSettings)
        #ioHub.print2stderr("kwargs: "+str(kwargs))

        self._lastPollTime=None

        if Joystick._joystickGLFWInitialized is False:
            Joystick._joystickGLFWInitialized=True
            glfw.Init()

            for i in xrange(glfw.JOYSTICK_LAST):
                if glfw.GetJoystickParam(i,glfw.PRESENT):
                    Joystick._detectedJoysticks.append(i)

        if 'joystick_index' in kwargs['dconfig']:
            self._jid=kwargs['dconfig']['joystick_index']
            if not glfw.GetJoystickParam(self._jid,glfw.PRESENT):
                raise ioDeviceError(self,"Requested joystick ID is not present on the computer: %d"%(deviceSettings['joystick_index']))
            jbuttons=glfw.GetJoystickButtons(self._jid)
            jpositions= glfw.GetJoystickPos(self._jid)
            self._joystickButtonStates=N.copy((jbuttons,jbuttons))
            self._joystickPositionStates=N.copy((jpositions,jpositions))

            #ioHub.print2stderr('Buttons:')
            #ioHub.print2stderr(str(self._jid)+' : '+str(self._joystickButtonStates.shape)+' : '+str(self._joystickButtonStates[0])+' : '+str(len(jbuttons)))

            #ioHub.print2stderr('Positions:')
            #ioHub.print2stderr(str(self._jid)+' : '+str(self._joystickPositionStates.shape)+' : '+str(self._joystickPositionStates[1])+' : '+str(len(jpositions)))
        else:
            raise ioDeviceError(self,"joystick_index must be supplied as an entry in the configuration for this device.")

    def getDetetectedJoysticks(self):
        return self._detectedJoysticks

    def _poll(self):
        sTime=int(currentUsec())
        try:
            ci=0
            if self._lastPollTime is not None:
                ci=sTime-self._lastPollTime

            self._joystickButtonStates[0]=self._joystickButtonStates[1]
            self._joystickPositionStates[0]=self._joystickPositionStates[1]

            self._joystickButtonStates[1]=glfw.GetJoystickButtons(self._jid)
            self._joystickPositionStates[1]=glfw.GetJoystickPos(self._jid)


            if not N.array_equal(self._joystickPositionStates[1],self._joystickPositionStates[0]):
                #ioHub.print2stderr("Joystick Position Event: "+str(self._jid)+' : '+str(self._joystickPositionStates[1]-self._joystickPositionStates[0]))
                #jpe= [0,0,Computer.getNextEventID(),ioHub.devices.EventConstants.EVENT_TYPES['JOYSTICK_POSITIONAL_EVENT'],
                #      ioHub.DEVICE_TYPES['JOYSTICK_DEVICE'], self.instance_code, currentTime,
                #      currentTime, currentTime, ci,ci/2.0,self.base_address,self.address_offset,currentValue,lrv]
                #self._nativeEventBuffer.append(jbe)
                pass
            if not N.array_equal(self._joystickButtonStates[1],self._joystickButtonStates[0]):
                #ioHub.print2stderr("Joystick Button Event: "+str(self._jid)+' : '+str(self._joystickButtonStates[1]-self._joystickButtonStates[0]))
                bchanges=self._joystickButtonStates[1]-self._joystickButtonStates[0]
                multibuttonEventCount=N.count_nonzero(bchanges)
                for i, bstate in enumerate(bchanges):
                    is_pressed = 0
                    etype=None
                    button_id=i+1
                    if bstate < 0:
                        is_pressed = 0
                        etype=JoystickButtonReleaseEvent.EVENT_TYPE_ID
                    elif bstate > 0 :
                        is_pressed = 1
                        etype=JoystickButtonPressEvent.EVENT_TYPE_ID

                    if etype:
                        jbe= [0,0,Computer.getNextEventID(),etype, self.instance_code, sTime,
                              sTime, sTime, ci, ci/2.0, self._jid, is_pressed, button_id,multibuttonEventCount]
                        #ioHub.print2stderr("Joystick Button Event: "+str(jbe))
                        self._nativeEventBuffer.append(jbe)

        except Exception as e:
            import ioHub
            ioHub.printExceptionDetailsToStdErr()
            raise ioDeviceError(self,"An error orricced what polling GAMEPAD_%d"%(self._jid+1),e)
        finally:
            self._lastPollTime=sTime

    @staticmethod
    def _getIOHubEventObject(event,device_instance_code):
        return event # already a Joystick Event

class JoystickEvent(DeviceEvent):
    _newDataTypes = [('joystick_index',N.uint8),('is_pressed',N.uint8),('button_id',N.uint8),('multiple_button_count',N.uint8)]
    __slots__=[e[0] for e in _newDataTypes]
    def __init__(self,*args,**kwargs):
        kwargs['device_type']=EventConstants.DEVICE_TYPES['JOYSTICK_DEVICE']
        DeviceEvent.__init__(self,*args,**kwargs)

class JoystickButtonEvent(JoystickEvent):
    EVENT_TYPE_STRING='JOYSTICK_BUTTON'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=EVENT_TYPE_STRING
    __slots__=[]
    def __init__(self,*args,**kwargs):
        JoystickEvent.__init__(self,*args,**kwargs)

class JoystickButtonPressEvent(JoystickButtonEvent):
    EVENT_TYPE_STRING='JOYSTICK_BUTTON_PRESS'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=JoystickButtonEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self,*args,**kwargs):
        JoystickButtonEvent.__init__(self,*args,**kwargs)

class JoystickButtonReleaseEvent(JoystickButtonEvent):
    EVENT_TYPE_STRING='JOYSTICK_BUTTON_RELEASE'
    EVENT_TYPE_ID=EventConstants.EVENT_TYPES[EVENT_TYPE_STRING]
    IOHUB_DATA_TABLE=JoystickButtonEvent.IOHUB_DATA_TABLE
    __slots__=[]
    def __init__(self,*args,**kwargs):
        JoystickButtonEvent.__init__(self,*args,**kwargs)