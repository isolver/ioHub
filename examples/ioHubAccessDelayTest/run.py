from __future__ import division

"""
Tests the round trip time to request and reveive events from the I/O hub. 
The test is performed 'numEventRequests' times. Only responses with >= 1 event count
toward the tally.

See the experiment_config.yaml and ioHub_config.yaml files for changes you need to make 
for this program to run in your environement, as well as the ioHub github project README for
a list of dependencies and install instructions.

Only keyboard and mouse events are enabled for this test, so once you start the program and see
the example psychopy application, move the mouse around, press mouse button, press keyboard keys,
etc. This will generate events. After a minute or so, the default 1000 requests will be satisfied
and the test will exit, printing out some stat's.

If you get high MAX delays, turn off cloud drive apps, especially Google Drive; that fixes it for me.
"""

import psychopy
from psychopy import logging, core, visual
import os,gc,psutil
import simpleIOHubRuntime
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print "*** Using Python based YAML Parsing"
    from yaml import Loader, Dumper
    
HERE_DIR=os.path.dirname(os.path.abspath(__file__))

class ExperimentRuntime(simpleIOHubRuntime.SimpleIOHubRuntime):
    def __init__(self,configFile):
        simpleIOHubRuntime.SimpleIOHubRuntime.__init__(self,configFile)
        
    def run(self,*args,**kwargs):
        '''
        tests the round trip time to request and reveive events from the I/O hub. 
        The test is performed 'numEventRequests' times. Only responses with >= 1 event count
        toward the tally.
        
        Only keyboard and mouse events are enabled for this test, so once you start the program and see
        the example psychopy application, move the mouse around, press mouse button, press keyboard keys,
        etc. This will generate events. After a minute or so, the default 1000 requests will be satisfied
        and the test will exit, printing out some stat's.
        
        If you get high MAX delays, turn off cloud drive apps, especially Google Drive; that fixes it for me.
        
        psychopy code is taken from an example psychopy scipt in the coder documentation.
        '''
        numEventRequests=kwargs['numEventRequests']
        
        if self.hub is None:
            print "Error: ioHub must be enabled to run the testEventRetrievalTiming test."
            return
        
        import numpy as N

        results=N.zeros((numEventRequests,3),dtype='f4')

        #create a window
        mywin = visual.Window([1024,768],monitor="testMonitor", units="deg")#fullscr=True)

        #create some stimuli    
        grating = visual.PatchStim(win=mywin, mask="circle", size=3,pos=[-4,0], sf=3)
        fixation = visual.PatchStim(win=mywin, size=0.5, pos=[0,0], sf=0, rgb=-1)

        # enable high priority mode for the experiment process.
        self.enableHighPriority()
        
        # get some shortcuts to save some '.'s in the looping call (they add up you know)
        hub=self.hub
        getEvents=hub.getEvents
        
        #enable high priority in the ioHub Server process
        #hub.sendToHub(('RPC','enableHighPriority'))

        #draw the stimuli and flip the window
        grating.draw()
        fixation.draw()
        mywin.flip()
        # clear the ioHub event Buffer before starting the test.
        # This is VERY IMPORTANT, given an existing bug in ioHub.
        # You would want to do this before each trial started until the bug is fixed. 
        hub.sendToHub(('RPC','clearEventBuffer'))

        i=0
        lastFlipTime=0.0
        while i < numEventRequests:
            # >>> psychopy drawing
            grating.setPhase(0.05, '+')#advance phase by 0.05 of a cycle
            grating.draw()
            fixation.draw()
            mywin.flip()
            # <<<
            
            # get the time we reqquest events from the ioHub
            stime=self.currentTime()
            r = getEvents()
            #print 'r:',r
            # this should be cleaned up, but the way the messaging protocal returns the events, 
            # the actual events start are the below index.
            r=r[0][1]
            if r:
                # so there were events returned in the request, so include this getEvent request in the tally
                etime=self.currentTime()    
                dur=etime-stime
                results[i][0]=dur*1000.0                    # converting to msec
                results[i][1]=len(r)                        # number of events returned
                results[i][2]=(stime-lastFlipTime)*1000.0   # calculating inter flip interval.
                lastFlipTime=stime
                i+=1                                        # incrementing tally counter 
        # OK, we have collected the number of requested getEvents, that have returned >0 events
        # so close psychopy window
        mywin.close()
        
        # disable high priority in both processes
        #self.disableHighPriority()
        #hub.sendToHub(('RPC','disableHighPriority'))
        
        # calculate stats on collected data
        import scipy.stats as stats
        durations=results[:,0]
        flips=results[1:,2]
        
        min=durations.min()
        max=durations.max()
        mean=durations.mean()
        std=durations.std()
        median=N.median(durations)
        # print out stat's, no nice histograms yet. ;)
        print "type:\tmin\tmax\tmean\tstd\tmedian"
        print "GED:\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f"%(min,max,mean,std,median)
        min=flips.min()
        max=flips.max()
        mean=flips.mean()
        std=flips.std()
        median=N.median(flips)
        print "IFI:\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f"%(min,max,mean,std,median)
        

##################################################################        
if __name__ == "__main__":
    import sys
    configFile='experiment_config.yaml'
    if len(sys.argv)>1:
        configFile=sys.argv[1]
    try:
        # create a simple ExperimentRuntime class instance, passing in the experiment_config.yaml data
        runtime=ExperimentRuntime(configFile)
        
        # run a test on event access delay
        runtime.run(numEventRequests=1000)
        
        # terminate the ioServer
        runtime.hub.shutDownServer()
        
        # terminate psychopy
        core.quit()
        
    except Exception:
        ExperimentRuntime.printExceptionDetails()