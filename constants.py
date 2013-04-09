# -*- coding: utf-8 -*-
"""
Created on Thu Nov 08 15:13:55 2012

@author: Sol
"""
try:
    
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
        KEYBOARD_KEY=21
        KEYBOARD_PRESS=22
        KEYBOARD_RELEASE=23
        KEYBOARD_CHAR=24
    
        MOUSE_INPUT=30
        MOUSE_BUTTON=31
        MOUSE_BUTTON_PRESS=32
        MOUSE_BUTTON_RELEASE=33
        # deprecated for MOUSE_MULTI_CLICK in 0.6RC1
        MOUSE_DOUBLE_CLICK=34
        MOUSE_MULTI_CLICK=34
        MOUSE_SCROLL=35
        MOUSE_MOVE=36
        MOUSE_DRAG=37
        
        EYETRACKER=50
        MONOCULAR_EYE_SAMPLE=51
        BINOCULAR_EYE_SAMPLE=52
        FIXATION_START=53
        FIXATION_END=54
        SACCADE_START=55
        SACCADE_END=56
        BLINK_START=57
        BLINK_END=58
    
        GAMEPAD_STATE_CHANGE=81
        GAMEPAD_DISCONNECT=82
    
        MULTI_CHANNEL_ANALOG_INPUT=122
    
        MESSAGE=151
    
        @classmethod
        def addClassMappings(cls):
            if cls._classes is None:
                import ioHub
                
                cls._classes={}
    
                for event_constant_string,event_class in ioHub.devices.loadedEventClasses.iteritems():
                    cls._classes[getattr(cls,event_constant_string)]=event_class
    
    
                cls._classes.update(dict([(kls,klsname) for klsname,kls in cls._classes.iteritems()]))
    
    EventConstants.initialize()
    
    class DeviceConstants(Constants):
        OTHER = 1
        KEYBOARD = 20
        MOUSE = 30
    #    KB_MOUSE_COMBO = 25
        EYETRACKER = 50
        XINPUT= 70
        GAMEPAD=80
    #    PARALLEL_PORT = 102
    #    SERIAL=104
        ANALOGINPUT = 120
    #    MBED=130
        EXPERIMENT = 150
        DISPLAY = 190
        COMPUTER = 200
    #    FILTER = 210
    #    STAMPE_FILTER=219
    
        @classmethod
        def addClassMappings(cls):
            if cls._classes is None:
                import ioHub
                
                cls._classes={}
    
                for device_constant_string,device_class in ioHub.devices.loadedDeviceClasses.iteritems():
                    cls._classes[getattr(cls,device_constant_string)]=device_class
    
                # update classes dict with v,k pairs
                cls._classes.update(dict([(kls,klsname) for klsname,kls in cls._classes.iteritems()]))
    
    DeviceConstants.initialize()
    
    class MouseConstants(Constants):
        MOUSE_BUTTON_NONE=0
        MOUSE_BUTTON_LEFT=1
        MOUSE_BUTTON_RIGHT=2
        MOUSE_BUTTON_MIDDLE=4
        MOUSE_BUTTON_4=8
        MOUSE_BUTTON_5=16
        MOUSE_BUTTON_6=32
        MOUSE_BUTTON_7=64
        MOUSE_BUTTON_8=128
        MOUSE_BUTTON_9=256
    
        MOUSE_BUTTON_STATE_RELEASED=10 # event has a  button released state
        MOUSE_BUTTON_STATE_PRESSED=11 # event has a  button pressed state
        MOUSE_BUTTON_STATE_DOUBLE_CLICK=12 # a button double click event
        MOUSE_BUTTON_STATE_MULTI_CLICK=12 # a button double click event
    
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
    
    import sys
    print sys.platform
    
    if sys.platform == 'win32':
        
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
        
            VK_LEFT_CMD  =  0x5B
            VK_RIGHT_CMD  =  0x5C
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
        
            VK_LEFT_SHIFT  =  0xA0
            VK_RIGHT_SHIFT  =  0xA1
            VK_LEFT_CTRL  =  0xA2
            VK_RIGHT_CTRL  =  0xA3
            VK_LEFT_ALT  =  0xA4
            VK_RIGHT_ALT  =  0xA5
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

    if sys.platform == 'linux2':
        
        class VirtualKeyCodes(Constants):
            # Mainly from the pyHook lookup Table, some from Pyglet
