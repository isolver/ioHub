# --------------------------------------------------------------------------
# Copyright 2012 Orson Peters. All rights reserved.
#
# Redistribution of this work, with or without modification, is permitted if
# Orson Peters is attributed as the original author or licensor of
# this work, but not in any way that suggests that Orson Peters endorses
# you or your use of the work.
#
# This work is provided by Orson Peters "as is" and any express or implied
# warranties are disclaimed. Orson Peters is not liable for any damage
# arising in any way out of the use of this work.
# --------------------------------------------------------------------------


__doc__ = """Python bindings for glfw 2.7.5 using ctypes.

These bindings are a thin layer over the raw ctypes bindings to the GLFW shared
library. No ctypes code is needed by the user, everything has a pure Python
interface.

Everything works as described in the GLFW reference manual, with a few changes:

 * All glfwFooBar functions should be accessed like glfw.FooBar. All
   GLFW_FOO_BAR constants should be accessed like glfw.FOO_BAR.
 * The threading and image loading functions have been removed from the API. The
   same goes for related defines, constants, etc. This was done because they are
   a deprecated featureset from the GLFW library, removed in version 3.0. On top
   of that, the threading is not very useful for Python, even potentially
   dangerous with the GIL. The image loading is hardly useful either, because it
   only loads TARGA files, and better image loading options exist for Python.
 * The functions glfwGetTime, glfwSetTime and glfwSleep are removed because they
   are unnecesarry in Python (use the `time` module).
 * The function glfwGetProcAddress returns the memory location as an integer.
 * Functions returning arguments by having types passed in as a pointer now
   return the values directly without accepting the argument. For example
   `void glfwGetVersion(int *major, int *minor, int *rev);` is wrapped as a
   function called glfw.GetVersion() taking no arguments and returning a tuple
   of 3 integers, respectively major, minor and rev. Similarly,
   glfw.GetWindowSize() returns a tuple of two integers giving the size of the
   window.
 * All of glfwGetVideoModes's arguments have been removed, and it simply returns
   a list of video modes.
 * The GLFWvidmode struct has been replaced with the class vidmode, who's
   member variables have the same names and meaning as GLFWvidmode's.
 * Type/value checking has been added to some functions, for example passing a
   negative size into glfw.OpenWindow raises a ValueError, and passing a list
   into glfw.SetWindowTitle results in a TypeError being raised. This is done
   because GLFW 2.7.5 has no error messages, and thus this will ease debugging.
 * glfw.Init does not return an integer indicating the status, instead it
   always returns None and raises an InitError if the initialization failed. The
   same goes for glfw.OpenWindow, except it raises OpeningWindowError.
 * The callback function typedefs have been removed. Instead, callback functions
   can be passed regular Python functions taking the appropriate number of
   arguments.
 * GLFW_KEY_SPACE is removed.
 * The functions/callbacks taking/returning either a latin-1 character or an
   integer in C take and return either a unicode or an int in the wrapper. Any
   integer value < 256 gets converted to a one-character unicode. This is the
   reason why GLFW_KEY_SPACE is removed - for unambigous checking. Otherwise the
   comparison key == GLFW_KEY_SPACE will fail when key == u" ", which is a hard
   situation to debug.
 * The callback set with glfw.SetCharCallback always gets called with a
   one-character unicode string and never with an integer value.
 * glfw.GetJoystickPos and glfw.GetJoystickButtons only take one parameter, the
   joystick id, and return a list of available data about respectively the axes
   positions and button states.
   
Other than the above changes everything works exactly as in the GLFW reference
manual.
"""

import inspect as _inspect
import ctypes as _ctypes
from ctypes.util import find_library as _find_library

# Python cross-version support
# We support a minimum of version 2.5 - it's final release was in August 2006,
# at the time of this writing that's over 5 years ago. Any older versions are
# not of any interest (not to mention that ctypes was not built-in until 2.5.)

import sys

if sys.version_info.major == 3:
    _unichr = chr
else:
    _unichr = unichr

    
if sys.version_info.major == 2 and sys.version_info.minor < 6:
    def _is_int(obj):
        """Returns True if obj is an int, else False."""
        
        return isinstance(obj, int)
    
    
    def _is_real(obj):
        """Returns True if obj is an int or float, else False."""
        
        return isinstance(obj, int) or isinstance(obj, float)
    
    
    def _is_callable_nargs(obj, nargs):
        """Returns True if obj is a callable taking nargs positional arguments, False otherwise.
        
        For builtins only the check for callable is made, since builtins can't be inspected for
        the amount of arguments they take.
        """
        
        try:
            _inspect.getcallargs(obj, *[None for _ in range(nargs)])
        except TypeError:
            # we can't inspect builtins, thus we can't reject them now
            # however we can do a simple "is callable" check
            if not (_inspect.isbuiltin(obj) and callable(obj)):
                return False
                
        return True
        
