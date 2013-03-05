# -*- coding: utf-8 -*-
"""
Created on Thu Nov 08 15:13:55 2012

@author: Sol
"""

class Constants(object):
    UNDEFINED=0
    _keys=None
    _names=None
    _classes=None

    _initialized=False

    @classmethod
    def getName(cls,id):
        return cls._names.get(id,cls._names[cls.UNDEFINED])
 
    @classmethod
    def getID(cls,name):
        return cls._names.get(name,None)

    @classmethod
    def getClass(cls,id):
        return cls._classes.get(id,None)

    @classmethod
    def initialize(cls,starting_index=1):
        if cls._initialized:
            return

        [setattr(cls,a,i+starting_index) for i,a in enumerate(dir(cls)) if ((a[0] != '_') and (not callable(getattr(cls,a))) and (getattr(cls,a) < 0))]
        cls._names=dict([(getattr(cls,a),a) for a in dir(cls) if ((a[0] != '_') and (not callable(getattr(cls,a))))])
        cls._keys=list(cls._names.keys())
        cls._names.update(dict([(v,k) for k,v in cls._names.iteritems()]))
        cls._initialized=True
 
class EventConstants(Constants):
    KEYBOARD_INPUT=20
    KEYBOARD_PRESS=21
    KEYBOARD_RELEASE=22
    KEYBOARD_CHAR=23

    MOUSE_INPUT=30
    MOUSE_BUTTON=31
    MOUSE_PRESS=32
    MOUSE_RELEASE=33
    MOUSE_DOUBLE_CLICK=34
    MOUSE_WHEEL=35
    MOUSE_WHEEL_UP=36
    MOUSE_WHEEL_DOWN=37
    MOUSE_MOVE=38

    EYETRACKER_INPUT=50
    EYE_SAMPLE=51
    BINOC_EYE_SAMPLE=52
    FIXATION_START=53
    FIXATION_END=54
    SACCADE_START=55
    SACCADE_END=56
    BLINK_START=57
    BLINK_END=58

    XINPUT=70
    XINPUT_STATE_CHANGE=71
    XINPUT_DISCONNECT=-72
    XINPUT_CONNECT=73

    GAMEPAD_EVENT=80
    GAMEPAD_BUTTON_EVENT=81
    GAMEPAD_THUMBSTICK_EVENT=82
    GAMEPAD_TRIGGER_EVENT=83
    GAMEPAD_DISCONNECT_EVENT=85

#    DIGITAL_INPUT=100
#    PARALLEL_PORT_INPUT=102
#    SERIAL_INPUT=104

#    ANALOG_INPUT=120
#    DA_SINGLE_CHANNEL_INPUT=121
    DA_MULTI_CHANNEL_INPUT=122

    EXPERIMENT=150
    MESSAGE=151

    DISPLAY_INPUT=190

    COMPUTER_INPUT=200

