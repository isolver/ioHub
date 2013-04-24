# -*- coding: utf-8 -*-
"""
ioHub
.. file: ioHub/examples/simple/run.py
"""
from psychopy import core,  visual, logging

import iohub
from iohub import OrderedDict
from iohub.devices import Computer
from iohub.constants import EventConstants
from iohub.util.experiment import ioHubExperimentRuntime,FullScreenWindow


class ExperimentRuntime(ioHubExperimentRuntime):
    """
    Create an experiment using psychopy and the ioHub framework by extending the 
    ioHubExperimentRuntime class. At minimum all that is needed in the __init__ 
    for the new class, here called ExperimentRuntime, is the a call to the
    ioHubExperimentRuntime __init__ itself.
    
    April, 2013 Updates:
        - Example now works as a Unicode char handling test. 
            > In the upper left of the display, the saved utf-8 code point for 
              the key pressed is displayed by converting the number to a 
              unicode char using the python unichr() function.
              NOTE: On the Mac, there are several 'non standard' code points defined and used
                as the utf-8 encoding for the key in question. For such keys, this field
                will be blank, as unichar() fails to convert the code point to utf-8 encoded 
                string. The upper right hand kext on the screen should show the correct
                value for the key (and modifiers) though.
            > The upper right displays the Unicode value for the key pressed. This is
               done by just passsnig the key event 'key' attribude, which  is a unicode string,
               to the psychopy text stim's setText.
            > The bottom middle of the screen displays the list of active modifiers. This 
              is the key.modifiers attribute, which is a list of modifier string labels used 
              by ioHub. Left and Right handed modifiers should be reported independently.
        - The Mouse cursor position is now updated on each frame with a random amount of noise
          if the 'ENABLE_NOISY_MOUSE' valiable defined at the start of the run() method is True. 
          This allows testing of udating mouse position and checking on how doing so
          effects the mouse position sample stream.
    """
    def run(self,*args,**kwargs):
        """
        """
        #Setup Logging        
        logging.LogFile('./lastRun.log',filemode='w',level=logging.NOTSET)
        logging.console.setLevel(logging.WARNING)
        # PLEASE REMEMBER , THE SCREEN ORIGIN IS ALWAYS IN THE CENTER OF THE SCREEN,
        # REGARDLESS OF THE COORDINATE SPACE YOU ARE RUNNING IN. THIS MEANS 0,0 IS SCREEN CENTER,
        # -x_min, -y_min is the screen bottom left
        # +x_max, +y_max is the screen top right
        
        
        # Let's make some short-cuts to the devices we will be using in this 'experiment'.
        mouse=self.devices.mouse
        display=self.devices.display
        kb=self.devices.kb
        experiment=self.devices.experimentRuntime
        #Computer.enableHighPriority()
        
        # Create a psychopy window, using settings from Display device config
        psychoWindow =  FullScreenWindow(display)#,res=(500,500),fullscr=False,allowGUI=True)

        # Hide the 'system mouse cursor' so we can display a cool gaussian mask for a mouse cursor.
        #mouse.setSystemCursorVisibility(False)
        # Set the mouse position to 0,0, which means the 'center' of the screen.
        mouse.setPosition((0.0,0.0))
        # Read the current mouse position (should be 0,0)  ;)
        currentPosition=mouse.getPosition()

        mouse.lockMouseToDisplayID(display.getIndex())
        # Create an ordered dictionary of psychopy stimuli. An ordered dictionary is one that returns keys in the order
        # they are added, you you can use it to reference stim by a name or by 'zorder'
        psychoStim=OrderedDict()
        
        coord_type=display.getCoordinateType()
        cl,ct,cr,cb=display.getCoordBounds()
        cw=cr-cl
        ch=ct-cb
        
        # ***** IMPORTANT: Must set coord type explicitly to match that of the
        # Display Device, as is done here....
        psychoStim['grating'] = visual.PatchStim(psychoWindow, units=coord_type, mask="circle", size=cw*.10,pos=[0,0], sf=0.25)
        psychoStim['keytext'] = visual.TextStim(psychoWindow,  units=coord_type, text=u'?', pos = [cw*0.25,ch*.25], height=ch*0.05, color=[-1,-1,-1], colorSpace='rgb',alignHoriz='center',alignVert='center',wrapWidth=cw*.9)
        psychoStim['ucodetext'] = visual.TextStim(psychoWindow, units=coord_type, text=u'?', pos = [-cw*0.25,ch*.25], height=ch*0.05, color=[-1,-1,-1], colorSpace='rgb',alignHoriz='center',alignVert='center',wrapWidth=cw*.9)
        psychoStim['mods'] = visual.TextStim(psychoWindow,  units=coord_type, text=u'?', pos = [0,-ch*.25], height=ch*0.05, color=[-1,-1,-1], colorSpace='rgb',alignHoriz='center',alignVert='center',wrapWidth=cw*.9)
        psychoStim['mouseDot'] =visual.GratingStim(psychoWindow, units=coord_type,tex=None, mask="gauss", pos=currentPosition,size=(cw*0.03,ch*.03),color='purple')

        
        # check for experiment events
        ex_events=experiment.getEvents()
        #for ee in ex_events:
        #    print "Got Experiment Event: ",ee
            
        # Clear all events from the global and device level event buffers.
        self.hub.clearEvents('all')
        
        QUIT_EXP=False
        # Loop until we get a keyboard event with the space, Enter (Return), or Escape key is pressed.
        while QUIT_EXP is False:
            
            # check for experiment events
            ex_events=experiment.getEvents()
            #for ee in ex_events:
            #    print "Got Experiment Event: ",ee
            
            # for each loop, update the grating phase
            psychoStim['grating'].setPhase(0.05, '+')#advance phase by 0.05 of a cycle

            # and update the mouse contingent gaussian based on the current mouse location
            mx,my=mouse.getPosition()
            
            psychoStim['mouseDot'].setPos((mx,my))

            
            #print 'mx, my:',mx,my,display.displayCoord2Pixel(mx,my,display_index)
            # redraw the stim
            [psychoStim[stimName].draw() for stimName in psychoStim]

            # flip the psychopy window buffers, so the stim changes you just made get displayed.
            psychoWindow.flip()
            # it is on this side of the call that you know the changes have been displayed, so you can
            # make a call to the ioHub time method and get the time of the flip, as the built in
            # time methods represent both experiment process and ioHub server process time.
            # Most times in ioHub are represented sec.msec format to match that of Psychopy.
            flip_time=Computer.currentSec()

            # send a message to the iohub with the message text that a flip occurred and what the mouse position was.
            # since we know the ioHub server time the flip occurred on, we can set that directly in the event.
            self.hub.sendMessageEvent("Flip %s"%(str(currentPosition),), sec_time=flip_time)

            # get any new keyboard char events from the keyboard device


            # for each new keyboard character event, check if it matches one of the end example keys.
            for k in kb.getEvents():
                if k.key.upper() in ['ESCAPE', ] and k.type==EventConstants.KEYBOARD_CHAR:
                    print 'Quit key pressed: ',k.key,' for ',k.duration,' sec.'
                    QUIT_EXP=True
                #print u'{0}: time: {1}\t\tord: {2}.\t\tKey: [{3}]\t\tMods: {4}'.format(k.time,EventConstants.getName(k.type),k.ucode,k.key,k.modifiers)
                psychoStim['keytext'].setText(k.key)
                psychoStim['ucodetext'].setText(unichr(k.ucode))
                psychoStim['mods'].setText(str(k.modifiers))
                

             #for e in mouse.getEvents():
            #    print 'Event: ',e
                
            self.hub.clearEvents('all')
        # wait 250 msec before ending the experiment (makes it feel less abrupt after you press the key)
        actualDelay=self.hub.wait(0.250)
        print "Delay requested %.6f, actual delay %.6f, Diff: %.6f"%(0.250,actualDelay,actualDelay-0.250)

        # for fun, test getting a bunch of events at once, likely causing a mutlipacket getEvents()
        stime = Computer.currentSec()
        events=self.hub.getEvents()
        etime=Computer.currentSec()
        
        if events is None:
            events=[]

        print 'event count: ', len(events),' delay (msec): ',(etime-stime)*1000.0

        # _close neccessary files / objects, 'disable high priority.
        psychoWindow.close()

        ### End of experiment logic

################################################################################
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
        
    configurationDirectory=iohub.module_directory(main)

    # run the main function, which starts the experiment runtime
    main(configurationDirectory)