else:
    import numbers as _numbers
    import collections as _collections
    
    def _is_int(obj):
        """Returns True if obj has numbers.Integral as ABC, else False."""
        
        return isinstance(obj, _numbers.Integral)
        
        
    def _is_real(obj):
        """Returns True if obj has numbers.Real as ABC, else False."""
        
        return isinstance(obj, _numbers.Real)
        
        
    def _is_callable_nargs(obj, nargs):
        """Returns True if obj is a callable taking nargs positional arguments, False otherwise.
        
        For builtins only the check for callable is made, since builtins can't be inspected for
        the amount of arguments they take.
        """
        
        try:
            _inspect.getcallargs(obj, *[None for _ in range(nargs)])
        except TypeError:
            if not (_inspect.isbuiltin(obj) and isinstance(obj, _collections.Callable)):
                return False
                
        return True
        
del sys


##################
# header defines #
##################

# version info
VERSION_MAJOR = 2
VERSION_MINOR = 7
VERSION_REVISION = 5

GLFW_RELEASE = 0
GLFW_PRESS = 1

# keyboard key definitions: 8-bit ISO-8859-1 (Latin 1) encoding is used
# for printable keys (such as A-Z, 0-9 etc), and values above 256
# represent special (non-printable) keys (e.g. F1, Page Up etc)
KEY_UNKNOWN = -1
# KEY_SPACE = 32 # this has been ommited to make all keycodes outside of latin 1
                 # range so we can safely translate all keys < 256 with chr()
                 # without having to worry about users checking for KEY_SPACE
KEY_SPECIAL = 256
KEY_ESC = KEY_SPECIAL + 1
KEY_F1 = KEY_SPECIAL + 2
KEY_F2 = KEY_SPECIAL + 3
KEY_F3 = KEY_SPECIAL + 4
KEY_F4 = KEY_SPECIAL + 5
KEY_F5 = KEY_SPECIAL + 6
KEY_F6 = KEY_SPECIAL + 7
KEY_F7 = KEY_SPECIAL + 8
KEY_F8 = KEY_SPECIAL + 9
KEY_F9 = KEY_SPECIAL + 10
KEY_F10 = KEY_SPECIAL + 11
KEY_F11 = KEY_SPECIAL + 12
KEY_F12 = KEY_SPECIAL + 13
KEY_F13 = KEY_SPECIAL + 14
KEY_F14 = KEY_SPECIAL + 15
KEY_F15 = KEY_SPECIAL + 16
KEY_F16 = KEY_SPECIAL + 17
KEY_F17 = KEY_SPECIAL + 18
KEY_F18 = KEY_SPECIAL + 19
KEY_F19 = KEY_SPECIAL + 20
KEY_F20 = KEY_SPECIAL + 21
KEY_F21 = KEY_SPECIAL + 22
KEY_F22 = KEY_SPECIAL + 23
KEY_F23 = KEY_SPECIAL + 24
KEY_F24 = KEY_SPECIAL + 25
KEY_F25 = KEY_SPECIAL + 26
KEY_UP = KEY_SPECIAL + 27
KEY_DOWN = KEY_SPECIAL + 28
KEY_LEFT = KEY_SPECIAL + 29
KEY_RIGHT = KEY_SPECIAL + 30
KEY_LSHIFT = KEY_SPECIAL + 31
KEY_RSHIFT = KEY_SPECIAL + 32
KEY_LCTRL = KEY_SPECIAL + 33
KEY_RCTRL = KEY_SPECIAL + 34
KEY_LALT = KEY_SPECIAL + 35
KEY_RALT = KEY_SPECIAL + 36
KEY_TAB = KEY_SPECIAL + 37
KEY_ENTER = KEY_SPECIAL + 38
KEY_BACKSPACE = KEY_SPECIAL + 39
KEY_INSERT = KEY_SPECIAL + 40
KEY_DEL = KEY_SPECIAL + 41
KEY_PAGEUP = KEY_SPECIAL + 42
KEY_PAGEDOWN = KEY_SPECIAL + 43
KEY_HOME = KEY_SPECIAL + 44
KEY_END = KEY_SPECIAL + 45
KEY_KP_0 = KEY_SPECIAL + 46
KEY_KP_1 = KEY_SPECIAL + 47
KEY_KP_2 = KEY_SPECIAL + 48
KEY_KP_3 = KEY_SPECIAL + 49
KEY_KP_4 = KEY_SPECIAL + 50
KEY_KP_5 = KEY_SPECIAL + 51
KEY_KP_6 = KEY_SPECIAL + 52
KEY_KP_7 = KEY_SPECIAL + 53
KEY_KP_8 = KEY_SPECIAL + 54
KEY_KP_9 = KEY_SPECIAL + 55
KEY_KP_DIVIDE = KEY_SPECIAL + 56
KEY_KP_MULTIPLY = KEY_SPECIAL + 57
KEY_KP_SUBTRACT = KEY_SPECIAL + 58
KEY_KP_ADD = KEY_SPECIAL + 59
KEY_KP_DECIMAL = KEY_SPECIAL + 60
KEY_KP_EQUAL = KEY_SPECIAL + 61
KEY_KP_ENTER = KEY_SPECIAL + 62
KEY_KP_NUM_LOCK = KEY_SPECIAL + 63
KEY_CAPS_LOCK = KEY_SPECIAL + 64
KEY_SCROLL_LOCK = KEY_SPECIAL + 65
KEY_PAUSE = KEY_SPECIAL + 66
KEY_LSUPER = KEY_SPECIAL + 67
KEY_RSUPER = KEY_SPECIAL + 68
KEY_MENU = KEY_SPECIAL + 69
KEY_LAST = KEY_MENU

