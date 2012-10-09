'''Wrapper for QuickLink2.h

Generated with:
ctypesgen.py -a -l QuickLink2 -o pyQuickLink2.py QuickLink2.h

Do not modify this file.
'''

__docformat__ =  'restructuredtext'

# Begin preamble

import ctypes, os, sys
from ctypes import *

_int_types = (c_int16, c_int32)
if hasattr(ctypes, 'c_int64'):
    # Some builds of ctypes apparently do not have c_int64
    # defined; it's a pretty good bet that these builds do not
    # have 64-bit pointers.
    _int_types += (c_int64,)
for t in _int_types:
    if sizeof(t) == sizeof(c_size_t):
        c_ptrdiff_t = t
del t
del _int_types

class c_void(Structure):
    # c_void_p is a buggy return type, converting to int, so
    # POINTER(None) == c_void_p is actually written as
    # POINTER(c_void), so it can be treated as a real pointer.
    _fields_ = [('dummy', c_int)]

def POINTER(obj):
    p = ctypes.POINTER(obj)

    # Convert None to a real NULL pointer to work around bugs
    # in how ctypes handles None on 64-bit platforms
    if not isinstance(p.from_param, classmethod):
        def from_param(cls, x):
            if x is None:
                return cls()
            else:
                return x
        p.from_param = classmethod(from_param)

    return p

class UserString:
    def __init__(self, seq):
        if isinstance(seq, basestring):
            self.data = seq
        elif isinstance(seq, UserString):
            self.data = seq.data[:]
        else:
            self.data = str(seq)
    def __str__(self): return str(self.data)
    def __repr__(self): return repr(self.data)
    def __int__(self): return int(self.data)
    def __long__(self): return long(self.data)
    def __float__(self): return float(self.data)
    def __complex__(self): return complex(self.data)
    def __hash__(self): return hash(self.data)

    def __cmp__(self, string):
        if isinstance(string, UserString):
            return cmp(self.data, string.data)
        else:
            return cmp(self.data, string)
    def __contains__(self, char):
        return char in self.data

    def __len__(self): return len(self.data)
    def __getitem__(self, index): return self.__class__(self.data[index])
    def __getslice__(self, start, end):
        start = max(start, 0); end = max(end, 0)
        return self.__class__(self.data[start:end])

    def __add__(self, other):
        if isinstance(other, UserString):
            return self.__class__(self.data + other.data)
        elif isinstance(other, basestring):
            return self.__class__(self.data + other)
        else:
            return self.__class__(self.data + str(other))
    def __radd__(self, other):
        if isinstance(other, basestring):
            return self.__class__(other + self.data)
        else:
            return self.__class__(str(other) + self.data)
    def __mul__(self, n):
        return self.__class__(self.data*n)
    __rmul__ = __mul__
    def __mod__(self, args):
        return self.__class__(self.data % args)

    # the following methods are defined in alphabetical order:
    def capitalize(self): return self.__class__(self.data.capitalize())
    def center(self, width, *args):
        return self.__class__(self.data.center(width, *args))
    def count(self, sub, start=0, end=sys.maxint):
        return self.data.count(sub, start, end)
    def decode(self, encoding=None, errors=None): # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.decode(encoding, errors))
            else:
                return self.__class__(self.data.decode(encoding))
        else:
            return self.__class__(self.data.decode())
    def encode(self, encoding=None, errors=None): # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.encode(encoding, errors))
            else:
                return self.__class__(self.data.encode(encoding))
        else:
            return self.__class__(self.data.encode())
    def endswith(self, suffix, start=0, end=sys.maxint):
        return self.data.endswith(suffix, start, end)
    def expandtabs(self, tabsize=8):
        return self.__class__(self.data.expandtabs(tabsize))
    def find(self, sub, start=0, end=sys.maxint):
        return self.data.find(sub, start, end)
    def index(self, sub, start=0, end=sys.maxint):
        return self.data.index(sub, start, end)
    def isalpha(self): return self.data.isalpha()
    def isalnum(self): return self.data.isalnum()
    def isdecimal(self): return self.data.isdecimal()
    def isdigit(self): return self.data.isdigit()
    def islower(self): return self.data.islower()
    def isnumeric(self): return self.data.isnumeric()
    def isspace(self): return self.data.isspace()
    def istitle(self): return self.data.istitle()
    def isupper(self): return self.data.isupper()
    def join(self, seq): return self.data.join(seq)
    def ljust(self, width, *args):
        return self.__class__(self.data.ljust(width, *args))
    def lower(self): return self.__class__(self.data.lower())
    def lstrip(self, chars=None): return self.__class__(self.data.lstrip(chars))
    def partition(self, sep):
        return self.data.partition(sep)
    def replace(self, old, new, maxsplit=-1):
        return self.__class__(self.data.replace(old, new, maxsplit))
    def rfind(self, sub, start=0, end=sys.maxint):
        return self.data.rfind(sub, start, end)
    def rindex(self, sub, start=0, end=sys.maxint):
        return self.data.rindex(sub, start, end)
    def rjust(self, width, *args):
        return self.__class__(self.data.rjust(width, *args))
    def rpartition(self, sep):
        return self.data.rpartition(sep)
    def rstrip(self, chars=None): return self.__class__(self.data.rstrip(chars))
    def split(self, sep=None, maxsplit=-1):
        return self.data.split(sep, maxsplit)
    def rsplit(self, sep=None, maxsplit=-1):
        return self.data.rsplit(sep, maxsplit)
    def splitlines(self, keepends=0): return self.data.splitlines(keepends)
    def startswith(self, prefix, start=0, end=sys.maxint):
        return self.data.startswith(prefix, start, end)
    def strip(self, chars=None): return self.__class__(self.data.strip(chars))
    def swapcase(self): return self.__class__(self.data.swapcase())
    def title(self): return self.__class__(self.data.title())
    def translate(self, *args):
        return self.__class__(self.data.translate(*args))
    def upper(self): return self.__class__(self.data.upper())
    def zfill(self, width): return self.__class__(self.data.zfill(width))