#            VK_CANCEL  =  0x03
#            VK_BACK  =  0x08
#            VK_TAB  =  0x09
#            VK_CLEAR  =  0x0C
#            VK_RETURN  =  0x0D
#        
#            VK_SHIFT  =  0x10
#            VK_CONTROL  =  0x11
#            VK_MENU  =  0x12
#            VK_PAUSE  =  0x13
#            VK_CAPITAL  =  0x14
#            VK_HANGUL  =  0x15
#            VK_JUNJA  =  0x17
#            VK_FINAL  =  0x18
#            VK_HANJA  =  0x19
#            VK_ESCAPE  =  0x1B
#            VK_CONVERT  =  0x1C
#            VK_NONCONVERT  =  0x1D
#            VK_ACCEPT  =  0x1E
#            VK_MODECHANGE  =  0x1F
#        
#            VK_SPACE  =  0x20
#            VK_PAGE_UP  =  0x21
#            VK_PAGE_DOWN  =  0x22
#            VK_END  =  0x23
#            VK_HOME  =  0x24
#            VK_LEFT  =  0x25
#            VK_UP  =  0x26
#            VK_RIGHT  =  0x27
#            VK_DOWN  =  0x28
#            VK_SELECT  =  0x29
#            VK_PRINT  =  0x2A
#            VK_EXECUTE  =  0x2B
#            VK_PRINT_SCREEN  =  0x2C
#            VK_INSERT  =  0x2D
#            VK_DELETE  =  0x2E
#            VK_HELP  =  0x2F
#        
#            VK_LEFT_CMD  =  0x5B
#            VK_RIGHT_CMD  =  0x5C
#            VK_APPS  =  0x5D
#        
#            VK_NUMPAD0  =  0x60
#            VK_NUMPAD1  =  0x61
#            VK_NUMPAD2  =  0x62
#            VK_NUMPAD3  =  0x63
#            VK_NUMPAD4  =  0x64
#            VK_NUMPAD5  =  0x65
#            VK_NUMPAD6  =  0x66
#            VK_NUMPAD7  =  0x67
#            VK_NUMPAD8  =  0x68
#            VK_NUMPAD9  =  0x69
#            VK_MULTIPLY  =  0x6A
#            VK_ADD  =  0x6B
#            VK_SEPARATOR  =  0x6C
#            VK_SUBTRACT  =  0x6D
#            VK_DECIMAL  =  0x6E
#            VK_DIVIDE  =  0x6F
#        
#            VK_F1  =  0x70
#            VK_F2  =  0x71
#            VK_F3  =  0x72
#            VK_F4  =  0x73
#            VK_F5  =  0x74
#            VK_F6  =  0x75
#            VK_F7  =  0x76
#            VK_F8  =  0x77
#            VK_F9  =  0x78
#            VK_F10  =  0x79
#            VK_F11  =  0x7A
#            VK_F12  =  0x7B
#            VK_F13  =  0x7C
#            VK_F14  =  0x7D
#            VK_F15  =  0x7E
#            VK_F16  =  0x7F
#            VK_F17  =  0x80
#            VK_F18  =  0x81
#            VK_F19  =  0x82
#            VK_F20  =  0x83
#            VK_F21  =  0x84
#            VK_F22  =  0x85
#            VK_F23  =  0x86
#            VK_F24  =  0x87
#        
#            VK_NUMLOCK  =  0x90
#            VK_SCROLL  =  0x91
#        
#            VK_LEFT_SHIFT  =  0xA0
#            VK_RIGHT_SHIFT  =  0xA1
#            VK_LEFT_CTRL  =  0xA2
#            VK_RIGHT_CTRL  =  0xA3
#            VK_LEFT_ALT  =  0xA4
#            VK_RIGHT_ALT  =  0xA5
#            VK_BROWSER_BACK  =  0xA6
#            VK_BROWSER_FORWARD  =  0xA7
#            VK_BROWSER_REFRESH  =  0xA8
#            VK_BROWSER_STOP  =  0xA9
#            VK_BROWSER_SEARCH  =  0xAA
#            VK_BROWSER_FAVORITES  =  0xAB
#            VK_BROWSER_HOME  =  0xAC
#            VK_VOLUME_MUTE  =  0xAD
#            VK_VOLUME_DOWN  =  0xAE
#            VK_VOLUME_UP  =  0xAF
#        
#            VK_MEDIA_NEXT_TRACK  =  0xB0
#            VK_MEDIA_PREV_TRACK  =  0xB1
#            VK_MEDIA_STOP  =  0xB2
#            VK_MEDIA_PLAY_PAUSE  =  0xB3
#            VK_LAUNCH_MAIL  =  0xB4
#            VK_LAUNCH_MEDIA_SELECT  =  0xB5
#            VK_LAUNCH_APP1  =  0xB6
#            VK_LAUNCH_APP2  =  0xB7
#        
#            VK_PROCESSKEY  =  0xE5
#            VK_PACKET  =  0xE7
#            VK_ATTN  =  0xF6
#            VK_CRSEL  =  0xF7
#            VK_EXSEL  =  0xF8
#            VK_EREOF  =  0xF9
#            VK_PLAY  =  0xFA
#            VK_ZOOM  =  0xFB
#            VK_NONAME  =  0xFC
#            VK_PA1  =  0xFD
#            VK_OEM_CLEAR  =  0xFE
        
            @classmethod
            def getName(cls,id):
                return cls._names.get(id,None)
        
        VirtualKeyCodes.initialize()


    
    if sys.platform == 'darwin':
        class UnicodeChars(Constants):
            TAB= u"\u0009" # "Tab"
            ESCAPE= u"\u001b" # "Escape"
            UP= u"\uf700" # "Up"
            DOWN= u"\uF701" # "Down"
            LEFT= u"\uF702" # "Left"
            RIGHT= u"\uF703" # "Right"
            F1= u"\uF704" # "F1"
            F2= u"\uF705" # "F2"
            F3= u"\uF706" # "F3"
            F4= u"\uF707" # "F4"
            F5= u"\uF708" # "F5"
            F6= u"\uF709" # "F6"
            F7= u"\uF70A" # "F7"
            F8= u"\uF70B" # "F8"
            F9= u"\uF70C" # "F9"
            F10= u"\uF70D" # "F10"
            F11= u"\uF70E" # "F11"
            F12= u"\uF70F" # "F12"
            F13= u"\uF710" # "F13"
            F14= u"\uF711" # "F14"
            F15= u"\uF712" # "F15"
            F16= u"\uF713" # "F16"
            F17= u"\uF714" # "F17"
            F18= u"\uF715" # "F18"
            F19= u"\uF716" # "F19"
            F20= u"\uF717" # "F20"
            F21= u"\uF718" # "F21"
            F22= u"\uF719" # "F22"
            F23= u"\uF71A" # "F23"
            F24= u"\uF71B" # "F24"
            F25= u"\uF71C" # "F25"
            F26= u"\uF71D" # "F26"
            F27= u"\uF71E" # "F27"
            F28= u"\uF71F" # "F28"
            F29= u"\uF720" # "F29"
            F30= u"\uF721" # "F30"
            F31= u"\uF722" # "F31"
            F32= u"\uF723" # "F32"
            F33= u"\uF724" # "F33"
            F34= u"\uF725" # "F34"
            F35= u"\uF726" # "F35"
            INSERT= u"\uF727" # "Insert"
            DELETE= u"\uF728" # "Delete"
            HOME= u"\uF729" # "Home"
            BEGIN= u"\uF72A" # "Begin"
            END= u"\uF72B" # "End"
            PAGE_UP= u"\uF72C" # "PageUp"
            PAGE_DOWN= u"\uF72D" # "PageDown"
            PRINT= u"\uF72E" # "PrintScreen"
            SCROLL_LOCK= u"\uF72F" # "ScrollLock"
            PAUSE= u"\uF730" # "Pause"
            SYSREQ= u"\uF731" # "SysReq"
            BREAK= u"\uF732" # "Break"
            RESET= u"\uF733" # "Reset"
            STOP= u"\uF734" # "Stop"
            MENU= u"\uF735" # "Menu"
            USER= u"\uF736" # "User"
            SYSTEM= u"\uF737" # "System"
            PRINT= u"\uF738" # "Print"
            CLEAR_LINE= u"\uF739" # "ClearLine"
            CLEAR= u"\uF73A" # "ClearDisplay"
            INSERT_LINE= u"\uF73B" # "InsertLine"
            DELETE_LINE= u"\uF73C" # "DeleteLine"
            INSERT= u"\uF73D" # "InsertChar"
            DELETE= u"\uF73E" # "DeleteChar"
            PREV= u"\uF73F" # "Prev"
            NEXT= u"\uF740" # "Next"
            SELECT= u"\uF741" # "Select"
            EXECUTE= u"\uF742" # "Execute"
            UNDO= u"\uF743" # "Undo"
            REDO= u"\uF744" # "Redo"
            FIND= u"\uF745" # "Find"
            HELP= u"\uF746" # "Help"
            MODE= u"\uF747" # "ModeSwitch"
    
            @classmethod
            def getName(cls,id):
                return cls._names.get(id,None)
        
        UnicodeChars.initialize()

        class VirtualKeyCodes(Constants):
            VK_RETURN                    = 0x24
            VK_TAB                       = 0x30
            VK_SPACE                     = 0x31
            VK_BACK                      = 0x33
            VK_ESCAPE                    = 0x35
            VK_FUNCTION                  = 0x3F
            VK_F17                       = 0x40
            VK_VOLUME_UP                 = 0x48
            VK_VOLUME_DOWN               = 0x49
            VK_VOLUME_MUTE               = 0x4A
            VK_F18                       = 0x4F
            VK_F19                       = 0x50
            VK_F20                       = 0x5A
            VK_F5                        = 0x60
            VK_F6                        = 0x61
            VK_F7                        = 0x62
            VK_F3                        = 0x63
            VK_F8                        = 0x64
            VK_F9                        = 0x65
            VK_F11                       = 0x67
            VK_F13                       = 0x69
            VK_F16                       = 0x6A
            VK_F14                       = 0x6B
            VK_F10                       = 0x6D
            VK_F12                       = 0x6F
            VK_F15                       = 0x71
            VK_HELP                      = 0x72
            VK_HOME                      = 0x73
            VK_PAGE_UP                   = 0x74
            VK_DELETE                    = 0x75
            VK_F4                        = 0x76
            VK_END                       = 0x77
            VK_F2                        = 0x78
            VK_PAGE_DOWN                 = 0x7D
            VK_LEFT                      = 0x7B
            VK_UP                        = 0x7E
            VK_RIGHT                     = 0x7C
            VK_DOWN                      = 0x7D      
            VK_F1                        = 0x7A
    
            @classmethod
            def getName(cls,id):
                return cls._names.get(id,None)
        
        VirtualKeyCodes.initialize()
    
    class ModifierKeyCodes(Constants):
        CONTROL_LEFT = 1
        CONTROL_RIGHT = 2
        SHIFT_LEFT = 4
        SHIFT_RIGHT = 8
        ALT_LEFT = 16
        ALT_RIGHT = 32
        COMMAND_LEFT = 64
        COMMAND_RIGHT = 128
        CAPLOCKS = 256
        MOD_SHIFT=512
        MOD_ALT=1024
        MOD_CTRL=2048
        MOD_CMD=4096
        
    ModifierKeyCodes.initialize()
    ModifierKeyCodes._keys.remove(ModifierKeyCodes.getID('UNDEFINED'))
    
    class KeyboardConstants(Constants):
        '''
        Stores internal windows hook constants including hook types, mappings from virtual
        keycode name to value and value to name, and event type value to name.
        '''
    
        _virtualKeyCodes=VirtualKeyCodes()
        
        if sys.platform == 'win32':
            _asciiKeyCodes=AsciiConstants()
        if sys.platform == 'darwin':
            _unicodeChars=UnicodeChars()
            
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
        FILTER_OFF=0
        FILTER_LEVEL_1=1
        FILTER_LEVEL_2=2
        FILTER_LEVEL_3=3
        FILTER_LEVEL_4=4
        FILTER_LEVEL_5=5
        FILTER_ON=9
    
        FILTER_FILE=10
        FILTER_NET=11
        FILTER_SERIAL=12
        FILTER_ANALOG=13
        FILTER_ALL=14
    
        LEFT_EYE=21
        RIGHT_EYE=22
        UNKNOWN_MONOCULAR=24
        BINOCULAR=23
        BINOCULAR_AVERAGED=25
        BINOCULAR_CUSTOM=26
        SIMULATED_MONOCULAR=27
        SIMULATED_BINOCULAR=28
    
        NO_POINTS=40
        ONE_POINT=41
        TWO_POINTS=42
        THREE_POINTS=43
        FOUR_POINTS=44
        FIVE_POINTS=45
        SEVEN_POINTS=47
        EIGHT_POINTS=48
        NINE_POINTS=49
        THIRTEEN_POINTS=53
        SIXTEEN_POINTS=56
        TWENTYFIVE_POINTS=65
        CUSTOM_POINTS=69
        
        PUPIL_AREA = 70
        PUPIL_DIAMETER = 71
        PUPIL_WIDTH = 72
        PUPIL_HEIGHT = 73
        PUPIL_MAJOR_AXIS = 74
        PUPIL_MINOR_AXIS = 75
        PUPIL_RADIUS = 76
        PUPIL_DIAMETER_MM = 77
        PUPIL_WIDTH_MM = 78
        PUPIL_HEIGHT_MM = 79
        PUPIL_MAJOR_AXIS_MM = 80
        PUPIL_MINOR_AXIS_MM = 81
        PUPIL_RADIUS_MM = 82
    
        AUTO_CALIBRATION_PACING=90
        MANUAL_CALIBRATION_PACING=91
    
        DEFAULT_SETUP_PROCEDURE=100
        TRACKER_FEEDBACK_STATE=101
        CALIBRATION_STATE=102
        VALIDATION_STATE=103
        DRIFT_CORRECTION_STATE=104
        
        CIRCLE_TARGET=121
        CROSSHAIR_TARGET=122
        IMAGE_TARGET=123
        MOVIE_TARGET=124
    
        CALIBRATION_HORZ_1D=130
        CALIBRATION_VERT_1D=131
        CALIBRATION_2D=132
        CALIBRATION_3D=133
    
        PUPIL_CR_TRACKING=140
        PUPIL_ONLY_TRACKING=141
    
        ELLIPSE_FIT=146
        CIRCLE_FIT = 147
        CENTROID_FIT = 148
    
        EYETRACKER_OK=200
        # EYETRACKER_ERROR deprecated for EYETRACKER_UNDEFINED_ERROR
        EYETRACKER_ERROR=201
        EYETRACKER_UNDEFINED_ERROR=201
        # FUNCTIONALITY_NOT_SUPPORTED deprecated for 
        # EYETRACKER_INTERFACE_METHOD_NOT_SUPPORTED
        FUNCTIONALITY_NOT_SUPPORTED=202
        EYETRACKER_INTERFACE_METHOD_NOT_SUPPORTED=202
        EYETRACKER_CALIBRATION_ERROR=203
        EYETRACKER_VALIDATION_ERROR=204
        EYETRACKER_SETUP_ABORTED=205
        EYETRACKER_NOT_CONNECTED=206
        EYETRACKER_MODEL_NOT_SUPPORTED=207
        EYETRACKER_RECEIVED_INVALID_INPUT=208
        
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
            
except:
    from . import printExceptionDetailsToStdErr
    printExceptionDetailsToStdErr()
    
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
