======================================
QuickStart Guide for PsychoPy Coders
======================================

.. note::

    This QuickStart Guide is intended to give a fast introduction to how use the 
    ioHub and PsychoPy packages together by going through the process of 'porting'
    two PsychoPy demo's to use ioHub for device event reporting. 
    
    Not all the functionality of the ioHub  is covered, nor are all device types.
    For a more complete review of the ioHub package features and how to use them,
    see the ioHub User Manual section.
    
    Obviously the PsychoPy package API is used heavily, so it is important
    that you have an understanding of how to use PsychoPy at a *coder* level.
    Please refer to the very good `documentation for PsychoPy <http://www.psychopy.org/>`_ 
    if / when needed.
        
Overview
==========

In this section we will introduce ioHub by converting the PsychoPy demo 'mouse.py'
to use the ioHub Event Monitoring Framework using a 'srcipt only' approach to
working with ioHub. We will then convert a second PsychoPy demo, 'joystick_universal.py',
but this time use the scipt + configuration file approach to using ioHub. 

Each approach has some strengths and weaknesses, however in general if the experiment
is using more complex device types, like an eye tracker or an analog to digital
converter, then the latter approach of using two configuration files to define 
experiment and session metadata and the specifics of how the devices being
used should be configured, plus  a python source file that contains your experiment logic,
is the better approach to use.

Converting PsychoPy's mouse.py Demo to use ioHub
================================================

First, let's take an example from one of the PsychoPy demo scripts and show how
to easily use the ioHub keyboard and mouse devices with it using iohub.quickStartHubServer.

The original PsychoPy Example (mouse.py taken from a recent version of the 
PsychoPy software installation)::

    from psychopy import visual, core, event

    #create a window to draw in
    myWin = visual.Window((600.0,600.0), allowGUI=True)

    #INITIALISE SOME STIMULI
    fixSpot = visual.PatchStim(myWin,tex="none", mask="gauss",
            pos=(0,0), size=(0.05,0.05),color='black', autoLog=False)
    grating = visual.PatchStim(myWin,pos=(0.5,0),
                               tex="sin",mask="gauss",
                               color=[1.0,0.5,-1.0],
                               size=(1.0,1.0), sf=(3,0),
                               autoLog=False)#this stim changes too much for autologging to be useful
    myMouse = event.Mouse(win=myWin)
    message = visual.TextStim(myWin,pos=(-0.95,-0.9),alignHoriz='left',height=0.08,
        text='left-drag=SF, right-drag=pos, scroll=ori',
        autoLog=False)

    while True: #continue until keypress
        #handle key presses each frame
        for key in event.getKeys():
            if key in ['escape','q']:
                core.quit()
                
        #get mouse events
        mouse_dX,mouse_dY = myMouse.getRel()
        mouse1, mouse2, mouse3 = myMouse.getPressed()
        if (mouse1):
            grating.setSF(mouse_dX, '+')
        elif (mouse3):
            grating.setPos([mouse_dX, mouse_dY], '+')
            
        #Handle the wheel(s):
        # Y is the normal mouse wheel, but some (e.g. mighty mouse) have an x as well
        wheel_dX, wheel_dY = myMouse.getWheelRel()
        grating.setOri(wheel_dY*5, '+')
        
        event.clearEvents()#get rid of other, unprocessed events
        
        #do the drawing
        fixSpot.draw()
        grating.setPhase(0.05, '+')#advance 0.05cycles per frame
        grating.draw()
        message.draw()
        myWin.flip()#redraw the buffer
        
