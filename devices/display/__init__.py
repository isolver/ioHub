# coding=utf-8
"""
ioHub
.. file: ioHub/devices/display/__init__.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""


from .. import Device,Computer
import ioHub
currentSec=Computer.currentSec
import unit_conversions as ucs

vis_degrees,screen_res,ppd=None,None,None

class Display(Device):
    _displayCoordinateType=None
    CATEGORY_LABEL='VISUAL_STIMULUS_PRESENTER'
    DEVICE_LABEL='DISPLAY_DEVICE'
    SCREEN_COUNT=1
    
    stimulus_screen_index=0
    stimulus_screen_info=None
    _screenInfoList=None
    _ppd=None
    _settings=None
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
    __slots__=['stimulus_screen_index']
    def __init__(self,*args,**kwargs):
        Display._settings=kwargs.get('dconfig',{})
        deviceSettings={
            'category_id':ioHub.devices.EventConstants.DEVICE_CATERGORIES[Display.CATEGORY_LABEL],
            'type_id':ioHub.devices.EventConstants.DEVICE_TYPES[Display.DEVICE_LABEL],
            'device_class':Display.__name__,
            'name':self._settings.get('name','display'),
            'os_device_code':'OS_DEV_CODE_NOT_SET',
            'max_event_buffer_length':16,
            'stimulus_screen_index':self._settings.get('display_index',0),
            'psychopy_config_file':self._settings.get('psychopy_config_file','ioHubDefault'),
            '_isReportingEvents':self._settings.get('auto_report_events',True)
            }
        
        Display.stimulus_screen_index=Display._settings.get('display_index',0)
        
        self._detectDisplayCountandResolutions()
        self._determineDisplayCoordSpace()
        self._createPsychopyCalibrationFile()
        Device.__init__(self,*args,**deviceSettings)

    @classmethod
    def _detectDisplayCountandResolutions(cls):
        if Display._screenInfoList is None:
            import wx
            wxapp=wx.PySimpleApp()             

            from collections import OrderedDict

            Display._screenInfoList=[]
            Display.SCREEN_COUNT=wx.Display.GetCount()

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
                
                Display._screenInfoList.append(amonitor)
            
            if Display.stimulus_screen_index >= Display.SCREEN_COUNT:
               Display.stimulus_screen_index=0
            
            wxapp.Exit()

    @staticmethod
    def getStimulusScreenInfo():
        """
        Get the stimuus monitor's information as an OrderedDict.

        Args: None
        Return (OrderedDict): key,value pais for various scrren attributes
        """
        if Display._screenInfoList is None:
            Display._detectDisplayCountandResolutions()
        return Display._screenInfoList[Display.stimulus_screen_index]

    @staticmethod
    def getMonitorCount():
        if Display._screenInfoList is None:
            Display._detectDisplayCountandResolutions()
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
    def setStimulusScreenIndex(i):
        """
        Get the index of display to use when creating the full screen window in multi display physical setups.

        Args: None
        Return (int): index of display in multi display psychical setups
        """
        if Display._screenInfoList is None:
            Display._detectDisplayCountandResolutions()
        if i < Display.SCREEN_COUNT:
            Display.stimulus_screen_index=i
            Display._ppd=None
        
        
    @staticmethod
    def getPPD(alg='simple'):
        if Display._screenInfoList is None:
            Display._detectDisplayCountandResolutions()
        if alg == 'simple':
             if Display._ppd is None:
                 import math

                 phys_width=Display._settings.get('physical_stimulus_area')['width']
                 phys_height=Display._settings.get('physical_stimulus_area')['height']
                 viewing_distance=float(Display._settings.get('default_eye_to_surface_distance')['surface_center'])

                 rx,ry=Display.getStimulusScreenResolution()
                 degree_width=57.2958 * math.atan(phys_width/viewing_distance)
                 degree_height=57.2958 * math.atan(phys_height/viewing_distance)
                 ppd_x=rx/degree_width
                 ppd_y=ry/degree_height

                 Display._ppd=ppd_x,ppd_y
             return Display._ppd
        else:
            return None

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

    def _determineDisplayCoordSpace(self):
        dispCoordType=self._settings.get('reporting_unit_type',None)

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
        return self._settings.get('psychopy_config_file','ioHubDefault')
        
    @classmethod
    def pixel2DisplayCoord(cls,px,py):
        try:
            dw,dh=cls.getStimulusScreenResolution()
            coordSpace=cls.getDisplayCoordinateType()

            dx= px-dw/2
            dy=-(py-dh/2)

            if coordSpace == 'pix':
                return dx,dy

            elif coordSpace == 'deg':
                #distH,distV=cls.pixelToDist(swidth/float(pixHres),sheight/float(pixVres),swidth,sheight,px,py)
                #eyeDist=cls._settings['default_eye_to_calibration_surface_distance']['surface_center']
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
        
        stim_area=self._settings.get('physical_stimulus_area',None)
        if stim_area is None:
            ioHub.print2err("WARNING: USING DEFAULT DISPLAY DIMENSION SETTINGS !!")
            dwidth=500.0
        else:
            dwidth=self._settings['physical_stimulus_area']['width']

        sdist_info=self._settings.get('default_eye_to_surface_distance',None)
        if sdist_info is None:
            ioHub.print2err("WARNING: USING DEFAULT DISPLAY DISTANCE SETTINGS !!")
            ddist=500.0
        else:
            ddist= self._settings['default_eye_to_surface_distance']['surface_center']
       
        psychoMonitor=monitors.Monitor(self._settings.get('psychopy_config_file','ioHubDefault'), 
                                       width=dwidth, distance=ddist, gamma=1.0)
        psychoMonitor.setSizePix(self.getStimulusScreenResolution())
        psychoMonitor.saveMon()
        psychoMonitor.setCurrent(0)

    def _poll(self):
        pass

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
    @staticmethod
    def distToPixel(hpix_per_dist_unit, vpix_perdist_unit, pixHres, pixVres, distH, distV):
        r = ucs.distToPixel(hpix_per_dist_unit,vpix_perdist_unit,pixHres, pixVres,distH,distV)
        return r

    @staticmethod
    def pixelToDist(hpix_per_dist_unit,vpix_perdist_unit,pixHres, pixVres, pixH, pixV):
        r = ucs.pixelToDist(hpix_per_dist_unit,vpix_perdist_unit,pixHres, pixVres, pixH, pixV)
        return r

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
    
    @staticmethod
    def convertDistToNd(eye2display,distH,distV):
        return ucs.convertDistToNd(eye2display,distH,distV)
        
    @staticmethod
    def convertNdToDist(eye2display, ndH, ndV):
        return ucs.convertNdToDist(eye2display, ndH, ndV)

    #
    # Convert between distance coordinates (distH, distV) and
    # 'Cartesian Angles' (caH, caV).
    # 'Cartesian Angles' are visual angles (from nominal eye point) along
    # horizontal and vertical display axes.  In other words, the horizontal coordinate is the
    # visual angle between the origin and the intersection of the Cartesian
    # coordinate line with the horizontal axes.
    #
    @staticmethod
    def distToCa(eye2display, distH, distV):
        return ucs.distToCa(eye2display, distH, distV)
    
    @staticmethod
    def caToDist(eye2display, caH, caV):
        return ucs.caToDist(eye2display, caH, caV)

        
    #
    # Convert between distance coordinates (distH, distV) and Fick Coordinates (as,el)
    #
    @staticmethod
    def distToFick(eye2display,distH,distV):
        return ucs.distToFick(eye2display,distH,distV)

    @staticmethod
    def fickToDist(eye2display, az, el):
        return ucs.fickToDist(eye2display, az, el)

    #
    # Convert between distance coordinates (distH, distV) and 'symmetric angle'
    # coordinates (saH, saV).
    # 'Symmetric angles' are visual angles between a point on the display and the central
    # axes lines, measured along lines parallel to the display axes.  The vertical coordinate is
    # same as the Fick elevation angle.  The horizontal coordinate is measured in a
    # symmetrical fashion and is not the same as the Fick azimuth angle.
    #
    @staticmethod
    def distToSa(eye2display, distH, distV):
        return ucs.distToSa(eye2display,distH,distV)
    
    @staticmethod
    def saToDist(self,eye2display, saH, saV):
        return ucs.saToDist(eye2display, saH, saV)


            
######### Display Events ###########