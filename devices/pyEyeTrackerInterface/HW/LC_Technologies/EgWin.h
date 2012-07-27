/*****************************************************************************

File Name:       EgWin.h

Company:         LC Technologies, Inc.
                 10363 Democracy Lane
                 Fairfax, VA 22030
                 (703) 385-8800

The Eyegaze functions run as a thread under Windows NT/2000/XP.  Prior to
creating the Eyegaze thread, the application program must set up an Eyegaze
control structure, stEgControl, and an Eyegaze data structure stEgData.
The application controls the Eyegaze image processing functions through the
stEgControl structure, and the Eyegaze functions pass the eyetracking data
to the application via the stEgData buffer.

*****************************************************************************/
#ifndef EGWIN_H_INCLUDED
#define EGWIN_H_INCLUDED
/****************************************************************************/
#ifdef __cplusplus
extern "C" {            /* Assume C declarations for C++ */
#endif  /* __cplusplus */

#include <windows.h>
#include <lctypdef.h>            /* Commonly used data type abbreviations   */

/****************************************************************************/
/* The stEgControl structure contains control and status variables to       */
/* be used by the Eyegaze application program to setup and control the      */
/* Eyegaze image processing software, and to access the Eyegaze data.       */

struct _stEgControl
{
                                  /* CONTROL INPUTS FROM APPLICATION:       */

   struct _stEgData *pstEgData;   /* pointer to the Eyegaze data structure  */
                                  /*   where EgGetData() places the next    */
                                  /*   gazepoint data sample.               */
                                  /*   This memory is allocated by the      */
                                  /*   EgInit() function.  The pointer to   */
                                  /*   data structure is returned to the    */
                                  /*   application.                         */
   int    iNDataSetsInRingBuffer; /* number of gazepoint data samples in    */
                                  /*   Eyegaze's internal ring buffer.      */
                                  /*   The application must set the ring-   */
                                  /*   buffer length in the stEgControl     */
                                  /*   structure before calling EgInit()    */
   BOOL   bTrackingActive;        /* flag controls whether eyetracking is   */
                                  /*   presently on (TRUE = 1) or off       */
                                  /*   (FALSE = 0). If the flag is on when  */
                                  /*   a new camera field finishes, the     */
                                  /*   Eyegaze thread processes the image   */
                                  /*   and puts the results in the data     */
                                  /*   ring buffer; if the flag is off,     */
                                  /*   the camera field is not processed.   */
                                  /*   The application may turn this        */
                                  /*   tracking flag on or off at any       */
                                  /*   time.                                */
                                  /* NOTE for non-Windows users: This BOOL  */
                                  /*    is a 4-byte integer                 */
   int    iScreenWidthPix;        /* Pixel dimensions of the full           */
   int    iScreenHeightPix;       /*   computer screen                      */
   BOOL   bEgCameraDisplayActive; /* flag controls whether or not the       */
                                  /*   full image from the Eyegaze          */
                                  /*   camera is displayed in a separate    */
                                  /*   window on the VGA.                   */
                                  /*   The application must set this flag   */
                                  /*   prior to calling EgInit() and may    */
                                  /*   turn the display flag on and off     */
                                  /*   at any time.                         */
   int    iEyeImagesScreenPos;    /* Screen position of the eye images.     */
                                  /*   0 = upper left, 1 = upper right      */
   int    iCommType;              /* Communication type:       Comp Config: */
                                  /*   EG_COMM_TYPE_LOCAL,       Single     */
                                  /*   EG_COMM_TYPE_SOCKET,      Double     */
   wchar_t *pszCommName;          /* Pointer to serial port name or IP      */
                                  /*   address of server machine.           */
                                  /*   used only in Double Computer Config  */
                                  /*   Note that this is a "wide character" */
   int    iVisionSelect;          /* Reserved - set to 0 (unused)           */

                                  /* OUTPUTS TO APPLICATION:                */

   int    iNPointsAvailable;      /* number of gazepoint data samples       */
                                  /*   presently available for the applica- */
                                  /*   tion to retrieve from Eyegaze's      */
                                  /*   internal ring buffer                 */
   int    iNBufferOverflow;       /* number of irretrievably missed gaze-   */
                                  /*   point data samples, i.e. the number  */
                                  /*   of valid data points at the tail of  */
                                  /*   the ring buffer that the application */
                                  /*   did not retrieve and that Eyegaze    */
                                  /*   overwrote since the application      */
                                  /*   last called EgGetData().             */
   int    iSamplePerSec;          /* Eyegaze image processing rate -        */
                                  /*   depends on the camera field rate:    */
                                  /*   RS_170               60 Hz           */
                                  /*   CCIR                 50 Hz           */
   float  fHorzPixPerMm;          /* Eyegaze monitor scale factors          */
   float  fVertPixPerMm;          /*   (pixel / millimeter)                 */
   void   *pvEgVideoBufferAddress;/* address of the video buffer containing */
                                  /*   the most recently processed camera   */
                                  /*   image field                          */

                                  /* INTERNAL EYEGAZE VARIABLE              */

   void   *hEyegaze;              /* Eyegaze handle -- used internally by   */
                                  /*   Eyegaze to keep track of which       */
                                  /*   vision subsubsystem is in use.       */
                                  /*   (not used by application)            */
};

/****************************************************************************/
/* The stEgData structure contains the results of the Eyegaze image         */
/* processing from a given field of video camera data.                      */

struct _stEgData
{
   BOOL   bGazeVectorFound;      /* flag indicating whether the image       */
                                 /*   processing software found the eye,    */
                                 /*   i.e. found a valid glint pupil vector */
                                 /*   (TRUE = 1, FALSE = 0)                 */
                                 /* NOTE for non-Windows users: This BOOL   */
                                 /*    is a 4-byte integer                  */
   int    iIGaze;                /* integer coordinates of the user         */
   int    iJGaze;                /*   gazepoint referenced to the full      */
                                 /*   computer display space (pixels)       */
                                 /*   0,0 origin at upper left corner       */
                                 /* NOTE: In the case of multiple monitors, */
                                 /*   this is the upper left corner of the  */
                                 /*   upper-most / left-most monitor        */
                                 /*   iIGaze positive rightward             */
                                 /*   iJGaze positive downward              */
   float  fPupilRadiusMm;        /* actual pupil radius (mm)                */
   float  fXEyeballOffsetMm;     /* offset of the eyeball center from       */
   float  fYEyeballOffsetMm;     /*  the camera axis (mm)                   */
                                 /*  Notes on polarity:                     */
                                 /*  x positive: head moves to user's right */
                                 /*  y positive: head moves up              */
   float  fFocusRangeImageTime;  /* distance from the camera sensor plane   */
                                 /*   to the camera focus plane, at the     */
                                 /*   time the camera captured the image    */
                                 /*   (mm)                                  */
   float  fFocusRangeOffsetMm;   /* range offset between the camera focus   */
                                 /*   plane and the corneal surface of the  */
                                 /*   eye, as measured from the size and    */
                                 /*   orientation of the corneal reflection */
                                 /*   in the eye image - at image time (mm) */
                                 /*   A positive offset means the eye is    */
                                 /*   beyond the lens' focus range.         */
   float  fLensExtOffsetMm;      /* distance that the lens extension would  */
                                 /*   have to be changed to bring the eye   */
                                 /*   into clear focus (millimeters)        */
                                 /*   (at image time)                       */
   ULONG  ulCameraFieldCount;    /* number of camera fields, i.e. 60ths of  */
                                 /*   a second, that have occurred since    */
                                 /*   the starting reference time (midnight */
                                 /*   January 1, this year)                 */
   double dGazeTimeSec;          /* The application time that the gazepoint */
                                 /*   was actually valid.  (dGazeTimeSec    */
                                 /*   represents the original image-capture */
                                 /*   time, not the time that the gazepoint */
                                 /*   calculation was completed.)           */
   double dAppMarkTimeSec;       /* Pentium TSC counter value at the moment */
                                 /*   that the mark was incremented.        */
   int    iAppMarkCount;         /* Mark count used in logging functions.   */
   double dReportTimeSec;        /* The application time that Eyegaze       */
                                 /*   reported the gazepoint                */

};
/****************************************************************************/
struct _stEyeImageInfo
{
   unsigned char *prgbEyeImage;  /* pointer to RGB eye image data           */
   BITMAPINFO bmiEyeImage;       /* bitmap information                      */
   int iWidth;
   int iHeight;
};

/****************************************************************************/
/* Function prototypes:                                                     */

int  EgInit(
        struct _stEgControl *pstEgControl);
                                 /* Initialize Eyegaze functions -          */
                                 /*   create eyetracking thread             */
void EgCalibrate(
        struct _stEgControl *pstEgControl,
        HWND hwnd,
        int iCalAppType);        /* Perform the Eyegaze calibration         */
                                 /*   procedure                             */
void EgCalibrate1(
        struct _stEgControl *pstEgControl,
        HWND hwnd,
        int iCalAppType);        /* Perform the Eyegaze calibration         */
                                 /*   procedure                             */
void EgCalibrate2(
        struct _stEgControl *pstEgControl,
        int iCalAppType);        /* Perform the Eyegaze calibration         */
                                 /*   procedure                             */
int  EgGetData(
        struct _stEgControl *pstEgControl);
                                 /* Retrieve data collected by eyegaze      */
                                 /*   image processing thread               */
                                 /*   EgGetData() returns the buffer index  */
                                 /*   of the last gazepoint sample          */
                                 /*   measured by Eyegaze                   */
int  EgGetEvent(
        struct _stEgControl *pstEgControl,
        void *pv);
int  EgGetVersion(void);         /* Returns the software version number     */
int  EgExit(
       struct _stEgControl *pstEgControl);
                                 /* Shut down Eyegaze operation -           */
                                 /*   terminate eyetracking thread          */
double EgGetApplicationStartTimeSec(void);

/* Log file functions:                                                      */

int  EgLogFileOpen(
        struct _stEgControl *pstEgControl,
        char                *pszFileName,
        char                *pszMode);
void EgLogWriteColumnHeader(
        struct _stEgControl *pstEgControl);
void EgLogAppendText(
        struct _stEgControl *pstEgControl,
        char                *pszText);
void EgLogStart(
        struct _stEgControl *pstEgControl);
void EgLogStop(
        struct _stEgControl *pstEgControl);
unsigned int  EgLogMark(
        struct _stEgControl *pstEgControl);
void EgLogFileClose(
        struct _stEgControl *pstEgControl);

void EgSetScreenDimensions(
        struct _stEgControl *pstEgControl,
        int    iEgMonWidthPix,
        int    iEgMonHeightPix,
        int    iEgMonHorzOffset,
        int    iEgMonVertOffset,
        int    iEgWindowWidthPix,
        int    iEgWindowHeightPix,
        int    iEgWindowHorzOffset,
        int    iEgWindowVertOffset);
void EgInitScreenDimensions(
        struct _stEgControl *pstEgControl, 
        int    iEgMonWidthPix,
        int    iEgMonHeightPix,
        int    iEgMonHorzOffsetPix,
        int    iEgMonVertOffsetPix,
        int    iEgWindowWidthPix,
        int    iEgWindowHeightPix,
        int    iEgWindowHorzOffset, 
        int    iEgWindowVertOffset);
void EgUpdateScreenResolutions(
        int  iEgMonWidthPix,
        int  iEgMonHeightPix);
void EgUpdateMonPixelOffsets(
        int  iEgMonHorzOffsetPix,
        int  iEgMonVertOffsetPix);
void EgUpdateWindowParameters(
        int  iEgWindowWidthPix,
        int  iEgWindowHeightPix,
        int  iEgWindowHorzOffset,
        int  iEgWindowVertOffset);
void EgWindowPixFromMonMm(
        int   *piIEgWindowPix,
        int   *piJEgWindowPix,
        float  fXMonMm,
        float  fYMonMm);
void MonMmFromEgWindowPix(
        float *pfXMonMm,
        float *pfYMonMm,
        float *pfZMonMm,          // pointer to Z may be null
        int    iIEgWindowPix,
        int    iJEgWindowPix);
void EgMonitorPixFromMonMm(
        int   *piIEgMontorPix,
        int   *piJEgMontorPix,
        float  fXMonMm,
        float  fYMonMm);
void MonMmFromEgMonitorPix(
        float *pfXMonMm,
        float *pfYMonMm,
        float *pfZMonMm,          // pointer to Z may be null
        int    iIEgMontorPix,
        int    iJEgMontorPix);
void EgMonitorPixFromEgWindowPix(
        int   *piIEgMonitorPix,
        int   *piJEgMonitorPix,
        int    iIEgWindowPix,
        int    iJEgWindowPix);
void EgWindowPixFromEgMonitorPix(
        int   *piIEgWindowPix,
        int   *piJEgWindowPix,
        int    iIEgMonitorPix,
        int    iJEgMonitorPix);
void GdsPixFromMonMm(
        int   *piIGdsPix,
        int   *piJGdsPix,
        float  fXMonMm,
        float  fYMonMm);
void MonMmFromGdsPix(
        float *pfXMonMm,
        float *pfYMonMm,
        float *pfZMonMm,          // pointer to Z may be null
        int    iIGdsPix,
        int    iJGdsPix);
void ScaleEgMonPixFromMm(
        int   *piIPix,
        int   *piJPix,
        float  fXMm,
        float  fYMm);
void ScaleEgMonMmFromPix(
        float *pfXMm,
        float *pfYMm,
        int    iIPix,
        int    iJPix);

/* Eye Image functions:                                                     */
struct _stEyeImageInfo *EgEyeImageInit(
          struct _stEyeImageInfo *stEyeImageInfo,
          int iDivisor);

void EgEyeImageDisplay(int iVis,
                       int iX, int iY, int iWidth, int iHeight, HDC hdc);

/****************************************************************************/

#define EG_COMM_TYPE_LOCAL  0    /* Single computer configuration.          */
#define EG_COMM_TYPE_SOCKET 1    /* 2 computers, comm over TCP/IP.          */

#define EG_MESSAGE_TYPE_GAZEINFO       0
#define EG_MESSAGE_TYPE_MOUSEPOSITION  1
#define EG_MESSAGE_TYPE_MOUSEBUTTON    2
#define EG_MESSAGE_TYPE_KEYBD_COMMAND  3
#define EG_MESSAGE_TYPE_MOUSERELATIVE  4
#define EG_MESSAGE_TYPE_VERGENCE       5
#define EG_MESSAGE_TYPE_IMAGEDATA      81

#define EG_MESSAGE_TYPE_CALIBRATE              10
#define EG_MESSAGE_TYPE_WORKSTATION_QUERY      11
#define EG_MESSAGE_TYPE_WORKSTATION_RESPONSE   12
#define EG_MESSAGE_TYPE_CLEAR_SCREEN           13
#define EG_MESSAGE_TYPE_SET_COLOR              14
#define EG_MESSAGE_TYPE_SET_DIAMETER           15
#define EG_MESSAGE_TYPE_DRAW_CIRCLE            16
#define EG_MESSAGE_TYPE_DRAW_CROSS             17
#define EG_MESSAGE_TYPE_DISPLAY_TEXT           18
#define EG_MESSAGE_TYPE_CALIBRATION_COMPLETE   19
#define EG_MESSAGE_TYPE_CALIBRATION_ABORTED    20
#define EG_MESSAGE_TYPE_TRACKING_ACTIVE        22
#define EG_MESSAGE_TYPE_TRACKING_INACTIVE      23
#define EG_MESSAGE_TYPE_VOICE_ACTIVE           24
#define EG_MESSAGE_TYPE_VOICE_INACTIVE         25

#define EG_MESSAGE_TYPE_BEGIN_SENDING_DATA     30
#define EG_MESSAGE_TYPE_STOP_SENDING_DATA      31
#define EG_MESSAGE_TYPE_CLOSE_AND_RECYCLE      32
#define EG_MESSAGE_TYPE_FILE_OPEN              33
#define EG_MESSAGE_TYPE_FILE_WRITE_HEADER      34
#define EG_MESSAGE_TYPE_FILE_APPEND_TEXT       35
#define EG_MESSAGE_TYPE_FILE_START_RECORDING   36
#define EG_MESSAGE_TYPE_FILE_STOP_RECORDING    37
#define EG_MESSAGE_TYPE_FILE_MARK_EVENT        38
#define EG_MESSAGE_TYPE_FILE_CLOSE             39
#define EG_MESSAGE_TYPE_CALIBRATE_ABORT        21
#define EG_MESSAGE_TYPE_BEGIN_SENDING_VERGENCE 40
#define EG_MESSAGE_TYPE_STOP_SENDING_VERGENCE  41

#define EG_EVENT_NONE              0
#define EG_EVENT_MOUSEPOSITION     1
#define EG_EVENT_MOUSERELATIVE     2
#define EG_EVENT_MOUSEBUTTON       3
#define EG_EVENT_KEYBOARD_COMMAND  4
#define EG_EVENT_UPDATE_EYE_IMAGE  5
#define EG_EVENT_TRACKING_ACTIVE   6
#define EG_EVENT_TRACKING_INACTIVE 7
#define EG_EVENT_VOICE_ACTIVE      8
#define EG_EVENT_VOICE_INACTIVE    9

#define EG_ERROR_EYEGAZE_ALREADY_INITIALIZED      9101
#define EG_ERROR_TRACKING_TERMINATED              9102
#define EG_ERROR_MEMORY_ALLOC_FAILED              9103
#define EG_ERROR_LCT_COMM_OPEN_FAILED             9104
                                              
/* Constants used in calls to EgCalibrate()                                 */
enum {EG_CALIBRATE_DISABILITY_APP,
      EG_CALIBRATE_NONDISABILITY_APP};

enum {CAL_KEY_COMMAND_ESCAPE,
      CAL_KEY_COMMAND_RESTART,
      CAL_KEY_COMMAND_SKIP,
      CAL_KEY_COMMAND_ACCEPT,
      CAL_KEY_COMMAND_RETRIEVE,
      CAL_KEY_COMMAND_SPACE};

/****************************************************************************/
#ifdef __cplusplus
}          /* Assume C declarations for C++ */
#endif  /* __cplusplus */
/****************************************************************************/
#endif // defined EGWIN_H_INCLUDED
/****************************************************************************/