# mouse button definitions
MOUSE_BUTTON_1 = 0
MOUSE_BUTTON_2 = 1
MOUSE_BUTTON_3 = 2
MOUSE_BUTTON_4 = 3
MOUSE_BUTTON_5 = 4
MOUSE_BUTTON_6 = 5
MOUSE_BUTTON_7 = 6
MOUSE_BUTTON_8 = 7
MOUSE_BUTTON_LAST = MOUSE_BUTTON_8

# mouse button aliases
MOUSE_BUTTON_LEFT = MOUSE_BUTTON_1
MOUSE_BUTTON_RIGHT = MOUSE_BUTTON_2
MOUSE_BUTTON_MIDDLE = MOUSE_BUTTON_3

# joystick identifiers
JOYSTICK_1 = 0
JOYSTICK_2 = 1
JOYSTICK_3 = 2
JOYSTICK_4 = 3
JOYSTICK_5 = 4
JOYSTICK_6 = 5
JOYSTICK_7 = 6
JOYSTICK_8 = 7
JOYSTICK_9 = 8
JOYSTICK_10 = 9
JOYSTICK_11 = 10
JOYSTICK_12 = 11
JOYSTICK_13 = 12
JOYSTICK_14 = 13
JOYSTICK_15 = 14
JOYSTICK_16 = 15
JOYSTICK_LAST = JOYSTICK_16

# glfw.OpenWindow modes
WINDOW = 0x00010001
FULLSCREEN = 0x00010002

# glfw.GetWindowParam tokens
OPENED = 0x00020001
ACTIVE = 0x00020002
ICONIFIED = 0x00020003
ACCELERATED = 0x00020004
RED_BITS = 0x00020005
GREEN_BITS = 0x00020006
BLUE_BITS = 0x00020007
ALPHA_BITS = 0x00020008
DEPTH_BITS = 0x00020009
STENCIL_BITS = 0x0002000A

# the following constants are used for both glfw.GetWindowParam
# and glfw.OpenWindowHint
REFRESH_RATE = 0x0002000B
ACCUM_RED_BITS = 0x0002000C
ACCUM_GREEN_BITS = 0x0002000D
ACCUM_BLUE_BITS = 0x0002000E
ACCUM_ALPHA_BITS = 0x0002000F
AUX_BUFFERS = 0x00020010
STEREO = 0x00020011
WINDOW_NO_RESIZE = 0x00020012
FSAA_SAMPLES = 0x00020013
OPENGL_VERSION_MAJOR = 0x00020014
OPENGL_VERSION_MINOR = 0x00020015
OPENGL_FORWARD_COMPAT = 0x00020016
OPENGL_DEBUG_CONTEXT = 0x00020017
OPENGL_PROFILE = 0x00020018

# glfw.OPENGL_PROFILE tokens
OPENGL_CORE_PROFILE = 0x00050001
OPENGL_COMPAT_PROFILE = 0x00050002

# glfw.Enable/glfw.Disable tokens
MOUSE_CURSOR = 0x00030001
STICKY_KEYS = 0x00030002
STICKY_MOUSE_BUTTONS = 0x00030003
SYSTEM_KEYS = 0x00030004
KEY_REPEAT = 0x00030005
AUTO_POLL_EVENTS = 0x00030006

