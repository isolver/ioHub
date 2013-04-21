###########################
ioHub Example Scripts
###########################

There are a set of example programs / experiments that are included with the 
ioHub source code. All examples can be found in the ioHub/examples/ directory.

Some examples require a specific device type to run, including several that 
require a supported eye tracking device.

Examples Overview
##################

A set of standard scripts / experiments / tests are available that do not require
an eye tracker to run. Unless otherwise noted, only a computer Monitor, Keyboard,
and Mouse are required to run the standard examples.

Using a Single Python Experiment Script File 
---------------------------------------------

Content TBC.

Using the ExperimentIOHubRuntime Class and YAML Configuration Files
--------------------------------------------------------------------

Many of the examples are written by creating a Python class that extends the
*iohub.util.experiment.psychopyIOHubRuntime.ExperimentIOHubRuntime* class, 
creates an instance of the class defined, and calls the classes .start() method. 

The class that extends *ExperimentIOHubRuntime* simply 
needs to define a run(*args,**kwargs) method and add the PsychoPy script code 
that you want for your experiment to it. 

By calling the start() method, your custom code defined in the run() method gets executed.

When using the *ExperimentIOHubRuntime* class extension method of interfacing 
with PsychoPy and the ioHub you should create a new directory for each experiment
you write, for example say you create an empty directory called *my_experiment_1*.
The experiment directory needs to have **three** files at minimum, one Python file
and two `YAML <http://www.pyyaml.org/wiki/PyYAMLDocumentation>`_ configuration files.
Using the above experiment directory name example, a minimum directory structure
would look like the following:

* path/to/my_experiment_1/
    * [myExperimentCode].py
    * [experiment_config].yaml
    * [ioHub_config].yaml

A Brief Description of Each File
*********************************

myExperimentCode.py Python File
++++++++++++++++++++++++++++++++

A python file that contains a class definition that extends the 
*ExperimentIOHubRuntime* class and implements the **run method** of the class.

For example:

```python
     import ioHub
     from iohub.util.experiment import ExperimentIOHubRuntime

     class MyExperimentRuntime(ExperimentIOHubRuntime):
        def __init__(self,configFileDirectory, configFile):
            ExperimentIOHubRuntime.__init__(self,configFileDirectory,configFile)

        def run(self,*args,**kwargs):
            print "Hello World"
```

**[myExperimentCode].py** is the name you have given to this python file. The file can be called what you like, the examples mainly call it **run.py**.

Besides defining the runtime class, the python file also contains a small amount of boilerplate code for **if __name__ == '__main__'**:

```python
    def main(configurationDirectory):
        import sys
        if len(sys.argv)>1:
            configFile=unicode(sys.argv[1])
            runtime=ExperimentRuntime(configurationDirectory, configFile)
        else:
            runtime=ExperimentRuntime(configurationDirectory, "experiment_config.yaml")

        runtime.start()

    if __name__ == "__main__":
        configurationDirectory=iohub.module_directory(main)
        main(configurationDirectory)
```

## 2. **[experiment_config].yaml**

A [YAML file](http://www.pyyaml.org/wiki/PyYAMLDocumentation) that contains configuration information for your experiment overall. The default name of the experiment configuration file is *experiment_config.yaml*. You can give it any name you like that is a valid file name for your OS, however if you change the default config file name and do not provide your new experiment config file name when you run your experiment .py file, then you need to change the boilerplate main() function and specify the correct *default* experiment config file name to use. For details on the experiment configuration .yaml file, please see the ioHub Tutorial section of the wiki.

## 3. **[ioHub_config].yaml**

A [YAML file](http://www.pyyaml.org/wiki/PyYAMLDocumentation) that contains configuration information for the ioHub process and ioServer class. This includes defining what devices you wish to enable for the current experiment. The default name of the ioHub configuration file is *ioHub_config.yaml*. You can give it any name you like that is a valid file name for your OS, however if you change the default config file name, then you need to change the experiment_config.yaml and specify the correct ioHub config file name to use. This is done by changing the ioHub: config: parameter in the experiment config file. For details on the ioHub configuration .yaml file, please see the ioHub Tutorial section of the wiki.

# B. Force Quitting an ioHub Example


> If for some reason your experiment, or one of the example experiments, does not end when expected and you
> are stuck with a full screen PsychoPy window open that you can not close, do the following to force kill
> the Experiment Process and ioHub Process:

1. Press Ctrl+Alt+Del on your Windows keyboard.
2. A dialog should appear that gives you the option to open the Windows Task Manager.
3. Select the Windows Task Manager option to start it.
4) In Windows Task Manager, go to the *Processes* Tab.
5) Press on the "Image Name" column header to sort the processes by name.
6) Press 'p' on your keyboard to go to the start of the process list with names starting with 'p'.
7) Your experiment / example program will be displayed as **two** python.exe processes (one for the experiment process, one for the ioHub process).
8) Select one of the two python.exe processes and then press the "End Process" button.
9) If the second python.exe process is still running, select it, and then press the "End Process" button.