#    FILTER_EVENT=210

    @classmethod
    def addClassMappings(cls):
        if cls._classes is None:
            cls._classes={}
            from ioHub.devices import deviceModulesAvailable

            if 'eyetracker' in deviceModulesAvailable:
                from ioHub.devices import (MonocularEyeSample, BinocularEyeSample,
                    FixationStartEvent,FixationEndEvent,SaccadeStartEvent,
                    SaccadeEndEvent,BlinkStartEvent,BlinkEndEvent)

                cls._classes[cls.EYE_SAMPLE]=MonocularEyeSample
                cls._classes[cls.BINOC_EYE_SAMPLE]=BinocularEyeSample
                cls._classes[cls.FIXATION_START]=FixationStartEvent
                cls._classes[cls.FIXATION_END]=FixationEndEvent
                cls._classes[cls.SACCADE_START]=SaccadeStartEvent
                cls._classes[cls.SACCADE_END]=SaccadeEndEvent
                cls._classes[cls.BLINK_START]=BlinkStartEvent
                cls._classes[cls.BLINK_END]=BlinkEndEvent

            if 'experiment' in deviceModulesAvailable:
                from ioHub.devices import MessageEvent
                cls._classes[cls.MESSAGE]=MessageEvent

            if 'mouse' in deviceModulesAvailable:
                from ioHub.devices import (MouseMoveEvent, MouseWheelEvent,
                        MouseWheelUpEvent,MouseWheelDownEvent,MouseButtonEvent,
                        MouseButtonDownEvent,MouseButtonUpEvent,MouseDoubleClickEvent)

                cls._classes[cls.MOUSE_MOVE]=MouseMoveEvent
                cls._classes[cls.MOUSE_WHEEL]=MouseWheelEvent
                cls._classes[cls.MOUSE_WHEEL_UP]=MouseWheelUpEvent
                cls._classes[cls.MOUSE_WHEEL_DOWN]=MouseWheelDownEvent
                cls._classes[cls.MOUSE_BUTTON]=MouseButtonEvent
                cls._classes[cls.MOUSE_PRESS]=MouseButtonDownEvent
                cls._classes[cls.MOUSE_RELEASE]=MouseButtonUpEvent
                cls._classes[cls.MOUSE_DOUBLE_CLICK]=MouseDoubleClickEvent

            if 'keyboard' in deviceModulesAvailable:
                from ioHub.devices import (KeyboardKeyEvent, KeyboardPressEvent,
                        KeyboardReleaseEvent,KeyboardCharEvent)

                cls._classes[cls.KEYBOARD_INPUT]=KeyboardKeyEvent
                cls._classes[cls.KEYBOARD_PRESS]=KeyboardPressEvent
                cls._classes[cls.KEYBOARD_RELEASE]=KeyboardReleaseEvent
                cls._classes[cls.KEYBOARD_INPUT]=KeyboardKeyEvent
                cls._classes[cls.KEYBOARD_PRESS]=KeyboardPressEvent
                cls._classes[cls.KEYBOARD_CHAR]=KeyboardCharEvent

            if 'gamepad' in deviceModulesAvailable:
                from ioHub.devices import GamePadStateChangeEvent,GamePadDisconnectEvent#,GamePadButtonEvent,
#                                           GamePadThumbStickEvent,GamePadTriggerEvent)
                cls._classes[cls.GAMEPAD_EVENT]=GamePadStateChangeEvent
                cls._classes[cls.GAMEPAD_DISCONNECT_EVENT]=GamePadDisconnectEvent
 
            if 'daq' in deviceModulesAvailable:
                from ioHub.devices import DAMultiChannelInputEvent
                cls._classes[cls.DA_MULTI_CHANNEL_INPUT]=DAMultiChannelInputEvent

#            if 'parallelPort' in deviceModulesAvailable:
#                from ioHub.devices import ParallelPortEvent
#                cls._classes[cls.PARALLEL_PORT_INPUT]=ParallelPortEvent

#            if 'serial' in deviceModulesAvailable:
#                from ioHub.devices import SerialInputEvent
#                cls._classes[cls.SERIAL_INPUT]=SerialInputEvent

#            if 'filter' in deviceModulesAvailable:
#                from ioHub.devices import GenericFilterEvent
#                cls._classes[cls.FILTER_EVENT]=GenericFilterEvent

            # update classes dict with v,k pairs
            cls._classes.update(dict([(kls,klsname) for klsname,kls in cls._classes.iteritems()]))

EventConstants.initialize()

class DeviceConstants(Constants):
    OTHER = 1
    KEYBOARD = 20
    MOUSE = 30
#    KB_MOUSE_COMBO = 25
    EYE_TRACKER = 50
    XINPUT= 70
    GAMEPAD=80
#    PARALLEL_PORT = 102
#    SERIAL=104
    DAQ = 120
#    MBED=130
    EXPERIMENT = 150
    DISPLAY = 190
    COMPUTER = 200
#    FILTER = 210
#    STAMPE_FILTER=219

    @classmethod
    def addClassMappings(cls):
        if cls._classes is None:
            cls._classes={}
            from ioHub.devices import deviceModulesAvailable

            if 'eyetracker' in deviceModulesAvailable:
                from ioHub.devices.eyeTracker import EyeTrackerDevice
                cls._classes[cls.EYE_TRACKER]=EyeTrackerDevice

            if 'experiment' in deviceModulesAvailable:
                from ioHub.devices import ExperimentDevice
                cls._classes[cls.EXPERIMENT]=ExperimentDevice

            if 'mouse' in deviceModulesAvailable:
                from ioHub.devices import Mouse
                cls._classes[cls.MOUSE]=Mouse

            if 'keyboard' in deviceModulesAvailable:
                from ioHub.devices import Keyboard
                cls._classes[cls.KEYBOARD]=Keyboard

            if 'daq' in deviceModulesAvailable:
                from ioHub.devices import DAQDevice
                cls._classes[cls.DAQ]=DAQDevice

            if 'display' in deviceModulesAvailable:
                from ioHub.devices import Display
                cls._classes[cls.DISPLAY]=Display

