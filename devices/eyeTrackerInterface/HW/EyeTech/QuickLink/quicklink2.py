"""
Quicklink.py
.. file: ioHub/devices/eyeTrackerInterface/HW/devices/pyEyeTrackerInterface/eyeTeck/QuickLink/quicklink.py

Copyright (C) 2012 EyeTech Inc.
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. fileauthor:: Eye Tech Inc. & Sol Simpson & Peter Hyatt
"""
from ctypes import *
from ql2types import  * 

import inspect

STRING_LENGTH_128 = 128
QL_SETTING_DEVICE_BANDWIDTH_MODE = "DeviceBandwidthMode"
QL_SETTING_DEVICE_BANDWIDTH_PERCENT_FULL = "DeviceBandwidthPercentFull"
QL_SETTING_DEVICE_BANDWIDTH_PERCENT_TRACKING = "DeviceBandwidthPercentTracking"
QL_SETTING_DEVICE_BINNING = "DeviceBinning"
QL_SETTING_DEVICE_CALIBRATE_ENABLED = "DeviceCalibrateEnabled"
QL_SETTING_DEVICE_DISTANCE = "DeviceDistance"
QL_SETTING_DEVICE_EXPOSURE = "DeviceExposure"
QL_SETTING_DEVICE_FLIP_X = "DeviceFlipX"
QL_SETTING_DEVICE_FLIP_Y = "DeviceFlipY"
QL_SETTING_DEVICE_GAIN_MODE = "DeviceGainMode"
QL_SETTING_DEVICE_GAIN_VALUE = "DeviceGainValue"
QL_SETTING_DEVICE_GAZE_POINT_FILTER_MODE = "DeviceGazePointFilterMode"
QL_SETTING_DEVICE_GAZE_POINT_FILTER_VALUE = "DeviceGazePointFilterValue"
QL_SETTING_DEVICE_IMAGE_PROCESSING_ENABLED = "DeviceImageProcessingEnabled"
QL_SETTING_DEVICE_IMAGE_PROCESSING_EYES_TO_FIND = "DeviceImageProcessingEyesToUse"
QL_SETTING_DEVICE_IMAGE_PROCESSING_EYE_RADIUS_LEFT = "DeviceImageProcessingEyeRadiusLeft"
QL_SETTING_DEVICE_IMAGE_PROCESSING_EYE_RADIUS_RIGHT = "DeviceImageProcessingEyeRadiusRight"
QL_SETTING_DEVICE_INTERPOLATE_ENABLED = "DeviceInterpolateEnabled"
QL_SETTING_DEVICE_IR_LIGHT_MODE = "DeviceIRLightMode"
QL_SETTING_DEVICE_LENS_FOCAL_LENGTH = "DeviceLensFocalLength"
QL_SETTING_DEVICE_ROI_MOVE_THRESHOLD_PERCENT_X = "DeviceRoiMoveThresholdPercentX"
QL_SETTING_DEVICE_ROI_MOVE_THRESHOLD_PERCENT_Y = "DeviceRoiMoveThresholdPercentY"
QL_SETTING_DEVICE_ROI_SIZE_PERCENT_X = "DeviceRoiSizePercentX"
QL_SETTING_DEVICE_ROI_SIZE_PERCENT_Y = "DeviceRoiSizePercentY"

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

if __name__ == "__main__":
    # If this file is ran expicitly, do a test of the functions here.
    testFrame = createFrameTest()

    if(false):
        # Print out the entire contents of the Pixel data
        # ioHub.print2err(testFrame.PixelData[0:testFrame.Width*testFrame.Height])
        print testFrame.PixelData[0:testFrame.Width*testFrame.Height]

    # Print out 50 lines at a time from the frame
    for i in range(testFrame.Width * testFrame.Height):
        print testFrame.PixelData[i],
        if(i%50 == 0 and i != 0):
            print " "
            print i/50, ":",
    print " "
    print "done"
        