class MutableString(UserString):
    """mutable string objects

    Python strings are immutable objects.  This has the advantage, that
    strings may be used as dictionary keys.  If this property isn't needed
    and you insist on changing string values in place instead, you may cheat
    and use MutableString.

    But the purpose of this class is an educational one: to prevent
    people from inventing their own mutable string class derived
    from UserString and than forget thereby to remove (override) the
    __hash__ method inherited from UserString.  This would lead to
    errors that would be very hard to track down.

    A faster and better solution is to rewrite your program using lists."""
    def __init__(self, string=""):
        self.data = string
    def __hash__(self):
        raise TypeError("unhashable type (it is mutable)")
    def __setitem__(self, index, sub):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data): raise IndexError
        self.data = self.data[:index] + sub + self.data[index+1:]
    def __delitem__(self, index):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data): raise IndexError
        self.data = self.data[:index] + self.data[index+1:]
    def __setslice__(self, start, end, sub):
        start = max(start, 0); end = max(end, 0)
        if isinstance(sub, UserString):
            self.data = self.data[:start]+sub.data+self.data[end:]
        elif isinstance(sub, basestring):
            self.data = self.data[:start]+sub+self.data[end:]
        else:
            self.data =  self.data[:start]+str(sub)+self.data[end:]
    def __delslice__(self, start, end):
        start = max(start, 0); end = max(end, 0)
        self.data = self.data[:start] + self.data[end:]
    def immutable(self):
        return UserString(self.data)
    def __iadd__(self, other):
        if isinstance(other, UserString):
            self.data += other.data
        elif isinstance(other, basestring):
            self.data += other
        else:
            self.data += str(other)
        return self
    def __imul__(self, n):
        self.data *= n
        return self

