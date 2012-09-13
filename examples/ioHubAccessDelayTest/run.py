"""
ioHub
.. file: ioHub/examples/ioHubAccessDelayTest/run.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>

------------------------------------------------------------------------------------------------------------------------

ioHubAccessDelayTest
++++++++++++++++++++

Overview:
---------

This script is implemnted by extending the ioHub.psychopyIOHubRuntime.SimpleIOHubRuntime class to a  class
called ExperimentRuntime. The ExperimentRuntime class provides a utility object to run a psychopy script and
also launches the ioHub server process so the script has access to the ioHub service and associated devices.

The program loads many configuration values for the experiment process by using the experiment_Config.yaml file that
is located in the same directory as this script. Configuration settings for the ioHub server process are defined in
the ioHub_configuration.yaml file.

The __main__ of this script file simply calls the start() function, which creates the ExperimentRuntime class instance,
calls the run() method for the instance which is what contains the actual 'program / experiment execution code' ,
and then when run() completes, closes the ioHubServer process and ends the local program.

Desciption:
-----------

The main purpose for the ioHubAccessDelayTest is to test the round trip time it takes to request and reveive events
from the I/O hub. Retrace intervals are also calculated and stored to monitor for skipped retraces.

A full screen Window is opened that shows some graphics, including a moving grating as well as a small gaussian
that is controlled by mouse events from the ioHub. At the top of the screen is an area that will display the last key
pressed on the keyboard.

The script runs for until 1000 getEvent() requests to the ioHub have returned with >= 1 event. A number near the
bottom of the screen displays the number of remaining successful getEvent calls before the experiment will end.
By default the script also sends an Experiment MessageEvent to the ioHub on each retrace. This message is stored
in the ioHub datafile, but is also sent back as an ioHub MessageEvent to the experiment. Therefore, the getEvent()
request counter shown on the screen will decrease even if you do not move your mouse or keyboard,
as the MessageEvents are retrieved from the ioHub Server.

At the end of the test, plots are displayed showing the getEvent() round trip delays in a histogram,
the retrace intervals as a fucntion of time, and the retrace intervals in a histogram. All times in the plots are
in msec.

To Run:
-------

1. Ensure you have followed the ioHub installation instructions at http://www.github.com/isolver/iohub
2. Edit the experiment_config.yaml file that is in the same directory as the run.py script you will be starting. See the
comments at the top of each config file regarding any paramemters that 'must' be changed for the program to run.
In this example, nothing 'must' be changed.
3. Open a command prompt to the directory containing this file.
4. Start the test program by running:
   python.exe run.py

Any issues or questions, please let me know.

Notes:
------

If you get high MAX delays, turn off cloud drive apps, especially Google Drive; that fixes it for me.

If you are getting dropped frames, try commenting out the text stim that changes based on the number of getEvents()
left to call. It seems that resetting text on a text stim is a 'very' expensive operation.

"""
from __builtin__ import len, isinstance, dict, float, sum, int, unicode
from exceptions import Exception
import time
import ioHub
from ioHub.psychopyIOHubRuntime import SimpleIOHubRuntime, core, visual
from numpy import zeros

