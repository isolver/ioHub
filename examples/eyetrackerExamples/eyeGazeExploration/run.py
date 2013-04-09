# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 09:21:11 2013

@author: isolver
"""
from psychopy import visual
import ioHub
from ioHub.devices import Computer
from ioHub.constants import EventConstants
from ioHub.util.experiment import ioHubExperimentRuntime, FullScreenWindow, pumpLocalMessageQueue

class ExperimentRuntime(ioHubExperimentRuntime):
    def run(self,*args,**kwargs):
        """
        The run method contains your experiment logic. It is equal to what would be in your main psychopy experiment
        script.py file in a standard psychopy experiment setup. That is all there is too it really.
        """

        tracker=self.hub.devices.tracker
        display=self.hub.devices.display
        keyboard=self.hub.devices.kb
        mouse=self.hub.devices.mouse

        trial_count=self.getExperimentConfiguration()['trial_count']
        image_names=self.getExperimentConfiguration()['image_names']

        # eye trackers, like other devices, should be conected to when the
        # ioHub Server starts, so this next call is not needed, but should not
        # hurt anythnig either:
        tracker.setConnectionState(True)
        
        # Create a psychopy window, full screen resolution, full screen mode, pix units.
        window = FullScreenWindow(display)

        # Hide the 'system mouse cursor' so we can display a cool gaussian mask for a mouse cursor.
        mouse.setSystemCursorVisibility(False)

        image_cache=dict()
        for i in image_names:
            iname='./images/{0}'.format(i)
            image_cache[i]=visual.ImageStim(window, image=iname, name=iname) 
            image_cache[i].draw()
        image_count=len(image_cache)
        window.clearBuffer()
        
        self.experiment_running=True
        # run the eye tracker calibration routine before starting trials
        tracker.runSetupProcedure()
        
        for t in range(trial_count):
            if self.experiment_running is False:
                print 'User Terminated Experiment. Quiting....'
                break
            # draw an image for this trial
            image_cache[image_names[t%image_count]].draw() 

            # start recording eye data
            tracker.setRecordingState(True)
            
            # flip and clear all events up to flip time (approx.)
            flip_time=window.flip()
            self.hub.clearEvents('all')
            
            # send and Experiment Message Event to the DataStore
            self.hub.sendMessageEvent("SYNCTIME %s"%(image_names[t%image_count],),sec_time=flip_time)
            
            # loop intil trial end condition is met
            self.trial_running=True            
            while self.experiment_running and self.trial_running:
                for ke in tracker.getEvents(EventConstants.KEYBOARD_CHAR):
                    self.handleKeyboardEvent(ke)    
            # a key was pressed so the loop was exited. We are clearing the event buffers to avoid an event overflow ( currently known issue)
            self.hub.clearEvents('all')
            tracker.setRecordingState(False)


        # wait 250 msec before ending the experiment (makes it feel less abrupt after you press the key)
        self.hub.wait(0.250)

        tracker.setConnectionState(False)

        ### End of experiment logic

    def handleKeyboardEvent(self,kb_event):
        print 'Exp Got keyboard char event:', kb_event
        
        if kb_event.key in ['q','ESCAPE']:
            # end experiment now!
            self.trial_running=False
            self.experiment_running =False
        elif kb_event.key == 'SPACE':
            # goto next trial
            self.trial_running=False
        elif kb_event.key == 'p':
            self.tracker.sendCommand('print_status')
        
        return True
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

#
#        char_events=keyboard.getEvents(eventTypeID=EventConstants.KEYBOARD_CHAR)
#        if char_events:
#            for char in char_events:
#                if char.key in ['q','ESCAPE']:
#                    print 'Terminating test...'
#                    run=False
#                    result=peg.EgExit(byref(stEgControl))
#                    print 'EgExit: ',result
#                    break
#                elif char.key == 'v':
#                    print 'EgGetVersion REQUESTED .....'
#                    result=peg.EgGetVersion(byref(stEgControl))
#                    print 'EgGetVersion: ',result
#                elif char.key == 'p':
#                    print 'stEgControl STATE PRINTOUT REQUESTED  .....'
#                    for a in stEgControl.__slots__:
#                        v=getattr(stEgControl,a)
#                        print a,' = ', v
#                    print 'stEgControl STATE PRINTOUT DONE.'
#                elif char.key == 'r':
#                    print 'Toggle Data Recording REQUESTED .....'
#                    print 'current status: ',stEgControl.bTrackingActive
#                    stEgControl.bTrackingActive = not stEgControl.bTrackingActive
#                    result=peg.EgGetVersion(byref(stEgControl))
#                    print 'new recording status: ',stEgControl.bTrackingActive                    
#            io.clearEvents('all')        
#        
#        # check for new data
#        while stEgControl.iNPointsAvailable > 0:
#            result=peg.EgGetData(&stEgControl);