class String(MutableString, Union):

    _fields_ = [('raw', POINTER(c_char)),
                ('data', c_char_p)]

    def __init__(self, obj=""):
        if isinstance(obj, (str, unicode, UserString)):
            self.data = str(obj)
        else:
            self.raw = obj

    def __len__(self):
        return self.data and len(self.data) or 0

    def from_param(cls, obj):
        # Convert None or 0
        if obj is None or obj == 0:
            return cls(POINTER(c_char)())

        # Convert from String
        elif isinstance(obj, String):
            return obj

        # Convert from str
        elif isinstance(obj, str):
            return cls(obj)

        # Convert from c_char_p
        elif isinstance(obj, c_char_p):
            return obj

        # Convert from POINTER(c_char)
        elif isinstance(obj, POINTER(c_char)):
            return obj

        # Convert from raw pointer
        elif isinstance(obj, int):
            return cls(cast(obj, POINTER(c_char)))

        # Convert from object
        else:
            return String.from_param(obj._as_parameter_)
    from_param = classmethod(from_param)

def ReturnString(obj, func=None, arguments=None):
    return String.from_param(obj)

# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.

# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to c_void_p.
def UNCHECKED(type):
    if (hasattr(type, "_type_") and isinstance(type._type_, str)
        and type._type_ != "P"):
        return type
    else:
        return c_void_p

# ctypes doesn't have direct support for variadic functions, so we have to write
# our own wrapper class
class _variadic_function(object):
    def __init__(self,func,restype,argtypes):
        self.func=func
        self.func.restype=restype
        self.argtypes=argtypes
    def _as_parameter_(self):
        # So we can pass this variadic function as a function pointer
        return self.func
    def __call__(self,*args):
        fixed_args=[]
        i=0
        for argtype in self.argtypes:
            # Typecheck what we can
            fixed_args.append(argtype.from_param(args[i]))
            i+=1
        return self.func(*fixed_args+list(args[i:]))

# End preamble

_libs = {}
_libdirs = []

# Begin loader

# ----------------------------------------------------------------------------
# Copyright (c) 2008 David James
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:

 # * Redistributions of source code must retain the above copyright
   # notice, this list of conditions and the following disclaimer.
 # * Redistributions in binary form must reproduce the above copyright
   # notice, this list of conditions and the following disclaimer in
   # the documentation and/or other materials provided with the
   # distribution.
 # * Neither the name of pyglet nor the names of its
   # contributors may be used to endorse or promote products
   # derived from this software without specific prior written
   # permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

import os.path, re, sys, glob
import ctypes
import ctypes.util

def _environ_path(name):
    if name in os.environ:
        return os.environ[name].split(":")
    else:
        return []

class LibraryLoader(object):
    def __init__(self):
        self.other_dirs=[]

    def load_library(self,libname):
        """Given the name of a library, load it."""
        paths = self.getpaths(libname)

        for path in paths:
            if os.path.exists(path):
                return self.load(path)

        raise ImportError("%s not found." % libname)

    def load(self,path):
        """Given a path to a library, load it."""
        try:
            # Darwin requires dlopen to be called with mode RTLD_GLOBAL instead
            # of the default RTLD_LOCAL.  Without this, you end up with
            # libraries not being loadable, resulting in "Symbol not found"
            # errors
            if sys.platform == 'darwin':
                return ctypes.CDLL(path, ctypes.RTLD_GLOBAL)
            else:
                return ctypes.cdll.LoadLibrary(path)
        except OSError,e:
            raise ImportError(e)

    def getpaths(self,libname):
        """Return a list of paths where the library might be found."""
        if os.path.isabs(libname):
            yield libname
        else:
            # FIXME / TODO return '.' and os.path.dirname(__file__)
            for path in self.getplatformpaths(libname):
                yield path

            path = ctypes.util.find_library(libname)
            if path: yield path

    def getplatformpaths(self, libname):
        return []

# Darwin (Mac OS X)

