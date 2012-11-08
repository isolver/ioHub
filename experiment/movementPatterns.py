# -*- coding: utf-8 -*-
"""
Created on Wed Nov 07 20:58:25 2012

@author: Sol
"""

import math
from ioHub.devices import Computer,Display

# sinusoidal movement pattern, based on code posted by
# Michael MacAskill @ psychopy-users:
# https://groups.google.com/forum/?hl=en&fromgroups=#!searchin/psychopy-users/smooth$20pursuit/psychopy-users/zCUjgYkfrVE/IIKROxhjCQsJ

# Changed:
#   -class based
#   -does not use current time to target position calc, but time of next
#    retrace start
#   -this tries to ensure a more consistent motiton, regardless of when the
#    position update is appied to the stim during the retrace interval
  
class SinusoidalMotion(object):
    PI = math.pi
    def __init__(self, 
                 amplitude_xy=(15.0,0.0), # max horizontal, vertical excursion
                 peak_velocity_xy=(10.0,10.0), # deg/s peak velocity x , y
                 phase_xy=(90.0,90.0),      # in degrees for x, y
                 display=None,              # ioHub display class
                 start_time=0.0,             # in seconds , 0.0 means use first flip time
                 ):       
        self.amplX , self.amplY = amplitude_xy 
        self.peakVelX, self.peakVelY = peak_velocity_xy
        self.phaseX, self.phaseY = math.radians(phase_xy[0]), math.radians(phase_xy[1]) 
        self.startTime=start_time        
        self.lastPositionTime = None
        self.nextFlipTimeEstimate=None
        
        if display is None:
            display=Display()
        
        self.reportedRetraceInterval=display.getStimulusScreenReportedRetraceInterval()/1000.0
        print "Stim Screen retrace interval: ", self.reportedRetraceInterval
        
        # calculate the omega constants needed for the simple 
        # harmonic motion equations: 
        
        self.wX = 0.0         
        if self.amplX != 0.0: 
            self.freqX = self.peakVelX/(-2.0*self.amplX*self.PI) 
            self.wX = 2.0*self.PI*self.freqX 

        self.wY = 0.0 
        if self.amplY != 0: 
            self.freqY = self.peakVelY/(-2.0*self.amplY*self.PI) 
            self.wY = 2.0*self.PI*self.freqY 

    def getPos(self):
        t=0.0
        if self.lastPositionTime:

            nextFlipTimeEstimate=self.lastPositionTime+self.reportedRetraceInterval
            while nextFlipTimeEstimate < Computer.getTime():
                nextFlipTimeEstimate+=self.reportedRetraceInterval
            self.nextFlipTimeEstimate=nextFlipTimeEstimate

            t=nextFlipTimeEstimate-self.startTime

        self.pos=(self.amplX*math.cos(self.wX*t + self.phaseX), 
                  self.amplY*math.sin(self.wY*t + self.phaseY))

        return self.pos

    def setLastFlipTime(self,t):
        if self.lastPositionTime is None:
            self.startTime=t
        self.lastPositionTime=t        


if __name__ == "__main__":
    from psychopy import core, visual
    from ioHub.client import ioHubConnection
    io=ioHubConnection()
    
    d=Display()
    d.setStimulusScreenIndex(0)
    
    win=win=visual.Window([800,600],units="deg",monitor=d.getPsychoPyMonitorSettingsName())

    smotion=SinusoidalMotion(display=d)

    SPstim = visual.PatchStim(win=win, tex = None, 
                                pos=[0,0], 
                                size=2.00, 
                                mask='circle', 
                                color='red', 
                                colorSpace='rgb',
                                units="deg"
                             ) 

    currentTime=Computer.currentTime                         
    startTime=currentTime()
    while (currentTime()-startTime) < 20.0: 
        # the amplitudes below need to be in degrees for PsychoPy but the phases need to be in radians for the trig functions: 
        p=smotion.getPos()
        #print 'pos: ',p, ' : ', smotion.lastPositionTime, smotion.nextFlipTimeEstimate
        SPstim.setPos(p) 
        SPstim.draw() 
        win.flip()
        smotion.setLastFlipTime(currentTime())