#            if 'parallelPort' in deviceModulesAvailable:
#                from ioHub.devices import ParallelPort
#                cls._classes[cls.PARALLEL_PORT]=ParallelPort

#            if 'serial' in deviceModulesAvailable:
#                from ioHub.devices import SerialIO
#                cls._classes[cls.SERIAL]=SerialIO

#            if 'filter' in deviceModulesAvailable:
#                from ioHub.devices import StampeFilter
#                cls._classes[cls.FILTER]=StampeFilter

#            if 'mbed' in deviceModulesAvailable:
#                from ioHub.devices import MBED1768
#                cls._classes[cls.MBED] = MBED1768

            # update classes dict with v,k pairs
            cls._classes.update(dict([(kls,klsname) for klsname,kls in cls._classes.iteritems()]))

DeviceConstants.initialize()

class MouseConstants(Constants):
    MOUSE_BUTTON_NONE=0
    MOUSE_BUTTON_LEFT=1
    MOUSE_BUTTON_RIGHT=2
    MOUSE_BUTTON_MIDDLE=4

    MOUSE_BUTTON_STATE_RELEASED=8 # event has a  button released state
    MOUSE_BUTTON_STATE_PRESSED=16 # event has a  button pressed state
    MOUSE_BUTTON_STATE_DOUBLE_CLICK=32 # a button double click event

MouseConstants.initialize()

class AsciiConstants(Constants):
    # Mainly from the pyHook lookup Table, some from Pyglet

    BACKSPACE = 0x08
    TAB = 0x09
    LINEFEED = 0x0A
    CLEAR = 0x0B
    RETURN = 0x0D
    SYSREQ = 0x15
    ESCAPE = 0x1B

    SPACE = 0x20
    EXCLAMATION = 0x21
    DOUBLEQUOTE = 0x22
    POUND = 0x23
    DOLLAR = 0x24
    PERCENT = 0x25
    AMPERSAND = 0x26
    APOSTROPHE = 0x27
    PARENLEFT = 0x28
    PARENRIGHT = 0x29
    ASTERISK = 0x2A
    PLUS = 0x2B
    COMMA = 0x2C
    MINUS = 0x2D
    PERIOD = 0x2E
    SLASH = 0x2F

    n0_=0x30
    n1_=0x31
    n2_=0x32
    n3_=0x33
    n4_=0x34
    n5_=0x35
    n6_=0x36
    n7_=0x37
    n8_=0x38
    n9_=0x39

    COLON = 0x3A
    SEMICOLON = 0x3B
    LESS = 0x3C
    EQUAL = 0x3D
    GREATER = 0x3E
    QUESTION = 0x3F
    AT = 0x40

    A=0x41
    B=0x42
    C=0x43
    D=0x44
    E=0x45
    F=0x46
    G=0x47
    H=0x48
    I=0x49
    J=0x4A
    K=0x4B
    L=0x4C
    M=0x4D
    N=0x4E
    O=0x4F
    P=0x50
    Q=0x51
    R=0x52
    S=0x53
    T=0x54
    U=0x55
    V=0x56
    W=0x57
    X=0x58
    Y=0x59
    Z=0x5A

    BRACKETLEFT = 0x5B
    BACKSLASH = 0x5C
    BRACKETRIGHT = 0x5D
    ASCIICIRCUM = 0x5E
    UNDERSCORE = 0x5F
    GRAVE = 0x60

    a = 0x61
    b = 0x62
    c = 0x63
    d = 0x64
    e = 0x65
    f = 0x66
    g = 0x67
    h = 0x68
    i = 0x69
    j = 0x6A
    k = 0x6B
    l = 0x6C
    m = 0x6D
    n = 0x6E
    o = 0x6F
    p = 0x70
    q = 0x71
    r = 0x72
    s = 0x73
    t = 0x74
    u = 0x75
    v = 0x76
    w = 0x77
    x = 0x78
    y = 0x79
    z = 0x7A

    BRACELEFT = 0x7B
    BAR = 0x7C
    BRACERIGHT = 0x7D
    ASCIITILDE = 0x7E

    @classmethod
    def getName(cls,id):
        return cls._names.get(id,None)

