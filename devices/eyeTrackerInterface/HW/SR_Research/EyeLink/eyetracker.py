"""
ioHub
pyEyeTracker Interface
.. file: ioHub/devices/eyeTrackerInterface/HW/SR_Research/EyeLink/eyetracker.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

---------------------------------------------------------------------------------------------------------------------
This file uses the pylink module, Copyright (C) SR Research Ltd. License type unknown as it is not provided in the
pylink distribution (atleast when downloaded May 2012). At the time of writting, Pylink is freely avalaible for
download from  www.sr-support.com once you are registered and includes the necessary C DLLs.
---------------------------------------------------------------------------------------------------------------------

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

import sys
import ioHub

from ..... import Computer, EventConstants
try:
    import EyeLinkCoreGraphicsPyglet
    from EyeLinkCoreGraphicsPyglet import EyeLinkCoreGraphicsPyglet
    import pylink
except:
    ioHub.print2err("warning: pylink module could not be found")

from .... import RTN_CODES, DATA_STREAMS,DATA_FILTER,EyeTrackerInterface

class EyeTracker(EyeTrackerInterface):
    """EyeTracker class is the main class for the pyEyeTrackerInterface module,
    containing the majority of the eye tracker functionality commonly needed
    for a range of experiments.

    With the integration of the pyEyeTrackerInterface into the ioHub module, the EyeTracker
    device is a device along with the other currently supported ioHub devices; Keyboard, Mouse,
    and Parallel Port.

    For implementers of pyEyeTracker interfaces, this means that the interface itself is running
    in the ioHub process, and communication between the computer and the eyetracker is done via
    the ioHub.

    For users of the pyEyeTrackerInterface for an eye tracker and psychopy, there is a second,
    experiment side ( psychopy side ) interface that has a parallel public API that 'talks'
    to the ioHub server. The good news for users is that this is transparent and you should not
    even realize this is happening in use. The good news for interface developers is that the
    client side interface is dynamically generated at the start-up of the experiment based on the
    server side interface, so you do not need to maintain 2 seperate interfaces or worry about
    keeping them in sync.

    Not every eye tracker implemenation of the pyEyeTrackerInterface specification will
    support all of the specifications functionality. This is to be expected and
    pyEyeTrackerInterface has been designed to handle this case. When a specific
    implementation does not support a given method, if that method is called,
    a default *not supported* behaviour is built into the base implemetation.

    On the other hand, some eye trackers offer very specialized functionality that
    is as common across the eye tracking field so is not part of the pyEyeTrackerInterface core,
    or functionality that is just currently missing from the pyEyeTrackerInterface. ;)

    In these cases, the specific eye tracker implemetation can expose the non core pyEyeTrackerInterace
    functionality for their device by adding extra command types to the
    sendCommand method, or as a last resort, via the *EyeTracker.EXT* attribute of the class.

    .. note::

        Only **one** instance of EyeTracker can be created within an experiment. Attempting to create > 1 instance will raise an exception. To get the current instance of the EyeTracker you can call the class method EyeTracker.getInstance(); this is useful as it saves needing to pass an eyeTracker instance variable around your code.

    Methods are broken down into several categories within the EyeTracker class:

    #. Eye Tracker Initalization / State Setting
    #. Ability to Define the Graphics Layer for the Eye Tracker to Use During Calibration / System Setup
    #. Starting and Stopping of Data Recording
    #. Sending Syncronization messages to the Eye Tracker
    #. Accessing the Eye Tracker Timebase
    #. Accessing Eye Tracker Data During Recording
    #. Syncronizing the Local Experiment timebase with the Eye Tracker Timebase, so Eye Tracker events can be provided with local time stamps when that is appropriate.
    #. Experiment Flow Generics
    """
    
    #: Used by pyEyeTrackerInterface implentations to store relationships between an eye 
    #: trackers command names supported for pyEyeTrackerInterface sendCommand method and  
    #: a private python function to call for that command. This allows an implemetation 
    #: of the interface to expose functions that are not in the core pyEyeTrackerInterface spec 
    #: without have to use the EXT extension class.
    _COMMAND_TO_FUNCTION={}     
    
    _INSTANCE=None #: Holds the reference to the current instance of the EyeTracker object in use and ensures only one is created.

    EXT=None  # IF Vendor specific extensioin of API must be done, create an extension of EyeTrackerVendorExtension class and add an instance of it here. 

    _setupGraphics=None # instance of EyeTrackerSetupGraphics class, if supported

    _latestSample=None # latest eye sample from tracker
    _latestGazePosition=0,0 # latest gaze position from eye sample. If binocular, average valid eye positions
    
    eyeTrackerConfig=None # holds the configuration / settings dict for the device
    displaySettings=None
    
    #  >>>> Class attributes used by parent Device class
    DEVICE_START_TIME = 0.0 # Time to subtract from future device time reads. 
                             # Init in Device init before any calls to getTime() 
    DEVICE_TIMEBASE_TO_SEC=0.001
    
    # <<<<<
    
    # used for simple lookup of device type and category number from strings
    CATEGORY_LABEL='EYE_TRACKER'
    DEVICE_LABEL='EYE_TRACKER_DEVICE'



    # >>> Custom class attributes
    _eyelink=None
    _OPEN_EDF=None
    _VALID_SAMPLING_RATES=[250,500,1000,2000]
    _VALID_CALIBRATION_TYPES=dict(H3="H3",HV3="HV3",HV5="HV5",HV9="HV9",HV13="HV13")
    lastPollTime=0.0
    currentSampleRate=None
    #_eventArrayLengths=dict()
    # <<<

    # >>> Overwritten class attributes
    __slots__=[]
    # <<<
    def __init__(self,*args,**kwargs):
        """
        EyeTracker class. This class is to be extended by each eye tracker specific implemetation
        of the pyEyeTrackerInterface.

        Please review the documentation page for the specific eye tracker model that you are using the
        pyEyeTrackerInterface with to get the appropriate module path for that eye tracker; for example,
        if you are using an interface that supports eye trackers developed by EyeTrackingCompanyET, you
        may initialize the eye tracker object for that manufacturer something similar too :

           eyeTracker = hub.eyetrackers.EyeTrackingCompanyET.EyeTracker(**kwargs)

        where hub is the instance of the ioHubConnection class that has been created for your experiment.

        **kwargs are an optional set of named parameters.

        **If an instance of EyeTracker has already been created, trying to create a second will raise an exception. Either destroy the first instance and then create the new instance, or use the class method EyeTracker.getInstance() to access the existing instance of the eye tracker object.**
        """

        if EyeTracker._INSTANCE is not None:
            raise ioHub.devices.ioDeviceError(EyeTracker._INSTANCE,'EyeTracker object has already been created; only one instance can exist.\n Delete existing instance before recreating EyeTracker object.')

        # >>>> eye tracker config
        EyeTracker.eyeTrackerConfig=kwargs['dconfig']
        #print " #### EyeTracker Configuration #### "
        #print self.eyeTrackerConfig
        #print ''
        # <<<<

        # create Device level class setting dictionary and pass it Device constructor
        deviceSettings={'instance_code':EyeTracker.eyeTrackerConfig['instance_code'],
            'category_id':ioHub.devices.EventConstants.DEVICE_CATERGORIES[EyeTracker.CATEGORY_LABEL],
            'type_id':ioHub.devices.EventConstants.DEVICE_TYPES[EyeTracker.DEVICE_LABEL],
            'device_class':EyeTracker.eyeTrackerConfig['device_class'],
            'name':EyeTracker.eyeTrackerConfig['name'],
            'os_device_code':'OS_DEV_CODE_NOT_SET',
            'max_event_buffer_length':EyeTracker.eyeTrackerConfig['event_buffer_length']
            }
        EyeTrackerInterface.__init__(self,*args,**deviceSettings)

        # set this instance as 'THE' instance of the eye tracker.
        EyeTracker._INSTANCE=self

        # >>>> implementation specific private attributes
        EyeTracker._eyelink=pylink.EyeLink()
        EyeTracker.currentSampleRate=EyeTracker._eyelink.getSampleRate()

        EyeTracker.DEVICE_START_TIME=int(self._eyelink.trackerTime())
        # <<<<

        # >>>> eye tracker setting to config (if possible)
        runtimeSettings=self.eyeTrackerConfig['runtime_settings']
        self._setRuntimeSettings(runtimeSettings)
        # <<<<

        # >>>> Display / Calibration related information to use for config if possible
        EyeTracker.displaySettings = self.eyeTrackerConfig['display_settings']
        # <<<<

    def _setRuntimeSettings(self,runtimeSettings):
        #print " #### EyeTracker Runtime Settings #### "
        #print runtimeSettings
        #print ''
        eyelink=self._eyelink

        eyelink.setOfflineMode();

        for pkey,v in runtimeSettings.iteritems():
            if pkey == 'auto_calibration':
                if v is True or v == 1 or v == 'ON':
                    eyelink.enableAutoCalibration()
                elif v is False or v == 0 or v == 'OFF':
                    eyelink.disableAutoCalibration()
            
            elif pkey == 'default_calibration':
                if v in EyeTracker._VALID_CALIBRATION_TYPES:
                    eyelink.setCalibrationType(EyeTracker._VALID_CALIBRATION_TYPES[v])
            
            elif pkey == 'runtime_filtering':
                linkValue=0
                fileValue=0
                for ftype,fvalue in v.iteritems():
                    if ftype == 'ANY':
                        linkValue=fvalue
                        fileValue=fvalue
                    elif ftype == 'NET':
                        linkValue=fvalue
                    elif ftype == 'ANALOG':
                        linkValue=fvalue
                    elif ftype == 'FILE':
                        fileValue=fvalue
                eyelink.setHeuristicLinkAndFileFilter(linkValue,fileValue)
            
            elif pkey == 'sampling_rate':
                if v in EyeTracker._VALID_SAMPLING_RATES:
                    ioHub.print2err("WARNING:sample_rate setting from config file not yet supported by eyelink implementation")#eyelink.sendCommand('sample_rate = %d'%(v))
            
            else:
                print "WARNING: UNHANDLED EYETRACKER CONFIG SETTING:",pkey,v
                print ""

        #Gets the display surface and sends a mesage to EDF file;
        width,height=ioHub.devices.Display.getScreenResolution()
        bounds=dict(left=-width/2,top=height/2,right=width/2,bottom=-height/2)

        ioHub.print2err('*display bounds: ',bounds)
        eyelink.sendCommand("screen_pixel_coords %.0f %.0f %.0f %.0f" %(bounds['left'],bounds['top'],bounds['right'],bounds['bottom']))
        eyelink.sendMessage("DISPLAY_COORDS  %.0f %.0f %.0f %.0f" %(bounds['left'],bounds['top'],bounds['right'],bounds['bottom']))

        tracker_software_ver = 0
        eyelink_ver = eyelink.getTrackerVersion()
        if eyelink_ver == 3:
            tvstr = eyelink.getTrackerVersionString()
            vindex = tvstr.find("EYELINK CL")
            tracker_software_ver = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))

        # set EDF file contents
        eyelink.sendCommand("file_event_filter = LEFT, RIGHT, FIXATION, SACCADE, BLINK, MESSAGE, BUTTON, INPUT")

        if tracker_software_ver>=4:
            eyelink.sendCommand("file_sample_data = LEFT, RIGHT,GAZE, GAZERES, HREF , PUPIL , AREA ,STATUS, BUTTON, INPUT, HTARGET")
        else:
            eyelink.sendCommand("file_sample_data = LEFT, RIGHT, GAZE, GAZERES, HREF , PUPIL , AREA ,STATUS, BUTTON, INPUT")

        # set link data
        eyelink.sendCommand("link_event_filter = LEFT, RIGHT, FIXATION, FIXUPDATE, SACCADE , BLINK, BUTTON, MESSAGE, INPUT")
        eyelink.sendCommand("link_event_data = GAZE, GAZERES, HREF , FIXAVG , AREA, NOSTART")

        if tracker_software_ver>=4:
            eyelink.sendCommand("link_sample_data = LEFT, RIGHT, GAZE, GAZERES, HREF , PUPIL , AREA ,STATUS, BUTTON, INPUT , HTARGET")
        else:
            eyelink.sendCommand("link_sample_data = LEFT, RIGHT, GAZE, GAZERES, HREF , PUPIL , AREA ,STATUS, BUTTON, INPUT")

        eyelink.sendCommand("button_function 5 'accept_target_fixation'");

        pylink.flushGetkeyQueue()

        '''
        'track_eyes': 'BINOC',
        'default_native_data_file_name': 'default',
        'vog_settings': {'pupil_illumination': 'dark', 'pupil_center_algorithm': 'centroid', 'tracking_mode': 'pupil-cr'},
        'save_native_data_file_to': 'C:\\Users\\isolver\\Desktop\\Dropbox\\EMDQ and EMRA\\EMRA\\EMRT\\DEV\\EMRTDISTRO\\emrt_lib\\emrt\\examples\\experiment\\',
        '''

    
    def experimentStartDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the start of an experiment.
        """
        try:
            recording_filename=None
            if 'filename' in kwargs:
                recording_filename=kwargs['filename']
            elif len(args)>0:
                recording_filename=args[0]
            else:
                recording_filename=(self.eyeTrackerConfig['runtime_settings']['default_native_data_file_name'])+'.edf'

            if recording_filename:
                self.createRecordingFile(recording_filename)

            pylink.flushGetkeyQueue()

            return RTN_CODES.ET_OK
        except Exception, e:
            ioHub.printExceptionDetailsToStdErr()
 
    def blockStartDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the start of an experiment block.
        """
        # TODO: need to determine how  to handle this given ioHub handling of
        #       keyboard and mouse events. Need to factor in echo of keys
        #       between Host and Display systems.
        # TODO: When built in graphics are implemted, allow for calibration, camera
        #       setup at start of each block (i.e. add code to this method
        
        pylink.flushGetkeyQueue()
        return RTN_CODES.ET_OK

    def trialStartDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the start of an experiment trial.
        """
        
        pylink.flushGetkeyQueue()
        return RTN_CODES.ET_OK
         
    def trialEndDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the end of an experiment trial.
        """
        # Currently does nothing; which is current 'implemented' state.
        return RTN_CODES.ET_OK
         
    def blockEndDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the end of an experiment block.
        """
        # Currently does nothing; which is current 'implemented' state.
        return RTN_CODES.ET_OK

    def experimentEndDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the end of an experiment session.
        """
        if self._eyelink != None:
            # File transfer and cleanup!
            
            self._eyelink.setOfflineMode();                          
            #pylink.msecDelay(200);                 

            #Close the file and transfer it to Display PC
            if self._OPEN_EDF is not None:
                self.closeRecordingFile()
                self.getFile(self._OPEN_EDF)
            
            self.setConnectionState(False);
 
            return RTN_CODES.ET_OK
        return ('EYETRACKER_ERROR','EyeLink EyeTracker is not initialized.')
        
    def trackerTime(self):
        """
        Current eye tracker time (in msec for eyelink since host app was last started)
        """
        return (self._eyelink.trackerTime()-EyeTracker.DEVICE_START_TIME)*self.DEVICE_TIMEBASE_TO_SEC
   
    def setConnectionState(self,*args,**kwargs):
        """
        setConnectionState is used to connect ( setConnectionState(True) ) or disable ( setConnectionState(False) )
        the connection of the pyEyeTrackerInterface to the eyetracker.

        Args:

            enabled (bool): True = enable the connection, False = disable the connection.
            kwargs (dict): any eye tracker specific parameters that should be passed.
        """
        enabled=args[0]
        if enabled is True or enabled is False:
            if enabled is True:
                self._eyelink.connect();
                #pylink.msecDelay(100);
                # With the pyLink module, when the EyeLink() class is create, a connection is made.
                return True; 
            else:
                self._eyelink.setOfflineMode();                          
                #pylink.msecDelay(250);
                self._eyelink.reset()
                return False
        else:
            return ['EYETRACKER_ERROR','Invalid arguement type','setConnectionState','enabled',enabled,kwargs]
            
    def isConnected(self):
        """
        isConnected returns whether the pyEyeTrackerInterface is connected to the eye tracker (returns True) or not (returns False)
        """
        return self._eyelink.isConnected()
            
    def sendCommand(self, *args, **kwargs):
        """
        sendCommand sends a text command and text command value to the eye tracker. Depending on the command and on the eye trackers
        implementation, when a command is send, the eye tracker may or n=may not response indicating the status of the command. If the
        command is not going to return a response from the eye tracker, the method will return RTN_CODES.ET_RESULT_UNKNOWN.
        Please see the specific eye tracker implementation you are working with for a list of supported command's and value's.

        Args:

           command (str): string command to send to the eye tracker. See the specific eye tracker documentation for pyEyeTracker for a list of valid commands.
           value (str): the string form of the value of the command to send.

        kwargs:
           wait (bool or callable) *NOT CURRENTLY SUPPORTED; FUNCTIONS AS ALWAYS == TRUE*: if bool, True = do not return from function until result of command if known (if it can be known); False = return immediately after sending the command, ignoring any possible return value. If wait is a callable, then wait fould be a reference to the callback function you want called when the return value is available. If no return value is possible for the command, wait is ignorded and RTN_CODES.ET_RESULT_UNKNOWN is returned immediately..

        Return: the result of the command call, or one of the ReturnCodes Constants ( ReturnCodes.ET_OK, ReturnCodes.ET_RESULT_UNKNOWN, ReturnCodes.ET_NOT_IMPLEMENTED )
        """
        if len(args)>=2:
            command=args[0]
            value=args[1]
        else:
            return ('EYETRACKER_ERROR','EyeTracker.sendCommand','requires args of length >=2, command==args[0],value==args[1]')
        wait=False
        if wait in kwargs:
            wait=kwargs['wait']
        
        r=None
        if command in EyeTracker._COMMAND_TO_FUNCTION:
            r=EyeTracker._COMMAND_TO_FUNCTION[command](*args,**kwargs)    
        else:
            r=self._eyelink.sendCommand(str(command)+" = "+str(value))
        if wait is True and r is None:
            ioHub.print2err("EyeLinkEyeTracker.sendCommand wait param not implemented")
            return RTN_CODES.ET_RESULT_UNKNOWN
        if r == 0: # means command was send, but did not wait / try
                   # to get response from tracker with status of command
            return RTN_CODES.ET_RESULT_UNKNOWN
        return r
        
    def sendMessage(self,*args,**kwargs):
        """
        sendMessage sends a text message to the eye tracker. Depending on the eye trackers implementation, when a message is send,
        the eye tracker may or may not response indicating the message was received. If the
        message is not going to receive a response from the eye tracker, the method will return RTN_CODES.ET_RESULT_UNKNOWN.
        Messages are generally used to send general text information you want saved with the eye data file  but more importantly
        are often used to syncronize stimulus changes in the experiment with the eye data stream. This means that the sendMessage
        implementation needs to perform in real-time, with a delay of <1 msec from when a message is sent to when it is logged in
        the eye tracker data file, for it to be accurate in this regard. If this standard can not be met, the expected delay and
        message precision (variability) should be provided in the eye tracker's implementation notes for the pyEyeTRacker interface.

        Args:
           message (str): string command to send to the eye tracker. The default maximum length of a message string is 128 characters.

        kwargs:
           time_offset (int): number of int msec that the time stamp of the message should be offset by. This can be used so that a message can be sent for a display change **BEFORE** or **AFTER** the aftual flip occurred (usually before), by sending the message, say 4 msec prior to when you know the next trace will occur, entering -4 into the offset field of the message, and then send it and calling flip() 4 msec before the retrace to ensure that the message time stampe and flip are both sent and schuled in advance. (4 msec is quite large buffer even on windows these days with morern hardware BTW)
        """
        message=args[0]
        
        time_offset=0
        if time_offset in kwargs:
            time_offset=kwargs['time_offset']
            
            r = self._eyelink.sendMessage("\t%d\t%s"%(time_offset,message))
        else:
            r=self._eyelink.sendMessage(message)

        if r == 0:
            return RTN_CODES.ET_RESULT_UNKNOWN
        return r
                
    def createRecordingFile(self, *args,**kwargs):
        """
        createRecordingFile instructs the eye tracker to open a new file on the eye tracker computer to save data collected to
        during the recording. If recording is started and stopped multiple times while a single recording file is open, each
        start/stop recording pair will be represented within the single file. A recording file is closed by calling
        closeRecordingFile(). Normally you would open a rtecoring file at the start of an experimental session and close it
        at the end of the experiment; starting and stopping recording of eye data between trials of the experiment.

        kwargs:
           fileName (str): Name of the recording file to save on the eye tracker. This does *not* include the path to the file. Some eye trackers have limitations to the length of their file name, so please refer to the specific implemtations documenation for any caviates.
           path (str): This optional parameter can be used to specify the path to the recording file that should be saved. The path must already exist. If this paramemter is not specified, then the defualt file location is used.
        """
        fileName=None
        if fileName in kwargs:
            fileName= kwargs['fileName']
        else:
            return ('EYETRACKER_ERROR','EyeTracker.createRecordingFile','fileName must be provided as a kwarg')
        
        pre=None
        post=None
        splitName=fileName.strip().split(".")
        if len(splitName) > 1:
            pre=splitName[:-1]
            post=splitName[-1]
        else:
            pre=splitName[0]
            post='edf'
        print "PRE : POST ",pre,post
        fileName='%s.%s'%(pre,post)
        
        if len(pre)>7 or len(post)>3:
            post='edf'
            if len(pre)>7:
                pre=pre[:7]
            fileName='%s.%s'%(pre,post)
            print "EyeLink.createRecordingFile filename must be ion 7.3 format. Sorry! Changing name to ",fileName
        
        self._eyelink._eyelink.openDataFile(fileName)
        self._eyelink._OPEN_EDF=fileName
        return RTN_CODES.ET_OK
        
    def closeRecordingFile(self,*args,**kwargs):
        """
        closeRecordingFile is used to close the currently open file that is being used to save data from the eye track to the eye tracker computer.
        Once a file has been closed, getFile(localFileName,fileToTransfer) can be used to transfer the file from the eye tracker computer to the
        experiment computer at the end of the experiment session.

        kwargs:
           fileName (str): Name of the recording file to save on the eye tracker. This does *not* include the path to the file. Some eye trackers have limitations to the length of their file name, so please refer to the specific implemtations documenation for any caviates.
           path (str): This optional parameter can be used to specify the path to the recording file that should be saved. The path must already exist. If this paramemter is not specified, then the defualt file location is used.
        """
        self._eyelink.closeDataFile()
        return RTN_CODES.ET_OK

    
    def getFile(self,*args,**kwargs):
        """
        getFile is used to transfer the file from the eye tracker computer to the experiment computer at the end of the experiment session.

        kwargs:
           localFileName (str): Name of the recording file to experiment computer.
           fileToTransfer (str): Name of the recording file to transfer from the eye tracker.
        """
        
        fileToTransfer=None
        if fileToTransfer in kwargs:
            fileToTransfer=kwargs['fileToTransfer']
        
        localFileName=None
        if localFileName in kwargs:
            localFileName=kwargs['localFileName']
        
        if fileToTransfer is None and self._OPEN_EDF:
            fileToTransfer=self._OPEN_EDF
            EyeTracker._OPEN_EDF=None
        
        if localFileName is None:
            localFileName=fileToTransfer
        
        self._eyelink.receiveDataFile(fileToTransfer,localFileName)
        return RTN_CODES.ET_OK

    
    def runSetupProcedure(self, *args ,**kwargs):
        """
        runSetupProcedure passes the graphics environment over to the eye tracker interface so that it can perform such things
        as camera setup, calibration, etc. This is a blocking call that will not return until the setup procedure is done; at which time
        the graphics environment can be taken back over by psychopy.  See the EyeTrackerSetupGraphics class for more information.

        The graphicsContext arguement should likely be the psychopy full screen window instance that has been created
        for the experiment.
        """
        try:
            import pyglet




            screen_resolution=ioHub.devices.display.Display.getScreenResolution()
            screen_index=self.displaySettings['display_index']
            import psychopy
            win=psychopy.visual.Window(screen_resolution, monitor="testMonitor", units='pix', fullscr=True, allowGUI=False,screen=screen_index)

            genv=EyeLinkCoreGraphicsPyglet(screen_resolution[0],screen_resolution[1],win.winHandle)

            pylink.openGraphicsEx(genv)

            genv.setup_event_handlers()
            self._eyelink.doTrackerSetup()
            genv.release_event_handlers()
        except:
            ioHub.print2err("Error during runSetupProcedure")
            ioHub.printExceptionDetailsToStdErr()
        return True
        #graphicsContext=None
        #if len(args)>0:
        #    graphicsContext=args[0]
        #else:
        #    return ['EYETRACKER_ERROR','runSetupProcedure requires graphicsContext==args[0]']
            
        #if self._setupGraphics is None:
        #    self._setupGraphics=EyeTrackerSetupGraphics(graphicsContext=graphicsContext,**kwargs)
        #return self._setupGraphics.run()

    def stopSetupProcedure(self):
        """
        stopSetupProcedure allows a user to cancel the ongoing eye tracker setup procedure. Given runSetupProcedure is a blocking
        call, the only way this will happen is if the user has another thread that makes the call, perhaps a watch dog type thread.
        So in practice, calling this method is not very likely I do not think.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
        #result=None
        #if self._setupGraphics is not None:
        #    result = self._setupGraphics.stop()
        #return result
                
    def setRecordingState(self,*args,**kwargs):
        """
        setRecordingState is used to start or stop the recording of data from the eye tracking device. Use sendCommand() set the necessary information
        for your eye tracker to enable what data you would like saved, send over to the experiment computer during recording, etc.

        args:
           recording (bool): if True, the eye tracker should start recordng data.; false = stop recording data.
        """
        if len(args)==0:
            return ('EYETRACKER_ERROR','EyeTracker.setRecordingState','recording(bool) must be provided as a args[0]')
        enable=args[0]
        
        if enable is True:
            # TODO: Recording to file and sending over link should be based on settings of device
            error = self._eyelink.startRecording(1,1,1,1)
            if error:
                print "Error starting eyelink recording", error
                return ('EYETRACKER_ERROR','EyeTracker.setRecordingState','Could not start Recording',error)

            if not self._eyelink.waitForBlockStart(100, 1, 0):
                print "ERROR: No link samples received!";
                return ('EYETRACKER_ERROR','EyeTracker.setRecordingState','Error in waitForBlockStart')
            else:
                EyeTracker.currentSampleRate=self._eyelink.getSampleRate()
                return RTN_CODES.ET_OK;
        
        elif enable is False:
            self._eyelink.stopRecording()
            return RTN_CODES.ET_OK;

    def isRecordingEnabled(self,*args,**kwargs):
       """
       isRecordingEnabled returns the recording state from the eye tracking device.
       True == the device is recording data
       False == Recording is not occurring
       """
       return self._eyelink.isRecording()  

    def getEyesToTrack(self,*args,**kwargs):
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def setEyesToTrack(self,*args,**kwargs):
        if len(args)==0:
            return RTN_CODES.ET_ERROR
        eyes=args[0]
        return RTN_CODES.ET_NOT_IMPLEMENTED


    def getSamplingRate(self,*args,**kwargs):
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def setSamplingRate(self,*args,**kwargs):
        if len(args)==0:
            return RTN_CODES.ET_ERROR
        srate=args[0]
        return RTN_CODES.ET_NOT_IMPLEMENTED


    def getDataFilterLevel(self,*args,**kwargs):
        """
        getDataFilterLevel returns the numerical code the current device side filter level
        set for the specific data_stream.

        Currently, filter levels 0 (meaning no filter) through
        5 (highest filter level) can be specified via the pyEyeTrackerInterface.
        They are defined in ET_FILTERS.

        data_streams specifies what output the filter is being applied to by the device. The
        currently defined output streams are defined in DATA_STREAMS and are
        ALL,FILE,NET,SERIAL,ANALOG. ALL indicates that the filter level for all available output streams should be
        provided, in which case a dictionary of stream keys, filter level values should be returned.

        If an ET device supports setting one filter level for all available output streams, it can simply return
        (ALL, filter_level).

        If a stream type that is not supported by the device for individual filtering is specified,
        an error should be generated.
        """
        data_stream=DATA_STREAMS.ALL
        if 'data_stream' in kwargs:
            data_stream=kwargs['data_stream']
        elif len(args)>0:
            data_stream=args[0]
        
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def setDataFilterLevel(self,*args,**kwargs):
        """
        setDataFilteringLevel sets the code for current ET device side filter level
        for the specific data_stream.

        Currently, filter levels OFF (meaning no filter) through
        LEVEL_5 (highest filter level) can be specified via the pyEyeTrackerInterface.
        They are defined in DATA_FILTER Enum.

        data_streams specifies what output the filter is being applied to by the device. The
        currently defined output streams are defined in DATA_STREAMS, and are
        ALL,FILE,NET,SERIAL,ANALOG. ALL indicates that the filter level should be applied to all
        available output streams,

        If an ET device supports setting one filter level for all available output streams,
        then setting using filter_level only should be done.

        If a stream type that is not supported by the device for individual filtering is specified,
        an error should be generated.

        For the SR Research EyeLink implementation, please note the following constraints and
        'oddities' that will be improved on in future versions:

        1) Filter Levels OFF to LEVEL_2 are supported. OFF maps to Filter OFF.
           LEVEL_1 maps to FILTER_NORMAL, and LEVEL_2 maps top FILTER_HIGH in the EyeLink system.

        2) Filter streams FILE, NET, and ANALOG are supported.

        3) ** If you set the filter level for NET it also sets the level for ANALOG, and visa versa.

        4) ** If you set the filter level for FILE, it sets the level for NET & ANALOG to OFF

        5) ** Given 4), it is suggested you either set the filter level for ALL, or you 'first' set the
              filter level for FILE, and then set the filter level for NET or ANALOG.
        """
        if len(args)==0:
            return ['EYETRACKER_ERROR',"EyeTracker.setDataFilterLevel", "level = args[0], but no args provided"]
        level=args[0]
        supportedLevels=(DATA_FILTER.OFF,DATA_FILTER.LEVEL_1,DATA_FILTER.LEVEL_2)
        if level not in supportedLevels:
            return ['EYETRACKER_ERROR',"EyeTracker.setDataFilterLevel", "Invalid level value provided; must be one of (DATA_FILTER.OFF,DATA_FILTER.LEVEL_1,DATA_FILTER.LEVEL_2)"]
        
        data_stream=DATA_STREAMS.ALL
        if data_stream in kwargs:
            data_stream=kwargs['data_stream']
        supportedFilterStreams=(DATA_STREAMS.ALL,DATA_STREAMS.NET,DATA_STREAMS.ANALOG)
        if data_stream not in supportedFilterStreams:
            return ['EYETRACKER_ERROR',"EyeTracker.setDataFilterLevel", "Invalid data_stream value provided; must be one of (DATA_STREAMS.ALL,DATA_STREAMS.NET,DATA_STREAMS.ANALOG)"]
        
        lindex = supportedLevels.index(level)
        
        if data_stream == DATA_STREAMS.ALL:
            self._eyelink.setHeuristicLinkAndFileFilter(lindex,lindex)
        elif data_stream == DATA_STREAMS.NET or data_stream == DATA_STREAMS.ANALOG:
            self._eyelink.setHeuristicLinkAndFileFilter(lindex)
        elif data_stream == DATA_STREAMS.FILE:
            self._eyelink.setHeuristicLinkAndFileFilter(0,lindex)
        return RTN_CODES.ET_OK

    def getLatestSample(self, *args, **kwargs):
        """
        Returns the latest sample retieved from the eye tracker device.
        """
        return self._latestSample

    def getLatestGazePosition(self, *args, **kwargs):
        """
        Returns the latest eye Gaze Position retieved from the eye tracker device.
        """
        return self._latestGazePosition

    def drawToGazeOverlayScreen(self,*args,**kwargs):
        """
        drawToGazeOverlayScreen provides a generic interface for ET devices that support
        having graphics drawn to the Host / Control computer gaze overlay area, or other similar
        graphics area functionality.

        The method should return the appropriate return code if successful or if the command failed,
        or if it is unsupported.

        There is no set list of values for any of the arguements for this command, so please refer to the
        ET imlpementation notes for your device for details. Hypothetical examples may be:
        """
        drawingcommand=None
        if len(args)==0:
            return ('EYETRACKER_ERROR','drawToGazeOverlayScreen','args must have length > 0: drawingcommand = args[0]')
        else:
            drawingcommand=args[0]
            
        if drawingcommand is None:
            return ('EYETRACKER_ERROR','drawToGazeOverlayScreen','drawingcommand can not be None.')
        elif drawingcommand=='TEXT':
            if 'value' in kwargs and 'position' in kwargs:
                text=kwargs['value']
                position=kwargs['position']
                return self._eyelink.drawText(str(text),position) # value = text to display. position = (-1,-1), or position in gaze orders to draw text.
            return ('EYETRACKER_ERROR','drawToGazeOverlayScreen','command: TEXT','kwargs "value" and "position" are required for this command.')
        elif drawingcommand=='CLEAR':
            if 'value' in kwargs:
                pcolor=int(kwargs['value'])
                if pcolor >=0 and pcolor <= 15:
                    return self._eyelink.clearScreen(pcolor) # value must be between 0 - 15 and is the color from the EyeLink Host PC pallette to use.
            return ('EYETRACKER_ERROR','drawToGazeOverlayScreen','command: CLEAR','kwargs "value" is required for this command')
        elif drawingcommand=='LINE': # value must be between 0 - 15 and is the color from the EyeLink Host PC pallette to use. position must be [(x1,y1),(x2,y2)]
            if 'value' in kwargs and 'position' in kwargs:
                pcolor=int(kwargs['value'])
                position = kwargs['position']
                if pcolor >=0 and pcolor <= 15 and len(position)==2:
                    return self._eyelink.drawLine(position[0], position[1],pcolor)
            return ('EYETRACKER_ERROR','drawToGazeOverlayScreen','command: LINE','kwargs "value" and "position" are required for this command')
        elif drawingcommand=='BOX':# value must be between 0 - 15 and is the color from the EyeLink Host PC pallette to use.  position must be (x,y,width,height) 
            if 'value' in kwargs and 'position' in kwargs:
                pcolor=int(kwargs['value'])
                position = kwargs['position']
                if pcolor >=0 and pcolor <= 15 and len(position)==4:
                    return self._eyelink.drawBox(position[0], position[1],position[2], position[3], pcolor)
            return ('EYETRACKER_ERROR','drawToGazeOverlayScreen','command: BOX','kwargs "value" and "position" are required for this command')
        elif drawingcommand=='CROSS': # Draws a small "+" to mark a target point.  # value must be between 0 - 15 and is the color from the EyeLink Host PC pallette to use.  position must be (x,y)
            if 'value' in kwargs and 'position' in kwargs:
                pcolor=int(kwargs['value'])
                position = kwargs['position']
                if pcolor >=0 and pcolor <= 15 and len(position)==2:
                    return self._eyelink.drawBox(position[0], position[1],pcolor)
            return ('EYETRACKER_ERROR','drawToGazeOverlayScreen','command: CROSS','kwargs "value" and "position" are required for this command')
        elif drawingcommand=='FILLEDBOX':
            if 'value' in kwargs and 'position' in kwargs:
                pcolor=int(kwargs['value'])
                position = kwargs['position']
                if pcolor >=0 and pcolor <= 15 and len(position)==4:
                    return self._eyelink.drawBox(position[0], position[1],position[2], position[3], pcolor)
            return ('EYETRACKER_ERROR','drawToGazeOverlayScreen','command: FILLEDBOX','kwargs "value" and "position" are required for this command')
        
        return ('EYETRACKER_ERROR','drawToGazeOverlayScreen','command: %s'%drawingcommand,'Unknown drawing command.')

    def getDigitalPortState(self, *args, **kwargs):
        """
        getDigitalPortState returns the current value of the specified digital port on the ET computer.
        This can be used to read the parallel port or idigial lines on the ET host PC if the ET has such functionality.

        args:
            port = the address to read from on the host PC. Consult your ET device documentation for appropriate values.
        """
        if len(args)==0:
            return ('EYETRACKER_ERROR','getDigitalPortState','port=args[0] is required.')
        port = int(args[0])    
        return self._eyelink.readIOPort(port)
         
    def setDigitalPortState(self, *args, **kwargs):
        """
        setDigitalPortState sets the value of the specified digital port on the ET computer.
        This can be used to write to the parallel port or idigial lines on the ET Host / Operator PC if the ET
        has such functionality.

        args:
            port = the address to write to on the host PC. Consult your ET device documentation for appropriate values.
            value = value to assign to port
        """
        if len(args)<2:
            return ('EYETRACKER_ERROR','setDigitalPortState','port=args[0] and value=args[1] are required.')        
        port = int(args[0])    
        value = int(args[1])
        return self._eyelink.writeIOPort(port, value)
    
    def _poll(self):
        """
        For the EyeLink systems, a polling model is used to check for new events and samples.
        If your eye tracker supports a more efficient event based call-back approach, this should be
        used instead of registering a timer with the device.
        """
        try:
            pollStartLocalTime=Computer.currentSec()
            eyelink=self._eyelink
            pollStartHostTime = eyelink.trackerTimeUsec()*0.000001


            confidenceInterval=EyeTracker.currentSampleRate*0.0000005

            #get native events queued up
            while 1:
                currentTime=Computer.currentSec()

                ne = eyelink.getNextData()

                if ne == 0 or ne is None:
                    break # no more events / samples to process

                ne=eyelink.getFloatData()

                if ne is None:
                    break

                event_timestamp=ne.getTime()*EyeTracker.DEVICE_TIMEBASE_TO_SEC
                event_delay=pollStartHostTime-(event_timestamp)

                hub_timestamp=currentTime-event_delay

                if isinstance(ne,pylink.Sample):
                    # now convert from native format to pyEyeTracker  common format

                    ppd=ne.getPPD()

                    # hubtime calculation needs to be finished / improved.
                    # - offset should be an integration of 1% to handle noise / spikes in
                    #   calulation
                    # - need to handle drift between clocks


                    if ne.isBinocular():
                        # binocular sample
                        event_type=ioHub.devices.EventConstants.EVENT_TYPES['BINOC_EYE_SAMPLE']
                        myeye=EventConstants.BINOCULAR
                        leftData=ne.getLeftEye()
                        rightData=ne.getRightEye()

                        leftPupilSize=leftData.getPupilSize()
                        leftRawPupil=leftData.getRawPupil()
                        leftHref=leftData.getHREF()
                        leftGaze=leftData.getGaze()

                        rightPupilSize=rightData.getPupilSize()
                        rightRawPupil=rightData.getRawPupil()
                        rightHref=rightData.getHREF()
                        rightGaze=rightData.getGaze()

                        # TO DO: EyeLink pyLink does not expose sample velocity fields. Patch and fix.
                        vel_x=-1.0
                        vel_y=-1.0
                        vel_xy=-1.0


                        #binocSample=(experiment_id=0,session_id=0,event_id=Computer.getNextEventID(),
                        #            event_type=etype,device_instance_code=self.eyeTrackerConfig['instance_code'],
                        #            device_time=event_timestamp, logged_time=currentTime, hub_time=hub_timestamp,
                        #            confidence_interval=confidenceInterval, delay=event_delay,
                        #            eye=myeye,left_gaze_x=leftGaze[0],left_gaze_y=leftGaze[1],left_gaze_z=-1.0,
                        #            left_eye_cam_x=-1,left_eye_cam_y=-1,left_eye_cam_z=-1.0,
                        #            left_angle_x=leftHref[0],left_angle_y=leftHref[1],left_raw_x=leftRawPupil[0],left_raw_y=leftRawPupil[1],
                        #            left_pupil_measure1=leftPupilSize,left_pupil_measure2=-1, left_ppd_x=ppd[0], left_ppd_y=ppd[1],
                        #            left_velocity_x=vel_x,left_velocity_y=vel_y,left_velocity_xy=vel_xy,
                        #            right_gaze_x=rightGaze[0],right_gaze_y=rightGaze[1],right_gaze_z=-1.0,
                        #            right_eye_cam_x=-1,right_eye_cam_y=-1,right_eye_cam_z=-1.0,
                        #            right_angle_x=rightHref[0],right_angle_y=rightHref[1],right_raw_x=rightRawPupil[0],right_raw_y=rightRawPupil[1],
                        #            right_pupil_measure1=rightPupilSize,right_pupil_measure2=-1, right_ppd_x=ppd[0], right_ppd_y=ppd[1],
                        #            right_velocity_x=vel_x,right_velocity_y=vel_y,right_velocity_xy=vel_xy,status=0)


                        binocSample=[
                                     0,
                                     0,
                                     Computer.getNextEventID(),
                                     event_type,
                                     self.eyeTrackerConfig['instance_code'],
                                     event_timestamp,
                                     currentTime,
                                     hub_timestamp,
                                     confidenceInterval,
                                     event_delay,
                                     myeye,
                                     leftGaze[0],
                                     leftGaze[1],
                                     -1.0,
                                     -1.0,
                                     -1.0,
                                     -1.0,
                                     leftHref[0],
                                     leftHref[1],
                                     leftRawPupil[0],
                                     leftRawPupil[1],
                                     leftPupilSize,
                                     EventConstants.AREA,
                                     -1,
                                     EventConstants.NOT_SUPPORTED_FIELD,
                                     ppd[0],
                                     ppd[1],
                                     vel_x,
                                     vel_y,
                                     vel_xy,
                                     rightGaze[0],
                                     rightGaze[1],
                                     -1.0,
                                     -1.0,
                                     -1.0,
                                     -1.0,
                                     rightHref[0],
                                     rightHref[1],
                                     rightRawPupil[0],
                                     rightRawPupil[1],
                                     rightPupilSize,
                                     EventConstants.AREA,
                                     -1,
                                     EventConstants.NOT_SUPPORTED_FIELD,
                                     ppd[0],
                                     ppd[1],
                                     vel_x,
                                     vel_y,
                                     vel_xy,
                                     0
                                     ]
                        #EyeTracker._eventArrayLengths['BINOC_EYE_SAMPLE']=len(binocSample)
                        EyeTracker._latestSample=binocSample
                        EyeTracker._latestGazePosition=(leftGaze[0]+rightGaze[0])/2.0,(leftGaze[1]+rightGaze[1])/2.0
                        self._addNativeEventToBuffer(binocSample)

                    else:
                        # monocular sample
                        event_type=ioHub.devices.EventConstants.EVENT_TYPES['EYE_SAMPLE']
                        leftEye=ne.isLeftSample()
                        eyeData=None
                        if leftEye == 1:
                            eyeData=ne.getLeftEye()
                            myeye=EventConstants.LEFT
                        else:
                            eyeData=ne.getRightEye()
                            myeye=EventConstants.RIGHT

                        pupilSize=eyeData.getPupilSize()
                        rawPupil=eyeData.getRawPupil()
                        href=eyeData.getHREF()
                        gaze=eyeData.getGaze()

                        # TO DO: EyeLink pyLink does not expose sample velocity fields. Patch and fix.
                        vel_x=-1.0
                        vel_y=-1.0
                        vel_xy=-1.0


                        #monoSample=(experiment_id=0,session_id=0,event_id=Computer.getNextEventID(),
                        #            event_type=etype,device_instance_code=self.eyeTrackerConfig['instance_code'],
                        #            device_time=event_timestamp, logged_time=currentTime, hub_time=hub_timestamp,
                        #            confidence_interval=confidenceInterval, delay=event_delay,
                        #            eye=myeye,gaze_x=gaze[0],gaze_y=gaze[1],gaze_z=-1.0,
                        #            eye_cam_x=-1,eye_cam_y=-1,eye_cam_z=-1.0,
                        #            angle_x=href[0],angle_y=href[1],raw_x=rawPupil[0],raw_y=rawPupil[1],
                        #            pupil_measure1=pupilSize,pupil_measure2=-1, ppd_x=ppd[0], ppd_y=ppd[1],
                        #            velocity_x=vel_x,velocity_y=vel_y,velocity_xy=vel_xy,status=0)

                        monoSample=[0,
                                    0,
                                    Computer.getNextEventID(),
                                    event_type,
                                    self.eyeTrackerConfig['instance_code'],
                                    event_timestamp,
                                    currentTime,
                                    hub_timestamp,
                                    confidenceInterval,
                                    event_delay,
                                    myeye,
                                    gaze[0],
                                    gaze[1],
                                    -1.0,
                                    -1.0,
                                    -1.0,
                                    -1.0,
                                    href[0],
                                    href[1],
                                    rawPupil[0],
                                    rawPupil[1],
                                    pupilSize,
                                    EventConstants.AREA,
                                    -1,
                                    EventConstants.NOT_SUPPORTED_FIELD,
                                    ppd[0],
                                    ppd[1],
                                    vel_x,
                                    vel_y,
                                    vel_xy,
                                    0
                                    ]
                       #EyeTracker._eventArrayLengths['MONOC_EYE_SAMPLE']=len(monoSample)
                        EyeTracker._latestGazePosition=gaze
                        EyeTracker._latestSample=monoSample
                        self._addNativeEventToBuffer(monoSample)

                elif isinstance(ne,pylink.EndFixationEvent):
                    etype=ioHub.devices.EventConstants.EVENT_TYPES['FIXATION_END']

                    estatus = ne.getStatus()

                    which_eye=ne.getEye()
                    if which_eye:
                        which_eye=EventConstants.RIGHT
                    else:
                        which_eye=EventConstants.LEFT

                    start_event_time= ne.getStartTime()*EyeTracker.DEVICE_TIMEBASE_TO_SEC
                    end_event_time = ne.getEndTime()*EyeTracker.DEVICE_TIMEBASE_TO_SEC
                    event_duration = end_event_time-start_event_time

                    s_gaze=ne.getStartGaze()
                    s_href=ne.getStartHREF()
                    s_vel=ne.getStartVelocity()
                    s_pupilsize=ne.getStartPupilSize()
                    s_ppd=ne.getStartPPD()

                    e_gaze=ne.getEndGaze()
                    e_href=ne.getEndHREF()
                    e_pupilsize=ne.getEndPupilSize()
                    e_vel=ne.getEndVelocity()
                    e_ppd=ne.getEndPPD()

                    a_gaze=ne.getAverageGaze()
                    a_href=ne.getAverageHREF()
                    a_pupilsize=ne.getAveragePupilSize()
                    a_vel=ne.getAverageVelocity()

                    peak_vel=ne.getPeakVelocity()

                    #fee=(experiment_id=0,session_id=0,event_id=Computer.getNextEventID(),
                    #                    event_type=etype,device_instance_code=self.eyeTrackerConfig['instance_code'],
                    #                    device_time=end_event_time, logged_time=currentTime, hub_time=hub_timestamp,
                    #                    confidence_interval=confidenceInterval, delay=event_delay, eye=which_eye,
                    #                    duration=event_duration,start_gaze_x=s_gaze[0],start_gaze_y=s_gaze[1],start_gaze_z=-1.0,
                    #                    start_angle_x=s_href[0], start_angle_y=s_href[1], start_raw_x=-1.0, start_raw_y=-1.0,
                    #                    start_pupil_measure1=s_pupilsize, start_pupil_measure2=-1.0, start_ppd_x=s_ppd[0], start_ppd_y=s_ppd[1],
                    #                    start_velocity_x = -1, start_velocity_y = -1, start_velocity_xy = s_vel,
                    #                    end_gaze_x = e_gaze[0], end_gaze_y = e_gaze[1], end_gaze_z = -1.0,
                    #                    end_angle_x= e_href[0], end_angle_y = e_href[1], end_raw_x = -1, end_raw_y = -1,
                    #                    end_pupil_measure1 = e_pupilsize, end_pupil_measure2 = -1, end_ppd_x = e_ppd[0], end_ppd_y= e_ppd[1],
                    #                    end_velocity_x = -1, end_velocity_y= -1, end_velocity_xy = e_vel,
                    #                    average_gaze_x=a_gaze[0],average_gaze_y=a_gaze[1],average_gaze_z=-1.0,
                    #                    average_angle_x=a_href[0],average_angle_y=a_href[1],average_raw_x=-1.0,average_raw_y=-1.0,
                    #                    average_pupil_measure1=a_pupilsize,average_pupil_measure2=-1.0,average_ppd_x=-1.0,average_ppd_y=-1.0,
                    #                    average_velocity_x=-1.0,average_velocity_y=-1.0,average_velocity_xy=a_vel,
                    #                    peak_velocity_x=-1.0, peak_velocity_y=-1.0, peak_velocity_xy=peak_vel,status=estatus)

                    fee=[0,
                         0,
                         Computer.getNextEventID(),
                         etype,
                         self.eyeTrackerConfig['instance_code'],
                        end_event_time,
                        currentTime,
                        hub_timestamp,
                        confidenceInterval,
                        event_delay,
                        which_eye,
                        event_duration,
                        s_gaze[0],
                        s_gaze[1],
                        -1.0,
                        s_href[0],
                        s_href[1],
                        -1.0,
                        -1.0,
                        s_pupilsize,
                        EventConstants.AREA,
                        -1,
                        EventConstants.NOT_SUPPORTED_FIELD,
                        s_ppd[0],
                        s_ppd[1],
                        -1,
                        -1,
                        s_vel,
                        e_gaze[0],
                        e_gaze[1],
                        -1.0,
                        e_href[0],
                        e_href[1],
                        -1,
                        -1,
                        e_pupilsize,
                        EventConstants.AREA,
                        -1,
                        EventConstants.NOT_SUPPORTED_FIELD,
                        e_ppd[0],
                        e_ppd[1],
                        -1,
                        -1,
                        e_vel,
                        a_gaze[0],
                        a_gaze[1],
                        -1.0,
                        a_href[0],
                        a_href[1],
                        -1.0,
                        -1.0,
                        a_pupilsize,
                        EventConstants.AREA,
                        -1,
                        EventConstants.NOT_SUPPORTED_FIELD,
                        -1.0,
                        -1.0,
                        -1.0,
                        -1.0,
                        a_vel,
                        -1.0,
                        -1.0,
                        peak_vel,
                        estatus
                        ]
                    #EyeTracker._eventArrayLengths['FIXATION_END']=len(fee)
                    self._addNativeEventToBuffer(fee)

                elif isinstance(ne,pylink.EndSaccadeEvent):
                    etype=ioHub.devices.EventConstants.EVENT_TYPES['SACCADE_END']

                    estatus = ne.getStatus()

                    which_eye=ne.getEye()
                    if which_eye:
                        which_eye=EventConstants.RIGHT
                    else:
                        which_eye=EventConstants.LEFT

                    start_event_time= ne.getStartTime()*EyeTracker.DEVICE_TIMEBASE_TO_SEC
                    end_event_time = ne.getEndTime()*EyeTracker.DEVICE_TIMEBASE_TO_SEC
                    event_duration = end_event_time-start_event_time

                    e_amp = ne.getAmplitude()
                    e_angle = ne.getAngle()

                    s_gaze=ne.getStartGaze()
                    s_href=ne.getStartHREF()
                    s_vel=ne.getStartVelocity()
                    s_pupilsize=-1.0
                    s_ppd=ne.getStartPPD()

                    e_gaze=ne.getEndGaze()
                    e_href=ne.getEndHREF()
                    e_pupilsize=-1.0
                    e_vel=ne.getEndVelocity()
                    e_ppd=ne.getEndPPD()

                    a_vel=ne.getAverageVelocity()
                    peak_vel=ne.getPeakVelocity()

                    see=[0,
                         0,
                         Computer.getNextEventID(),
                        etype,
                        self.eyeTrackerConfig['instance_code'],
                        end_event_time,
                        currentTime,
                        hub_timestamp,
                        confidenceInterval,
                        event_delay,
                        which_eye,
                        event_duration,
                        e_amp[0],
                        e_amp[1],
                        e_angle,
                        s_gaze[0],
                        s_gaze[1],
                        -1.0,
                        s_href[0],
                        s_href[1],
                        -1.0,
                        -1.0,
                        s_pupilsize,
                        EventConstants.AREA,
                        -1,
                        EventConstants.NOT_SUPPORTED_FIELD,
                        s_ppd[0],
                        s_ppd[1],
                        -1,
                        -1,
                        s_vel,
                        e_gaze[0],
                        e_gaze[1],
                        -1.0,
                        e_href[0],
                        e_href[1],
                        -1,
                        -1,
                        e_pupilsize,
                        EventConstants.AREA,
                        -1,
                        EventConstants.NOT_SUPPORTED_FIELD,
                        e_ppd[0],
                        e_ppd[1],
                        -1,
                        -1,
                        e_vel,
                        -1.0,
                        -1.0,
                        a_vel,
                        -1.0,
                        -1.0,
                        peak_vel,
                        estatus
                        ]
                    #EyeTracker._eventArrayLengths['SACCADE_END']=len(see)
                    self._addNativeEventToBuffer(see)
                elif isinstance(ne,pylink.EndBlinkEvent):
                    etype=ioHub.devices.EventConstants.EVENT_TYPES['BLINK_END']

                    estatus = ne.getStatus()

                    which_eye=ne.getEye()
                    if which_eye:
                        which_eye=EventConstants.RIGHT
                    else:
                        which_eye=EventConstants.LEFT

                    start_event_time= ne.getStartTime()*EyeTracker.DEVICE_TIMEBASE_TO_SEC
                    end_event_time = ne.getEndTime()*EyeTracker.DEVICE_TIMEBASE_TO_SEC
                    event_duration = end_event_time-start_event_time

                    bee=[
                        0,
                        0,
                        Computer.getNextEventID(),
                        etype,
                        self.eyeTrackerConfig['instance_code'],
                        end_event_time,
                        currentTime,
                        hub_timestamp,
                        confidenceInterval,
                        event_delay,
                        which_eye,
                        event_duration,
                        estatus
                        ]
                    #EyeTracker._eventArrayLengths['BLINK_END']=len(bee)
                    self._addNativeEventToBuffer(bee)

                elif isinstance(ne,pylink.StartFixationEvent) or isinstance(ne,pylink.StartSaccadeEvent):
                    etype=ioHub.devices.EventConstants.EVENT_TYPES['FIXATION_START']
                    #ioEventClass=FixationStartEvent

                    if isinstance(ne,pylink.StartSaccadeEvent):
                        etype=ioHub.devices.EventConstants.EVENT_TYPES['SACCADE_START']
                        #ioEventClass=SaccadeStartEvent
                    which_eye=ne.getEye()
                    if which_eye:
                        which_eye=EventConstants.RIGHT
                    else:
                        which_eye=EventConstants.LEFT

                    pupil_size=-1
                    if etype == ioHub.devices.EventConstants.EVENT_TYPES['FIXATION_START']:
                        pupil_size=ne.getStartPupilSize()
                    gaze=ne.getStartGaze()
                    href=ne.getStartHREF()
                    velocity=ne.getStartVelocity()
                    ppd=ne.getStartPPD()
                    estatus=ne.getStatus()

                    se=[
                        0,                                      # exp ID
                        0,                                      # sess ID
                        Computer.getNextEventID(),              # event ID
                        etype,                                  # event type
                        self.eyeTrackerConfig['instance_code'], # device_instance_code
                        event_timestamp,                        # event time stamp
                        currentTime,                            # logged time
                        hub_timestamp,                          # hub time
                        confidenceInterval,                     # ci
                        event_delay,                            # delay
                        which_eye,                              # eye
                        gaze[0],                                # gaze x
                        gaze[1],                                # gaze y
                        -1,                                     # gaze z
                        href[0],                                # angle x
                        href[1],                                # angle y
                        -1.0,                                   # raw x
                        -1.0,                                   # raw y
                        pupil_size,                             # pupil area
                        EventConstants.AREA,                    # pupil measure type 1
                        -1.0,                                   # pupil measure 2
                        EventConstants.NOT_SUPPORTED_FIELD,     # pupil measure 2 type
                        ppd[0],                                 # ppd x
                        ppd[1],                                 # ppd y
                       -1.0,                                    # velocity x
                       -1.0,                                    # velocity y
                       velocity,                                # velocity xy
                       estatus                                  # status
                        ]
                    #EyeTracker._eventArrayLengths[ioHub.devices.EventConstants.EVENT_TYPES[etype]]=len(se)
                    self._addNativeEventToBuffer(se)

                elif isinstance(ne,pylink.StartBlinkEvent):
                    etype=ioHub.devices.EventConstants.EVENT_TYPES['BLINK_START']

                    estatus = ne.getStatus()

                    which_eye=ne.getEye()
                    if which_eye:
                        which_eye=EventConstants.RIGHT
                    else:
                        which_eye=EventConstants.LEFT

                    start_event_time= ne.getStartTime()*EyeTracker.DEVICE_TIMEBASE_TO_SEC

                    bse=[
                        0,
                        0,
                        Computer.getNextEventID(),
                        etype,
                        self.eyeTrackerConfig['instance_code'],
                        start_event_time,
                        currentTime,
                        hub_timestamp,
                        confidenceInterval,
                        event_delay,
                        which_eye,
                        estatus
                        ]
                    #EyeTracker._eventArrayLengths['BLINK_START']=len(bse)
                    self._addNativeEventToBuffer(bse)

            pollEndLocalTime=Computer.currentSec()
            EyeTracker.lastPollTime=pollEndLocalTime
        except Exception, e:
            ioHub.printExceptionDetailsToStdErr()
    
    def _handleNativeEvent(self,*args,**kwargs):
        pass
    
    @staticmethod    
    def _getIOHubEventObject(*args,**kwargs):
        """
        _getIOHubEventObject is used to convert a devices events from their 'native' format
        to the ioHub DeviceEvent obejct for the relevent event type.

        If a polling model is used to retrieve events, this conversion is actually done in
        the polling method itself.

        If an event driven callback method is used, then this method should be employed to do
        the conversion between object types, so a minimum of work is done in the callback itself.

        The method expects two args:
            (logged_time,event)=args[0] (when the callback is used to register device events)
            event = args[0] (when polling is used to get device events)
            device_instance_code=args[1]
        """
        
        # CASE 1: Polling is being used to get events:
        #
        if len(args)==2:
            event=args[0]
            device_instance_code=args[1]
            
        return event
        
        

    def _eyeTrackerToDisplayCoords(self,*args,**kwargs):
        """
        For eye tracker that have a static or fixed type internal mapping,
        this method is used to convert from eye tracker units to display units.
        Default implementation is to just pass the data through untouched.
        """
        if len(args<2):
            return ['EYETRACKER_ERROR','_eyeTrackerToDisplayCoords requires two args gaze_x=args[0], gaze_y=args[1]']
        gaze_x=args[0]
        gaze_y=args[1]
        
        # do mapping if necessary
        # default is no mapping 
        display_x=gaze_x
        display_y=gaze_y
        
        return display_x,display_y
        
        
    
    def _displayToEyeTrackerCoords(self,*args,**kwargs):
        """
        For eye tracker that have a static or fixed type internal mapping,
        this method is used to convert from display units to eye tracker units.
        Default implementation is to just pass the data through untouched.
        """
        if len(args<2):
            return ['EYETRACKER_ERROR','_displayToEyeTrackerCoords requires two args display_x=args[0], display_y=args[1]']
        display_x=args[0]
        display_y=args[1]
        
        # do mapping if necessary
        # default is no mapping 
        gaze_x=display_x
        gaze_y=display_y
        
        return gaze_x,gaze_y

    #def getEventArrayLengths(self,*args,**kwargs):
    #    return (EyeTracker._eventArrayLengths,)

    def __del__(self):
        """
        Do any final cleanup of the eye tracker before the object is destroyed. Users should not call or change this method. It is for implemetaion by interface creators and is autoatically called when an object is destroyed by the interpreter.
        """
        EyeTracker._INSTANCE=None
        
 