# glfw.GetJoystickParam tokens
PRESENT = 0x00050001
AXES = 0x00050002
BUTTONS = 0x00050003


##############
# structures #
##############

class vidmode(object):
    def __init__(self, Width, Height, RedBits, GreenBits, BlueBits):
        self.Width = Width
        self.Height = Height
        self.RedBits = RedBits
        self.GreenBits = GreenBits
        self.BlueBits = BlueBits
    
    def __repr__(self):
        return "glfw.vidmode(%d, %d, %d, %d, %d)" % (self.Width, self.Height, self.RedBits, self.GreenBits, self.BlueBits)
    
    # C vidmode struct
    class _struct(_ctypes.Structure):
        _fields_ = [
            ("Width", _ctypes.c_int),
            ("Height", _ctypes.c_int),
            ("RedBits", _ctypes.c_int),
            ("BlueBits", _ctypes.c_int),
            ("GreenBits", _ctypes.c_int),
        ]


#############
# functions #
#############

# First we define all the appropriate ctypes function definitions, then we write
# Python wrappers for all functions. We write wrapper functions for all
# ctypes functions, regardless if it's necessary or not, to give everything
# a Python feel (call overhead is pretty much irrelevant for a windowing
# library like GLFW.)

import os
import warnings

# load the GLFW shared library
if os.name == "nt":
    try:
        _glfwdll = _ctypes.windll.LoadLibrary(os.path.join(os.path.dirname(os.path.abspath(__file__)), "glfw.dll"))
    except:
        # make dll searching a bit more like windows does it
        # save path
        old_path = os.environ["PATH"]
        
        # add the directory containing the main script to path, if any
        import __main__
        if hasattr(__main__, "__file__") and __main__.__file__:
            os.environ["PATH"] = os.path.dirname(os.path.abspath(__main__.__file__)) + os.pathsep + os.environ["PATH"]
        del __main__
        
        # add cwd to path
        os.environ["PATH"] = os.path.abspath(".") + os.pathsep + os.environ["PATH"]
        
        # try to find the library
        glfw_loc = _find_library("glfw")
        
        # restore old path
        os.environ["PATH"] = old_path
        del old_path
        
        if glfw_loc is None:
            raise RuntimeError("no GLFW shared library found")
        else:
            warnings.warn("no GLFW shared library found in the module directory, using the system's library", RuntimeWarning)
            _glfwdll = _ctypes.windll.LoadLibrary(glfw_loc)
        
        del glfw_loc
else:
    try:
        _glfwdll = _ctypes.cdll.LoadLibrary(os.path.abspath(os.path.join(os.path.dirname(__file__), "libglfw.so")))
    except:
        try:
            _glfwdll = _ctypes.cdll.LoadLibrary(os.path.abspath(os.path.join(os.path.dirname(__file__), "libglfw.dylib")))
        except:
            glfw_loc = _find_library("glfw")
            
            if glfw_loc is None:
                raise RuntimeError("no GLFW shared library found")
            else:
                warnings.warn("no GLFW shared library found in the module directory, using the system's library", RuntimeWarning)
                _glfwdll = _ctypes.cdll.LoadLibrary(glfw_loc)
                
            del glfw_loc
    
# helper function for typedefs
# these are different thanks to different calling conventions
if os.name == "nt":
    func_typedef = _ctypes.WINFUNCTYPE
else:
    func_typedef = _ctypes.CFUNCTYPE
    
del warnings
del os


# helper function for function declarations
# restype before the function, like in C declarations
def func_def(restype, func, *argtypes):
    func.restype = restype
    func.argtypes = list(argtypes)
    
    return func
    
    
# GLFW initialization, termination and version querying
func_def(_ctypes.c_int, _glfwdll.glfwInit)
func_def(None, _glfwdll.glfwTerminate)
func_def(None, _glfwdll.glfwGetVersion, _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int))