AsciiConstants.initialize()

class VirtualKeyCodes(Constants):
    # Mainly from the pyHook lookup Table, some from Pyglet
    VK_CANCEL  =  0x03
    VK_BACK  =  0x08
    VK_TAB  =  0x09
    VK_CLEAR  =  0x0C
    VK_RETURN  =  0x0D

    VK_SHIFT  =  0x10
    VK_CONTROL  =  0x11
    VK_MENU  =  0x12
    VK_PAUSE  =  0x13
    VK_CAPITAL  =  0x14
    VK_HANGUL  =  0x15
    VK_JUNJA  =  0x17
    VK_FINAL  =  0x18
    VK_HANJA  =  0x19
    VK_ESCAPE  =  0x1B
    VK_CONVERT  =  0x1C
    VK_NONCONVERT  =  0x1D
    VK_ACCEPT  =  0x1E
    VK_MODECHANGE  =  0x1F

    VK_SPACE  =  0x20
    VK_PAGE_UP  =  0x21
    VK_PAGE_DOWN  =  0x22
    VK_END  =  0x23
    VK_HOME  =  0x24
    VK_LEFT  =  0x25
    VK_UP  =  0x26
    VK_RIGHT  =  0x27
    VK_DOWN  =  0x28
    VK_SELECT  =  0x29
    VK_PRINT  =  0x2A
    VK_EXECUTE  =  0x2B
    VK_PRINT_SCREEN  =  0x2C
    VK_INSERT  =  0x2D
    VK_DELETE  =  0x2E
    VK_HELP  =  0x2F

    VK_LWIN  =  0x5B
    VK_RWIN  =  0x5C
    VK_APPS  =  0x5D

    VK_NUMPAD0  =  0x60
    VK_NUMPAD1  =  0x61
    VK_NUMPAD2  =  0x62
    VK_NUMPAD3  =  0x63
    VK_NUMPAD4  =  0x64
    VK_NUMPAD5  =  0x65
    VK_NUMPAD6  =  0x66
    VK_NUMPAD7  =  0x67
    VK_NUMPAD8  =  0x68
    VK_NUMPAD9  =  0x69
    VK_MULTIPLY  =  0x6A
    VK_ADD  =  0x6B
    VK_SEPARATOR  =  0x6C
    VK_SUBTRACT  =  0x6D
    VK_DECIMAL  =  0x6E
    VK_DIVIDE  =  0x6F

    VK_F1  =  0x70
    VK_F2  =  0x71
    VK_F3  =  0x72
    VK_F4  =  0x73
    VK_F5  =  0x74
    VK_F6  =  0x75
    VK_F7  =  0x76
    VK_F8  =  0x77
    VK_F9  =  0x78
    VK_F10  =  0x79
    VK_F11  =  0x7A
    VK_F12  =  0x7B
    VK_F13  =  0x7C
    VK_F14  =  0x7D
    VK_F15  =  0x7E
    VK_F16  =  0x7F
    VK_F17  =  0x80
    VK_F18  =  0x81
    VK_F19  =  0x82
    VK_F20  =  0x83
    VK_F21  =  0x84
    VK_F22  =  0x85
    VK_F23  =  0x86
    VK_F24  =  0x87

    VK_NUMLOCK  =  0x90
    VK_SCROLL  =  0x91

    VK_LSHIFT  =  0xA0
    VK_RSHIFT  =  0xA1
    VK_LCONTROL  =  0xA2
    VK_RCONTROL  =  0xA3
    VK_LMENU  =  0xA4
    VK_RMENU  =  0xA5
    VK_BROWSER_BACK  =  0xA6
    VK_BROWSER_FORWARD  =  0xA7
    VK_BROWSER_REFRESH  =  0xA8
    VK_BROWSER_STOP  =  0xA9
    VK_BROWSER_SEARCH  =  0xAA
    VK_BROWSER_FAVORITES  =  0xAB
    VK_BROWSER_HOME  =  0xAC
    VK_VOLUME_MUTE  =  0xAD
    VK_VOLUME_DOWN  =  0xAE
    VK_VOLUME_UP  =  0xAF

    VK_MEDIA_NEXT_TRACK  =  0xB0
    VK_MEDIA_PREV_TRACK  =  0xB1
    VK_MEDIA_STOP  =  0xB2
    VK_MEDIA_PLAY_PAUSE  =  0xB3
    VK_LAUNCH_MAIL  =  0xB4
    VK_LAUNCH_MEDIA_SELECT  =  0xB5
    VK_LAUNCH_APP1  =  0xB6
    VK_LAUNCH_APP2  =  0xB7

    VK_PROCESSKEY  =  0xE5
    VK_PACKET  =  0xE7
    VK_ATTN  =  0xF6
    VK_CRSEL  =  0xF7
    VK_EXSEL  =  0xF8
    VK_EREOF  =  0xF9
    VK_PLAY  =  0xFA
    VK_ZOOM  =  0xFB
    VK_NONAME  =  0xFC
    VK_PA1  =  0xFD
    VK_OEM_CLEAR  =  0xFE

    @classmethod
    def getName(cls,id):
        return cls._names.get(id,None)