To convert the mouse.py script as literally as possible and use the ioHub for
the keyboard and mouse device inputs, the script would look as follows. The ioHub
version is much longer here because loads of comments have been added to the 
script explaining the ioHub API calls being made in some detail. Please review the
comments added to the below source code, as they explain differences to note when using
the ioHub package instead of the built in PsychoPy event functionality. The source
code can be found in the ioHub example folder in the ioMouse example::

	# -*- coding: utf-8 -*-
	"""
	Converted PsychoPy mouse.py demo script to use ioHub package for keyboard and
	mouse input.
	"""
	import sys

	from psychopy import visual, core

	from iohub import quickStartHubServer
	from iohub.client import Computer
	from iohub.constants import EventConstants
	from iohub.util.experiment import FullScreenWindow

	# Create and start the ioHub Server Process, enabling the 
	# the default ioHub devices: Keyboard, Mouse, Experiment, and Display.
	#
	# If you want to use the ioDataStore, an experiment_code and session_code
	# must be provided. 
	# If you do not want to use the ioDataStore, remove these two kwargs,
	# or set them to None. 
	# 
	# When specifying the experiment code, it should never change within runs of the same
	# experiment. 
	# However the session code must be unique from experiment run to experiment run
	# or an error will occur and the experiment will be aborted.
	#
	# If you would like to use a psychopy monitor config file, provide it's name 
	# in the psychopy_monitor_name kwarg, otherwise remove the arg or set it to None.
	# If psychopy_monitor_name is not specified or is None, a default psychopy monitor
	# config is used.
	#
	# All args to quickStartHubServer **must be** kwargs
	#
	# The function returns an instance of the ioHubClientConnection class (see docs
	# for full details), which is the experiment scripts interface to the ioHub
	# device and event framework.
	#
	import random
	io=quickStartHubServer(experiment_code="exp_code",session_code="s%d"%(random.randint(1,100000)))
					   
	# By default, keyboard, mouse, experiment, and display devices are created 
	# by the quickStartHubServer function. 
	#
	# If you would like other devices added, specify each my adding a kwarg to the 
	# quickStartHubServer function, where the kwarg is the ioHub Device class name,
	# and the kwarg value is the device configuration dictionary for the device.
	#
	# Any device configuration properties not specified in the device configuration 
	# use the device's default value for the configuration property.  See the 
	# ioHub Device and DeviceEvent documentation for details. 
	#
	# The ioHub interface automatically creates a ioHubDeviceView class for each
	# device created that is used to access device events or to call other device methods.
	# All available devices are accessed via the io.devices attribute.
	# 
	# Lets create 'short-cuts' to the created devices to save a bit of typing later on.
	#
	myMouse=io.devices.mouse
	display=io.devices.display
	myKeyboard=io.devices.keyboard

	# This is an example of calling an ioHub device method. It looks and functions
	# just like it would if you were calling a normal method of a class created in the 
	# experiment process. This is all that really matters.
	# 
	# However, for those interested,  remember that when using the ioHub the Devices
	# and all device event monitoring and processing is done in a seperate
	# system process (the ioHub Server Process). When this method is called,
	# the ioHub Process is informed of the request, calls the method with any
	# provided arguements using the actual MouseDevice instance that exists
	# on the ioHub Server Process, and returns the result of the method call to your
	# Experiment process Script. This all happens without you needing to think about it,
	# but it is nice to know what is actually happenning behind the scenes.
	#
	myMouse.setSystemCursorVisibility(False)

	# Currently ioHub supports mapping operating system event positions to a single
	# full screen psychopy window (that uses any of the supported psychopy window unit types,
	# other than height). Therefore, it is most convient to create this window using
	# the FullScreenWindow utility function, which returns a psychopy window using
	# the configuration settings provided when the ioHub Display device was created.
	#
	# If you provided a valid psychopy_monitor_name when creating the ioHub connection,
	# and did not provide Display device configuration settings, then the psychopy monitor
	# config specified by psychopy_monitor_name is read and the monitor size and eye to monitor
	# distance are used in the ioHub Display device as well. Otherwise the settings provided 
	# for the iohub Display device are used and the psychopy monitor config is updated with 
	# these display size settings and eye to monitor distance. 
	#
	myWin = FullScreenWindow(display)

	# We will read some of the ioHub DIsplay device settings and store
	# them in local variables for future use.
	#
	# Get the pixel width and height of the Display the full screen Window has been created on.
	#
	screen_resolution=display.getPixelResolution()
	#
	# Get the index of the Display. In a single Display configuration, this will always be 0.
	# If there are two Displays connected and active on your computer, then possible
	# values are 0 or 1, depending on which you told ioHub to create the Display Device for.
	# The default is always to use the Display with index 0.
	#
	display_index=display.getIndex()
	#
	# Get the Display's full screen window coordinate type (unit type). This is also specified when
	# the Display device is created . Coordinate systems match those specified by PsychoPy (excluding 'height').
	# The default is 'pix'. 	
	#
	coord_type=display.getCoordinateType()
	#
	# Get the calculated number of pixels per visual degree in the horizonal (x) dimension of the Display.
	#
	pixels_per_degree_x=display.getPixelsPerDegree()[0]
	
	# Create some psychopy visual stim. This is identical to how you would do so normally.
	# The only consideration is that you currently need to pass the unit type used by the Display
	# device to each stim reasource created, as is done here.
	#
	fixSpot = visual.PatchStim(myWin,tex="none", mask="gauss",
			pos=(0,0), size=(30,30),color='black', autoLog=False, units=coord_type)
			
	grating = visual.PatchStim(myWin,pos=(300,0),
							   tex="sin",mask="gauss",
							   color=[1.0,0.5,-1.0],
							   size=(150.0,150.0), sf=(0.01,0.0),
							   autoLog=False, units=coord_type)
							   
	message = visual.TextStim(myWin,pos=(0.0,-250),alignHoriz='center',
							  alignVert='center',height=40,
							  text='move=mv-spot, left-drag=SF, right-drag=mv-grating, scroll=ori',
							  autoLog=False,wrapWidth=screen_resolution[0]*.9,
							  units=coord_type)

	last_wheelPosY=0

	# Run the example until the 'q' or 'ESCAPE' key is pressed
	#
	while True: 
		# Get the current mouse position.
		#
		# Note that this is 'not' the same as getting mouse motion events, 
		# since you are getting the latest position information, and not information about how
		# the mouse has moved since the last time mouse events were accessed.
		# 
		position, posDelta = myMouse.getPositionAndDelta()		
		mouse_dX,mouse_dY=posDelta
	
		# Get the current state of each of the Mouse Buttons. True means the button is
		# pressed, False means it is released.
		#
		left_button, middle_button, right_button = myMouse.getCurrentButtonStates()
		
		# If the left button is pressed, change the visual gratings spatial frequency 
		# by the number of pixels the mouse moved in the x dimenstion divided by the 
		# calculated number of pixels per visual degree for x.
		#
		if left_button:
			grating.setSF(mouse_dX/pixels_per_degree_x/20.0, '+')
		#
		# If the right mouse button is pressed, move the grating to the position of the mouse.
		#
		elif right_button:
			grating.setPos(position)
		
		# If no buttons are pressed on the Mouse, move the position of the mouse cursor.
		#
		if True not in (left_button, middle_button, right_button):
			fixSpot.setPos(position)
			
		if sys.platform == 'darwin':
			# On OS X, both x and y mouse wheel events can be detected, assuming the mouse being used
			# supported 2D mouse wheel motion.
			#
			wheelPosX,wheelPosY = myMouse.getScroll()		
		else:
			# On Windows and Linux, only vertical (Y) wheel position is supported.
			#
			wheelPosY = myMouse.getScroll()
		
		# keep track of the wheel position 'delta' since the last frame.
		#
		wheel_dY=wheelPosY-last_wheelPosY
		last_wheelPosY=wheelPosY

		# Change the orientation of the visual grating based on any vertical mouse wheel movement.
		#
		grating.setOri(wheel_dY*5, '+')
		
		#
		# Advance 0.05 cycles per frame.
		grating.setPhase(0.05, '+')
		
		# Redraw the stim for this frame.
		#
		fixSpot.draw()
		grating.draw()
		message.draw()
		myWin.flip()#redraw the buffer

		# Handle key presses each frame. Since no event type is being given
		# to the getEvents() method, all KeyboardEvent types will be 
		# returned (KeyboardPressEvent, KeyboardReleaseEvent, KeyboardCharEvent), 
		# and used in this evaluation.
		#
		for event in myKeyboard.getEvents():
			#
			# If the keyboard event reports that the 'q' or 'ESCAPE' key was pressed
			# then exit the example. 
			# Note that specifying the lower case 'q' will only cause the experiment
			# to exit if a lower case q is what was actually pressed (i.e. a 'SHIFT'
			# key modifier was not being pressed and the 'CAPLOCKS' modifier was not 'on').
			# If you want the experiment to exit regardless of whether an upper or lower
			# case letter was pressed, either include both in the list of keys to match
			# , i.e. ['ESCAPE', 'q', 'Q'], or use the string.upper() method, i.e.
			# if event.key.upper() in ['ESCAPE','Q']
			#
			if event.key in ['ESCAPE','q']:
				io.quit()
				core.quit()
				
		# Clear out events that were not accessed this frame.
		#
		io.clearEvents('all')

	#
	## End of Example
	#
	
