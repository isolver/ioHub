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
import ctypes
import unit_conversions as ucs

vis_degrees,screen_res,ppd=None,None,None

class Display(Device):
    _displayCoordinateType=None
    CATEGORY_LABEL='VISUAL_STIMULUS_PRESENTER'
    DEVICE_LABEL='DISPLAY_DEVICE'
    _user32=ctypes.windll.user32
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
    __slots__=[]
    def __init__(self,*args,**kwargs):
        Display._settings=kwargs['dconfig']
        deviceSettings={'instance_code':self._settings['instance_code'],
            'category_id':ioHub.devices.EventConstants.DEVICE_CATERGORIES[Display.CATEGORY_LABEL],
            'type_id':ioHub.devices.EventConstants.DEVICE_TYPES[Display.DEVICE_LABEL],
            'device_class':self._settings['device_class'],
            'name':self._settings['name'],
            'os_device_code':'OS_DEV_CODE_NOT_SET',
            'max_event_buffer_length':16,
            '_isReportingEvents':self._settings.get('auto_report_events',True)
            }

        self._determineDisplayCoordSpace()
        self._createPsychopyCalibrationFile()
        Device.__init__(self,*args,**deviceSettings)

    def _createPsychopyCalibrationFile(self):
        from psychopy import monitors
        psychoMonitor=monitors.Monitor(self._settings['name'], width=self._settings['calibration_surface_dimensions']['width'],
            distance=self._settings['default_eye_to_calibration_surface_distance']['plane_center'], gamma=1.0,
            notes=self._settings['comments'])
        psychoMonitor.setCalibDate()
        psychoMonitor.setSizePix(self.getScreenResolution())
        psychoMonitor.saveMon()
        psychoMonitor.setCurrent(0)

    def _determineDisplayCoordSpace(self):
        dispCoordType=self._settings['reporting_unit_type']

        for ctype,cvalues in self.ccordinateTypes.iteritems():
            if dispCoordType in cvalues:
                Display._displayCoordinateType=ctype
                break

        if Display._displayCoordinateType is None:
            Display._displayCoordinateType='pix'
            ioHub.print2err("ERROR: Display._determineDIsplayCoordSpace: Unknown coord space parameter setting; using 'pix': "+dispCoordType)

        return Display._displayCoordinateType

    @classmethod
    def getDisplayCoordinateType(cls):
        return cls._displayCoordinateType

    @classmethod
    def pixel2DisplayCoord(cls,px,py):
        try:
            dw,dh=cls.getScreenResolution()
            coordSpace=cls.getDisplayCoordinateType()

            dx= px-dw/2
            dy=-(py-dh/2)

            if coordSpace == 'pix':
                return dx,dy

            elif coordSpace == 'deg':
                #distH,distV=cls.pixelToDist(swidth/float(pixHres),sheight/float(pixVres),swidth,sheight,px,py)
                #eyeDist=cls._settings['default_eye_to_calibration_surface_distance']['plane_center']
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
            dw,dh=cls.getScreenResolution()
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

    @classmethod
    def getScreenResolution(cls):
        """
        Get the monitor's current pixel resolution based on the current graphics mode.

        Args: None
        Return (list): (width,height) of the monitor based on it's current graphics mode.
        """
        #  >> WIN32_ONLY
        r= cls._user32.GetSystemMetrics(0), cls._user32.GetSystemMetrics(1)
        #  << WIN32_ONLY
        return r

    @staticmethod
    def getScreenIndex():
        """
        Get the index of display to use when creating the full screen window in multi display physical setups.

        Args: None
        Return (int): index of display in multi display psychical setups
        """
        return Display._settings.get('display_index',0)

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