VirtualKeyCodes.initialize()

class ModifierKeyCodes(Constants):
    CONTROL_LEFT = 1
    CONTROL_RIGHT = 2
    SHIFT_LEFT = 4
    SHIFT_RIGHT = 8
    ALT_LEFT = MENU_LEFT = 16
    ALT_RIGHT = MENU_RIGHT = 32
    WIN_LEFT = 64

ModifierKeyCodes.initialize()
ModifierKeyCodes._keys.remove(ModifierKeyCodes.getID('UNDEFINED'))



class KeyboardConstants(Constants):
    '''
    Stores internal windows hook constants including hook types, mappings from virtual
    keycode name to value and value to name, and event type value to name.
    '''

    _virtualKeyCodes=VirtualKeyCodes()
    _asciiKeyCodes=AsciiConstants()
    _modifierCodes=ModifierKeyCodes()
      
    @classmethod
    def getName(cls,id):
        return cls._names.get(id,None)

    @classmethod
    def _getKeyNameAndModsForEvent(cls,keyEvent):

        mods= cls.getModifiersForEvent(keyEvent)

        vcode_name=KeyboardConstants._virtualKeyCodes.getName(keyEvent.KeyID)
        if vcode_name:
            return vcode_name[3:],mods

        if mods is None or ('CONTROL_LEFT' not in mods and 'CONTROL_RIGHT' not in mods):
            ascii_name=KeyboardConstants._asciiKeyCodes.getName(keyEvent.Ascii)
            if ascii_name:
                if ascii_name[-1] == '_': # it is a number between 0 and 9
                    return ascii_name[1],mods
                return ascii_name,mods

        # TODO: When key mapper falls to this stage, clean up OEM_XXXX mappings that pyHook has.

        return keyEvent.GetKey().upper(),mods


    @classmethod
    def getModifiersForEvent(cls,event):
        mods = event.Modifiers
        if mods == 0:
            return None

        modconstants=cls._modifierCodes
        modNameList=[]
        for k in modconstants._keys:
            mc=modconstants._names[k]
            if mods&k == k:
                modNameList.append(mc)
                mods=mods-k
                if mods==0:
                    return modNameList
        return modNameList

KeyboardConstants.initialize()

