"""
Example of using XInput gamepad support from ioHub in PsychoPy Exp.
"""

from psychopy import visual
from ioHub.util.experiment import ioHubExperimentRuntime

class ExperimentRuntime(ioHubExperimentRuntime):
    """
    Create an experiment using psychopy and the ioHub framework by extending the ioHubExperimentRuntime class. At minimum
    all that is needed in the __init__ for the new class, here called ExperimentRuntime, is the a call to the
    ioHubExperimentRuntime __init__ itself.
    """
    def __init__(self,configFileDirectory, configFile):
        ioHubExperimentRuntime.__init__(self,configFileDirectory,configFile)

    def run(self,*args,**kwargs):
        """
        The run method contains your experiment logic. It is equal to what would
        be in your main psychopy experiment script.py file in a standard psychopy
        experiment setup. That is all there is too it really.
        """

        # PLEASE REMEMBER , THE SCREEN ORIGIN IS ALWAYS IN THE CENTER OF THE SCREEN,
        # REGARDLESS OF THE COORDINATE SPACE YOU ARE RUNNING IN. THIS MEANS 0,0 IS SCREEN CENTER,
        # -x_min, -y_min is the screen bottom left
        # +x_max, +y_max is the screen top right
        #
        # RIGHT NOW, ONLY PIXEL COORD SPACE IS SUPPORTED. THIS WILL BE FIXED.
        
        #create a window to draw in
        mouse=self.devices.mouse
        display=self.devices.display
        keyboard=self.devices.keyboard
        gamepad=self.devices.gamepad
        computer=self.devices.computer

        # Read the current resolution of the displays screen in pixels.
        # We will set our window size to match the current screen resolution 
        # and make it a full screen boarderless window.
        screen_resolution= display.getStimulusScreenResolution()
        screen_index=display.getStimulusScreenIndex()

        # Create a psychopy window, full screen resolution, full screen mode, 
        # pix units, with no boarder.
        myWin = visual.Window(screen_resolution, 
                              units=display.getDisplayCoordinateType(), 
                              fullscr=True, 
                              allowGUI=False,
                              screen=screen_index)
            
        # Hide the 'system mouse cursor'
        mouse.setSystemCursorVisibility(False)

        gamepad.updateBatteryInformation()
        bat=gamepad.getLastReadBatteryInfo()
        print "Battery Info: ",bat

        gamepad.updateCapabilitiesInformation()
        caps=gamepad.getLastReadCapabilitiesInfo()
        print "Capabilities: ",caps
    
        fixSpot = visual.PatchStim(myWin,tex="none", mask="gauss",pos=(0,0), 
                                   size=(30,30),color='black')
        grating = visual.PatchStim(myWin,pos=(0,0),
                            tex="sin",mask="gauss",
                            color='white',
                            size=(200,200), sf=(2,0))
        message = visual.TextStim(myWin,pos=(0,-300),text='Hit "r" key to Rumble; Hit "q" to quit')
    
        END_DEMO=False
        
        while not END_DEMO:
            

            #update stim from joystick
            x,y,mag=gamepad.getThumbSticks()['RightStick'] # sticks are 3 item lists (x,y,magnitude)
            xx=self.normalizedValue2Pixel(x*mag,screen_resolution[0], -1)
            yy=self.normalizedValue2Pixel(y*mag,screen_resolution[1], -1)
            grating.setPos((xx, yy))
            
            x,y,mag=gamepad.getThumbSticks()['LeftStick'] # sticks are 3 item lists (x,y,magnitude)
            xx=self.normalizedValue2Pixel(x*mag,screen_resolution[0], -1)
            yy=self.normalizedValue2Pixel(y*mag,screen_resolution[1], -1)
            fixSpot.setPos((xx, yy))

            # change sf
            sf=gamepad.getTriggers()['LeftTrigger']
            grating.setSF(sf*4.0) #so should be in the range 0:4

            #change ori
            ori=gamepad.getTriggers()['RightTrigger']
            grating.setOri(ori*90.0) 

            #if any button is pressed then make the stimulus coloured
            if gamepad.getPressedButtonList():
                grating.setColor('red')
            else:
                grating.setColor('white')
                    
            #drift the grating
            t=computer.getTime()
            grating.setPhase(t*2)
            grating.draw()
            
            fixSpot.draw()
            message.draw()
            myWin.flip()#redraw the buffer

            #print joy.getAllAxes()#to see what your axes are doing!
            
            for event in keyboard.getEvents():
                if event.key in ['q',]:                
                    END_DEMO=True
                elif event.key in ['r',]:
                    # rumble the pad , 50% low frequency motor,
                    # 25% high frequency motor, for 1 second.
                    r=gamepad.setRumble(50.0,25.0,1.0)                    
                
            self.hub.clearEvents()#do this each frame to avoid getting clogged with mouse events

    def normalizedValue2Pixel(self,nv,screen_dim,minNormVal):
        if minNormVal==0:
            pv=nv*screen_dim-(screen_dim/2.0)
        else:
            pv=nv*(screen_dim/2.0)
        return int(pv)

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

if __name__ == "__main__":
    # This code only gets called when the python file is executed, not if it is loaded as a module by another python file
    #
    # The module_directory function determines what the current directory is of the function that is passed to it. It is
    # more reliable when running scripts via IDEs etc in terms of reporting the true file location.
    import ioHub
    configurationDirectory=ioHub.module_directory(main)

    # run the main function, which starts the experiment runtime
    main(configurationDirectory)