Now the full screen window should be gone and you should have normal control of your desktop. The command prompt window will still be open and some Python stack trace information may have been written to it.

> If this situation occurs with any of the standard example projects and you have not modified them in any
> way (including the .yaml files), please report the issue to me and send any stack trace output that may be
> in the command prompt window so I can try and determine the source of the problem. Please zip up the
> example project that is causing the issue as well and send it to me as an attachment.

# C. Running a Standard Example

To run one of the standard examples:

1. Make a copy of the example directory you wish to run and put the copy where you like in your file system.(this step is not mandatory, but is a good practice to follow)
2. Open a command prompt and go to ( cd ) the example directory copy you just made. Note that on Windows 7, if you have the example directory visible in the Right side of your File Explorer, if you hold SHIFT and click the Right mouse button when the mouse cursor is over the example folder icon, a pop-up menu appears that includes a *"Open Command window here"* entry that will open a console window already at your example directory.
3. With the command prompt in your example directory, type:

`    python [myExperimentCode].py [my_experiment_config.yaml]`

where myExperimentCode is the name of your python file as described above, and the *optional*  [my_experiment_config.yaml] is a non-default experiment configuration file name that is located in the current directory. If [experiment_config.yaml] is not provided, a file called *experiment_config.yaml* is looked for in the current directory.

# D. Standard ioHub Example List

The current ioHub standard examples are:

## 1. startingTemplate

This is the "Hello World" ioHub example. ;) The directory can be copied and used as the starting point for an ioHub / PsychoPy experiment. The template has the necessary files and the minimum necessary code in the run.py file to start creating an experiment. As is, all the template does if run is print 'Hello World' to stdout.

After making a copy of the template project, just start adding your experiment logic to the *run* method of the ExperimentRuntime class. To run the template project as is, go to the template directory in a command prompt and type:

`python run.py`

and press Enter and the project should run, eventually printing Hello World to the command prompt window.

## 2. simple

The simple example is an extension of one of the examples found in the PsychoPy Coder Guide. The example creates a full screen window, with a resolution equal to the current resolution of the Display being used.
The program draws a central fixation square, a moving grating in a circular shape, and a mouse contingent Gaussian blob that is updated each retrace based on the last mouse position read. The program continues to run until either the spacebar, Return (Enter), or Escape key is pressed on the keyboard.

This is a pretty straight forward example that still shows how to integrate ioHub event buffers from the keyboard and mouse into a simple PsychoPy retrace loop. The run.py code is pretty well documented, so please refer to it for details on this example.

To run the example, go to the simple example directory in a command prompt and type:

`python run.py`

and press Enter and the project should run, displaying the graphics described above.

To end the experiment, press the spacebar, Return (Enter), or Escape key.

## 3. ioHubAccessDelayTest

The main purpose for the ioHubAccessDelayTest is to test the round trip time it takes for the experiment process to request and receive events from the ioHub Process running the ioServer. Retrace intervals are
also calculated and stored to monitor for skipped retraces.

This is a more involved example, so the code has been broken out into several chunks, each as a method of the ExperimentRuntime class. The ExperimentRuntime.run() method then calls these custom defined methods, making the run() method itself more readable.

A full screen Window is opened that shows some graphics, including a moving grating as well as a small Gaussian that is controlled by mouse events from the iohub. At the top of the screen is an area that will display the last key pressed on the keyboard.

The script runs for until 1000 getEvent() requests to the ioHub have returned with >= 1 event. A number near the bottom of the screen displays the number of remaining successful getEvent calls before the experiment will end.

By default the script also sends an Experiment MessageEvent to the ioHub on each retrace. This message is stored in the ioDataStore file, but is also sent back as an ioHub MessageEvent to the experiment process.
Therefore, the getEvent() request counter shown on the screen will decrease even if you do not move your mouse or keyboard, as the MessageEvents are retrieved from the ioHub Server.

At the end of the test, plots are displayed showing the getEvent() round trip delays in a histogram,
the retrace intervals as a function of time, and the retrace intervals in a histogram. All times in the plots are in msec.usec time.

To run the example, go to the ioHubAccessDelayTest example directory in a command prompt and type:

`python run.py`

and press Enter and the project should run.

# Eye Tracker Examples: Using the pyEyeTrackerInterface

