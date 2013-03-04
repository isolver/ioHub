# coding=utf-8
"""
ioHub
.. file: ioHub/devices/display/__init__.py

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""


from .. import Device,Computer
import ioHub
currentSec=Computer.currentSec
import unit_conversions as ucs
import threading
import Queue

class RetraceDetector(threading.Thread):
    """Threaded retrace detection"""
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.running=True
        self._hidden_window=None
    def run(self):
        try:
            import pyglet
            import pyglet.gl as GL
            from pyglet.window import Window
            self._hidden_window = Window(width=1, height=1, visible=False)
            while self.running:
                ioHub.print2err("RD S..")
                self._hidden_window.switch_to()
                GL.glBegin(GL.GL_POINTS)
                GL.glColor4f(0,0,0,0)
                GL.glVertex2i(10,10)
                GL.glEnd()
                GL.glFinish()
                t=Computer.getTime()
                ioHub.print2err("RD S.. ",t)
                self.queue.put(t)
            
            self.queue.put(None)
            self._hidden_window=None
        except:
            ioHub.print2err("Error running Display Retrace Detection Thread")
            ioHub.printExceptionDetailsToStdErr()
            self.queue.put(None)
            
class Display(Device):
    _displayCoordinateType=None
    screenInfoList=None
    _ppd=None
    ccordinateTypes={'pix':('pixels','pix','pixs','pixel'),     # - You can also specify the size and location of your stimulus in pixels. Obviously this has the disadvantage that
                                                                # sizes are specific to your monitor (because all monitors differ in pixel size). Spatial frequency: `cycles per pixel`
                                                                # (this catches people out but is used to be in keeping with the other units. If using pixels as your units you probably
                                                                # want a spatial frequency in the range 0.2-0.001 (i.e. from 1 cycle every 5 pixels to one every 100 pixels). Requires :
                                                                # information about the size of the screen (not window) in pixels, although this can often be deduce from the operating 
                                                                # system if it has been set correctly there.
                     'degrees':('ang','angle','deg','degree','degrees'),  # - Use degrees of visual angle to set the size and location of the stimulus. This is, of course, dependent on the
                                                                # distance that the participant sits from the screen as well as the screen itself, so make sure that this is controlled,
                                                                # and remember to change the setting in Monitor Center if the viewing distance changes. Spatial frequency: cycles per degree
                                                                # Requires : information about the screen width in cm and pixels and the viewing distance in cm
                     'height':('height',),                      # - With ‘height’ units everything is specified relative to the height of the window (note the window, not the screen).
                                                                # As a result, the dimensions of a screen with standard 4:3 aspect ratio will range (-0.6667,-0.5) in the bottom left
                                                                # to (+0.6667,+0.5) in the top right. For a standard widescreen (16:10 aspect ratio) the bottom left of the screen 
                                                                # is (-0.8,-0.5) and top-right is (+0.8,+0.5).
                     'normalized':('norm','normal'),            # - In normalised (‘norm’) units the window ranges in both x and y from -1 to +1. That is, the top right of the window has
                                                                # coordinates (1,1), the bottom left is (-1,-1). Note that, in this scheme, setting the height of the stimulus to be 1.0,
                                                                # will make it half the height of the window, not the full height (because the window has a total height of 1:-1 = 2!). 
                                                                # Also note that specifying the width and height to be equal will not result in a square stimulus if your window is not square
                                                                # the image will have the same aspect ratio as your window. e.g. on a 1024x768 window the size=(0.75,1) will be square.
                                                                # Spatial frequency: cycles per stimulus (so will scale with the size of the stimulus).
                    'cm':('cm',)}                                 # - Set the size and location of the stimulus in centimeters on the screen.Spatial frequency: cycles per cm.
                                                                # Requires : information about the screen width in cm and size in pixels Assumes : pixels are square. Can be verified by drawing
                                                                # a stimulus with matching width and height and verifying that it is in fact square. For a CRT this can be controlled by setting
                                                                # the size of the viewable screen (settings on the monitor itself). Requires : No monitor information
    SCREEN_COUNT=1
    stimulus_screen_index=0
    stimulus_screen_info=None

#    _retraceDetectionThread=None
    
    ALL_EVENT_CLASSES=[]
    
    DEVICE_TYPE_ID=ioHub.DeviceConstants.DISPLAY
    DEVICE_TYPE_STRING=ioHub.DeviceConstants.getName(DEVICE_TYPE_ID)
    __slots__=['stimulus_screen_index']
    def __init__(self,*args,**kwargs):
        Display.ALL_EVENT_CLASSES=[]
        dconfig=kwargs.get('dconfig',{})
        deviceSettings={
            'type_id':ioHub.DeviceConstants.DISPLAY,
            'device_class':Display.__name__,
            'name':dconfig.get('name','display'),
            'os_device_code':'OS_DEV_CODE_NOT_SET',
            'max_event_buffer_length':16,
            'monitor_event_types':dconfig.get('monitor_event_types',self.ALL_EVENT_CLASSES),
            'stimulus_screen_index':dconfig.get('display_index',0),
            'psychopy_config_file':dconfig.get('psychopy_config_file','ioHubDefault'),
            '_isReportingEvents':dconfig.get('auto_report_events',True)
            }
        Device.__init__(self,*args,**deviceSettings)

        self._startupConfiguration=dconfig

        Display.stimulus_screen_index=self._startupConfiguration.get('display_index',0)
        
        Display._detectDisplayCountAndResolutions(self._startupConfiguration)
        self._determineDisplayCoordSpace()
        self._createPsychopyCalibrationFile()
        
        #if Display._retraceDetectionThread is None and Computer.isIoHubProcess==True:
        #    Display._startRetraceDetectionThread()
            

    def _close(self):
        Display._stopRetraceDetectionThread()
        Device._close(self) 
    
    @classmethod
    def getScreenInfoList(cls):
        sl=[]
        for sil in Display.screenInfoList:
            sd={}
            for key,value in sil.iteritems():
                if not key.startswith('screen_physical_info'):
                    sd[key]=value 
            sl.append(sd)
        return sl
        
    @classmethod
    def _detectDisplayCountAndResolutions(cls, screen_physical_info=None):
        if Display.screenInfoList is None:
            import wx
            wxapp=wx.PySimpleApp()             

            from ioHub import OrderedDict

            Display.screenInfoList=[]

            Display.SCREEN_COUNT=wx.Display.GetCount()

            if Display.stimulus_screen_index >= Display.SCREEN_COUNT:
                Display.stimulus_screen_index=0

            for i in range(Display.SCREEN_COUNT):
                d=wx.Display(i)
                mode=d.GetCurrentMode()
                mode.w,mode.h,mode.bpp,mode.refresh
                x,y,w,h=d.GetGeometry()
                primary=d.IsPrimary()
                ok=d.IsOk()
                
                amonitor=OrderedDict()
                amonitor['width']=w
                amonitor['height']=h
                amonitor['mode']=(mode.w,mode.h,mode.bpp,mode.refresh)
                amonitor['index']=i
                amonitor['primary']=primary
                amonitor['resolution']=w,h
                amonitor['region']=(x,y,w,h)

                if Display.stimulus_screen_index == i and screen_physical_info is not None:
                    amonitor['screen_physical_info']=screen_physical_info
                    origin=screen_physical_info.get('display_pixel_origin',(0.0,0.0))
                    origin=origin[0]*w,origin[1]*h
                    amonitor['origin']=origin
                    
                Display.screenInfoList.append(amonitor)
            wxapp.Exit()

    @staticmethod
    def getStimulusScreenInfo():
        """
        Get the stimuus monitor's information as an OrderedDict.

        Args: None
        Return (OrderedDict): key,value pais for various scrren attributes
        """
        if Display.screenInfoList is None:
            Display._detectDisplayCountAndResolutions()
        return Display.screenInfoList[Display.stimulus_screen_index]

    @staticmethod
    def getMonitorCount():
        if Display.screenInfoList is None:
            Display._detectDisplayCountAndResolutions()
        return Display.SCREEN_COUNT

    @staticmethod
    def getStimulusScreenIndex():
        """
        Get the index of display to use when creating the full screen window in multi display physical setups.

        Args: None
        Return (int): index of display in multi display psychical setups
        """
        return Display.stimulus_screen_index

    @staticmethod
    def setStimulusScreenIndex(i,screen_physical_info):
        """
        Get the index of display to use when creating the full screen window in multi display physical setups.

        Args: None
        Return (int): index of display in multi display psychical setups
        """
        if i < Display.SCREEN_COUNT:
            Display.stimulus_screen_index=i
        if Display.screenInfoList is None:
            Display._detectDisplayCountAndResolutions(screen_physical_info)
            Display._ppd=None
            Display.getPPD(screen_physical_info=screen_physical_info)


        
    @staticmethod
    def getPPD(alg='simple',screen_physical_info=None):
        try:
            #ioHub.print2err("getPPD: isHubProcess: {0} Current Display._ppd: {1} Display.screenInfoList : {2} screen_physical_info : {3}".format(ioHub.devices.Computer.isIoHubProcess,Display._ppd, Display.screenInfoList,screen_physical_info ))
            if Display.screenInfoList is None:
                Display._detectDisplayCountAndResolutions(screen_physical_info)
            if Display._ppd is None:
                if alg == 'simple':
                     import math
                     stim_screen_info=Display.screenInfoList[Display.stimulus_screen_index]


                     phys_width=stim_screen_info['screen_physical_info']['physical_stimulus_area']['width']
                     phys_height=stim_screen_info['screen_physical_info']['physical_stimulus_area']['height']
                     viewing_distance=float(stim_screen_info['screen_physical_info']['default_eye_to_surface_distance']['surface_center'])

                     rx,ry=stim_screen_info['width'],stim_screen_info['height']
                     degree_width=57.2958 * math.atan(phys_width/viewing_distance)
                     degree_height=57.2958 * math.atan(phys_height/viewing_distance)
                     ppd_x=rx/degree_width
                     ppd_y=ry/degree_height
                     Display._ppd=ppd_x,ppd_y
                     #ioHub.print2err("Display._ppd: ",Display._ppd)
                     return Display._ppd
                else:
                    raise Exception ("Only 'simple' PPD calculation type is supported at this time")
            #ioHub.print2err("Display._ppd: ",Display._ppd)
            return Display._ppd
        except:
            ioHub.print2err("ERROR GETTING PPD ! returning default 30,30 PPD")
            ioHub.printExceptionDetailsToStdErr()
            return 30, 30

    @staticmethod
    def getStimulusScreenOrigin():
        """
        Get the stimulus monitor's 0,0 pixel position in 0,0==screen top-left, screen_width,screen_height=bottom-right pixel pixel coords.

        Args: None
        Return (list): (width,height) of the monitor based on it's current graphics mode.
        """
        return Display.getStimulusScreenInfo().get('origin',(0.0,0.0))

    @staticmethod
    def setStimulusScreenOrigin(o):
        """
        Get the stimulus monitor's 0,0 pixel position in 0,0==screen top-left, screen_width,screen_height=bottom-right pixel pixel coords.

        Args: None
        Return (list): (width,height) of the monitor based on it's current graphics mode.
        """
        Display.screenInfoList[Display.stimulus_screen_index]['origin']=o

    @staticmethod
    def getStimulusScreenResolution():
        """
        Get the stimulus monitor's pixel resolution based on the current graphics mode.

        Args: None
        Return (list): (width,height) of the monitor based on it's current graphics mode.
        """
        return Display.getStimulusScreenInfo()['resolution']

    @staticmethod
    def getStimulusScreenReportedRetraceInterval():
        """
        Get the stimulus monitor's reported retrace 'interval' (1000.0/retrace_rate) based on the current graphics mode.

        Args: None
        Return (list): (width,height) of the monitor based on it's current graphics mode.
        """
        return 1000.0/Display.getStimulusScreenInfo()['mode'][-1]

    def getConfigFileDistance(self):
        return self._startupConfiguration['default_eye_to_surface_distance']['surface_center']
    
    def getConfigFileWidth(self):
        return self._startupConfiguration['physical_stimulus_area']['width']

    def getConfigFileHeight(self):
        return self._startupConfiguration['physical_stimulus_area']['height']
        
    def _determineDisplayCoordSpace(self):
        dispCoordType=self._startupConfiguration.get('reporting_unit_type',None)

        if dispCoordType:
            for ctype,cvalues in self.ccordinateTypes.iteritems():
                if dispCoordType in cvalues:
                    Display._displayCoordinateType=ctype
                    break

        if Display._displayCoordinateType is None:
            Display._displayCoordinateType='pix'
            ioHub.print2err("ERROR: Display._determineDIsplayCoordSpace: Unknown coord space parameter setting; using 'pix': "+str(dispCoordType))

        return Display._displayCoordinateType

    @classmethod
    def getDisplayCoordinateType(cls):
        return cls._displayCoordinateType

    def getPsychoPyMonitorSettingsName(self):
        return self._startupConfiguration.get('psychopy_config_file','ioHubDefault')

    @classmethod
    def getStimulusScreenBounds(cls):
        dw,dh=cls.getStimulusScreenResolution()
        ox,oy=cls.getStimulusScreenOrigin()
        return 0-ox,0-oy,0-ox+dw,0-oy+dh 
            
    @classmethod
    def pixel2DisplayCoord(cls,px,py):
        try:
            dw,dh=cls.getStimulusScreenResolution()
            coordSpace=cls.getDisplayCoordinateType()
            ox,oy=cls.getStimulusScreenOrigin()
            if ox==0:
                dx=px
            else:
                dx= (px-(dw-ox))
            if ox==0:
                dy=py
            else:
                dy= -(py-(dh-oy))


            if coordSpace == 'pix':
                return dx,dy

            elif coordSpace == 'deg':
                #distH,distV=cls.pixelToDist(swidth/float(pixHres),sheight/float(pixVres),swidth,sheight,px,py)
                #eyeDist=self._startupConfiguration['default_eye_to_calibration_surface_distance']['surface_center']
                #r=cls.convertDistToNd(eyeDist,distH,distV)
                #ioHub.print2stderr(">>>> Pixels x,y to Angle h,v: "+str((px,py))+" : "+str(r))
                ioHub.print2err(">>>> UNIMPLEMENTED dispCoordType: "+coordSpace)
                return 0.0,0.0
            else:
                ioHub.print2err(">>>> UNKNOWN dispCoordType: "+coordSpace)
                return 0.0,0.0
        except Exception, e:
            ioHub.print2err('ERROR pixel2DisplayCoord: '+str(e))
            ioHub.printExceptionDetailsToStdErr()
            return 0.0,0.0


    @classmethod
    def displayCoord2Pixel(cls,dx,dy,):
        try:
            dw,dh=cls.getStimulusScreenResolution()
            coordSpace=cls.getDisplayCoordinateType()

            if coordSpace == 'pix':
                px=dx+dw/2
                py=(dy+dh/2)
                return px,py

            elif coordSpace == 'deg':
                ioHub.print2err(">>>> getDisplayCoordinateType for degrees not implemented yet.: "+coordSpace)
                return 0.0,0.0
            else:
                ioHub.print2err(">>>> UNIMPLEMENTED dispCoordType: "+coordSpace)
                return 0.0,0.0
        except Exception, e:
            ioHub.print2err('ERROR displayCoord2Pixel: '+str(e))
            ioHub.printExceptionDetailsToStdErr()
            return 0.0,0.0

    def _createPsychopyCalibrationFile(self):
        from psychopy import monitors

        #TODO: TRY TO BETTER INTEGRATE Display classs with PsychoPy Monitor file
        
        stim_area=self._startupConfiguration.get('physical_stimulus_area',None)
        if stim_area is None:
            ioHub.print2err("WARNING: USING DEFAULT DISPLAY DIMENSION SETTINGS !!")
            dwidth=500.0
        else:
            dwidth=self._startupConfiguration['physical_stimulus_area']['width']

        sdist_info=self._startupConfiguration.get('default_eye_to_surface_distance',None)
        if sdist_info is None:
            ioHub.print2err("WARNING: USING DEFAULT DISPLAY DISTANCE SETTINGS !!")
            ddist=500.0
        else:
            ddist= self._startupConfiguration['default_eye_to_surface_distance']['surface_center']
       
        psychoMonitor=monitors.Monitor(self._startupConfiguration.get('psychopy_config_file','ioHubDefault'),
                                       width=dwidth, distance=ddist, gamma=1.0)
        psychoMonitor.setSizePix(self.getStimulusScreenResolution())
        psychoMonitor.saveMon()
        psychoMonitor.setCurrent(0)

    def _poll(self):
        pass

#    def _getIOHubEventObject(self,event):
#        ioHub.print2err("Retrace Event at: ",event)
#        return None
#    
#    def _getNativeEventBuffer(self):
#        if Display._retraceDetectionThread is None or Display._retraceDetectionThread.running is False:
#            return []
#            
#        events=[]
#        try:
#            e=Display._retraceEventQueue.get_nowait()
#            if e is not None:            
#                events.append(e)
#                Display._retraceEventQueue.task_done()
#        except Queue.Empty:
#            return events
#        return []
        
#    @staticmethod
#    def _startRetraceDetectionThread():
#        Display._retraceEventQueue=Queue.Queue()          
#        Display._retraceDetectionThread=RetraceDetector(Display._retraceEventQueue)
#        Display._retraceDetectionThread.start()
#        ioHub.print2err("Display Device Retrace Detection Thread Started.")
#
#
#    @staticmethod
#    def _stopRetraceDetectionThread():
#        if Display._retraceDetectionThread.running:
#            Display._retraceDetectionThread.running=False
#            
#            e=1
#            while e is not None:
#                e=Display._retraceEventQueue.get()
#                Display._retraceEventQueue.task_done()
#            Display._retraceEventQueue.join()
#            Display._retraceEventQueue=None
#            Display._retraceDetectionThread=None
#            ioHub.print2err("Display Device Retrace Detection Thread Stopped.")
            
            
    ################################################
    #
    # distToPixel
    #
    # Convert between distance coordinates and pixel coordinates.
    #
    # Distance coordinates are 2D Cartesian coordinates, measured from an origin at the
    # center pixel,  and are real distance units (inches, centimeters, etc.) along horizontal and
    # vertical screen axes.
    #
#    @staticmethod
#    def distToPixel(hpix_per_dist_unit, vpix_perdist_unit, pixHres, pixVres, distH, distV):
#        r = ucs.distToPixel(hpix_per_dist_unit,vpix_perdist_unit,pixHres, pixVres,distH,distV)
#        return r

#    @staticmethod
#    def pixelToDist(hpix_per_dist_unit,vpix_perdist_unit,pixHres, pixVres, pixH, pixV):
#        r = ucs.pixelToDist(hpix_per_dist_unit,vpix_perdist_unit,pixHres, pixVres, pixH, pixV)
#        return r

    #
    # All of following assume a nominal eye point 'eye2display' distance units from display
    # with line-of-gaze normal to the display at the display center.  Angle variable are
    # assumed to have units of degrees.
    #
    # Since the Python math lib trig functions work with radians,
    # a radian to angle conversion factor (deg/rad = 57.2958) is included to give angle
    # variables 'degree' units.
    #

    #
    # Convert between distance coordinates (distH, distV) and 'normalized Cartesian
    # coordinates' (ndH, ndV).
    #
    # 'Normalized Cartesian coordinates' are Cartesian distance coordinates, normalized by
    # by the distance from the nominal eye point to the display.  For very small distances
    # from the origin, these values coorespond to visual angle from the origin along the
    # horizontal and vertical display axes. A factor of 57.2958 is used so that the values
    # correspond to degrees rather than radians.
    #
    
#    @staticmethod
#    def convertDistToNd(eye2display,distH,distV):
#        return ucs.convertDistToNd(eye2display,distH,distV)
        
#    @staticmethod
#    def convertNdToDist(eye2display, ndH, ndV):
#        return ucs.convertNdToDist(eye2display, ndH, ndV)

    #
    # Convert between distance coordinates (distH, distV) and
    # 'Cartesian Angles' (caH, caV).
    # 'Cartesian Angles' are visual angles (from nominal eye point) along
    # horizontal and vertical display axes.  In other words, the horizontal coordinate is the
    # visual angle between the origin and the intersection of the Cartesian
    # coordinate line with the horizontal axes.
    #
#    @staticmethod
#    def distToCa(eye2display, distH, distV):
#        return ucs.distToCa(eye2display, distH, distV)
    
#    @staticmethod
#    def caToDist(eye2display, caH, caV):
#        return ucs.caToDist(eye2display, caH, caV)

        
    #
    # Convert between distance coordinates (distH, distV) and Fick Coordinates (as,el)
    #
#    @staticmethod
#    def distToFick(eye2display,distH,distV):
#        return ucs.distToFick(eye2display,distH,distV)

#    @staticmethod
#    def fickToDist(eye2display, az, el):
#        return ucs.fickToDist(eye2display, az, el)

    #
    # Convert between distance coordinates (distH, distV) and 'symmetric angle'
    # coordinates (saH, saV).
    # 'Symmetric angles' are visual angles between a point on the display and the central
    # axes lines, measured along lines parallel to the display axes.  The vertical coordinate is
    # same as the Fick elevation angle.  The horizontal coordinate is measured in a
    # symmetrical fashion and is not the same as the Fick azimuth angle.
    #
#    @staticmethod
#    def distToSa(eye2display, distH, distV):
#        return ucs.distToSa(eye2display,distH,distV)
    
#    @staticmethod
#    def saToDist(self,eye2display, saH, saV):
#        return ucs.saToDist(eye2display, saH, saV)


            
######### Display Events ###########