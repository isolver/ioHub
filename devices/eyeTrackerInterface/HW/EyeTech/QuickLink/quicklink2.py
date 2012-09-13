"""
Quicklink.py
.. file: ioHub/devices/eyeTrackerInterface/HW/devices/pyEyeTrackerInterface/eyeTeck/QuickLink/quicklink.py

Copyright (C) 2012 EyeTech Inc.
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. fileauthor:: Eye Tech Inc. & Sol Simpson
"""
from ctypes import *

# QLRectInt
#
# typedef struct
# {
# int x;
# int y;
# int width;
# int height;
# } QLRectInt;
class pyQLRectInt(Structure):
    _fields_ = [("x", c_int),
                ("y", c_int),
                ("width", c_int),
                ("height", c_int)]

# QLImageData
# ( 32 bit version)
# typedef struct
# {
#     unsigned char* PixelData;
#     int            Width;
#     int            Height;
#     double         Timestamp;
#     int            Gain;
#     long           FrameNumber;
#     QLRectInt      ROI;
#     void*          Reserved[12];
# } QLImageData;

class pyQLImageData(Structure):
    _fields_ = [("PixelData", POINTER(c_ubyte)),
                ("Width", c_int),
                ("Height", c_int),
                ("Timestamp", c_long),
                ("Gain", c_int),
                ("FrameNumber", c_long),
                ("ROI", pyQLRectInt),
                ("Reserved", c_void_p * 12)]

def createFrameTest():
    i_w=640
    i_h=480
    num_pix=i_w*i_h

    # create some dummy image data contents, since I do not have real frame data
    import numpy
    pixel_data=numpy.ones(num_pix,dtype=numpy.uint8)
    pixel_data[:]=128
    pixel_data=list(pixel_data)

    qlImageData=pyQLImageData()
    qlImageData.Width=i_w
    qlImageData.Height=i_h
    qlImageData.Timestamp=1234567
    qlImageData.Gain=100
    qlImageData.FrameNumber=11111
    qlImageData.ROI.x=160
    qlImageData.ROI.y=120
    qlImageData.ROI.width=320
    qlImageData.ROI.height=240
    qlImageData.PixelData=(c_ubyte * num_pix)(*pixel_data)

    return qlImageData