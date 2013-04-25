"""
ioHub
.. file: ioHub/examples/simpleGamePad/run.py

------------------------------------------------------------------------------------------------------------------------

simpleGamePad- IMPLEMENTED WITH SUPPORT FOR XINPUT GAMEPADS ONLY, a.k.a XBOX 360, some LOGITECH
++++++++++++++

Desciption:
-----------

The main purpose for the simpleTest is to illustrate the use of xinput events
in PsychoPy when the joystick is an ioHub Device.

To Run:
-------

1. Ensure you have followed the ioHub installation instructions 
   in the ioHub HTML Documentation.
2. Open a command prompt to the directory containing this file.
3. Ensure you have a xinput compliment gamepad connected to the experiment
   computer and that it is turned on.
3. Start the test program by running:
   python.exe run.py

Any issues or questions, please let me know.
"""

from psychopy import  visual

import iohub
from iohub.client import  Computer
from iohub.constants import EventConstants
from iohub.util.experiment import ioHubExperimentRuntime,FullScreenWindow
from iohub import OrderedDict


class ExperimentRuntime(ioHubExperimentRuntime):
    """
    Create an experiment using psychopy and the ioHub framework by extending 
    the ioHubExperimentRuntime class. 
    """
    def run(self,*args,**kwargs):
        # PLEASE REMEMBER , THE SCREEN ORIGIN IS ALWAYS IN THE CENTER OF THE SCREEN,
        # REGARDLESS OF THE COORDINATE SPACE YOU ARE RUNNING IN. THIS MEANS 0,0 IS SCREEN CENTER,
        # -x_min, -y_min is the screen bottom left
        # +x_max, +y_max is the screen top right

        print "THIS DEMO REQUIRES A CONNECTED (WIRED OR WIRELESS) XBOX 360"
        print "GAMEPAD OR OTHER XINPUT COMPATIBLE DEVICE. DEVICE ALSO NEEDS TO "
        print " BE TURNED ON. ;) "

        print ""
        print "\tPRESS 'ESCAPE' KEY TO EXIT."
        print "\tPRESS 'b' KEY TO PRINT BATTERY INFO TO STDOUT."
        print "\tPRESS 'u' KEY TO PRINT CAPABILITIES INFO TO STDOUT."
        print "\tPRESS ANY OTHER KEY TO MAKE GAMEPAD *RUMBLE* FOR 1 SEC."


        # Let's make some short-cuts to the devices we will be using in this 'experiment'.
        mouse=self.devices.mouse
        display=self.devices.display
        kb=self.devices.kb
        gamepad=self.devices.gamepad


        # Read the current resolution of the monitors screen in pixels.
        # We will set our window size to match the current screen resolution and make it a full screen boarderless window.
        screen_resolution= display.getPixelResolution()


        # Create psychopy full screen window using the display device config.
        psychoWindow = FullScreenWindow(display)
        
        # Set the mouse position to 0,0, which means the 'center' of the screen.
        mouse.setPosition((0.0,0.0))

        # Read the current mouse position (should be 0,0)  ;)
        currentPosition=mouse.getPosition()

        # Hide the 'system mouse cursor' so we can display a cool gaussian mask for a mouse cursor.
        mouse.setSystemCursorVisibility(False)

        # Create an ordered dictionary of psychopy stimuli. An ordered dictionary is one that returns keys in the order
        # they are added, you you can use it to reference stim by a name or by 'zorder'
        psychoStim=OrderedDict()
        psychoStim['grating'] = visual.PatchStim(psychoWindow, mask="circle", size=75,pos=[-100,0], sf=.075)
        psychoStim['fixation'] =visual.PatchStim(psychoWindow, size=25, pos=[0,0], sf=0,  color=[-1,-1,-1], colorSpace='rgb')
        psychoStim['mouseDot'] =visual.GratingStim(psychoWindow,tex=None, mask="gauss", pos=currentPosition,size=(50,50),color='purple')
        psychoStim['text'] = visual.TextStim(psychoWindow, text='key', pos = [0,300], height=48, color=[-1,-1,-1], colorSpace='rgb',alignHoriz='center',wrapWidth=800.0)


        # Clear all events from the global event buffer, and from the keyboard event buffer.
        self.hub.clearEvents('all')

        QUIT_EXP=False
        # Loop until we get a keyboard event with the space, Enter (Return), or Escape key is pressed.
        while QUIT_EXP is False:

            # read gamepad events and take the last one if any exist
            gpevents=gamepad.getEvents()
            if len(gpevents)>0:
                gpevents=gpevents[-1]

                ## Display pressed buttons
                #
                psychoStim['text'].setText(str([k for k,v in gpevents.buttons.iteritems() if v is True]))
                #
                ###

                # Use 2 finger triggers for fixation square position (so it will be at bottom left hand corner of screen
                # when the triggers are not presses
                #
                fixationX=self.normalizedValue2Pixel(gpevents.leftTrigger,screen_resolution[0], 0)
                fixationY=self.normalizedValue2Pixel(gpevents.rightTrigger,screen_resolution[1], 0)
                psychoStim['fixation'].setPos((fixationX,fixationY))
                #
                #####

                # Use the Right Thumb Stick for the purple gaussian  spot position
                #

                x,y,mag=gpevents.rightThumbStick # sticks are 3 item lists (x,y,magnitude)
                currentPosition[0]=self.normalizedValue2Pixel(x*mag,screen_resolution[0], -1)
                currentPosition[1]=self.normalizedValue2Pixel(y*mag,screen_resolution[1], -1)
                psychoStim['mouseDot'].setPos(currentPosition)
                #
                ###

            # for each loop, update the grating phase
            psychoStim['grating'].setPhase(0.05, '+')#advance phase by 0.05 of a cycle

            # redraw stim
            [psychoStim[stimName].draw() for stimName in psychoStim]

            # flip the psychopy window buffers, so the stim changes you just made get displayed.
            psychoWindow.flip()
            # it is on this side of the call that you know the changes have been displayed, so you can
            # make a call to one of the built-in time methods and get the event time of the flip, as the built in
            # time methods represent both experiment process and ioHub server process time.
            # Most times in ioHub are represented as unsigned 64 bit integers when they are saved, so using usec
            # as a timescale is appropriate.
            flip_time=Computer.currentSec()

            # send a message to the iohub with the message text that a flip occurred and what the mouse position was.
            # since we know the ioHub server time the flip occurred on, we can set that directly in the event.
            self.hub.sendMessageEvent("Flip %s"%(str(currentPosition),), sec_time=flip_time)


            # for each new keyboard event, check if it matches one of the end example keys.
            for k in kb.getEvents():
                if k.key in ['ESCAPE',]:
                    print 'Quit key pressed: ',k.key
                    QUIT_EXP=True
                else:
                    if k.type == EventConstants.KEYBOARD_PRESS:
                        if k.key in['B','b']:
                            bat=gamepad.updateBatteryInformation()
                            print "Bat Update: ",bat
                            bat=gamepad.getLastReadBatteryInfo()
                            print "Bat Last Read: ",bat
                        elif k.key in['U','u']:
                            bat=gamepad.updateCapabilitiesInformation()
                            print "Cap Update: ",bat
                            bat=gamepad.getLastReadCapabilitiesInfo()
                            print "Cap Last Read: ",bat
                        else:
                            # rumble the pad , 50% low frequency motor,
                            # 25% high frequency motor, for 1 second.
                            r=gamepad.setRumble(50.0,25.0,1.0)

        # wait 250 msec before ending the experiment (makes it feel less
        # abrupt after you press the key)
        self.hub.wait(0.250)

        # for fun, test getting a bunch of events at once,
        # likely causing a mutlipacket getEvents()
        stime = Computer.currentSec()
        events=self.hub.getEvents()
        etime= Computer.currentSec()
        print 'event count: ', len(events),' delay (msec): ',(etime-stime)*1000.0

        # _close neccessary files / objects, 'disable high priority.
        psychoWindow.close()

        ### End of experiment logic

    def normalizedValue2Pixel(self,nv,screen_dim,minNormVal):
        if minNormVal==0:
            pv=nv*screen_dim-(screen_dim/2.0)
        else:
            pv=nv*(screen_dim/2.0)
        return int(pv)

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