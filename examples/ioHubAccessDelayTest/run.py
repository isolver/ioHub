"""
ioHub
.. file: ioHub/examples/ioHubAccessDelayTest/run.py

"""


from psychopy import visual
import ioHub
from ioHub.devices import Computer
from ioHub.constants import EventConstants
from ioHub.util.experiment import ioHubExperimentRuntime
from ioHub import OrderedDict
from numpy import zeros


class ExperimentRuntime(ioHubExperimentRuntime):
    def __init__(self,configFileDirectory, configFile):
        ioHubExperimentRuntime.__init__(self,configFileDirectory,configFile)
        self.initAttributes()

    def initAttributes(self):
        """

        """
        self.psychoStim = OrderedDict()
        self.totalEventRequestsForTest=1000
        self.numEventRequests=0
        self.psychoWindow=None
        self.lastFlipTime=0.0
        self.events=None

    def run(self,*args,**kwargs):
        """
        psychopy code is taken from an example psychopy script in the coder documentation.
        """

        #report process affinities
        print "Current process affinities (experiment proc, ioHub proc):", Computer.getProcessAffinities()

        # create 'shortcuts' to the devices of interest for this experiment
        self.mouse=self.hub.devices.mouse
        self.kb=self.hub.devices.kb
        self.expRuntime=self.hub.devices.experimentRuntime
        self.display=self.hub.devices.display


        # let's print out the public method names for each device type for fun.
        #print "ExperimentPCkeyboard methods:",self.kb.getDeviceInterface()
        #print "ExperimentPCmouse methods:",self.mouse.getDeviceInterface()
        #print "ExperimentRuntime methods:",self.expRuntime.getDeviceInterface()
        #print "Display methods:",self.display.getDeviceInterface()

        # create fullscreen pyglet window at current resolution, as well as required resources / drawings
        self.createPsychoGraphicsWindow()

        # create stats numpy arrays, set experiment process to high priority.
        self.initStats()

        # enable high priority mode for the experiment process
        Computer.enableHighPriority()

        #draw and flip to the updated graphics state.
        ifi=self.drawAndFlipPsychoWindow()

        # START TEST LOOP >>>>>>>>>>>>>>>>>>>>>>>>>>

        while self.numEventRequests < self.totalEventRequestsForTest:
            # send an Experiment Event to the ioHub server process
            self.hub.sendMessageEvent("This is a test message %.3f"%self.flipTime)

            # check for any new events from any of the devices, and return the events list and the time it took to
            # request the events and receive the reply
            self.events,callDuration=self.checkForEvents()
            if self.events:
                # events were available
                self.updateStats(self.events, callDuration, ifi)
                #draw and flip to the updated graphics state.

            ifi=self.drawAndFlipPsychoWindow()

        # END TEST LOOP <<<<<<<<<<<<<<<<<<<<<<<<<<

        # close necessary files / objects, disable high priority.
        self.spinDownTest()

        # plot collected delay and retrace detection results.
        self.plotResults()

    def createPsychoGraphicsWindow(self):
        #create a window
        self.psychoWindow = ioHub.util.experiment.FullScreenWindow(self.display)
        
        currentPosition=self.mouse.setPosition((0,0))
        self.mouse.setSystemCursorVisibility(False)

        self.instructionText2Pattern='%d'

        self.psychoStim['grating'] = visual.PatchStim(self.psychoWindow, mask="circle", size=75,pos=[-100,0], sf=.075)
        self.psychoStim['fixation'] = visual.PatchStim(self.psychoWindow, size=25, pos=[0,0], sf=0,  color=[-1,-1,-1], colorSpace='rgb')
        self.psychoStim['title'] = visual.TextStim(win=self.psychoWindow, text="ioHub getEvents Delay Test", pos = [0,125], height=36, color=[1,.5,0], colorSpace='rgb',alignHoriz='center',wrapWidth=800.0)
        self.psychoStim['instructions'] = visual.TextStim(win=self.psychoWindow, text='Move the mouse around, press keyboard keys and mouse buttons', pos = [0,-125], height=32, color=[-1,-1,-1], colorSpace='rgb',alignHoriz='center',wrapWidth=800.0)
        self.psychoStim['instructions2'] = visual.TextStim(win=self.psychoWindow, text=self.instructionText2Pattern%(self.totalEventRequestsForTest,), pos = [0,-250],  color=[-1,-1,-1], height=32, colorSpace='rgb',alignHoriz='center',wrapWidth=800.0)
        self.psychoStim['keytext'] = visual.TextStim(win=self.psychoWindow, text='key', pos = [0,300], height=48, color=[-1,-1,-1], colorSpace='rgb',alignHoriz='left',wrapWidth=800.0)
        self.psychoStim['mouseDot'] = visual.GratingStim(win=self.psychoWindow,tex=None, mask="gauss", pos=currentPosition,size=(50,50),color='purple')


    def drawAndFlipPsychoWindow(self):
        self.psychoStim['grating'].setPhase(0.05, '+')#advance phase by 0.05 of a cycle
        currentPosition,currentDisplayIndex=self.mouse.getPosition(return_display_index=True)
        
        if currentDisplayIndex == self.display.getIndex():       
            currentPosition=(float(currentPosition[0]),float(currentPosition[1]))
            self.psychoStim['mouseDot'].setPos(currentPosition)


        if self.events:
            self.psychoStim['instructions2'].setText(self.instructionText2Pattern%(self.totalEventRequestsForTest-self.numEventRequests,))

            for r in self.events:
                if r.type is EventConstants.KEYBOARD_PRESS: #keypress code
                    self.psychoStim['keytext'].setText(r.key.decode('utf-8'))

            self.events=None

        [self.psychoStim[skey].draw() for skey in self.psychoStim]

        self.flipTime=self.psychoWindow.flip()
        d=self.flipTime-self.lastFlipTime
        self.lastFlipTime=self.flipTime
        return d

    def checkForEvents(self):
        # get the time we request events from the ioHub
        stime=Computer.currentTime()
        r = self.hub.getEvents()
        if r and len(r) > 0:
            # so there were events returned in the request, so include this getEvent request in the tally
            etime=Computer.currentTime()
            dur=etime-stime
            return r, dur*1000.0
        return None,None


    def initStats(self):
        if self.hub is None:
            print "Error: ioHub must be enabled to run the testEventRetrievalTiming test."
            return

        # Init Results numpy array
        self.results= zeros((self.totalEventRequestsForTest,3),dtype='f4')

        self.numEventRequests=0
        self.flipTime=0.0
        self.lastFlipTime=0.0

        # clear the ioHub event Buffer before starting the test.
        # This is VERY IMPORTANT, given an existing bug in ioHub.
        # You would want to do this before each trial started until the bug is fixed.
        self.hub.clearEvents('all')

    def updateStats(self, events, duration, ifi):
        self.results[self.numEventRequests][0]=duration     # ctime it took to get events from ioHub
        self.results[self.numEventRequests][1]=len(events)  # number of events returned
        self.results[self.numEventRequests][2]=ifi*1000.0   # calculating inter flip interval.
        self.numEventRequests+=1                            # incrementing tally counterfgh


    def spinDownTest(self):
        # OK, we have collected the number of requested getEvents, that have returned >0 events
        # so _close psychopy window
        self.psychoWindow.close()

        # disable high priority in both processes
        Computer.disableHighPriority()


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
        title('$\mathrm{{Histogram\ of\ Delay:}}\ \min={0},\ \max={1},\ \mu={2},\ \sigma={3}$'.format(
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
        droppedString = "Dropped/Frames = {0:d}/{1:d} = {2}%".format(nDropped, nTotal, int(nDropped) / float(nTotal))

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
# The below code should never need to be changed, unless you want to get command
# line arguements or something. 

if __name__ == "__main__":
    def main(configurationDirectory):
        """
        Creates an instance of the ExperimentRuntime class, checks for an experiment config file name parameter passed in via
        command line, and launches the experiment logic.
        """
        import sys
        if len(sys.argv)>1:
            configFile=sys.argv[1]
            runtime=ExperimentRuntime(configurationDirectory, configFile)
        else:
            runtime=ExperimentRuntime(configurationDirectory, "experiment_config.yaml")
    
        runtime.start()
        
    configurationDirectory=ioHub.module_directory(main)

    # run the main function, which starts the experiment runtime
    main(configurationDirectory)