class DarwinLibraryLoader(LibraryLoader):
    name_formats = ["lib%s.dylib", "lib%s.so", "lib%s.bundle", "%s.dylib",
                "%s.so", "%s.bundle", "%s"]

    def getplatformpaths(self,libname):
        if os.path.pathsep in libname:
            names = [libname]
        else:
            names = [format % libname for format in self.name_formats]

        for dir in self.getdirs(libname):
            for name in names:
                yield os.path.join(dir,name)

    def getdirs(self,libname):
        '''Implements the dylib search as specified in Apple documentation:

        http://developer.apple.com/documentation/DeveloperTools/Conceptual/
            DynamicLibraries/Articles/DynamicLibraryUsageGuidelines.html

        Before commencing the standard search, the method first checks
        the bundle's ``Frameworks`` directory if the application is running
        within a bundle (OS X .app).
        '''

        dyld_fallback_library_path = _environ_path("DYLD_FALLBACK_LIBRARY_PATH")
        if not dyld_fallback_library_path:
            dyld_fallback_library_path = [os.path.expanduser('~/lib'),
                                          '/usr/local/lib', '/usr/lib']

        dirs = []

        if '/' in libname:
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
        else:
            dirs.extend(_environ_path("LD_LIBRARY_PATH"))
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))

        dirs.extend(self.other_dirs)
        dirs.append(".")
        dirs.append(os.path.dirname(__file__))

        if hasattr(sys, 'frozen') and sys.frozen == 'macosx_app':
            dirs.append(os.path.join(
                os.environ['RESOURCEPATH'],
                '..',
                'Frameworks'))

        dirs.extend(dyld_fallback_library_path)

        return dirs

# Posix

class PosixLibraryLoader(LibraryLoader):
    _ld_so_cache = None

    def _create_ld_so_cache(self):
        # Recreate search path followed by ld.so.  This is going to be
        # slow to build, and incorrect (ld.so uses ld.so.cache, which may
        # not be up-to-date).  Used only as fallback for distros without
        # /sbin/ldconfig.
        
        # We assume the DT_RPATH and DT_RUNPATH binary sections are omitted.

        directories = []
        for name in ("LD_LIBRARY_PATH",
                     "SHLIB_PATH", # HPUX
                     "LIBPATH", # OS/2, AIX
                     "LIBRARY_PATH", # BE/OS
                    ):
            if name in os.environ:
                directories.extend(os.environ[name].split(os.pathsep))
        directories.extend(self.other_dirs)
        directories.append(".")
        directories.append(os.path.dirname(__file__))

        try: directories.extend([dir.strip() for dir in open('/etc/ld.so.conf')])
        except IOError: pass

        directories.extend(['/lib', '/usr/lib', '/lib64', '/usr/lib64'])

        cache = {}
        lib_re = re.compile(r'lib(.*)\.s[ol]')
        ext_re = re.compile(r'\.s[ol]$')
        for dir in directories:
            try:
                for path in glob.glob("%s/*.s[ol]*" % dir):
                    file = os.path.basename(path)

                    # Index by filename
                    if file not in cache:
                        cache[file] = path

                    # Index by library name
                    match = lib_re.match(file)
                    if match:
                        library = match.group(1)
                        if library not in cache:
                            cache[library] = path
            except OSError:
                pass

        self._ld_so_cache = cache

    def getplatformpaths(self, libname):
        if self._ld_so_cache is None:
            self._create_ld_so_cache()

        result = self._ld_so_cache.get(libname)
        if result: yield result

        path = ctypes.util.find_library(libname)
        if path: yield os.path.join("/lib",path)

# Windows

class _WindowsLibrary(object):
    def __init__(self, path):
        self.cdll = ctypes.cdll.LoadLibrary(path)
        self.windll = ctypes.windll.LoadLibrary(path)

    def __getattr__(self, name):
        try: return getattr(self.cdll,name)
        except AttributeError:
            try: return getattr(self.windll,name)
            except AttributeError:
                raise