# window handling
func_def(_ctypes.c_int, _glfwdll.glfwOpenWindow, _ctypes.c_int, _ctypes.c_int, _ctypes.c_int, _ctypes.c_int, _ctypes.c_int, _ctypes.c_int, _ctypes.c_int, _ctypes.c_int, _ctypes.c_int)
func_def(None, _glfwdll.glfwOpenWindowHint, _ctypes.c_int, _ctypes.c_int)
func_def(None, _glfwdll.glfwCloseWindow)
func_def(None, _glfwdll.glfwSetWindowTitle, _ctypes.c_char_p)
func_def(None, _glfwdll.glfwGetWindowSize, _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int))
func_def(None, _glfwdll.glfwSetWindowSize, _ctypes.c_int, _ctypes.c_int)
func_def(None, _glfwdll.glfwSetWindowPos, _ctypes.c_int, _ctypes.c_int)
func_def(None, _glfwdll.glfwIconifyWindow)
func_def(None, _glfwdll.glfwRestoreWindow)
func_def(None, _glfwdll.glfwSwapBuffers)
func_def(None, _glfwdll.glfwSwapInterval, _ctypes.c_int)
func_def(_ctypes.c_int, _glfwdll.glfwGetWindowParam, _ctypes.c_int)
# we pass callback functions as void pointers because the prototypes are defined at the wrapper functions themselves
func_def(None, _glfwdll.glfwSetWindowSizeCallback, _ctypes.c_void_p)
func_def(None, _glfwdll.glfwSetWindowCloseCallback, _ctypes.c_void_p)
func_def(None, _glfwdll.glfwSetWindowRefreshCallback, _ctypes.c_void_p)

# video mode functions
func_def(_ctypes.c_int, _glfwdll.glfwGetVideoModes, _ctypes.POINTER(vidmode._struct), _ctypes.c_int);
func_def(None, _glfwdll.glfwGetDesktopMode, _ctypes.POINTER(vidmode._struct))

# input handling
func_def(None, _glfwdll.glfwPollEvents)
func_def(None, _glfwdll.glfwWaitEvents)
func_def(_ctypes.c_int, _glfwdll.glfwGetKey, _ctypes.c_int)
func_def(_ctypes.c_int, _glfwdll.glfwGetMouseButton, _ctypes.c_int)
func_def(None, _glfwdll.glfwGetMousePos, _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int))
func_def(None, _glfwdll.glfwSetMousePos, _ctypes.c_int, _ctypes.c_int)
func_def(_ctypes.c_int, _glfwdll.glfwGetMouseWheel)
func_def(None, _glfwdll.glfwSetMouseWheel, _ctypes.c_int)
func_def(None, _glfwdll.glfwSetKeyCallback, _ctypes.c_void_p)
func_def(None, _glfwdll.glfwSetCharCallback, _ctypes.c_void_p)
func_def(None, _glfwdll.glfwSetMouseButtonCallback, _ctypes.c_void_p)
func_def(None, _glfwdll.glfwSetMousePosCallback, _ctypes.c_void_p)
func_def(None, _glfwdll.glfwSetMouseWheelCallback, _ctypes.c_void_p)

# extension support
func_def(_ctypes.c_int, _glfwdll.glfwExtensionSupported, _ctypes.c_char_p)
func_def(_ctypes.c_void_p, _glfwdll.glfwGetProcAddress, _ctypes.c_char_p)
func_def(None, _glfwdll.glfwGetGLVersion, _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int))

# joystick input
func_def(_ctypes.c_int, _glfwdll.glfwGetJoystickParam, _ctypes.c_int, _ctypes.c_int)
func_def(_ctypes.c_int, _glfwdll.glfwGetJoystickPos, _ctypes.c_int, _ctypes.POINTER(_ctypes.c_float), _ctypes.c_int)
func_def(_ctypes.c_int, _glfwdll.glfwGetJoystickButtons, _ctypes.c_int, _ctypes.POINTER(_ctypes.c_ubyte), _ctypes.c_int)

# enable/disable functions
func_def(None, _glfwdll.glfwEnable, _ctypes.c_int)
func_def(None, _glfwdll.glfwDisable, _ctypes.c_int)


# Normally argument checking is a no-go in Python (duck typing), but we're dealing 
# with a C library here - even worse - one that has no error messages at all, so
# any checking we can do before passing things to C and possibly failing is a must.
# So we accept any real number for sizes, integers where only integers make sense
# (such as channel depths) and only the appropriate integer flags where asked for.


# error for failed init
class InitError(Exception):
    pass
    

# error for failed opening window
class OpeningWindowError(Exception):
    pass


def Init():
    if not _glfwdll.glfwInit():
        raise InitError("couldn't initialize GLFW")

        
def Terminate():
    _glfwdll.glfwTerminate()
    
    
def GetVersion():
    major, minor, rev = _ctypes.c_int(), _ctypes.c_int(), _ctypes.c_int()
    
    _glfwdll.glfwGetVersion(_ctypes.byref(major), _ctypes.byref(minor), _ctypes.byref(rev))
    
    return (major.value, minor.value, rev.value)
    