With your experiment file saved, you can run this example by running the python
file script.


Converting the PsychoPy Demo 'joystick_universal.py' Using ioHub Configuration Files 
=====================================================================================

The second approach to creating an ioHub experiment is to use a combination of
the python experiment script files(s) needed for the experiment with two
configuration files that are used by ioHub to learn about high level experiment
data, any experiment session level variables that should be tracked, and the details of
the devices to be used during the experiment runtime.

This approach is most useful when your experiment uses more complex devices like
an eye tracker or analog to digital input device. However it can be used for any experiment,
and has the advantage of cleanly seperating device configuration from the experiment
runtime logic. This seperation allows, for example, the same experiment script to
be used while still being able to easily change the eye tracker device that is used
during the experiment runtime. Nothing in the python experiment logic needs to change,
the eye tracker device configuration is instead updated to reflect the change in
eye tracking hwardware being used.

First, the PsychoPy demo script we will 'convert' is the joystick_universal.py demo::

    from psychopy import visual, core, event
    from psychopy.hardware import joystick

    """There are two ways to retrieve info from the first 3 joystick axes. You can use::
        joy.getAxis(0)
        joy.getX()
    Beyond those 3 axes you need to use the getAxis(id) form.
    Although it may be that these don't always align fully. This demo should help you
    to find out which physical axis maps to which number for your device.

    Known issue: Pygame 1.91 unfortunately spits out a debug message every time the 
    joystick is accessed and there doesn't seem to be a way to get rid of those messages.
    """

    joystick.backend='pyglet'
    #create a window to draw in
    myWin = visual.Window((800.0,800.0), allowGUI=False, 
        winType=joystick.backend)#as of v1.72.00 you need the winType and joystick.backend to match

    nJoysticks=joystick.getNumJoysticks()

    if nJoysticks>0:
        joy = joystick.Joystick(0)
        print 'found ', joy.getName(), ' with:'
        print '...', joy.getNumButtons(), ' buttons'
        print '...', joy.getNumHats(), ' hats'
        print '...', joy.getNumAxes(), ' analogue axes'
    else:
        print "You don't have a joystick connected!?"
        myWin.close()
        core.quit()
    nAxes=joy.getNumAxes()
    #INITIALISE SOME STIMULI
    fixSpot = visual.PatchStim(myWin,tex="none", mask="gauss",pos=(0,0), size=(0.05,0.05),color='black')
    grating = visual.PatchStim(myWin,pos=(0.5,0),
                        tex="sin",mask="gauss",
                        color=[1.0,0.5,-1.0],
                        size=(0.2,.2), sf=(2,0))
    message = visual.TextStim(myWin,pos=(0,-0.95),text='Hit "q" to quit')

    trialClock = core.Clock()
    t = 0
    while 1:#quits after 20 secs
        #update stim from joystick
        xx = joy.getX()
        yy = joy.getY()
        grating.setPos((xx, -yy))
        #change SF
        if nAxes>3: 
            sf = (joy.getZ()+1)*2.0#so should be in the range 0:4?
            grating.setSF(sf)
        #change ori
        if nAxes>6: 
            ori = joy.getAxis(5)*90
            grating.setOri(ori)
        #if any button is pressed then make the stimulus coloured
        if sum(joy.getAllButtons()):
            grating.setColor('red')
        else:
            grating.setColor('white')
            
        #drift the grating
        t=trialClock.getTime()
        grating.setPhase(t*2)
        grating.draw()
        
        fixSpot.draw()
        message.draw()
        print joy.getAllAxes()#to see what your axes are doing!
        
        if 'q' in event.getKeys():
            core.quit()
            
        event.clearEvents()#do this each frame to avoid getting clogged with mouse events
        myWin.flip()#redraw the buffer

