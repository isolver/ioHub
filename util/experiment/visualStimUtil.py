# -*- coding: utf-8 -*-
"""
Created on Wed Nov 07 20:58:25 2012

@author: Sol

"""
from __future__ import division
import scipy, numpy
from ioHub.devices import Computer,Display
from psychopy import visual

_getTime=Computer.getTime
_flip=visual.Window.flip

pi     = scipy.pi
dot    = scipy.dot
sin    = scipy.sin
cos    = scipy.cos
ar     = scipy.array
rand   = scipy.rand
arange = scipy.arange
rad    = scipy.deg2rad

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



if __name__ == "__main__":
    testRotate2D()