def OpenWindow(width, height, redbits, greenbits, bluebits, alphabits, depthbits, stencilbits, mode):
    if not _is_real(width) or not _is_real(height):
        raise TypeError("width and height must be numbers")
        
    if width < 0  or height < 0:
        raise ValueError("width and height must be non-negative")
    
    if not all([_is_int(channel) for channel in (redbits, greenbits, bluebits, alphabits)]):
        raise TypeError("redbits, greenbits, bluebits and alphabits must be integers")
        
    if not all([channel >= 0 for channel in (redbits, greenbits, bluebits, alphabits)]):
        raise ValueError("redbits, greenbits, bluebits and alphabits must be non-negative")
    
    if not all([_is_int(buffersize) for buffersize in (depthbits, stencilbits)]):
        raise TypeError("depthbits and stencilbits must be integers")
        
    if not all([buffersize >= 0 for buffersize in (depthbits, stencilbits)]):
        raise ValueError("depthbits and stencilbits must be non-negative")
    
    if not _is_int(mode):
        raise TypeError("mode must be an integer")
        
    if mode not in (WINDOW, FULLSCREEN):
        raise ValueError("mode must be equal to WINDOW or FULLSCREEN")
    
    opened = _glfwdll.glfwOpenWindow(int(width), int(height), redbits, greenbits, bluebits, alphabits, depthbits, stencilbits, mode)
    
    if not opened:
        raise OpeningWindowError("couldn't open GLFW window")

        
def CloseWindow():
    _glfwdll.glfwCloseWindow()
    
    
def SetWindowTitle(title):
    title = title.encode("latin-1")
    
    _glfwdll.glfwSetWindowTitle(title)

    
def GetWindowSize():
    width, height = _ctypes.c_int(), _ctypes.c_int()
    
    _glfwdll.glfwGetWindowSize(_ctypes.byref(width), _ctypes.byref(height))
    
    return width.value, height.value
    
    
def SetWindowSize(width, height):
    if not _is_real(width) or not _is_real(height):
        raise TypeError("width and height must be numbers")
    
    if width < 0 or height < 0:
        raise ValueError("width and height must be non-negative")
        
    _glfwdll.glfwSetWindowSize(int(width), int(height))
    
    
def SetWindowPos(x, y):
    if not _is_real(x) or not _is_real(y):
        raise ValueError("x and y must be numbers")
    
    _glfwdll.glfwSetWindowPos(int(x), int(y))
    
    
def IconifyWindow():
    _glfwdll.glfwIconifyWindow()

    
def RestoreWindow():
    _glfwdll.glfwRestoreWindow()

    
def SwapBuffers():
    _glfwdll.glfwSwapBuffers()
    
    
def SwapInterval(interval):
    if not _is_int(interval):
        raise TypeError("interval must be an integer")
        
    if interval < 0:
        raise ValueError("interval must be non-negative")
        
    _glfwdll.glfwSwapInterval(interval)
    
    
def GetWindowParam(param):
    if not _is_int(param):
        raise TypeError("param must be a integer")
    
    if not param in (
        OPENED, ACTIVE, ICONIFIED, ACCELERATED, RED_BITS, GREEN_BITS, BLUE_BITS,
        ALPHA_BITS, DEPTH_BITS, STENCIL_BITS, REFRESH_RATE, ACCUM_RED_BITS, ACCUM_GREEN_BITS, ACCUM_BLUE_BITS, ACCUM_ALPHA_BITS,
        AUX_BUFFERS, STEREO, WINDOW_NO_RESIZE, FSAA_SAMPLES,
        OPENGL_VERSION_MAJOR, OPENGL_VERSION_MINOR, OPENGL_FORWARD_COMPAT, OPENGL_DEBUG_CONTEXT, OPENGL_PROFILE
    ):
        raise ValueError("invalid requested parameter")
    
    return _glfwdll.glfwGetWindowParam(param)


def SetWindowSizeCallback(func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 2):
            raise TypeError("incompatible callback (a callable taking two arguments is required)")
            
        callback = SetWindowSizeCallback._callbacktype(func)
    
    # we must keep a reference
    SetWindowSizeCallback._callback = callback
    _glfwdll.glfwSetWindowSizeCallback(_ctypes.cast(callback, _ctypes.c_void_p))
    

def SetWindowCloseCallback(func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 0):
            raise TypeError("incompatible callback (a callable taking no arguments is required)")
            
        callback = SetWindowCloseCallback._callbacktype(lambda: bool(func()))
        
    SetWindowCloseCallback._callback = callback
    _glfwdll.glfwSetWindowCloseCallback(_ctypes.cast(callback, _ctypes.c_void_p))