.. note:: Currently ioHub has support for XInput compatible Gamepads only. This includes the 
    Xbox 360 Gamepad for PCs (Wired or wireless) and some models of Logitech
    Gamepads, such as the Logitech F310 and F710. To run this example, you will need
    one of these Gamepad models, or another gamepad that supports the XInput interface.
    
    Full XInput Gamepad 1.3 functionality is supported by ioHub, including reading all 
    Gamepad inputs, setting the vibration state for the two vibration mechanisms
    in the Xbox 360 PC and Logitech F710 controllers, and even getting the battery status 
    of wireless versions of the gamepads.
    
    Note that your computer needs to have XInput version 1.3 installed in order
    for the ioHub Gamepad device to work. if you do not, when you run your experiment
    you will get an error at the start of the experiment printed to your python console.
    
    You can check if you already have XInput 1.3 installed on your Windows system
    by searching for xinput1_3.dll in the c:\Windows directory of your PC. If the file 
    is found, you do not need to do anything further. (Windows 7 seems to come with the file
    already, Windows XP SP2 or 3 may not have the file.)
    
    The easiest way to install XInput 1.3 if it is not already on your PC is to run
    the DirectX 10 upgrade utility provided by Miscrosoft. It can be downloaded 
    `here. <http://www.microsoft.com/en-us/download/details.aspx?id=35>`_
    This will install xinput1_3.dll into your C:\Windows\System32 and 
    C:\Windows\SysWOW64. Please check that this DLL is present after you run 
    the DirectX 10 upgrade utility.
    
