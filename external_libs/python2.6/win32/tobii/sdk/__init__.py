
import threading
import datetime

from tobii.sdk._native import tobiisdkpy, BoundHandler

from tobii.sdk.xds import Converter
from tobii.sdk import types

global _initialized
_initialized = False

def init():
    """Initializes the Tobii SDK, you must call this function before
    any other function in the SDK.
    """
    tobiisdkpy.init()

    for T in (types.Point2D, types.Point3D):
        Converter.register(T.NODE_ID, T._node_converter)
   
    global _initialized
    _initialized = True

def error_code_to_string(code):
    return tobiisdkpy.convert_error_code_to_string(code)


# internal helper function
def _check_init():
    global _initialized
    if not _initialized:
        raise Exception("You must call tobii.sdk.init() first")

def _require_callable(obj, optional=False, argument_name="argument"):
    if obj is None and optional:
        return
    
    if not callable(obj):
        raise TypeError("%s must be callable" % (argument_name))


class CoreException(Exception):
    pass