def SetWindowRefreshCallback(func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 0):
            raise TypeError("incompatible callback (a callable taking no arguments is required)")
        
        callback = SetWindowRefreshCallback._callbacktype(func)
        
    SetWindowRefreshCallback._callback = callback
    _glfwdll.glfwSetWindowRefreshCallback(_ctypes.cast(callback, _ctypes.c_void_p))
    
        
def GetVideoModes():
    video_modes = (vidmode._struct * GetVideoModes.MAX_MODES)()
    num_modes = _glfwdll.glfwGetVideoModes(video_modes, GetVideoModes.MAX_MODES)
    
    result = []
    for i in range(num_modes):
        video_mode = video_modes[i]
        result.append(vidmode(video_mode.Width, video_mode.Height, video_mode.RedBits, video_mode.GreenBits, video_mode.BlueBits))
    
    return result

# this should be sufficient, but we put it in a function attribute so one can change it if nessecary
GetVideoModes.MAX_MODES = 128
    
    
def GetDesktopMode():
    video_mode = vidmode._struct()
    
    _glfwdll.glfwGetDesktopMode(_ctypes.byref(video_mode))
    
    return vidmode(video_mode.Width, video_mode.Height, video_mode.RedBits, video_mode.GreenBits, video_mode.BlueBits)


def PollEvents():
    _glfwdll.glfwPollEvents()
    
    
def WaitEvents():
    _glfwdll.glfwWaitEvents()

    
def GetKey(key):
    try:
        # passed a string?
        key = ord(key.encode("latin-1").upper())
    except:
        # must be an integer, no?
        if not key in GetKey._legal_keycodes:
            raise ValueError("key must be one of the keycodes or a one-character latin-1 string")
    
    return _glfwdll.glfwGetKey(key)
    
# too tedious to repeat here, use locals()
GetKey._legal_keycodes = set([code for var, code in list(globals().items()) if var.startswith("KEY_")])
GetKey._legal_keycodes.remove(KEY_UNKNOWN)
GetKey._legal_keycodes.remove(KEY_SPECIAL)
try:
	del var, code
except NameError: # not in all versions these "leak"
	pass
    
def GetMouseButton(button):
    if not _is_int(button):
        raise TypeError("button must be a integer")
        
    if not button in (MOUSE_BUTTON_1, MOUSE_BUTTON_2, MOUSE_BUTTON_3, MOUSE_BUTTON_4,
                      MOUSE_BUTTON_5, MOUSE_BUTTON_6, MOUSE_BUTTON_7, MOUSE_BUTTON_8):
        raise ValueError("button must be one of the button codes")
    
    return _glfwdll.glfwGetMouseButton(button)

    
def GetMousePos():
    x, y = _ctypes.c_int(), _ctypes.c_int()
    
    _glfwdll.glfwGetMousePos(_ctypes.byref(x), _ctypes.byref(y))
    
    return x.value, y.value

    
def SetMousePos(x, y):
    if not _is_real(x) or not _is_real(y):
        raise TypeError("x and y should be numbers")
    
    _glfwdll.glfwSetMousePos(int(x), int(y))
    

def GetMouseWheel():
    return _glfwdll.glfwGetMouseWheel()
    

def SetMouseWheel(pos):
    if not _is_int(pos):
        raise TypeError("pos should be an integer")
    
    _glfwdll.glfwSetMouseWheel(pos)
    

def SetKeyCallback(func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 2):
            raise TypeError("incompatible callback (a callable taking two arguments is required)")
        
        callback = SetKeyCallback._callbacktype(lambda key, action: func(chr(key) if key < 256 else key, action))
        
    SetKeyCallback._callback = callback
    _glfwdll.glfwSetKeyCallback(_ctypes.cast(callback, _ctypes.c_void_p))
    
    
def SetCharCallback(func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 2):
            raise TypeError("incompatible callback (a callable taking two arguments is required)")
        
        callback = SetCharCallback._callbacktype(lambda char, action: func(chr(char), action))
        
    SetCharCallback._callback = callback
    _glfwdll.glfwSetCharCallback(_ctypes.cast(callback, _ctypes.c_void_p))
    
    
def SetMouseButtonCallback(func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 2):
            raise TypeError("incompatible callback (a callable taking two arguments is required)")
        
        callback = SetMouseButtonCallback._callbacktype(func)
        
    SetMouseButtonCallback._callback = callback
    _glfwdll.glfwSetMouseButtonCallback(_ctypes.cast(callback, _ctypes.c_void_p))
    
    