class EyeTrackerSetupGraphics(object):
    """
    EyeTrackerUserSetupGraphics provides a minimalistic standard 'public' interface
    that can be used for taking control of the experiment runtime graphics environment
    and keyboard / mouse by the eye tracker interface during 'black box' modes such as
    camera setup, calibration, validation, etc.

    Developers of eye tracker interfaces for CETI can extend this class and implement
    the specifics necessary to have the eye tracker perform whatever functionality is
    supported by the eye tracker in terms of user facing graphics for these types of tasks.

    * Users 'enter' the graphics mode provided by the EyeTrackerUserCalibrationGraphics class by
      calling a method of the eyetracker object from their experiment script:

      runSetupProcedure(*args,**kwargs):

      which in turn calls the run(....) method the this class.

    * This call blocks the user script, handing over control of the graphics state to the eye tracker interface.
      The user script will remain blocked until you call the objects returnToUserSpace() method, or the user
      manages to call the eyetracker.stopSetupProcedure() method.

    * Devlopers can access keyboard and mouse events occurring on the experiment computer by calling:

      events = getKeyboardMouseEvents() # returns all keyboard and mouse events since
                                        # the last call or since the last time
                                        # clearKeyboardAndMouseEvents() was called.
    """
    def __init__(self,graphicsContext,**kwargs):
        """
        The EyeTrackerSetupGraphics instance is created the first time eyetracker.runSetupProcedure(graphicsContext)
        is called. The class instance is then reused in future calls.
        graphicsContext object type is dependent on the graphics environment being used.
        Since psychopy normalizes everything in this regard to psychopy.visual.Window (regardless of
        whether pyglet or pygame backend is being used), then likely graphicsContext should be the instance of
        Window that has been created for your psychopy experiment. For an eye tracking experiment
        this would normally be a single 'full screen' window.
        """
        self.graphicsContext=graphicsContext
        
    def run(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics.run is not implemented."
        return self._handleDefaultState(*args,**kwargs)

    def _handleDefaultState(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleDefaultState is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def _handleCameraSetupState(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleCameraSetupState is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def _handleParticipantSetupState(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleParticipantSetupState is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCalibrateState(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleCalibrateState is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleValidateState(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleValidateState is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleDCState(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleDCState is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCM_A_State(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleCM_A_State is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCM_B_State(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleCM_B_State is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCM_C_State(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleCM_C_State is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCM_D_State(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleCM_D_State is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCM_E_State(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleCM_E_State is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def _handleCM_F_State(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics._handleCM_F_State is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def stop(self, returnMessage):
        print "EyeTrackerSetupGraphics.stop is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def getKeyboardMouseEvents(self):
        print "EyeTrackerSetupGraphics.getKeyboardMouseEvents is not implemented."
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
class EyeTrackerVendorExtension(object):
    """
    EyeTrackerVendorExtension is the base class used to add custom functionality to the pyEyeTracker
    module when the standard pyEyeTracker functionality set can not be used to meet the requirements
    of the specific eye trackers needs. This should be used AS A LAST RESORT to add the necessary
    functionality for any eye tracker. If you believe that certain functionality can not be met with
    the current pyEyeTracker core API, please first contact the pyEyeTracker development team and discuss
    your requirements and needs. It may a) be possible to achieve what you need already, or b) be the
    case that your requirement is agreed to be a use case that should be added to the core pyEyeTracker
    fucntionality instead of being added via an EyeTrackerVendorExtension. If either of these two situations
    are the case, the development team will put your requirements on the roadmap for the pyEyeTracker development
    and you or someone else are welcome to submit a patch for review containing the added functionality to the
    base pyEyeTracker code.
    """
    
    def __init__(self):
        pass
