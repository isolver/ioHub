# lctigaze.py
#
# Defines structures
# Loads in lctigaze.dll
# This script shows how to set up an experiment with Python 2.7.1 (with ctypes Library)
#
# Author: Interactive Minds Dresden GmbH
# June 1st, 2012


from ctypes import *

EG_COMM_TYPE_LOCAL = c_int(0)    #/* Single computer configuration.          */
EG_COMM_TYPE_SOCKET = c_int(1) #    /* 2 computers, comm over TCP/IP.          */

#===========================
#		Struct Definition
#===========================


'''
/****************************************************************************/
/* The stEgData structure contains the results of the Eyegaze image         */
/* processing from a given field of video camera data.                      */

struct _stEgData
{
   BOOL   bGazeVectorFound;
   int    iIGaze;                /* integer coordinates of the user         */
   int    iJGaze;                /*   gazepoint referenced to the full      */
   float  fPupilRadiusMm;        /* actual pupil radius (mm)                */
   float  fXEyeballOffsetMm;     /* offset of the eyeball center from       */
   float  fYEyeballOffsetMm;     /*  the camera axis (mm)                   */
   float  fFocusRangeImageTime;  /* distance from the camera sensor plane   */
   float  fFocusRangeOffsetMm;   /* range offset between the camera focus   */
   float  fLensExtOffsetMm;      /* distance that the lens extension would  */
   ULONG  ulCameraFieldCount;    /* number of camera fields, i.e. 60ths of  */
   double dGazeTimeSec;          /* The application time that the gazepoint */
   double dAppMarkTimeSec;       /* Pentium TSC counter value at the moment */
   int    iAppMarkCount;         /* Mark count used in logging functions.   */
   double dReportTimeSec;        /* The application time that Eyegaze       */
                                 /*   reported the gazepoint                */

};
'''
class stEgData(Structure):
	_fields_ = [("bGazeVectorFound", c_int),
                ("iIGaze", c_int),
                ("iJGaze", c_int),
                ("fPupilRadiusMm", c_float),
                ("fXEyeballOffsetMm", c_float),
                ("fYEyeballOffsetMm", c_float),
                ("fFocusRangeImageTime", c_float),
                ("fFocusRangeOffsetMm", c_float),
                ("fLensExtOffsetMm", c_float),
                ("ulCameraFieldCount", c_ulong),
                ("dGazeTimeSec", c_double),
                ("dAppMarkTimeSec", c_double),
                ("iAppMarkCount", c_int),
                ("dReportTimeSec", c_double)]

'''
struct _stEgControl
{
   struct _stEgData *pstEgData;   /* pointer to the Eyegaze data structure  */
    int    iNDataSetsInRingBuffer; /* number of gazepoint data samples in    */
   BOOL   bTrackingActive;        /* flag controls whether eyetracking is   */
   int    iScreenWidthPix;        /* Pixel dimensions of the full           */
   int    iScreenHeightPix;       /*   computer screen                      */
   BOOL   bEgCameraDisplayActive; /* flag controls whether or not the       */
   int    iEyeImagesScreenPos;    /* Screen position of the eye images.     */
   int    iCommType;              /* Communication type:       Comp Config: */
   wchar_t *pszCommName;          /* Pointer to serial port name or IP      */
   int    iVisionSelect;          /* Reserved - set to 0 (unused)           */
   int    iNPointsAvailable;      /* number of gazepoint data samples       */
   int    iNBufferOverflow;       /* number of irretrievably missed gaze-   */
   int    iSamplePerSec;          /* Eyegaze image processing rate -        */
   float  fHorzPixPerMm;          /* Eyegaze monitor scale factors          */
   float  fVertPixPerMm;          /*   (pixel / millimeter)                 */
   void   *pvEgVideoBufferAddress;/* address of the video buffer containing */
   void   *hEyegaze;              /* Eyegaze handle -- used internally by   */
};
'''
class stEgControl(Structure):
	_fields_ = [("_stEgData", POINTER(stEgData)),
                ("iNDataSetsInRingBuffer", c_int),
                ("bTrackingActive", c_bool),
                ("iScreenWidthPix", c_int),
                ("iScreenHeightPix", c_int),
                ("bEgCameraDisplayActive", c_bool),
                ("iCommType", c_int),
                ("pszCommName", c_wchar_p),
                ("iVisionSelect", c_int),
                ("iNPointsAvailable", c_int),
                ("iNBufferOverflow", c_int),
                ("iSamplePerSec", c_int),
                ("fHorzPixPerMm", c_float),
                ("fVertPixPerMm", c_float),
                ("pvEgVideoBufferAddress", c_void_p),
                ("hEyegaze", c_void_p)]


#===========================
#		Loading lctigaze.dll
#===========================



'''
/****************************************************************************/
/* Function prototypes:                                                     */

int  EgInit(
        struct _stEgControl *pstEgControl);
                                 /* Initialize Eyegaze functions -          */
                                 /*   create eyetracking thread             */

'''