def SetMousePosCallback(func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 2):
            raise TypeError("incompatible callback (a callable taking two arguments is required)")
        
        callback = SetMousePosCallback._callbacktype(func)
        
    SetMousePosCallback._callback = callback
    _glfwdll.glfwSetMousePosCallback(_ctypes.cast(callback, _ctypes.c_void_p))
    
    
def SetMouseWheelCallback(func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 1):
            raise TypeError("incompatible callback (a callable taking one arguments is required)")
        
        callback = SetMouseWheelCallback._callbacktype(func)
        
    SetMouseWheelCallback._callback = callback
    _glfwdll.glfwSetMouseWheelCallback(_ctypes.cast(callback, _ctypes.c_void_p))
    

def ExtensionSupported(extension):
    return _glfwdll.glfwExtensionSupported(extension.encode("latin-1")) == GL_TRUE


def GetProcAddress(procname):
    return _glfwdll.glfwGetProcAddress(procname.encode("latin-1"))


def GetGLVersion():
    major, minor, rev = _ctypes.c_int(), _ctypes.c_int(), _ctypes.c_int()
    
    _glfwdll.glfwGetGLVersion(_ctypes.byref(major), _ctypes.byref(minor), _ctypes.byref(rev))
    
    return (major.value, minor.value, rev.value)   


def GetJoystickParam(joy, param):
    if not _is_int(joy) or not _is_int(param):
        raise TypeError("joy and param must be integers")
    
    # the last time I checked the JOYSTICK_n were simply from 0 to 15 inclusive
    if not joy in set(range(16)):
        raise ValueError("joy must be one of the glfw.JOYSTICK_n constants")
    
    if not param in (PRESENT, AXES, BUTTONS):
        raise ValueError("param must be one of glfw.PRESENT, glfw.AXES or glfw.BUTTONS")
    
    return _glfwdll.glfwGetJoystickParam(joy, param)
    

def GetJoystickPos(joy):
    if not _is_int(joy):
        raise TypeError("joy must an integer")
    
    if not joy in set(range(16)):
        raise ValueError("joy must be one of the glfw.JOYSTICK_n constants")
    
    max_axes = _glfwdll.glfwGetJoystickParam(joy, AXES)
    pos = (_ctypes.c_float * max_axes)()
    num_axes = _glfwdll.glfwGetJoystickPos(joy, pos, max_axes)
    
    return [pos[i] for i in range(num_axes)]


def GetJoystickButtons(joy):
    if not _is_int(joy):
        raise TypeError("joy must an integer")
    
    if not joy in set(range(16)):
        raise ValueError("joy must be one of the glfw.JOYSTICK_n constants")
    
    max_buttons = _glfwdll.glfwGetJoystickParam(joy, BUTTONS)
    buttons = (_ctypes.c_ubyte * max_buttons)()
    num_buttons = _glfwdll.glfwGetJoystickButtons(joy, buttons, max_buttons)
    
    return [buttons[i] for i in range(num_buttons)]
    

def Enable(token):
    if not _is_int(token):
        raise TypeError("token must be an integer")
    
    if not token in (MOUSE_CURSOR, STICKY_KEYS, STICKY_MOUSE_BUTTONS, SYSTEM_KEYS, KEY_REPEAT, AUTO_POLL_EVENTS):
        raise ValueError("token must be a valid feature code")
    
    _glfwdll.glfwEnable(token)

    
def Disable(token):
    if not _is_int(token):
        raise TypeError("token must be an integer")
    
    if not token in (MOUSE_CURSOR, STICKY_KEYS, STICKY_MOUSE_BUTTONS, SYSTEM_KEYS, KEY_REPEAT, AUTO_POLL_EVENTS):
        raise ValueError("token must be a valid feature code")
    
    _glfwdll.glfwDisable(token)
    
    
#####################
# function typedefs #
#####################

SetWindowSizeCallback._callbacktype = func_typedef(None, _ctypes.c_int, _ctypes.c_int)
SetWindowCloseCallback._callbacktype = func_typedef(_ctypes.c_int)
SetWindowRefreshCallback._callbacktype = func_typedef(None)
SetKeyCallback._callbacktype = func_typedef(None, _ctypes.c_int, _ctypes.c_int)
SetCharCallback._callbacktype = func_typedef(None, _ctypes.c_int, _ctypes.c_int)
SetMouseButtonCallback._callbacktype = func_typedef(None, _ctypes.c_int, _ctypes.c_int)
SetMousePosCallback._callbacktype = func_typedef(None, _ctypes.c_int, _ctypes.c_int)
SetMouseWheelCallback._callbacktype = func_typedef(None, _ctypes.c_int)

# delete no longer needed helper functions
del func_def
del func_typedef

# load submodules
import glfw.ext