class WindowsLibraryLoader(LibraryLoader):
    name_formats = ["%s.dll", "lib%s.dll", "%slib.dll"]

    def load_library(self, libname):
        try:
            result = LibraryLoader.load_library(self, libname)
        except ImportError:
            result = None
            if os.path.sep not in libname:
                for name in self.name_formats:
                    try:
                        result = getattr(ctypes.cdll, name % libname)
                        if result:
                            break
                    except WindowsError:
                        result = None
            if result is None:
                try:
                    result = getattr(ctypes.cdll, libname)
                except WindowsError:
                    result = None
            if result is None:
                raise ImportError("%s not found." % libname)
        return result

    def load(self, path):
        return _WindowsLibrary(path)

    def getplatformpaths(self, libname):
        if os.path.sep not in libname:
            for name in self.name_formats:
                dll_in_current_dir = os.path.abspath(name % libname)
                if os.path.exists(dll_in_current_dir):
                    yield dll_in_current_dir
                path = ctypes.util.find_library(name % libname)
                if path:
                    yield path

# Platform switching

# If your value of sys.platform does not appear in this dict, please contact
# the Ctypesgen maintainers.

loaderclass = {
    "darwin":   DarwinLibraryLoader,
    "cygwin":   WindowsLibraryLoader,
    "win32":    WindowsLibraryLoader
}

loader = loaderclass.get(sys.platform, PosixLibraryLoader)()

def add_library_search_dirs(other_dirs):
    loader.other_dirs = other_dirs

load_library = loader.load_library

del loaderclass

# End loader

add_library_search_dirs([])

# Begin libraries

_libs["QuickLink2"] = load_library("QuickLink2")

# 1 libraries
# End libraries

# No modules

QLDeviceId = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 316

QLDeviceGroupId = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 327

QLDeviceOrGroupId = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 341

QLSettingsId = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 353

QLCalibrationId = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 365

QLTargetId = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 377

enum_anon_1 = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 402

QL_CALIBRATION_STATUS_OK = 0 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 402

QL_CALIBRATION_STATUS_CALIBRATING = 1 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 402

QL_CALIBRATION_STATUS_NO_LEFT_DATA = 2 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 402

QL_CALIBRATION_STATUS_NO_RIGHT_DATA = 3 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 402

QL_CALIBRATION_STATUS_NO_DATA = 4 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 402

QLCalibrationStatus = enum_anon_1 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 402

enum_anon_2 = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 421

QL_CALIBRATION_TYPE_5 = 0 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 421

QL_CALIBRATION_TYPE_9 = 1 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 421

QL_CALIBRATION_TYPE_16 = 2 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 421

QLCalibrationType = enum_anon_2 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 421

enum_anon_3 = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 439

QL_DEVICE_BANDWIDTH_MODE_AUTO = 0 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 439

QL_DEVICE_BANDWIDTH_MODE_MANUAL = 1 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 439

QLDeviceBandwidthMode = enum_anon_3 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 439

enum_anon_4 = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 463

QL_DEVICE_EYES_TO_USE_LEFT = 0 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 463

QL_DEVICE_EYES_TO_USE_RIGHT = 1 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 463

QL_DEVICE_EYES_TO_USE_LEFT_OR_RIGHT = 2 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 463

QL_DEVICE_EYES_TO_USE_LEFT_AND_RIGHT = 3 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 463

QLDeviceEyesToUse = enum_anon_4 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 463

enum_anon_5 = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 480

QL_DEVICE_GAIN_MODE_AUTO = 0 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 480

QL_DEVICE_GAIN_MODE_MANUAL = 1 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 480

QLDeviceGainMode = enum_anon_5 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 480

enum_anon_6 = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 537

QL_DEVICE_GAZE_POINT_FILTER_NONE = 0 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 537

QL_DEVICE_GAZE_POINT_FILTER_MEDIAN_FRAMES = 1 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 537

QL_DEVICE_GAZE_POINT_FILTER_MEDIAN_TIME = 2 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 537

QL_DEVICE_GAZE_POINT_FILTER_HEURISTIC_FRAMES = 3 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 537

QL_DEVICE_GAZE_POINT_FILTER_HEURISTIC_TIME = 4 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 537

QL_DEVICE_GAZE_POINT_FILTER_WEIGHTED_PREVIOUS_FRAME = 5 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 537

QLDeviceGazePointFilterMode = enum_anon_6 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 537

enum_anon_7 = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 554

