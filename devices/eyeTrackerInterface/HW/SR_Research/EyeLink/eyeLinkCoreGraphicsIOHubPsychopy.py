"""
ioHub
pyEyeTrackerInterface
.. file: ioHub/devices/eyeTrackerInterface/HW/SR_Research/EyeLink/eyeLinkCoreGraphicsIOHubPsychopy.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

---------------------------------------------------------------------------------------------------------------------
This file uses the pylink module, Copyright (C) SR Research Ltd. License type unknown as it is not provided in the
pylink distribution (atleast when downloaded May 2012). At the time of writing, Pylink is freely avalaible for
download from  www.sr-support.com once you are registered and includes the necessary C DLLs.
---------------------------------------------------------------------------------------------------------------------

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

from psychopy import visual
import ioHub.external_libs
import ioHub.devices as ioDevices

global Nsound
try:
    import Nsound
except:
    Nsound=None

import pylink
from pylink import EyeLinkCustomDisplay

from collections import OrderedDict
import sys, os, math, array, timeit

def currentSecTime():
    return timeit.default_timer()

EventConstants=ioHub.devices.EventConstants

class EyeLinkCoreGraphicsIOHubPsychopy(EyeLinkCustomDisplay):
    IOHUB_HEARTBEAT_INTERVAL=0.050   # seconds between forced run through of
                                     # micro threads, since one is blocking
                                     # on camera setup.

        # ** KEY: Escape ,key_id: 27 ,ascii_code: 27 ,scan_code: 1
        # ** KEY: F10 ,key_id: 121 ,ascii_code: 0 ,scan_code: 68
        # ** KEY: F9 ,key_id: 120 ,ascii_code: 0 ,scan_code: 67
        # ** KEY: F8 ,key_id: 119 ,ascii_code: 0 ,scan_code: 66
        # ** KEY: F7 ,key_id: 118 ,ascii_code: 0 ,scan_code: 65
        # ** KEY: F6 ,key_id: 117 ,ascii_code: 0 ,scan_code: 64
        # ** KEY: F5 ,key_id: 116 ,ascii_code: 0 ,scan_code: 63
        # ** KEY: F4 ,key_id: 115 ,ascii_code: 0 ,scan_code: 62
        # ** KEY: F3 ,key_id: 114 ,ascii_code: 0 ,scan_code: 61
        # ** KEY: F2 ,key_id: 113 ,ascii_code: 0 ,scan_code: 60
        # ** KEY: F1 ,key_id: 112 ,ascii_code: 0 ,scan_code: 59
        # ** KEY: Down ,key_id: 40 ,ascii_code: 0 ,scan_code: 80
        # ** KEY: Right ,key_id: 39 ,ascii_code: 0 ,scan_code: 77
        # ** KEY: Left ,key_id: 37 ,ascii_code: 0 ,scan_code: 75
        # ** KEY: Up ,key_id: 38 ,ascii_code: 0 ,scan_code: 72
        
    """
    65472 : 15616
    
    65473 : 15872
    
    65474 : 16128
    
    65475 : 16384
    
    65476 : 16640
    
    65477 : 16896
    
    65478 : 17152
    
    65479 : 17408
    
    65288 : 
    
    65293 : 13
    
    65361 : 19200
    
    65362 : 18432
    
    65363 : 19712
    
    65364 : 20480
    
    65365 : 18688
    
    65366 : 20736
    
    65307 : 27
    
    65470 : 15104
    
    65471 : 15360
    
    """
    IOHUB2PYLINK_KB_MAPPING={
            EventConstants.F1: pylink.F1_KEY,
            EventConstants.F2: pylink.F2_KEY,
            EventConstants.F3: pylink.F3_KEY,
            EventConstants.F4: pylink.F4_KEY,
            EventConstants.F5: pylink.F5_KEY,
            EventConstants.F6: pylink.F6_KEY,
            EventConstants.F7: pylink.F7_KEY,
            EventConstants.F8: pylink.F8_KEY,
            EventConstants.F9: pylink.F9_KEY,
            EventConstants.F10: pylink.F10_KEY,
            EventConstants.PAGEUP: pylink.PAGE_UP,
            EventConstants.PAGEDOWN: pylink.PAGE_DOWN,
            EventConstants.UP: pylink.CURS_UP,
            EventConstants.DOWN: pylink.CURS_DOWN,
            EventConstants.LEFT: pylink.CURS_LEFT,
            EventConstants.RIGHT: pylink.CURS_RIGHT,
            EventConstants.BACKSPACE: '\b',
            EventConstants.RETURN: pylink.ENTER_KEY,
            EventConstants.ESCAPE: pylink.ESC_KEY,
            EventConstants.F10: pylink.F10_KEY,
            EventConstants.F10: pylink.F10_KEY,
            }                                 
    
    SOUND_MAPPINGS={
                    -1 : 'wav/error.wav', #cal error beep
                    -2 : 'wav/error.wav', # DC error beep
                    0 : 'wav/qbeep.wav', # cal. good beep
                    1: 'wav/type.wav', # cal target beep
                    2:  'wav/qbeep.wav', # DC good beep
                    3 : 'wav/type.wav'  # dc target beep
                    #'wav/error.wav': None, # file name to Nsound buffer mapping
                    #'wav/qbeep.wav': None, # file name to Nsound buffer mapping
                    #'wav/type.wav': None, # file name to Nsound buffer mapping
                  }

    WINDOW_BACKGROUND_COLOR=(128,128,128)
    CALIBRATION_POINT_OUTER_RADIUS=15.0,15.0
    CALIBRATION_POINT_OUTER_EDGE_COUNT=64
    CALIBRATION_POINT_OUTER_COLOR=(255,255,255)
    CALIBRATION_POINT_INNER_RADIUS=3.0,3.0
    CALIBRATION_POINT_INNER_EDGE_COUNT=32
    CALIBRATION_POINT_INNER_COLOR=(25,25,25)

    def __init__(self, eyetrackerInterface, targetForegroundColor=None, targetBackgroundColor=None, screenColor=None, targetOuterDiameter=None, targetInnerDiameter=None, dc_sounds=["","",""], cal_sounds=["","",""]):
        EyeLinkCustomDisplay.__init__(self)
        
        ppd_x,ppd_y=ioDevices.Display.getPPD()

        self.screenSize = ioDevices.Display.getStimulusScreenResolution()
        self.tracker = eyetrackerInterface._eyelink

        if targetForegroundColor is not None:
            EyeLinkCoreGraphicsIOHubPsychopy.CALIBRATION_POINT_OUTER_COLOR=targetForegroundColor

        if targetBackgroundColor is not None:
            EyeLinkCoreGraphicsIOHubPsychopy.CALIBRATION_POINT_INNER_COLOR=targetBackgroundColor

        if screenColor is not None:
            EyeLinkCoreGraphicsIOHubPsychopy.WINDOW_BACKGROUND_COLOR=screenColor

        if targetOuterDiameter is not None:
            EyeLinkCoreGraphicsIOHubPsychopy.CALIBRATION_POINT_OUTER_RADIUS=targetOuterDiameter/2.0,targetOuterDiameter/2.0
        else:
            EyeLinkCoreGraphicsIOHubPsychopy.CALIBRATION_POINT_OUTER_RADIUS=ppd_x/2.0,ppd_y/2.0

        if targetInnerDiameter is not None:
            EyeLinkCoreGraphicsIOHubPsychopy.CALIBRATION_POINT_INNER_RADIUS=targetInnerDiameter/2.0,targetInnerDiameter/2.0
        else:
            EyeLinkCoreGraphicsIOHubPsychopy.CALIBRATION_POINT_INNER_RADIUS=ppd_x/6.0,ppd_y/6.0

        if dc_sounds is not None:
            targetS, goodS, errorS = dc_sounds
            if targetS is None or targetS.lower() == 'off':
                del EyeLinkCoreGraphicsIOHubPsychopy.SOUND_MAPPINGS[3]
            elif targetS.lower() == '':
                pass
            else:
                EyeLinkCoreGraphicsIOHubPsychopy.SOUND_MAPPINGS[3]=targetS

            if goodS is None or goodS.lower() == 'off':
                del EyeLinkCoreGraphicsIOHubPsychopy.SOUND_MAPPINGS[2]
            elif goodS.lower() == '':
                pass
            else:
                EyeLinkCoreGraphicsIOHubPsychopy.SOUND_MAPPINGS[2]=goodS

            if errorS is None or errorS.lower() == 'off':
                del EyeLinkCoreGraphicsIOHubPsychopy.SOUND_MAPPINGS[-2]
            elif errorS.lower() == '':
                pass
            else:
                EyeLinkCoreGraphicsIOHubPsychopy.SOUND_MAPPINGS[-2]=errorS

        if cal_sounds is not None:
            targetS, goodS, errorS = cal_sounds
            if targetS is None or targetS.lower() == 'off':
                del EyeLinkCoreGraphicsIOHubPsychopy.SOUND_MAPPINGS[1]
            elif targetS.lower() == '':
                pass
            else:
                EyeLinkCoreGraphicsIOHubPsychopy.SOUND_MAPPINGS[1]=targetS

            if goodS is None or goodS.lower() == 'off':
                del EyeLinkCoreGraphicsIOHubPsychopy.SOUND_MAPPINGS[0]
            elif goodS.lower() == '':
                pass
            else:
                EyeLinkCoreGraphicsIOHubPsychopy.SOUND_MAPPINGS[0]=goodS

            if errorS is None or errorS.lower() == 'off':
                del EyeLinkCoreGraphicsIOHubPsychopy.SOUND_MAPPINGS[-1]
            elif errorS.lower() == '':
                pass
            else:
                EyeLinkCoreGraphicsIOHubPsychopy.SOUND_MAPPINGS[-1]=errorS

        self._eyetrackerinterface=eyetrackerInterface
        self._ioKeyboard=None
        self._ioMouse=None
        self._ioServer=None
        
        self.img_size=None
 
        self.imagebuffer = array.array('I')
        self.pal = None

        self.width=self.screenSize[0]
        self.height=self.screenSize[1]

        self.keys=[]
        self.pos = []
        self.state = 0
        
        if sys.byteorder == 'little':
            self.byteorder = 1
        else:
            self.byteorder = 0
 
        self.tracker.setOfflineMode();           

#        ioHub.print2err("Completed EyeLinkCoreGraphicsIOHubPsychopy Init...")

        self.window = visual.Window(self.screenSize, monitor="calibrationMonitor", units='pix', fullscr=True, allowGUI=False, screen=ioDevices.Display.getStimulusScreenIndex())
        self.window.setColor(self.WINDOW_BACKGROUND_COLOR,'rgb255')        
        self.window.flip(clearBuffer=True)
        self.window.flip(clearBuffer=True)
        
        self._createStim()
        
#        ioHub.print2err("Completed EyeLinkCoreGraphicsIOHubPsychopy _createStim...")

        self._registerEventMonitors()
        self._ioMouse.setSystemCursorVisibility(False)
        self._lastMsgPumpTime=currentSecTime()

        if Nsound is not None:
            #create sound files and player.
            skeys=self.SOUND_MAPPINGS.keys()
            for k in skeys:
                if isinstance(k,int) and self.SOUND_MAPPINGS[k] not in self.SOUND_MAPPINGS.keys():
                    sname=self.SOUND_MAPPINGS[k]
                    spath=os.path.join(ioHub.module_directory(currentSecTime),sname)
                    a=Nsound.AudioStream(spath)
                    self.SOUND_MAPPINGS[sname]=(a,Nsound.AudioPlayback(a.getSampleRate(), a.getNChannels(), 16))
        else:
            ioHub.print2err('Nsound module not present. Sound support during EyeLink calibration is disabled.')

        #        ioHub.print2err("Completed EyeLinkCoreGraphicsIOHubPsychopy create Sounds...")
        #self._printKeyMapping()
        
        self.clearAllEventBuffers()

    def clearAllEventBuffers(self):
        pylink.flushGetkeyQueue();
        self.tracker.resetData()
        self._ioServer.eventBuffer.clear()
        for d in self._ioServer.devices:
            d.clearEvents()
            
    def _registerEventMonitors(self):
        import ioHub
#        ioHub.print2err('_registerEventMonitors')
        import ioHub.server
        for evl in self._eyetrackerinterface._getEventListeners():
            #ioHub.print2err("evl: ",evl.__class__.__name__)
            if evl.__class__.__name__ == 'ioServer':
                self._ioServer=evl
                if 'Keyboard' in evl.deviceDict:
                    self._ioKeyboard=evl.deviceDict['Keyboard']
                    self._ioKeyboard._addEventListener(self)                   
                else:
                    ioHub.print2err("Warning: elCG could not connect to Keyboard device for events.")
                if 'Mouse' in evl.deviceDict:
                    self._ioMouse=evl.deviceDict['Mouse']
                    self._ioMouse._addEventListener(self)                   
                else:
                    ioHub.print2err("Warning: elCG could not connect to Mouse device for events.")
                break
    
    def _unregisterEventMonitors(self):
#        ioHub.print2err('_unregisterEventMonitors')
        if self._ioKeyboard:
            self._ioKeyboard._removeEventListener(self)
        if self._ioMouse:
            self._ioMouse._removeEventListener(self)
     
    def _handleEvent(self,ioe):
        #ioHub.print2err("Got Event: ",ioe)
        if ioe[EventConstants.EVENT_TYPE_ID_INDEX] == EventConstants.KEYBOARD_PRESS_EVENT:
            #ioHub.print2err('Should handle keyboard event for: ', ioe[-4], ' key_id: ',ioe[-5],' key_mods: ',ioe[-2]) #key pressed
#            ioHub.print2err('** KEY: ', ioe[-4]," ,key_id: ",ioe[-5]," ,ascii_code: ",ioe[-6]," ,scan_code: ",ioe[-7])               
            self.translate_key_message((ioe[-5],ioe[-2]))
                
        elif ioe[EventConstants.EVENT_TYPE_ID_INDEX] == EventConstants.MOUSE_PRESS_EVENT:
#            ioHub.print2err('Should handle mouse pressed event for button id: ', ioe[-7])
            self.state=1
        elif ioe[EventConstants.EVENT_TYPE_ID_INDEX] == EventConstants.MOUSE_RELEASE_EVENT:
#            ioHub.print2err('Should handle mouse release event for button id: ', ioe[-7])
            self.state=0
            
        elif ioe[EventConstants.EVENT_TYPE_ID_INDEX] == EventConstants.MOUSE_MOVE_EVENT:
            self.pos=self._ioMouse.getPosition()

#    def _printKeyMapping(self):
#        ioHub.print2err("===========================================")
#        for iokey, pylkey in self.IOHUB2PYLINK_KB_MAPPING.iteritems():
#            ioHub.print2err(iokey,' : ',pylkey)
#        ioHub.print2err("===========================================")
        
    def translate_key_message(self,event):
        key = 0
        mod = 0
        if len(event) >0 :
            if event[0] in self.IOHUB2PYLINK_KB_MAPPING:
                key=self.IOHUB2PYLINK_KB_MAPPING[event[0]]
            else:
                key = event[0]
            
            self.keys.append(pylink.KeyInput(key,mod))

        return key

    def get_input_key(self):
        #keep the psychopy window happy ;)
        if currentSecTime()-self._lastMsgPumpTime>self.IOHUB_HEARTBEAT_INTERVAL:                
            # try to keep ioHub, being blocked. ;(
            if self._ioServer:
                for dm in self._ioServer.deviceMonitors:
                    dm.device._poll()
                self._ioServer._processDeviceEventIteration()

            self._lastMsgPumpTime=currentSecTime()
                
        if len(self.keys) > 0:
            k= self.keys
            self.keys=[]
            #ioHub.print2err('KEY get_input_key: ',k)
            return k
        else:
            return None


    def _createStim(self):        

        class StimSet(object):
            def __setattr__(self, item, value):
                if item in self.__dict__: 
                    i=self.__dict__['_stimNameList'].find(item)
                    self.__dict__['_stimValueList'][i]=value
                else:
                    if '_stimNameList' not in self.__dict__:
                        self.__dict__['_stimNameList']=[]
                        self.__dict__['_stimValueList']=[]
                        self.__dict__['_stimNameList'].append(item)
                        self.__dict__['_stimValueList'].append(value)
                self.__dict__[item]=value
            
            def updateStim(self,name,**kwargs):
                astim=getattr(self,name)
                if isinstance(astim,OrderedDict):
                    for stimpart in astim.itervalues():
                        for argName,argValue in kwargs.iteritems():
                            a=getattr(stimpart,argName)
                            if callable(a):
                                a(argValue)
                            else:    
                                setattr(stimpart,argName,argValue)
                else:
                    for argName,argValue in kwargs.iteritems():
                        a=getattr(astim,argName)
                        if callable(a):
                            a(argValue)
                        else:    
                            setattr(astim,argName,argValue)

            def draw(self):
                for s in self._stimValueList:                    
                    if isinstance(s,OrderedDict):
                        for stimpart in s.itervalues():
                            stimpart.draw()
                    else:
                        s.draw()
                        
        self.calStim=StimSet()
                
        self.calStim.calibrationPoint=OrderedDict()
        self.calStim.calibrationPoint['OUTER'] = visual.Circle(self.window,pos=(0,0) ,lineWidth=0.0,radius=self.CALIBRATION_POINT_OUTER_RADIUS,name='CP_OUTER', units='pix',opacity=1.0, interpolate=False)
        self.calStim.calibrationPoint['INNER'] = visual.Circle(self.window,pos=(0,0),lineWidth=0.0, radius=self.CALIBRATION_POINT_INNER_RADIUS, name='CP_INNER',units='pix',opacity=1.0, interpolate=False)
        
        self.calStim.calibrationPoint['OUTER'].setFillColor(self.CALIBRATION_POINT_OUTER_COLOR,'rgb255')
        self.calStim.calibrationPoint['OUTER'].setLineColor(None,'rgb255')
        self.calStim.calibrationPoint['INNER'].setFillColor(self.CALIBRATION_POINT_INNER_COLOR,'rgb255')
        self.calStim.calibrationPoint['INNER'].setLineColor(None,'rgb255 ')

        self.imageStim=StimSet()
        self.imageStim.imageTitle = visual.TextStim(self.window, text = "EL CAL", pos=(0,0), units='pix', alignHoriz='center')        
        
    def setup_cal_display(self):
        #ioHub.print2err('setup_cal_display entered')
        self.window.flip(clearBuffer=True)
        #ioHub.print2err('setup_cal_display exiting')

    def exit_cal_display(self):
        #ioHub.print2err('exit_cal_display entered')
        self.window.flip(clearBuffer=True)
        #ioHub.print2err('exit_cal_display exiting')

    def record_abort_hide(self):
        pass

    def clear_cal_display(self):
        self.window.flip(clearBuffer=True)
        
    def erase_cal_target(self):
        self.window.flip(clearBuffer=True)
        
    def draw_cal_target(self, x, y):
        self.calStim.updateStim('calibrationPoint',setPos=(x,y))  
        self.calStim.draw()
        self.window.flip(clearBuffer=True)
        
    def play_beep(self, beepid):
        if (Nsound is not None) and (beepid in self.SOUND_MAPPINGS):
            sname=self.SOUND_MAPPINGS[beepid]
            audiobuffer,audioplayer=self.SOUND_MAPPINGS[sname]
            audiobuffer >> audioplayer
        elif Nsound is None:
            pass
        else:
            ioHub.print2err('play_beep ERROR: Unsupported beep id: %d.'%(beepid))
                    
    def exit_image_display(self):
        #ioHub.print2err('exit_image_display entered')
        self.window.flip(clearBuffer=True)
        #ioHub.print2err('exit_image_display exiting')

    def alert_printf(self,msg):
        ioHub.print2err('**************************************************')
        ioHub.print2err('EYELINK CG ERROR: %s'%(msg))
        ioHub.print2err('**************************************************')
        
    def image_title(self, text):
        #ioHub.print2err('image_title entered')
        self.imageStim.updateStim('imageTitle',setText=text)
        self.imageStim.draw()        
        self.window.flip(clearBuffer=True)
        #ioHub.print2err('image_title exiting')

############# From Pyglet Custom Graphics #####################################
#
## NOT YET CONVERTED
#
#
#
###############################################################################
#
#
#   pyglet impl.
    def get_mouse_state(self):
        ioHub.print2err('get_mouse_state entered')
        if len(self.pos) > 0 :
            l = (int)(self.width*0.5-self.width*0.5*0.75)
            r = (int)(self.width*0.5+self.width*0.5*0.75)
            b = (int)(self.height*0.5-self.height*0.5*0.75)
            t = (int)(self.height*0.5+self.height*0.5*0.75)

            mx, my = 0,0
            if self.pos[0]<l:
                mx = l
            elif self.pos[0] >r:
                mx = r
            else:
                mx = self.pos[0]

            if self.pos[1]<b:
                my = b
            elif self.pos[1]>t:
                my = t
            else:
                my = self.pos[1]

            mx = (int)((mx-l)*self.img_size[0]//(r-l))
            my = self.img_size[1] - (int)((my-b)*self.img_size[1]//(t-b))
            ioHub.print2err('get_mouse_state exiting')
            return ((mx, my),self.state)
        else:
            ioHub.print2err('get_mouse_state exiting')
            return((0,0), 0)

###############################################################################
#
#
#   PYGLET IMP.
    def setup_image_display(self, width, height):
        ioHub.print2err('setup_image_display entered')
        self.img_size = (width,height)
        self.window.clearBuffer()
        self.window.flip(clearBuffer=True)
        ioHub.print2err('setup_image_display exiting')
      
###############################################################################
#
#   PYGLET Imp.
    def draw_image_line(self, width, line, totlines,buff):
        ioHub.print2err('draw_image_line entered')
        i =0
        while i <width:
            if buff[i]>=len(self.pal):
                buff[i]=len(self.pal)-1
            self.imagebuffer.append(self.pal[buff[i]&0x000000FF])
            i = i+1
        if line == totlines:
            #asp = ((float)(self.size[1]))/((float)(self.size[0]))
            asp = 1
            r = (float)(self.width*0.5-self.width*0.5*0.75)
            l = (float)(self.width*0.5+self.width*0.5*0.75)
            t = (float)(self.height*0.5+self.height*0.5*asp*0.75)
            b = (float)(self.height*0.5-self.height*0.5*asp*0.75)

            self.window.clearBuffer()
            
            tx = (int)(self.width*0.5)
            ty = b - 30
            self.stim.drawStim('imageTitle',{'setPos':(tx,ty)})            

            self.draw_cross_hair()
#            glEnable(GL_TEXTURE_RECTANGLE_ARB)
#            glBindTexture(GL_TEXTURE_RECTANGLE_ARB, self.texid.value)
#            glTexParameteri(GL_TEXTURE_RECTANGLE_ARB, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
#            glTexParameteri(GL_TEXTURE_RECTANGLE_ARB, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
#            glTexEnvi( GL_TEXTURE_ENV,GL_TEXTURE_ENV_MODE, GL_REPLACE )
#            glTexImage2D( GL_TEXTURE_RECTANGLE_ARB, 0,GL_RGBA8, width, totlines, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.imagebuffer.tostring())
#
#            glBegin(GL_QUADS)
#            glTexCoord2i(0, 0)
#            glVertex2f(r,t)
#            glTexCoord2i(0, self.img_size[1])
#            glVertex2f(r, b)
#            glTexCoord2i(self.img_size[0],self.img_size[1])
#            glVertex2f(l, b)
#            glTexCoord2i(self.img_size[1],0)
#            glVertex2f(l, t)
#            glEnd()
#            glDisable(GL_TEXTURE_RECTANGLE_ARB)
            self.draw_cross_hair()

            self.window.flip(clearBuffer=True)
            
            self.imagebuffer = array.array('I')
        ioHub.print2err('draw_image_line exiting')


###############################################################################
#
#   Pyglet impl.
    def draw_line(self,x1,y1,x2,y2,colorindex):
        ioHub.print2err('draw_line entered')
        if colorindex   ==  pylink.CR_HAIR_COLOR:          color = (1.0,1.0,1.0,1.0)
        elif colorindex ==  pylink.PUPIL_HAIR_COLOR:       color = (1.0,1.0,1.0,1.0)
        elif colorindex ==  pylink.PUPIL_BOX_COLOR:        color = (0.0,1.0,0.0,1.0)
        elif colorindex ==  pylink.SEARCH_LIMIT_BOX_COLOR: color = (1.0,0.0,0.0,1.0)
        elif colorindex ==  pylink.MOUSE_CURSOR_COLOR:     color = (1.0,0.0,0.0,1.0)
        else: color =(0.0,0.0,0.0,0.0)

        #asp = ((float)(self.size[1]))/((float)(self.size[0]))
        asp = 1
        r = (float)(self.width*0.5-self.width*0.5*0.75)
        l = (float)(self.width*0.5+self.width*0.5*0.75)
        t = (float)(self.height*0.5+self.height*0.5*asp*0.75)
        b = (float)(self.height*0.5-self.height*0.5*asp*0.75)

        x11= float(float(x1)*(l-r)/float(self.img_size[0]) + r)
        x22= float(float(x2)*(l-r)/float(self.img_size[0]) + r)
        y11= float(float(y1)*(b-t)/float(self.img_size[1]) + t)
        y22= float(float(y2)*(b-t)/float(self.img_size[1]) + t)

#        glBegin(GL_LINES)
#        glColor4f(color[0],color[1],color[2],color[3] )
#        glVertex2f(x11,y11)
#        glVertex2f(x22,y22)
#        glEnd()
        ioHub.print2err('draw_line exiting')
        

###############################################################################
#
#   Pyglet Implementation
    def draw_lozenge(self,x,y,width,height,colorindex):
        ioHub.print2err('draw_lozenge entered')
        if colorindex   ==  pylink.CR_HAIR_COLOR:          color = (1.0,1.0,1.0,1.0)
        elif colorindex ==  pylink.PUPIL_HAIR_COLOR:       color = (1.0,1.0,1.0,1.0)
        elif colorindex ==  pylink.PUPIL_BOX_COLOR:        color = (0.0,1.0,0.0,1.0)
        elif colorindex ==  pylink.SEARCH_LIMIT_BOX_COLOR: color = (1.0,0.0,0.0,1.0)
        elif colorindex ==  pylink.MOUSE_CURSOR_COLOR:     color = (1.0,0.0,0.0,1.0)
        else: color =(0.0,0.0,0.0,0.0)

        width=int((float(width)/float(self.img_size[0]))*self.img_size[0])
        height=int((float(height)/float(self.img_size[1]))*self.img_size[1])

        #asp = ((float)(self.size[1]))/((float)(self.size[0]))
        asp = 1
        r = (float)(self.width*0.5-self.width*0.5*0.75)
        l = (float)(self.width*0.5+self.width*0.5*0.75)
        t = (float)(self.height*0.5+self.height*0.5*asp*0.75)
        b = (float)(self.height*0.5-self.height*0.5*asp*0.75)

        x11= float(float(x)*(l-r)/float(self.img_size[0]) + r)
        x22= float(float(x+width)*(l-r)/float(self.img_size[0]) + r)
        y11= float(float(y)*(b-t)/float(self.img_size[1]) + t)
        y22= float(float(y+height)*(b-t)/float(self.img_size[1]) + t)

        r=x11
        l=x22
        b=y11
        t=y22

        #glColor4f(color[0],color[1],color[2],color[3])

        xw = math.fabs(float(l-r))
        yw = math.fabs(float(b-t))
        sh = min(xw,yw)
        rad = float(sh*0.5)

        x = float(min(l,r)+rad)
        y = float(min(t,b)+rad)

        if xw==sh:
            st = 180
        else:
            st = 90
#        glBegin(GL_LINE_LOOP)
#        i=st
#        degInRad = (float)(float(i)*(3.14159/180.0))
#
#        for i in range (st, st+180):
#            degInRad = (float)(float(i)*(3.14159/180.0))
#            glVertex2f((float)(float(x)+math.cos(degInRad)*rad),float(y)+(float)(math.sin(degInRad)*rad))
#
#        if xw == sh:    #short horizontally
#            y = (float)(max(t,b)-rad)
#        else:  		  # short vertically
#            x = (float)(max(l,r)-rad)
#
#        i = st+180
#        for i in range (st+180, st+360):
#            degInRad = (float)(float(i)*(3.14159/180.0))
#            glVertex2f((float)(float(x)+math.cos(degInRad)*rad),float(y)+(float)(math.sin(degInRad)*rad))
#
#        glEnd()
        ioHub.print2err('draw_lozenge exiting')

###############################################################################
#
#   PYGLET Imp.
    def set_image_palette(self, r,g,b):
        ioHub.print2err('set_image_palette entered')
        self.imagebuffer = array.array('I')
        self.clear_cal_display()
        sz = len(r)
        i =0
        self.pal = []
        while i < sz:
            rf = int(r[i])
            gf = int(g[i])
            bf = int(b[i])
            if self.byteorder:
                self.pal.append(0xff<<24|(bf<<16)|(gf<<8)|(rf))
            else:
                self.pal.append((rf<<24)|(gf<<16)|(bf<<8)|0xff)
            i = i+1
        ioHub.print2err('set_image_palette exiting')
        
