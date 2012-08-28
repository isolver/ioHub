from __future__ import division
import psychopy
from psychopy import logging, core, visual
import os,gc,psutil
from yaml import load, dump
from eyeTrackerConstants import *
import simpleIOHubRuntime

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print "*** Using Python based YAML Parsing"
    from yaml import Loader, Dumper
    
HERE_DIR=os.path.dirname(os.path.abspath(__file__))

class ExperimentRuntime(simpleIOHubRuntime.SimpleIOHubRuntime):
    def __init__(self, configFile):
        print 'configFile',configFile
        simpleIOHubRuntime.SimpleIOHubRuntime.__init__(self,configFile)
               
    def run(self,*args,**kwargs):
        TEST_BLOCK_COUNT=2
        TEST_TRIAL_COUNT=3
        print '\n\n'
        print "Starting Experiment 1 Test"

        print "ExperimentPCkeyboard:",self.hub.devices.ExperimentPCkeyboard._methods
        print "ExperimentPCmouse:",self.hub.devices.ExperimentPCmouse._methods
        
        #create a window
        mywin = visual.Window([1024,768],monitor="testMonitor", units="deg")#,fullscr=True)
        
        DIVIDER="-----------------------"
        """
         'drawToGazeOverlayScreen', 
         'getDataFilteringLevel', 
        'getDigitalPortState', 'getEventHandler', 
        'runSetupProcedure', 
        'setDataFilteringLevel', 'setDigitalPortState', 'stopSetupProcedure'
        
        """
        eyetracker = self.hub.devices.tracker
        
        self.hub.sendToHub(('RPC','clearEventBuffer'))
        
        print DIVIDER
        print 'isConnected():',eyetracker.isConnected()

        print DIVIDER
        print 'setConnectionState:',eyetracker.setConnectionState(True)
        
        print DIVIDER
        print 'isConnected() 2:',eyetracker.isConnected()

        print DIVIDER
        print 'trackerTime 1:',eyetracker.trackerTime()
        
        print DIVIDER
        # sets which button on the Host button box will accept fixations during calibration
        # this is EyeLink specific; comment out and add a test for your implementation.
        # TO DO: we can test that many of the eye tracker setting defined in the settings
        #        file work via the sendCommand method as standard 'eye tracker independent'
        #        command tokens.
        #
        print 'sendCommand:',eyetracker.sendCommand("button_function"," 5 'accept_target_fixation'")
        
        print DIVIDER
        print 'setDataFilterLevel:',eyetracker.setDataFilterLevel(DATA_FILTER.LEVEL_2)
        print DIVIDER
        print 'getDataFilterLevel:',eyetracker.getDataFilterLevel()
        print DIVIDER
        print 'setDataFilterLevel:',eyetracker.setDataFilterLevel(DATA_FILTER.OFF)
        print DIVIDER
        print 'getDataFilterLevel:',eyetracker.getDataFilterLevel()
        
        print DIVIDER
        #
        # experimentStartDefaultLogic also runs:
        #   - createRecordingFile
        #
        print 'experimentStartDefaultLogic("test.edf"):',eyetracker.experimentStartDefaultLogic('test.edf')
        
        for b in xrange(1,TEST_BLOCK_COUNT+1):
            print DIVIDER
            print 'blockStartDefaultLogic() %d:'%(b),eyetracker.blockStartDefaultLogic()
            
            for t in xrange(1,TEST_TRIAL_COUNT+1):
                print DIVIDER
                print 'trialStartDefaultLogic() %d:'%((t*b)),eyetracker.trialStartDefaultLogic()
                
                print DIVIDER
                print 'isRecordingEnabled():',eyetracker.isRecordingEnabled()

                print DIVIDER
                self.clearEvents()
                print 'setRecordingState(True):',eyetracker.setRecordingState(True)

                actualdelay=self.msecDelay(5003)
                print DIVIDER
                print "Requested Delay / Actual Delay / Diff (msec):",5003.0,actualdelay,actualdelay-5003.0
                print DIVIDER
                
                stime=self.currentMsec()
                e=self.getEvents('ExperimentPCkeyboard')
                etime=self.currentMsec()
                print 'Get Keyboard Events (msec):',etime-stime
 
                print DIVIDER
                
                stime=self.currentMsec()
                e=self.getEvents('ExperimentPCmouse')
                etime=self.currentMsec()
                print 'Get Mouse Events (msec):',etime-stime
                
                print DIVIDER
                print 'isRecordingEnabled():',eyetracker.isRecordingEnabled()
                
                print DIVIDER
                print 'sendMessage("msg"):',eyetracker.sendMessage("This is a message for trial %d"%((t*b)))
                print DIVIDER
                print 'sendMessage("msg",message_offset=-10):',eyetracker.sendMessage("This is a message for trial %d with offset %d"%((t*b),-10))

                print DIVIDER
                print 'setRecordingState(False):',eyetracker.setRecordingState(False)
                
                print DIVIDER
                print 'isRecordingEnabled():',eyetracker.isRecordingEnabled()

                print DIVIDER
                print 'trialEndDefaultLogic() %d:'%((t*b)),eyetracker.trialEndDefaultLogic()
            
            print DIVIDER
            print 'blockEndDefaultLogic() %d:'%(b),eyetracker.blockEndDefaultLogic()
        
        print DIVIDER
        print 'trackerTime 2:',eyetracker.trackerTime()
        
        print DIVIDER
        print 'isConnected() 3:',eyetracker.isConnected()

        print DIVIDER
        print 'setConnectionState:',eyetracker.setConnectionState(False)

        print DIVIDER
        #
        # experimentEndDefaultLogic also runs:
        #     - closeRecordingFile
        #     - getFile
        #        
        print 'experimentEndDefaultLogic():',eyetracker.experimentEndDefaultLogic()
  
        print DIVIDER
        print 'isConnected() 4:',eyetracker.isConnected()        
        print '\n\n'
        
        mywin.close()

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
        runtime.run()
        
        # terminate the ioServer
        runtime.hub.shutDownServer()
        
        # terminate psychopy
        core.quit()
        
    except Exception:
        ExperimentRuntime.printExceptionDetails()
###################################################################
 