QL_DEVICE_IR_LIGHT_MODE_OFF = 0 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 554

QL_DEVICE_IR_LIGHT_MODE_AUTO = 1 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 554

QLDeviceIRLightMode = enum_anon_7 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 554

enum_anon_8 = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 576

QL_DEVICE_STATUS_UNAVAILABLE = 0 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 576

QL_DEVICE_STATUS_STOPPED = 1 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 576

QL_DEVICE_STATUS_INITIALIZED = 2 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 576

QL_DEVICE_STATUS_STARTED = 3 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 576

QLDeviceStatus = enum_anon_8 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 576

enum_anon_9 = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QL_ERROR_OK = 0 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QL_ERROR_INVALID_DEVICE_ID = 1 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QL_ERROR_INVALID_SETTINGS_ID = 2 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QL_ERROR_INVALID_CALIBRATION_ID = 3 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QL_ERROR_INVALID_TARGET_ID = 4 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QL_ERROR_INVALID_PASSWORD = 5 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QL_ERROR_INVALID_PATH = 6 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QL_ERROR_INVALID_DURATION = 7 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QL_ERROR_INVALID_POINTER = 8 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QL_ERROR_TIMEOUT_ELAPSED = 9 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QL_ERROR_INTERNAL_ERROR = 10 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QL_ERROR_BUFFER_TOO_SMALL = 11 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QL_ERROR_CALIBRAION_NOT_INITIALIZED = 12 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QL_ERROR_DEVICE_NOT_STARTED = 13 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QL_ERROR_NOT_SUPPORTED = 14 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QL_ERROR_NOT_FOUND = 15 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QL_ERROR_UNAUTHORIZED_APPLICATION_RUNNING = 16 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QL_ERROR_INVALID_DEVICE_GROUP_ID = 17 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

QLError = enum_anon_9 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 640

enum_anon_10 = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 657

QL_EYE_TYPE_LEFT = 0 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 657

QL_EYE_TYPE_RIGHT = 1 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 657

QLEyeType = enum_anon_10 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 657

enum_anon_11 = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 688

QL_INDICATOR_MODE_OFF = 0 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 688

QL_INDICATOR_MODE_ON = 1 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 688

QL_INDICATOR_MODE_LEFT_EYE_STATUS = 2 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 688

QL_INDICATOR_MODE_RIGHT_EYE_STATUS = 3 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 688

QL_INDICATOR_MODE_LEFT_EYE_STATUS_FILTERED = 4 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 688

QL_INDICATOR_MODE_RIGHT_EYE_STATUS_FILTERED = 5 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 688

QLIndicatorMode = enum_anon_11 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 688

enum_anon_12 = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 705

QL_INDICATOR_TYPE_LEFT = 0 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 705

QL_INDICATOR_TYPE_RIGHT = 1 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 705

QLIndicatorType = enum_anon_12 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 705

enum_anon_13 = c_int # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 761

QL_SETTING_TYPE_INT = 0 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 761

QL_SETTING_TYPE_INT8 = 1 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 761

QL_SETTING_TYPE_INT16 = 2 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 761

QL_SETTING_TYPE_INT32 = 3 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 761

QL_SETTING_TYPE_INT64 = 4 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 761

QL_SETTING_TYPE_UINT = 5 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 761

QL_SETTING_TYPE_UINT8 = 6 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 761

QL_SETTING_TYPE_UINT16 = 7 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 761

QL_SETTING_TYPE_UINT32 = 8 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 761

QL_SETTING_TYPE_UINT64 = 9 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 761

QL_SETTING_TYPE_FLOAT = 10 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 761

QL_SETTING_TYPE_DOUBLE = 11 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 761

QL_SETTING_TYPE_BOOL = 12 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 761

QL_SETTING_TYPE_STRING = 13 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 761

QL_SETTING_TYPE_VOID_POINTER = 14 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 761

QLSettingType = enum_anon_13 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 761

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 788
class struct_anon_14(Structure):
    pass

