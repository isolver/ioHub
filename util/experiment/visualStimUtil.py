# -*- coding: utf-8 -*-
"""
Created on Wed Nov 07 20:58:25 2012

@author: Sol

"""
from __future__ import division
import scipy, numpy
from ioHub.devices import Computer,Display

pi     = scipy.pi
dot    = scipy.dot
sin    = scipy.sin
cos    = scipy.cos
ar     = scipy.array
rand   = scipy.rand
arange = scipy.arange
rad    = scipy.deg2rad

#
##  Rotate a set of points
#

# FROM: http://gis.stackexchange.com/questions/23587/how-do-i-rotate-the-polygon-about-an-anchor-point-using-python-script
def Rotate2D(pts,cnt,ang=pi/4):
    '''pts = {} Rotates points(nx2) about center cnt(2) by angle ang(1) in radian'''
    return dot(pts-cnt,ar([[cos(ang),sin(ang)],[-sin(ang),cos(ang)]]))+cnt

def testRotate2D():
    import pylab
    plot   = pylab.plot
    show   = pylab.show
    axis   = pylab.axis
    grid   = pylab.grid
    title  = pylab.title

    #the code for test
    pts = ar([[0,0],[1,0],[1,1],[0.5,1.5],[0,1]])
    plot(*pts.T,lw=5,color='k')                     #points (poly) to be rotated
    for ang in arange(0,2*pi,pi/8):
        ots = Rotate2D(pts,ar([0.5,0.5]),ang)       #the results
        plot(*ots.T)
    axis('image')
    grid(True)
    title('Rotate2D about a point')
    show()

####################################################################################

#
## Generate a set of points in a NxM grid. Useful for creating calibration target positions,
## or grid spaced fixation point positions that can be used for validation / fixation accuracy.
#

def generatedPointGrid(pixel_width,pixel_height,width_scalar=1.0,
                                    height_scalar=1.0, horiz_points=5, vert_points=5):

    swidth=pixel_width*width_scalar
    sheight=pixel_height*height_scalar

    # center 0 on screen center
    x,y = numpy.meshgrid( numpy.linspace(-swidth/2.0,swidth/2.0,horiz_points),
                       numpy.linspace(-sheight/2.0,sheight/2.0,vert_points))
    points=numpy.column_stack((x.flatten(),y.flatten()))

    return points

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
        
        if display is None:
            display=Display()
        
        self.reportedRetraceInterval=display.getStimulusScreenReportedRetraceInterval()/1000.0
        print "Stim Screen retrace interval: ", self.reportedRetraceInterval
        
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


def testSinusoidalMotion():
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


if __name__ == "__main__":
    testRotate2D()
    testSinusoidalMotion()