Once the information in the above Note has been followed, and you have the XInput
capable device plugged into your PC, then getting to the task of creating the ioHub 
compatible version of the demo can be started. Note that all source files for this 
example are in the ioGamepad directory of the ioHub Examples folder.

The following steps should be followed if a new version of the demo is being created:
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#. Create a directory (location of your choice) called ioXInputGamePad. The directory can be any name you wish, but here it is assumed it is called ioXInputPsychoPy.
#. Within the ioXInputGamePad directory, create the python source file that will hold the example python source code. This example assumes it has been named run.py
#. Within the ioXInputGamePad directory, create a file that will hold the experiment configuration for the demo. This file **must** be called experiment_config.yaml
#. Within the ioXInputGamePad directory, create a file that will hold the ioHub configuration for the demo. This file can be of any name, but the standard is to call it iohub_config.yaml.

With the above directory and file structure created, contents can now be added to the
python source file and the two .yaml configuration files as described below. 

.. note:: When using this approach to creating the experiment,
    the above expriment folder structure will always be used. To save time in creating
    this initial experiment folder setup, there is a folder called startingTemplate
    in the ioHub examples folder that contains the necessary python source file with
    the ExperimentIOHubRuntime class extension already defined, so only your experiment
    code needs to be added to the class run method. The folder also contains a base 
    experiment_config.yaml and io_hub.yaml which can just be modified as necessary 
    for your experiment. In this QuickStart example, it will be assumed that all files are
    being created from scratch.
    
run.py Python Source File Contents
++++++++++++++++++++++++++++++++++++

Add the following python source code to the run.py file that was created::

    """
    Example of using XInput gamepad support from ioHub in PsychoPy Exp.
    """

    from psychopy import core, visual
    import iohub
    from iohub.client import Computer
    from iohub.util.experiment import ioHubExperimentRuntime,FullScreenWindow

    class ExperimentRuntime(ioHubExperimentRuntime):
        """
        Create an experiment using psychopy and the ioHub framework by extending the ioHubExperimentRuntime class. At minimum
        all that is needed in the __init__ for the new class, here called ExperimentRuntime, is the a call to the
        ioHubExperimentRuntime __init__ itself.
        """
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
            
            #create a window to draw in
            mouse=self.devices.mouse
            display=self.devices.display
            keyboard=self.devices.keyboard
            gamepad=self.devices.gamepad
            computer=self.devices.computer

            # Read the current resolution of the displays screen in pixels.
            # We will set our window size to match the current screen resolution 
            # and make it a full screen boarderless window.
            screen_resolution= display.getPixelResolution()

            unit_type = display.getCoordinateType()
            # Create a psychopy window, full screen resolution, full screen mode, 
            # pix units, with no boarder.
            myWin = FullScreenWindow(display)
                
            # Hide the 'system mouse cursor'
            mouse.setSystemCursorVisibility(False)

            gamepad.updateBatteryInformation()
            bat=gamepad.getLastReadBatteryInfo()
            print "Battery Info: ",bat

            gamepad.updateCapabilitiesInformation()
            caps=gamepad.getLastReadCapabilitiesInfo()
            print "Capabilities: ",caps
        
            fixSpot = visual.PatchStim(myWin,tex="none", mask="gauss",pos=(0,0), 
                                size=(30,30),color='black',units=unit_type)
            
            grating = visual.PatchStim(myWin,pos=(0,0), tex="sin",mask="gauss",
                                color='white',size=(200,200), sf=(0.01,0),units=unit_type)

            msgText='Left Stick = Spot Pos; Right Stick = Grating Pos;\nLeft Trig = SF; Right Trig = Ori;\n"r" key = Rumble; "q" = Quit\n'
            message = visual.TextStim(myWin,pos=(0,-200),
                                text=msgText,units=unit_type,
                                alignHoriz='center',alignVert='center',height=24,
                                wrapWidth=screen_resolution[0]*.9)
        
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
                
                grating.setSF((sf/display.getPixelsPerDegree()[0])*2+0.01) #so should be in the range 0:4

                #change ori
                ori=gamepad.getTriggers()['RightTrigger']
                grating.setOri(ori*360.0) 

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
        
    ############################ End of run.py Script #########################