struct_anon_14.__slots__ = [
    'targetId',
    'x',
    'y',
]
struct_anon_14._fields_ = [
    ('targetId', QLTargetId),
    ('x', c_float),
    ('y', c_float),
]

QLCalibrationTarget = struct_anon_14 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 788

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 812
class struct_anon_15(Structure):
    pass

struct_anon_15.__slots__ = [
    'x',
    'y',
    'score',
]
struct_anon_15._fields_ = [
    ('x', c_float),
    ('y', c_float),
    ('score', c_float),
]

QLCalibrationScore = struct_anon_15 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 812

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 834
class struct_anon_16(Structure):
    pass

struct_anon_16.__slots__ = [
    'sensorWidth',
    'sensorHeight',
    'serialNumber',
    'modelName',
]
struct_anon_16._fields_ = [
    ('sensorWidth', c_int),
    ('sensorHeight', c_int),
    ('serialNumber', c_char * 128),
    ('modelName', c_char * 128),
]

QLDeviceInfo = struct_anon_16 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 834

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 845
class struct_anon_17(Structure):
    pass

struct_anon_17.__slots__ = [
    'x',
    'y',
]
struct_anon_17._fields_ = [
    ('x', c_double),
    ('y', c_double),
]

QLXYPairDouble = struct_anon_17 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 845

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 856
class struct_anon_18(Structure):
    pass

struct_anon_18.__slots__ = [
    'x',
    'y',
]
struct_anon_18._fields_ = [
    ('x', c_float),
    ('y', c_float),
]

QLXYPairFloat = struct_anon_18 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 856

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 876
class struct_anon_19(Structure):
    pass

struct_anon_19.__slots__ = [
    'x',
    'y',
    'width',
    'height',
]
struct_anon_19._fields_ = [
    ('x', c_int),
    ('y', c_int),
    ('width', c_int),
    ('height', c_int),
]

QLRectInt = struct_anon_19 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 876

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 920
class struct_anon_20(Structure):
    pass

struct_anon_20.__slots__ = [
    'PixelData',
    'Width',
    'Height',
    'Timestamp',
    'Gain',
    'FrameNumber',
    'ROI',
    'Reserved',
]
struct_anon_20._fields_ = [
    ('PixelData', POINTER(c_ubyte)),
    ('Width', c_int),
    ('Height', c_int),
    ('Timestamp', c_double),
    ('Gain', c_int),
    ('FrameNumber', c_long),
    ('ROI', QLRectInt),
    ('Reserved', POINTER(None) * 12),
]

QLImageData = struct_anon_20 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 920

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 959
class struct_anon_21(Structure):
    pass

struct_anon_21.__slots__ = [
    'Found',
    'Calibrated',
    'PupilDiameter',
    'Pupil',
    'Glint0',
    'Glint1',
    'GazePoint',
    'Reserved',
]
struct_anon_21._fields_ = [
    ('Found', c_long),
    ('Calibrated', c_long),
    ('PupilDiameter', c_float),
    ('Pupil', QLXYPairFloat),
    ('Glint0', QLXYPairFloat),
    ('Glint1', QLXYPairFloat),
    ('GazePoint', QLXYPairFloat),
    ('Reserved', POINTER(None) * 16),
]

QLEyeData = struct_anon_21 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 959

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 988
class struct_anon_22(Structure):
    pass

struct_anon_22.__slots__ = [
    'Valid',
    'x',
    'y',
    'LeftWeight',
    'RightWeight',
    'Reserved',
]
struct_anon_22._fields_ = [
    ('Valid', c_long),
    ('x', c_float),
    ('y', c_float),
    ('LeftWeight', c_float),
    ('RightWeight', c_float),
    ('Reserved', POINTER(None) * 16),
]

QLWeightedGazePoint = struct_anon_22 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 988

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 1033
class struct_anon_23(Structure):
    pass

