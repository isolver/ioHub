"""
ioHub
.. file: ioHub/examples/ioHubEyeTrackerAccessTest/run.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

import os
from devices.eyeTrackerInterface import DATA_FILTER
import ioHub
from ioHub.psychopyIOHubRuntime import SimpleIOHubRuntime, core, visual
from numpy import zeros


class ExperimentRuntime(SimpleIOHubRuntime):
    def __init__(self,configFileDirectory, configFile):
        SimpleIOHubRuntime.__init__(self,configFileDirectory,configFile)
        self.initAttributes()

    def initAttributes(self):
        pass


    def run(self,*args,**kwargs):
        TEST_BLOCK_COUNT=2
        TEST_TRIAL_COUNT=3
        print '\n\n'
        print "Starting Experiment 1 Test"

        print "ExperimentPCkeyboard methods:",self.hub.devices.ExperimentPCkeyboard._methods
        print "ExperimentPCmouse methods:",self.hub.devices.ExperimentPCmouse._methods
        
        #create a window
        mywin = visual.Window([1024,768],monitor="testMonitor", units="deg",fullscr=True)
        
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
        print 'isConnected():',eyetracker.isConnected

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
                events=self.getEvents(asType='dict')
                etime=self.currentMsec()
                #for e in events:
                #    print '%s %s'%(ioHub.devices.EventConstants.EVENT_TYPES[e['event_type']],str(e['hub_time']))
                print 'Get All Events (msec):',etime-stime
                print 'Event Count:',len(events)
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

        # save ioHubFile to xlsx format
        print "Saving Sample Excel File ...."
        import ioHub.ioDataStore.util as dsUtil
        tstart=self.currentMsec()
        nrows=dsUtil.hubTableToExcel(os.getcwdu(),self.ioHubConfig['ioDataStore']['filename']+'.hdf5',tableName='MonocularEyeSample',experiment_id=0,session_id=0)
        tend=self.currentMsec()
        print "Saved %d rows to excel file in %.3f sec (%.3f msec / row)"%(nrows,(tend-tstart)/1000.0,(tend-tstart)/nrows)



###################################################################
def start(cfile=u'experiment_config.yaml'):
    configFile=cfile
    try:
        import os
        # create a simple ExperimentRuntime class instance, passing in the experiment_config.yaml data
        runtime=ExperimentRuntime(os.getcwd(), configFile)

        # run a test on event access delay
        runtime.run()

        # close ioHub, shut down ioHub process, clean-up.....
        runtime.close()

    except Exception:
        ExperimentRuntime.printExceptionDetails()


##################################################################
if __name__ == "__main__":
    import sys
    if len(sys.argv)>1:
        configFile=unicode(sys.argv[1])
        start(configFile)
    else:
        start()