There are also a set of examples that include the use of an EyeTracker device. The ioHub uses the pyEyeTrackerInterface as its' EyeTracker device API. The pyEyeTrackerInterface is a common eye tracker run-time API written in Python that has been designed to be as hardware independent as possible. This means that multiple different eye tracking systems can implement a version of the pyEyeTrackerInterface for their eye tracker, providing users with a consistent Python API that can be used with PsychoPy for interacting with eye tracker devices and accessing eye tracker events. This makes writing eye tracking experiments that can then be run using different eye tracking hardware much more feasible, and also greatly reduces the learning curve of eye tracking users wanting to run experiments with supported eye tracking devices.

As of writing, there is a beta version of the eye tracker interface available for the SMI iViewX line of systems, as well as a beta version for the SR Research EyeLink II and EyeLink 1000 systems. Both of these eye tracker models can be used to run any of the included example eye tracking experiments; with only a few changes to a configuration file.

Interface implementations are also currently being developed for the LC Technologies eye tracking systems and the EyeTech eye trackers. These are not yet at a usable stage however.

All the eye tracking examples have the same general structure as the standard ioHub / psychoPy examples outlied above. The main difference is that these examples include an EyeTracker device in the ioHub_config.yaml settings file. The device configuration for an eye tracker will look something like this:

```yaml
    - device:
        # the device_class setting for the eye tracker devices which implementation,
        # or which eye tracking model, you will use for the experiment.
        #device_class: eyeTrackerInterface.HW.SMI.iViewX.EyeTracker
        device_class: eyeTrackerInterface.HW.SR_Research.EyeLink.EyeTracker

        # the name parameter is what is used to define the device when accessing it via the ioHubConnection's
        # devices attribute. So here, the eye tracker will be accessed as devices.tracker in your script.
        name: tracker

        # instance_code allows you to provide a unique identifier for the eye tracker. It's serial number is
        #often good to use.
        instance_code: et_serial_number

        # should eye tracker events be saved to the ioHub ioDataStore (i.e. the HDF5 file?) by the ioHub Process?
        saveEvents: True

        # should eye tracker events be streamed to the experiment Process (i.e PsychoPy)?
        streamEvents: True

        # for EyeLink, events are polled; this sets the polling interval. i.e. every 1 msec right now
        # for SMI, events are sent to the ioHub via a callback function, so the event_timer section
        # should be commented out.
        device_timer:
            interval: 0.001

        # what is the maximum number of events (and samples) that the ioHub will hold before overwrites start to occur.
        event_buffer_length: 2048

        #
        # display_settings: provides a copy of all the Display Device settings
        #
        display_settings: *DisplaySettings

        #
        # runtime_settings: contains settings that are used during eye tracker initialization
        #                   to set various values in the eye tracker configuration so that they
        #                   do not need to be set explicidly by sending commands via the the
        #                   send command method. Refer to your devices implementation for
        #                   which runtime_setting and values are supported.
        #
        runtime_settings:
            #
            # Save native eye tracker data file to this local directory
            #
            save_native_data_file_to: .
            #
            # Default native data file name (NOT including appropriate file name extenstion / postfix)
            #
            default_native_data_file_name: default
            #
            # EyeTrackerConfig['sampling_rate'] = FLOAT_HZ
            #
            # Sampling rate to track at in Hz. Must be supported by eye tracker being used. ;)
            #
            sampling_rate: 1000
            #
            # EyeTrackerConfig['track_eyes']=('BINOC' | 'MONO', [ 'MEAN' | 'SIM' ])
            #
            # which eyes to track?
            # BINOC == binocular, seperate data provided for both eyes
            # BINOC, AVERAGE == record binocular data, but ioHub sends
            #      mono sample stream of averaged data from 2 eye fields.
            #     (TO DO: not yet implemented)
            # BINOC, SIM == binocular,
            #     running in simulation mode supported by tracker
            # MONO == monocular , eye selected during setup of system.
            #    'LEFT' or 'RIGHT' can be used instead of 'MONO'
            #    to request a specific eye, but this can not be guarenteed.
            # MONO, SIM == monocular recording,
            #    running in simulation mode supported by tracker
            #    'LEFT' or 'RIGHT' can be used instead of 'MONO'
            #    to request a specific eye, but this can not be guarenteed.
            track_eyes: BINOC
            #
            # default_calibration: NONE | 3P_HOR | 3P_VERT | 3P_2D |
            #                      4P_CORNERS | 4P_SIDE_CENTERS |
            #                      5P_X | 5P_+ | 9P | 13_P
            #
            # Defines the default calibration grid to use. Not all options
            # Will be available for all eye trackers. Check with the eye
            # tracker implementation otes for the available options for
            # your tracker.
            #
            default_calibration: 9P
            #
            # vog_settings:
            #
            # Setting related specifically to video based eye tracking systems.
            #
            # tracking_mode: pupil-cr | pupil-only
            #
            # tracking_mode specifies which features, or signals, are tracked while
            # while calculating eye position.
            # pupil-cr inications that the pupil and one or more corneal reflections are
            # used during image processing.
            # pupil-only indicates that the eye trcacker uses only the pupil to determine
            # eye position.
            # Your eye tracker may only support one of these modes; check your implementation
            # specific documentation for details.
            #
            # pupil_illumination: dark | bright | mixed
            #
            # pupil_illumination specifes the illumination type being used for the tracker.
            # (dark == off-axis, bright == on-axis, mixed == some form of alternating dark , bright)
            # while most eye trackers have a fixed, pupil_illumination type, some allow this to be
            # changed whileusing the same core system. Again, check with your trackers implementation doc
            # for details.
            #
            # pupil_center_algorithm: centroid | circle_fit | elipse_fit | *implementation_defined*
            #
            # pupil_center_algorithm defines the algorithm to use for determining the center the the pupil
            # mass by the eye tracker image processing layer. Some eye trackers support > 1 algorithm
            # that is user selectable, so this setting allows you to specify which algorithm to use.
            # Again, check with your eye tracker implementation for the valid options for your implementation.
            # *implementation_defined* indicates that values not listed here may be specified
            # by a specific implementation and used in a configuration file.
            vog_settings:
                tracking_mode: pupil-cr
                pupil_illumination: dark
                pupil_center_algorithm: centroid
            #
            # auto_calibration: True | False
            #
            # should tracker auto accept fixations (True) or should fixations
            # be manually accepted by a button or key press (False)
            #
            auto_calibration: True
            #
            # runtime_filtering: ANY | LINK | FILE | ANALOG | SERIAL : NONE | LEVEL_1 | LEVEL_2 |
            #                                                          LEVEL_3 | LEVEL_4 | LEVEL_5
            #
            # Sets runtime filtering of the sample stream for the system
            # 0 == no filtering, see specific interface implementation
            # 'ANY' == set the provided filter level for any data streams that
            # can be filtered. Some eye trackers support independent filtering
            # of different data streams, for example the real-time sample feed
            # vs. the sample stream saved to file.
            # Therefore 'ANY' may also be 'LINK' or 'FILE' or 'ANALOG',
            # as examples, to set a specific streams filter level, with
            # different entries for different stream values. Again,
            # please see specific interfaces implementation page for specifics.
            # Safest bet is to use 'ANY' if you are unsure, as this must be supported.
            runtime_filtering:
                ANY: 0
```