struct_anon_23.__slots__ = [
    'ImageData',
    'LeftEye',
    'RightEye',
    'WeightedGazePoint',
    'Focus',
    'Distance',
    'Bandwidth',
    'DeviceId',
    'Reserved',
]
struct_anon_23._fields_ = [
    ('ImageData', QLImageData),
    ('LeftEye', QLEyeData),
    ('RightEye', QLEyeData),
    ('WeightedGazePoint', QLWeightedGazePoint),
    ('Focus', c_float),
    ('Distance', c_float),
    ('Bandwidth', c_int),
    ('DeviceId', QLDeviceId),
    ('Reserved', POINTER(None) * 14),
]

QLFrameData = struct_anon_23 # ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 1033

__const = c_int # <command-line>: 5

# <command-line>: 8
try:
    CTYPESGEN = 1
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 19
try:
    STRING_LENGTH_128 = 128
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 58
try:
    QL_SETTING_DEVICE_BANDWIDTH_MODE = 'DeviceBandwidthMode'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 69
try:
    QL_SETTING_DEVICE_BANDWIDTH_PERCENT_FULL = 'DeviceBandwidthPercentFull'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 80
try:
    QL_SETTING_DEVICE_BANDWIDTH_PERCENT_TRACKING = 'DeviceBandwidthPercentTracking'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 92
try:
    QL_SETTING_DEVICE_BINNING = 'DeviceBinning'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 102
try:
    QL_SETTING_DEVICE_CALIBRATE_ENABLED = 'DeviceCalibrateEnabled'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 109
try:
    QL_SETTING_DEVICE_DISTANCE = 'DeviceDistance'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 116
try:
    QL_SETTING_DEVICE_EXPOSURE = 'DeviceExposure'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 127
try:
    QL_SETTING_DEVICE_FLIP_X = 'DeviceFlipX'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 138
try:
    QL_SETTING_DEVICE_FLIP_Y = 'DeviceFlipY'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 148
try:
    QL_SETTING_DEVICE_GAIN_MODE = 'DeviceGainMode'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 159
try:
    QL_SETTING_DEVICE_GAIN_VALUE = 'DeviceGainValue'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 169
try:
    QL_SETTING_DEVICE_GAZE_POINT_FILTER_MODE = 'DeviceGazePointFilterMode'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 179
try:
    QL_SETTING_DEVICE_GAZE_POINT_FILTER_VALUE = 'DeviceGazePointFilterValue'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 189
try:
    QL_SETTING_DEVICE_IMAGE_PROCESSING_ENABLED = 'DeviceImageProcessingEnabled'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 198
try:
    QL_SETTING_DEVICE_IMAGE_PROCESSING_EYES_TO_FIND = 'DeviceImageProcessingEyesToUse'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 211
try:
    QL_SETTING_DEVICE_IMAGE_PROCESSING_EYE_RADIUS_LEFT = 'DeviceImageProcessingEyeRadiusLeft'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 224
try:
    QL_SETTING_DEVICE_IMAGE_PROCESSING_EYE_RADIUS_RIGHT = 'DeviceImageProcessingEyeRadiusRight'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 234
try:
    QL_SETTING_DEVICE_INTERPOLATE_ENABLED = 'DeviceInterpolateEnabled'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 242
try:
    QL_SETTING_DEVICE_IR_LIGHT_MODE = 'DeviceIRLightMode'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 249
try:
    QL_SETTING_DEVICE_LENS_FOCAL_LENGTH = 'DeviceLensFocalLength'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 260
try:
    QL_SETTING_DEVICE_ROI_MOVE_THRESHOLD_PERCENT_X = 'DeviceRoiMoveThresholdPercentX'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 271
try:
    QL_SETTING_DEVICE_ROI_MOVE_THRESHOLD_PERCENT_Y = 'DeviceRoiMoveThresholdPercentY'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 281
try:
    QL_SETTING_DEVICE_ROI_SIZE_PERCENT_X = 'DeviceRoiSizePercentX'
except:
    pass

# ioHub\\devices\\eyeTrackerInterface\\HW\\EyeTech\\QuickLink\\reference\\QLTypes.h: 291
try:
    QL_SETTING_DEVICE_ROI_SIZE_PERCENT_Y = 'DeviceRoiSizePercentY'
except:
    pass

# No inserted files

