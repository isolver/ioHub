"""
et_graphics

Part of the pyEyeTracker library 
Copyright (C) 2012 Sol Simpson 
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version). 

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""
from et_constants import *

class pyEyeTrackerCalibrationDisplay(object):
    def __init__(self,eyetracker,w,h):
        self.eyetracker=eyetracker
        self.calibrationWidth=w
        self.calibrationHeight=h

    def setupCalDisplay (self):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def exitCalDisplay(self): 
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def recordAbortHide(self):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def clearCalDisplay(self):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def eraseCalTarget(self):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def drawCalTarget(self, x, y):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
        #    
        #    def playBeep(self,beepid):
        #        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
        #

    def translateKeyMessage(self,event):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
            #key = event.key;
            #if key == ET_JUNK_KEY:
            #	return 0
            #return key	
            #return 0

    def getInputKey(self):
        ky=[]
        for key in []:# key event handler that is being used pygame.event.get([KEYDOWN]):
            try:
                tkey = self.translateKeyMessage(key)
                ky.append((tkey,key.mod))
            except Exception, err:
                print err

        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
        #return ky

    def getMouseState(self):
        #pos = pygame.mouse.get_pos()
        #   state = pygame.mouse.get_pressed()
        #return (pos,state[0])	
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def exitImageDisplay(self):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
        
    def alertPrintf(self,msg): 
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED	

    def setupImageDisplay(self, width, height):
        self.imgSize = (width,height)
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED		

    def imageTitle(self, text): 
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED		

    def drawImageLine(self, width, line, totlines,buff):		
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED


    def drawLozenge(self,x,y,width,height,colorindex):
        if colorindex   ==  ET_EYE_IMAGE_COLOR.CR_HAIR_COLOR:   color = (255,255,255,255)
        elif colorindex ==  ET_EYE_IMAGE_COLOR.PUPIL_HAIR_COLOR:       color = (255,255,255,255)
        elif colorindex ==  ET_EYE_IMAGE_COLOR.PUPIL_BOX_COLOR:        color = (0,255,0,255)
        elif colorindex ==  ET_EYE_IMAGE_COLOR.SEARCH_LIMIT_BOX_COLOR: color = (255,0,0,255)
        elif colorindex ==  ET_EYE_IMAGE_COLOR.MOUSE_CURSOR_COLOR:     color = (255,0,0,255)
        else: color =(0,0,0,0)

        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def drawLine(self,x1,y1,x2,y2,colorindex):
        if x1<0: x1 =0
        if x2<0: x2 =0
        if y1<0: y1 =0
        if y2<0: y2 =0

        if colorindex   ==  ET_EYE_IMAGE_COLOR.CR_HAIR_COLOR:   color = (255,255,255,255)
        elif colorindex ==  ET_EYE_IMAGE_COLOR.PUPIL_HAIR_COLOR:       color = (255,255,255,255)
        elif colorindex ==  ET_EYE_IMAGE_COLOR.PUPIL_BOX_COLOR:        color = (0,255,0,255)
        elif colorindex ==  ET_EYE_IMAGE_COLOR.SEARCH_LIMIT_BOX_COLOR: color = (255,0,0,255)
        elif colorindex ==  ET_EYE_IMAGE_COLOR.MOUSE_CURSOR_COLOR:     color = (255,0,0,255)
        else: color =(0,0,0,0)

        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def setImagePalette(self, r, g, b): 
        self.imagebuffer = array.array('l')
        self.clearCalDisplay()
        sz = len(r)
        i =0
        self.pal = []
        while i < sz:
            rf = int(b[i])
            gf = int(g[i])
            bf = int(r[i])
            self.pal.append((rf<<16) | (gf<<8) | (bf))
            i = i+1

