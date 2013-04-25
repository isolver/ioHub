# -*- coding: utf-8 -*-
"""
Created on Sat Nov 03 19:09:25 2012

@author: Sol
"""

from __future__ import division
from psychopy.visual import Window


from ...devices import Computer
from .. import pi,cos,sin,rad
#
## Windows Message Pumping
#

def pumpLocalMessageQueue():
    pass
 
if Computer.system == 'win32':
    global pumpLocalMessageQueue
    import pythoncom
    
    def pumpLocalMessageQueue():
        """
        Pumps the Experiment Process Windows Message Queue so the PsychoPy Window
        does not appear to be 'dead' to the OS. If you are not flipping regularly
        (say because you do not need to and do not want to block frequently,
        you can call this, which will not block waiting for messages, but only
        pump out what is in the que already. On an i7 desktop, this call method
        takes between 10 and 90 usec.
        """
        if pythoncom.PumpWaitingMessages() == 1:
            raise KeyboardInterrupt()   
#
## Create a FullScreenWindow based on an ioHub Displays settings
# 

class FullScreenWindow(Window):
    def __init__(self,iohub_display,res=None,color=[128,128,128], colorSpace='rgb255',
                 winType='pyglet',gamma=1.0,fullscr=True,allowGUI=False,
                 waitBlanking=True):
        if res == None:
            res=iohub_display.getPixelResolution()
        Window.__init__(self,res,monitor=iohub_display.getPsychopyMonitorName(),
                                    units=iohub_display.getCoordinateType(),
                                    color=color, colorSpace=colorSpace,
                                    fullscr=fullscr,
                                    allowGUI=allowGUI,
                                    screen=iohub_display.getIndex(),
                                    waitBlanking=waitBlanking,
                                    winType=winType, 
                                    gamma=gamma
                                    )
            
    def flip(self,clearBuffer=True):
        Window.flip(self,clearBuffer)
        return Computer.getTime()


####################################################################################
#
## MovementPatterns for Visual Stimuli
#

# sinusoidal movement pattern, based on code posted by
# Michael MacAskill @ psychopy-users:
# https://groups.google.com/forum/psychopy-users

# Changed:
#   - made code class based
#   - does not use current time for target position calc, but time of next
#    retrace start
#   -this tries to ensure a more consistent motion, regardless of when the
#    position update is applied to the stimulus during the retrace interval
  
class SinusoidalMotion(object):
    def __init__(self, 
                 amplitude_xy=(15.0,0.0), # max horizontal, vertical excursion
                 peak_velocity_xy=(10.0,10.0), # deg/s peak velocity x , y
                 phase_xy=(90.0,90.0),      # in degrees for x, y
                 display=None,              # ioHub display class
                 start_time=0.0,             # in seconds , 0.0 means use first flip time
                 ):       
        self.amplX , self.amplY = amplitude_xy 
        self.peakVelX, self.peakVelY = peak_velocity_xy
        self.phaseX, self.phaseY = rad(phase_xy[0]), rad(phase_xy[1])
        self.startTime=start_time        
        self.lastPositionTime = None
        self.nextFlipTimeEstimate=None

        self.reportedRetraceInterval=display.getRetraceInterval()
        print "Display retrace interval: ", self.reportedRetraceInterval
        
        # calculate the omega constants needed for the simple 
        # harmonic motion equations: 
        
        self.wX = 0.0         
        if self.amplX != 0.0: 
            self.freqX = self.peakVelX/(-2.0*self.amplX*pi)
            self.wX = 2.0*pi*self.freqX

        self.wY = 0.0 
        if self.amplY != 0: 
            self.freqY = self.peakVelY/(-2.0*self.amplY*pi)
            self.wY = 2.0*pi*self.freqY

    def getPos(self):
        t=0.0
        if self.lastPositionTime:

            nextFlipTimeEstimate=self.lastPositionTime+self.reportedRetraceInterval
            while nextFlipTimeEstimate < Computer.getTime():
                nextFlipTimeEstimate+=self.reportedRetraceInterval
            self.nextFlipTimeEstimate=nextFlipTimeEstimate

            t=nextFlipTimeEstimate-self.startTime

        self.pos=(self.amplX*cos(self.wX*t + self.phaseX),
                  self.amplY*sin(self.wY*t + self.phaseY))

        return self.pos

    def setLastFlipTime(self,t):
        if self.lastPositionTime is None:
            self.startTime=t
        self.lastPositionTime=t   

###############################################################################
#
## Import experiment sub modules
#    
        
from variableProvider import ExperimentVariableProvider

from psychopyIOHubRuntime import ioHubExperimentRuntime

from screenState import TimeTrigger,DeviceEventTrigger,ScreenState,ClearScreen,InstructionScreen,ImageScreen
from dialogs import ProgressBarDialog, MessageDialog, FileDialog, ioHubDialog

