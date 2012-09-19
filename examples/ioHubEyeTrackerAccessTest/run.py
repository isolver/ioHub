"""
ioHub
.. file: ioHub/examples/ioHubEyeTrackerAccessTest/run.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

import os
import ioHub
from ioHub.devices.eyeTrackerInterface import DATA_FILTER
from ioHub.psychopyIOHubRuntime import SimpleIOHubRuntime, core, visual


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

        keyboard=self.hub.devices.kb

        mouse=self.hub.devices.mouse
        eyetracker=self.hub.devices.tracker
        display=self.hub.devices.display

        print "kb methods:",keyboard.getRemoteMethodNames()
        print "mouse methods:",mouse.getRemoteMethodNames()
        print "display methods:",display.getRemoteMethodNames()
        print "tracker methods:",eyetracker.getRemoteMethodNames()

        #create a window
        pix_res=display.getScreenResolution()
        mywin = visual.Window(pix_res,monitor="testMonitor", units="pix",fullscr=True)
        
        DIVIDER="-----------------------"

        # 'drawToGazeOverlayScreen',
        # 'getDataFilteringLevel',
        #'getDigitalPortState', 'getEventHandler',
        #'runSetupProcedure',
        #'setDataFilteringLevel', 'setDigitalPortState', 'stopSetupProcedure'
        
        self.clearEvents()
        
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
            print 'blockStartDefaultLogic() %d:'%(b,),eyetracker.blockStartDefaultLogic()
            
            for t in xrange(1,TEST_TRIAL_COUNT+1):
                self.clearEvents()
                print DIVIDER
                print 'trialStartDefaultLogic() %d:'%((t*b)),eyetracker.trialStartDefaultLogic()
                
                print DIVIDER
                print 'isRecordingEnabled():',eyetracker.isRecordingEnabled()

                print DIVIDER
                print 'setRecordingState(True):',eyetracker.setRecordingState(True)

                d1=5003.0
                actualdelay=self.msecDelay(d1)
                print DIVIDER
                print "Requested Delay / Actual Delay / Diff (msec):",d1,actualdelay,actualdelay-d1
                print DIVIDER

                print "EARs:", eyetracker.getEventArrayLengths()

                print DIVIDER
                print "getLatestGazePosition():",eyetracker.getLatestGazePosition()
                print DIVIDER

                self.clearEvents()
                self.clearEvents(deviceLabel='mouse')
                self.clearEvents(deviceLabel='kb')

                d2=20.0
                actualdelay=self.msecDelay(d2)
                print DIVIDER
                print "Requested Delay / Actual Delay / Diff (msec):",d2,actualdelay,actualdelay-d2
                print DIVIDER

                stime=self.currentMsec()
                events=self.getEvents()
                etime=self.currentMsec()

                print 'Get All Events (msec):',etime-stime
                print 'events:',events
                if events:
                    print 'Event Count:',len(events)
                print DIVIDER

                stime=self.currentMsec()
                e=self.getEvents('kb')
                etime=self.currentMsec()
                print 'Get Keyboard Events (msec):',etime-stime
 
                print DIVIDER
                
                stime=self.currentMsec()
                e=self.getEvents('mouse')
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
        
        mywin._close()

        # save ioHubFile to xlsx format
        print "Saving Sample Excel File ...."
        import ioHub.ioDataStore.util as dsUtil
        tstart=self.currentMsec()
        nrows=dsUtil.hubTableToExcel(os.getcwdu(),self.ioHubConfig['ioDataStore']['filename']+'.hdf5',tableName='MonocularEyeSample',experiment_id=0,session_id=0)
        tend=self.currentMsec()
        print "Saved %d rows to excel file in %.3f sec (%.3f msec / row)"%(nrows,(tend-tstart)/1000.0,(tend-tstart)/nrows)



###################################################################
def main(configurationDirectory):
    """
    Creates an instance of the ExperimentRuntime class, checks for an experiment config file name parameter passed in via
    command line, and launches the experiment logic.
    """
    import sys
    if len(sys.argv)>1:
        configFile=unicode(sys.argv[1])
        runtime=ExperimentRuntime(configurationDirectory, configFile)
    else:
        runtime=ExperimentRuntime(configurationDirectory, "experiment_config.yaml")

    runtime.start()

if __name__ == "__main__":
    # This code only gets called when the python file is executed, not if it is loaded as a module by another python file
    #
    # The module_directory function determines what the current directory is of the function that is passed to it. It is
    # more reliable when running scripts via IDEs etc in terms of reporting the true file location.
    configurationDirectory=ioHub.module_directory(main)

    # run the main function, which starts the experiment runtime
    main(configurationDirectory)