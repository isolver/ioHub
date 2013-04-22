# -*- coding: utf-8 -*-
from __future__ import division
import datetime
import warnings
import scipy, numpy

import fix_encoding

###############################################################################
#
## Some commonly used math functions pulled from scipy as (I am told) they run
## faster than the std python equiv's.
#

pi     = scipy.pi
dot    = scipy.dot
sin    = scipy.sin
cos    = scipy.cos
ar     = scipy.array
rand   = scipy.rand
arange = scipy.arange
rad    = scipy.deg2rad

###############################################################################
#
## A RingBuffer ( circular buffer) implemented using a numpy array as the backend. You can use
## the sumary stats methods etc. that are built into the numpty array class
## with this class as well. i.e ::
##      a = NumPyRingBuffer(max_size=100)
##      for i in xrange(0,150):
##          a.append(i)
##      print a.mean()
##      print a.std()
#

class NumPyRingBuffer(object):
    def __init__(self, max_size, dtype=numpy.float32):
        self._npa=numpy.empty(max_size*2,dtype=dtype)
        self.max_size=max_size
        self._index=0
        
    def append(self, e):
        i=self._index
        self._npa[i%self.max_size]=e
        self._npa[(i%self.max_size)+self.max_size]=e
        self._index+=1

    def __setitem__(self, indexs,v):
        if isinstance(indexs,(list,tuple)):
            for i in indexs:
                if isinstance(i, (int,long)):
                    i=i+self._index
                    self._npa[i%self.max_size]=v
                    self._npa[(i%self.max_size)+self.max_size]=v
                elif isinstance(i,slice):
                    start=i.start+self._index
                    stop=i.stop+self._index            
                    self._npa[slice(start%self.max_size,stop%self.max_size,i.step)]=v
                    self._npa[slice((start%self.max_size)+self.max_size,(stop%self.max_size)+self.max_size,i.step)]=v
        elif isinstance(indexs, (int,long)):
            i=indexs+self._index
            self._npa[i%self.max_size]=v
            self._npa[(i%self.max_size)+self.max_size]=v
        elif isinstance(indexs,slice):
            start=indexs.start+self._index
            stop=indexs.stop+self._index            
            self._npa[slice(start%self.max_size,stop%self.max_size,indexs.step)]=v
            self._npa[slice((start%self.max_size)+self.max_size,(stop%self.max_size)+self.max_size,indexs.step)]=v
        else:
            raise TypeError()
    
    def __getattr__(self,a):
        if self._index<self.max_size:
            return getattr(self._npa[:self._index],a)
        return getattr(self._npa[self._index%self.max_size:(self._index%self.max_size)+self.max_size],a)
    
    def elements(self):
        return self._npa[self._index%self.max_size:(self._index%self.max_size)+self.max_size]

###############################################################################
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

###############################################################################
#
##  Rotate a set of points in 2D
#
## Rotate a set of n 2D points in the form [[x1,x1],[x2,x2],...[xn,xn]]
## around the 2D point origin (x0,y0), by ang radians.
## Returns the rotated point list.
#
# FROM: http://gis.stackexchange.com/questions/23587/how-do-i-rotate-the-polygon-about-an-anchor-point-using-python-script

def Rotate2D(pts,origin,ang=pi/4):
    '''pts = {} Rotates points(nx2) about center cnt(2) by angle ang(1) in radian'''
    return dot(pts-origin,ar([[cos(ang),sin(ang)],[-sin(ang),cos(ang)]]))+origin


###############################################################################
#
## A couple date / time related utility functions
#

getCurrentDateTime = datetime.datetime.now
getCurrentDateTimeString = lambda : getCurrentDateTime().strftime("%Y-%m-%d %H:%M")


###############################################################################
#
## Verify the validity of a given Python release number
#    

try:
    from verlib import suggest_normalized_version, NormalizedVersion

    def validate_version(version):
        rversion = suggest_normalized_version(version)
        if rversion is None:
            raise ValueError('Cannot work with "%s"' % version)
        if rversion != version:
            warnings.warn('"%s" is not a normalized version.\n'
                          'It has been transformed into "%s" '
                          'for interoperability.' % (version, rversion))
        return NormalizedVersion(rversion)

except:
    # just use the version provided if verlib is not installed.
    validate_version=lambda version: version

###############################################################################
#
## Import utils sub modules
#    

try:
    import experiment
except:
    pass


###############################################################################
#
## Test code
#    

if __name__ == '__main__':
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