class EyeTrackerConstants(Constants):

    FILTER_LEVEL_OFF=0
    FILTER_LEVEL_1=1
    FILTER_LEVEL_2=2
    FILTER_LEVEL_3=3
    FILTER_LEVEL_4=4
    FILTER_LEVEL_5=5

    FILTER_FILE=10
    FILTER_NET=11
    FILTER_SERIAL=12
    FILTER_ANALOG=13
    FILTER_ALL=14

    LEFT_EYE=21
    RIGHT_EYE=22
    BINOCULAR=23
    UNKNOWN_MONOCULAR=24
    BINOCULAR_AVERAGED=25
    SIMULATED_MONOCULAR=26
    SIMULATED_BINOCULAR=26
    ARTIFICIAL_MONOCULAR_EYE=28
    ARTIFICIAL_BINOCULAR=29

    H3_POINTS=40
    V3_POINTS=41
    HV3_POINTS=42
    HV5_POINTS=43
    HV9_POINTS=44
    HV13_POINTS=45

    PUPIL_CR_TRACKING=50
    PUPIL_ONLY_TRACKING=51

    ELLIPSE_FIT=60
    CENTROID_FIT=61

    PUPIL_AREA = 70
    PUPIL_DIAMETER = 71
    PUPIL_WIDTH = 72
    PUPIL_HEIGHT = 73
    PUPIL_MAJOR_AXIS = 74
    PUPIL_MINOR_AXIS = 75
    PUPIL_RADIUS = 76
    PUPIL_HEIGHT = 77
    PUPIL_WIDTH= 78

    AUTO_CALIBRATION_PACING=82
    MANUAL_CALIBRATION_PACING=81

    EYETRACKER_OK=100
    EYETRACKER_ERROR=101
    FUNCTIONALITY_NOT_SUPPORTED=102

EyeTrackerConstants.initialize()


#
## Gamepad related
#

class XInputBatteryTypeConstants(Constants):
    BATTERY_TYPE_DISCONNECTED = 0x00       # The device is not connected. 
    BATTERY_TYPE_WIRED = 0x01              # The device is a wired device and does not 
                                           # have a battery. 
    BATTERY_TYPE_ALKALINE = 0x02           # The device has an alkaline battery. 
    BATTERY_TYPE_NIMH = 0x03	               # The device has a nickel metal hydride battery. 
    BATTERY_TYPE_UNKNOWN = 0xFF            # The device has an unknown battery type. 
XInputBatteryTypeConstants.initialize() 
try:
    XInputBatteryTypeConstants._keys.remove(XInputBatteryTypeConstants.getID('UNDEFINED'))
except:
    pass

class XInputBatteryLevelConstants(Constants):
    # BatteryLevels
    BATTERY_LEVEL_EMPTY = 0x00
    BATTERY_LEVEL_LOW = 0x01
    BATTERY_LEVEL_MEDIUM = 0x02
    BATTERY_LEVEL_FULL = 0x03

XInputBatteryLevelConstants.initialize()
try:
    XInputBatteryLevelConstants._keys.remove(XInputBatteryLevelConstants.getID('UNDEFINED'))
except:
    pass

class XInputGamePadConstants(Constants):
    DPAD_UP = 0x0001
    DPAD_DOWN = 0x0002
    DPAD_LEFT = 0x0004
    DPAD_RIGHT = 0x0008
    START = 0x0010
    BACK = 0x0020
    LEFT_THUMB = 0x0040
    RIGHT_THUMB = 0x0080
    LEFT_SHOULDER = 0x0100
    RIGHT_SHOULDER = 0x0200
    A = 0x1000
    B = 0x2000
    X = 0x4000
    Y = 0x8000

    _batteryTypes=XInputBatteryTypeConstants()
    _batteryLevels=XInputBatteryLevelConstants()
    
XInputGamePadConstants.initialize()
try:
    XInputGamePadConstants._keys.remove(XInputGamePadConstants.getID('UNDEFINED'))
except:
    pass


#class SerialConstants(Constants):
#    import serial
#    XON=serial.XON
#    XOFF=serial.XOFF
#
#    CR=serial.CR
#    LF=serial.LF
#
#    PARITY_NONE=serial.PARITY_NONE
#    PARITY_EVEN=serial.PARITY_EVEN
#    PARITY_ODD=serial.PARITY_ODD
#    PARITY_MARK=serial.PARITY_MARK
#    PARITY_SPACE=serial.PARITY_SPACE
#
#    STOPBITS_ONE=serial.STOPBITS_ONE
#    STOPBITS_ONE_POINT_FIVE=serial.STOPBITS_ONE_POINT_FIVE
#    STOPBITS_TWO=serial.STOPBITS_TWO
#
#    FIVEBITS=serial.FIVEBITS
#    SIXBITS=serial.SIXBITS
#    SEVENBITS=serial.SEVENBITS
#    EIGHTBITS=serial.EIGHTBITS
#
#SerialConstants.initialize()
#SerialConstants._keys.remove(SerialConstants.getID('UNDEFINED'))