class ExperimentRuntime(SimpleIOHubRuntime):
    def __init__(self,configFileDirectory, configFile):
        SimpleIOHubRuntime.__init__(self,configFileDirectory,configFile)
        self.initAttributes()

    def initAttributes(self):
        """

        """
        self.psychoStim = None
        self.totalEventRequestsForTest=None
        self.numEventRequests=0
        self.totalEventRequestsForTest=None
        self.psychoWindow=None

    def run(self,*args,**kwargs):
        """
        psychopy code is taken from an example psychopy script in the coder documentation.
        """
        self.totalEventRequestsForTest=1000

        #report process affinities
        print "Current process affinities (experiment proc, ioHub proc):", self.getProcessAffinities()


        print "ExperimentPCkeyboard methods:",self.hub.devices.kb.getRemoteMethodNames()
        print "ExperimentPCmouse methods:",self.hub.devices.mouse.getRemoteMethodNames()
        print "ExperimentRuntime methods:",self.hub.devices.experimentRuntime.getRemoteMethodNames()
        print "ParallelPort methods:",self.hub.devices.parallelPort.getRemoteMethodNames()

        self.hub.devices.mouse.setPosition((0.0,0.0))

        # create fullscreen pyglet window at current resolution, as well as required resources / drawings
        self.createPsychoGraphicsWindow()

        # create stats numpy arrays, set experiment process and ioHubServer to high priority.
        self.initTestResourcesAndState()

        #draw and flip to the updated graphics state.
        self.drawAndFlipPsychoWindow()

        # START TEST LOOP >>>>>>>>>>>>>>>>>>>>>>>>>>

        while self.numEventRequests < self.totalEventRequestsForTest:
            # try sending an Experiment Event
            self.hub.sendMessageEvent("This is a test message %.3f"%self.flipTime)


            #draw and flip to the updated graphics state.
            ifi=self.drawAndFlipPsychoWindow()

            events,callDuration=self.checkForEvents()

            if events:
                # events were available
                self.updateStats(events, callDuration, ifi)

        # END TEST LOOP <<<<<<<<<<<<<<<<<<<<<<<<<<

        # _close neccessary files / objects, 'disable high priority.
        print "plot spinDownTest"
        self.spinDownTest()

        # plot collected delay and retrace detection results.
        print "plot results"
        self.plotResults()

    def createPsychoGraphicsWindow(self):
        #create a window

        self.mouse=self.hub.devices.mouse
        self.kb=self.hub.devices.kb
        self.expRuntime=self.hub.devices.experimentRuntime
        self.pport=self.hub.devices.parallelPort
        self.display=self.hub.devices.display

        self.hub.devices.display.getScreenResolution()
        self.psychoWindow = visual.Window(self.display.getScreenResolution(),monitor="testMonitor", units=self.display.getDisplayCoordinateType(), fullscr=True, allowGUI=False)

        currentPosition=self.mouse.setPosition((0,0))

        print '###self.mouse.setVisibility:',  self.mouse.setSysCursorVisibility(False)

        self.instructionText2Pattern='%d'

        self.psychoStim=ioHub.LastUpdatedOrderedDict()
        self.psychoStim['grating'] = visual.PatchStim(self.psychoWindow, mask="circle", size=75,pos=[-100,0], sf=.075)
        self.psychoStim['fixation'] =visual.PatchStim(self.psychoWindow, size=25, pos=[0,0], sf=0,  color=[-1,-1,-1], colorSpace='rgb')
        self.psychoStim['title'] =visual.TextStim(win=self.psychoWindow, text="ioHub getEvents Delay Test", pos = [0,125], height=36, color=[1,.5,0], colorSpace='rgb',alignHoriz='center',wrapWidth=800.0)
        self.psychoStim['instructions'] =visual.TextStim(win=self.psychoWindow, text='Move the mouse around, press keyboard keys and mouse buttons', pos = [0,-125], height=32, color=[-1,-1,-1], colorSpace='rgb',alignHoriz='center',wrapWidth=800.0)
        self.psychoStim['instructions2'] =visual.TextStim(win=self.psychoWindow, text=self.instructionText2Pattern%(self.totalEventRequestsForTest,), pos = [0,-250],  color=[-1,-1,-1], height=32, colorSpace='rgb',alignHoriz='center',wrapWidth=800.0)
        self.psychoStim['keytext'] =visual.TextStim(win=self.psychoWindow, text='key', pos = [0,300], height=48, color=[-1,-1,-1], colorSpace='rgb',alignHoriz='left',wrapWidth=800.0)
        self.psychoStim['mouseDot'] =visual.GratingStim(win=self.psychoWindow,tex=None, mask="gauss", pos=currentPosition,size=(50,50),color='purple')

    def drawAndFlipPsychoWindow(self):
        self.psychoStim['grating'].setPhase(0.05, '+')#advance phase by 0.05 of a cycle
        currentPosition=self.mouse.getPosition()
        #print "Current Position:",currentPosition
        self.psychoStim['mouseDot'].setPos(currentPosition)
        [self.psychoStim[stimName].draw() for stimName in self.psychoStim]
        self.flipTime=self.psychoWindow.flip()
        d=self.flipTime-self.lastFlipTime
        self.lastFlipTime=self.flipTime
        return d

    def checkForEvents(self):
        # get the time we request events from the ioHub
        stime=self.currentTime()
        r = self.getEvents()
        if r and len(r) > 0:
            # so there were events returned in the request, so include this getEvent request in the tally
            etime=self.currentTime()
            dur=etime-stime
            return r, dur*1000.0
        return None,None


    def initTestResourcesAndState(self):
        if self.hub is None:
            print "Error: ioHub must be enabled to run the testEventRetrievalTiming test."
            return

        # Init Results numpy array
        self.results= zeros((self.totalEventRequestsForTest,3),dtype='f4')

        self.numEventRequests=0
        self.flipTime=0.0
        self.lastFlipTime=0.0

        # enable high priority mode for the experiment process and optionally the ioHub server process.
        self.enableHighPriority()

        # clear the ioHub event Buffer before starting the test.
        # This is VERY IMPORTANT, given an existing bug in ioHub.
        # You would want to do this before each trial started until the bug is fixed.
        self.clearEvents()

    def updateStats(self, events, duration, ifi):
        self.results[self.numEventRequests][0]=duration     # ctime it took to get events from ioHub
        self.results[self.numEventRequests][1]=len(events)  # number of events returned
        self.results[self.numEventRequests][2]=ifi*1000.0   # calculating inter flip interval.
        self.numEventRequests+=1                            # incrementing tally counter

        self.psychoStim['instructions2'].setText(self.instructionText2Pattern%(self.totalEventRequestsForTest-self.numEventRequests,))

        for r in events:
            if not isinstance(r,dict):
                r=self._eventListToDict(r)
            if r['event_type'] == ioHub.devices.EventConstants.EVENT_TYPES['KEYBOARD_PRESS']: #keypress code
                keystring=r['key']
                self.psychoStim['keytext'].setText(keystring)

    def spinDownTest(self):
        # OK, we have collected the number of requested getEvents, that have returned >0 events
        # so _close psychopy window
        self.psychoWindow.close()

        # disable high priority in both processes
        self.disableHighPriority()


    def plotResults(self):
        #### calculate stats on collected data and draw some plots ####
        import matplotlib.mlab as mlab
        from matplotlib.pyplot import axis, title, xlabel, hist, grid, show, ylabel, plot
        import pylab

        results= self.results

        durations=results[:,0]
        flips=results[1:,2]

        dmin=durations.min()
        dmax=durations.max()
        dmean=durations.mean()
        dstd=durations.std()

        fmean=flips.mean()
        fstd=flips.std()

        pylab.figure(figsize=[30,10])
        pylab.subplot(1,3,1)


        # the histogram of the delay data
        n, bins, patches = hist(durations, 50, normed=True, facecolor='blue', alpha=0.75)
        # add a 'best fit' line
        y = mlab.normpdf( bins, dmean, dstd)
        plot(bins, y, 'r--', linewidth=1)
        xlabel('ioHub getEvents Delay')
        ylabel('Percentage')
        title(
            r'$\mathrm{{Histogram\ of\ Delay:}}\ \min={0:.3f},\ \max={1:.3f},\ \mu={2:.3f},\ \sigma={3:.4f}$'.format(
                dmin, dmax, dmean, dstd))
        axis([0, dmax+1.0, 0, 25.0])
        grid(True)


        # graphs of the retrace data ( taken from retrace example in psychopy demos folder)
        intervalsMS = flips
        m=fmean
        sd=fstd
        distString= "Mean={0:.1f}ms,    s.d.={1:.1f},    99%CI={2:.1f}-{3:.1f}".format(m, sd, m - 3 * sd, m + 3 * sd)
        nTotal=len(intervalsMS)
        nDropped=sum(intervalsMS>(1.5*m))
        droppedString = "Dropped/Frames = {0:d}/{1:d} = {2:.3f}%".format(nDropped, nTotal, int(nDropped) / float(nTotal))

        pylab.subplot(1,3,2)

        #plot the frameintervals
        pylab.plot(intervalsMS, '-')
        pylab.ylabel('t (ms)')
        pylab.xlabel('frame N')
        pylab.title(droppedString)

        pylab.subplot(1,3,3)
        pylab.hist(intervalsMS, 50, normed=0, histtype='stepfilled')
        pylab.xlabel('t (ms)')
        pylab.ylabel('n frames')
        pylab.title(distString)

        show()


##################################################################
def main(configurationDirectory):
    import sys
    if len(sys.argv)>1:
        configFile=unicode(sys.argv[1])
        runtime=ExperimentRuntime(configurationDirectory, configFile)
    else:
        runtime=ExperimentRuntime(configurationDirectory, "experiment_config.yaml")

    runtime.start()

if __name__ == "__main__":
    configurationDirectory=ioHub.module_directory(main)
    main(configurationDirectory)