Defining the Experiment Configuration Setting
++++++++++++++++++++++++++++++++++++++++++++++

The experiment configuration settings, including session level information, are
represented in a YAML formatted configuration filecalled experiment_config.yaml.
This file is placed in the same directory as the main experiment python script file.
Three types of settings are defined within the experiment_config.yaml file:

#.  Custom session variables you want displayed in a dialog for input at the start 
    of each session of the experiment. These are defined in the 
    session_defaults: user_variables section. 
#.  Configuration settings related to the local Experiment process. 
#.  Custom experiment preferences can also be added, as long as the preference name is 
    not a standard ioHub experiment configuration preference name.

ioHub Configuration files are specified using YAML syntax. For this quickstart section,
we will not go into details abuot each setting with the files.

Enter the following into your experiment_config.yaml for this example::

    # Experiment level configuration settings in YAML format
    title: ioHub XInput Gamepad Example with PsychoPy
    code: ioXInput
    version: '1.0'
    description: Uses an XInput compatible gamepad within a psychoPy script.
    session_defaults:
        name: Session Name
        code: E1S01
        comments: None
    session_variable_order: [ name, code, comments ]
    ioHub:
        enable: True
        config: ioHub_config.yaml

    
Defining Device Information in the iohub_config.yaml File.
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

ioHub specific configuration settings, mainly in regard to the devices that will be used
within your experiment, are represented in the iohub_config.yaml file.
There are two types of ioHub settings in the iohub_config.yaml file:

#.  General ioHub Server configuration settings.
#.  Details about the setup of each ioHub Device to be used.

Enter the following into your iohub_config.yaml for this example::

    # iohub_config.yaml: settings related to the iohub process and the device types 
    # that are to be enabled for the experiment.

    monitor_devices:
        - Display:
            name: display
            reporting_unit_type: pix
            device_number: 0
            physical_dimensions:
                width: 500
                height: 281
                unit_type: mm
            default_eye_distance:
                surface_center: 500
                unit_type: mm
            psychopy_monitor_name: default
            origin: center
        - Keyboard:
            name: keyboard
            save_events: True
            stream_events: True
            auto_report_events: True
            event_buffer_length: 256
        - Mouse:
            name: mouse
            save_events: True
            stream_events: True
            auto_report_events: True
            event_buffer_length: 256
        - Experiment:
            name: experimentRuntime
            save_events: True
            stream_events: True
            auto_report_events: True
            event_buffer_length: 128
        - xinput.Gamepad:
            name: gamepad
            device_number: -1
            enable: True
            save_events: True
            stream_events: True
            auto_report_events: True
            event_buffer_length: 256
            device_timer:
                interval: 0.005
    data_store:
        enable: True    
        
The iohub_config.yaml file also resides in the same folder as your main experiment script.

With all three files saved, and a supported XInput compatible gamepad connected
to the computer (powered on if a wireless gamepad), you can run the gamepad example
by starting the run.py script. 

While at first this approach may seem like more work than a script only approach to 
creating your experiment, I think once you have used it a couple times it will become
clear that the configuration file vs. experiment logic approach to dividing how
information is represented for an experiment often results in less work and the
promotion of experiment python script reuse. This is because there is less of a need
to be repeatedly 'configuring' more complex device types within the script environment itself, 
but instead within a better suited, more constrained, device configuration specification.

Please let us know your opinions on this after working with this experiment structure.

For details on the ioHub configuration file definition and the valid settings 
supported by each device please see the API section of the Manual.