Running an eye tracking example is the same as a standard example. The eye tracking examples often have extra steps in them, like performing user calibration, that are unique to eye tracking experiments. See the pyEyeTrackerInterface API for details on the eye tracker device class and associated device events.

# Eye Tracker Example List

## 1. simpleEyeTracker

This is a good first eye tracking example to start with. The example starts with a user calibration, after which a screen identical to the *simple* example is shown, but the Gaussian blob is gaze contingent in this example instead of mouse contingent. You can end the example by pressing any key on the PsychoPy keyboard.

After making a copy of the simpleEyeTracker project, go to the example directory you copied in a command prompt and type:

`python simpleTrackerTest.py`

and press Enter and the project should run.

** Be sure you updated the iohub_config.yaml and at minimum changed the eye tracker device_class to the supported eye tracker type you will be using. **

## 2. eyeTrackerFixationCounter

This eye tracker example demonstrated how to monitor the eye event stream for fixation end events, track the number of fixations made and the total dwell time, and then ends when a key is pressed on the Psychopy keyboard. The fixation information collected is printed to stdout. The example starts with a user calibration, after which an image is drawn to the screen. When PsychoPy indicates that the retrace for the start of the image display has occurred, the time is taken and a message is sent to the ioDataDtore. The event buffers are also cleared at this point. Data collection on fixation events then starts, as well as monitoring for a key press, which will end the demo.

After making a copy of the eyeTrackerFixationCounter project, go to the example directory you copied in a command prompt and type:

`python run.py`

and press Enter and the project should run.

** Be sure you updated the iohub_config.yaml and at minimum changed the eye tracker device_class to the supported eye tracker type you will be using. **


## 3. ioHubEyeTrackerAccessTest

The ioHubEyeTrackerAccessTest is mainly a test program that can be used by pyEyeTrackerInterface implementers to test their implementation of the common eye tracker API. The test program opens a full screen window but does not display anything in it. All output is via stdout. The test goes through the methods of the eye tracker interface several times, calling them with expected arguments, and printing out the return values. A developer of an eye tracker implementation can use the program to see what API methods are returning appropriate values, which are not, and if any unhandled exceptions are created.

After making a copy of the ioHubEyeTrackerAccessTest project, go to the example directory you copied in a command prompt and type:

`python run.py`

and press Enter and the project should run.

** Be sure you updated the iohub_config.yaml and at minimum changed the eye tracker device_class to the supported eye tracker type you will be using. **

***
