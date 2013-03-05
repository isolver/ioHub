"""
ioHub
pyEyeTracker Interface
.. file: ioHub/devices/eyeTracker/HW/SR_Research/EyeLink/eyetracker.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

---------------------------------------------------------------------------------------------------------------------
This file uses the pylink module, Copyright (C) SR Research Ltd. License type unknown as it is not provided in the
pylink distribution (atleast when downloaded May 2012). At the time of writing, Pylink is freely avalaible for
download from  www.sr-support.com once you are registered and includes the necessary C DLLs.
---------------------------------------------------------------------------------------------------------------------

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

import os,sys
import numpy as np

import ioHub
from ioHub.constants import EventConstants, DeviceConstants, EyeTrackerConstants
from ..... import Computer
from .... import EyeTrackerDevice

try:
    import pylink
    pylink.enableUTF8EyeLinkMessages()
except:
    pass

class EyeTracker(EyeTrackerDevice):
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

    #. Eye Tracker Initialization / State Setting
    #. Ability to Define the Graphics Layer for the Eye Tracker to Use During Calibration / System Setup
    #. Starting and Stopping of Data Recording
    #. Sending Synchronization messages to the Eye Tracker
    #. Accessing the Eye Tracker Timebase
    #. Accessing Eye Tracker Data During Recording
    #. Synchronizing the Local Experiment timebase with the Eye Tracker Timebase, so Eye Tracker events
       can be provided with local time stamps when that is appropriate.
    #. Experiment Flow Generics
    """

    # >>> Constants:
    EYELINK=1
    EYELINK_II=2
    EYELINK_1000=3

    # >>> Custom class attributes
    _eyelink=None
    _localEDFDir='.'
    _fullEDFName='temp'
    _remoteEDFName=None
    _ACTIVE_EDF_FILE=None
    _fileTransferProgress=None
    # <<<

    # >>> Overwritten class attributes
    DEVICE_TIMEBASE_TO_SEC=0.001
    _COMMAND_TO_FUNCTION={}
    _INSTANCE=None #: Holds the reference to the current instance of the EyeTracker object in use and ensures only one is created.
    _latestSample=None # latest eye sample from tracker
    _latestGazePosition=0,0 # latest gaze position from eye sample. If binocular, average valid eye positions
    _displaySettings=None

    ALL_EVENT_CLASSES=[]

    DEVICE_TYPE_ID=DeviceConstants.EYE_TRACKER
    DEVICE_TYPE_STRING=DeviceConstants.getName(DeviceConstants.EYE_TRACKER)
    __slots__=[]
    # <<<

    def __init__(self, dconfig, *args,**kwargs):
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

        **If an instance of EyeTracker has already been created, trying to create a second will raise an exception.
        Either destroy the first instance and then create the new instance, or use the class method
        EyeTracker.getInstance() to access the existing instance of the eye tracker object.**
        """
        
        self._lastPollTime=0
        
        if EyeTracker._INSTANCE is not None:
            raise ioHub.devices.ioDeviceError(EyeTracker._INSTANCE,'EyeTracker object has already been created;'
                                                                   ' only one instance can exist.\n Delete existing'
                                                                   ' instance before recreating EyeTracker object.')

        from ..... import (MonocularEyeSample,BinocularEyeSample,FixationStartEvent,
                         FixationEndEvent, SaccadeStartEvent, SaccadeEndEvent,
                         BlinkStartEvent, BlinkEndEvent)

        EyeTracker.ALL_EVENT_CLASSES=[MonocularEyeSample,BinocularEyeSample,
                                               FixationStartEvent,FixationEndEvent, SaccadeStartEvent,
                                               SaccadeEndEvent, BlinkStartEvent, BlinkEndEvent]

        self.monitor_event_types=EyeTracker.ALL_EVENT_CLASSES

        EyeTracker._ioServer=dconfig['_ioServer']

        # create Device level class setting dictionary and pass it Device constructor
        deviceSettings={
            'type_id':self.DEVICE_TYPE_ID,
            'device_class':EyeTracker.__name__,
            'name':dconfig.get('name','tracker'),
            'monitor_event_types':dconfig.get('monitor_event_types',EyeTracker.ALL_EVENT_CLASSES),
            'os_device_code':'OS_DEV_CODE_NOT_SET',
            'max_event_buffer_length':dconfig.get('event_buffer_length',1024)
            }
        EyeTrackerDevice.__init__(self,*args,**deviceSettings)

                            
        self._startupConfiguration=dconfig

        # set this instance as 'THE' instance of the eye tracker.
        EyeTracker._INSTANCE=self

        dummyModeEnabled=self._startupConfiguration['runtime_settings'].get('enable_api_without_connection',False)
        if dummyModeEnabled:
            self._eyelink.dummy_open()

        EyeTracker._eyelink=None
        
        try:
            EyeTracker._eyelink=pylink.EyeLink(self._startupConfiguration['runtime_settings'].get('network_settings','100.1.1.1'))
            self._eyelink.setOfflineMode()
            EyeTracker._eyelink.progressUpdate=self._fileTransferProgressUpdate
        except:
            pass
        

        # >>>> Display / Calibration related information to use for config if possible
        EyeTracker._displaySettings = self._startupConfiguration['display_settings']
        # <<<<

        if EyeTracker._eyelink:
            self._addCommandFunctions()
    
            try:
                self._eyelinkSetScreenPhysicalData()
            except:
                ioHub.print2err('ERROR: could not run _eyelinkSetScreenPhysicalData')
                ioHub.printExceptionDetailsToStdErr()
    
            try:
                self._eyelinkSetLinkAndFileContents()
            except:
                ioHub.print2err('ERROR: could not run _eyelinkSetLinkAndFileContents')
                ioHub.printExceptionDetailsToStdErr()
    
            self._eyelink.sendCommand("button_function 5 'accept_target_fixation'")
    
            # >>>> eye tracker setting to config (if possible)
    
            runtimeSettings=self._startupConfiguration['runtime_settings']
    
    
            if ioHub.data_paths is None:
                EyeTracker._localEDFDir=os.path.abspath('.')
            else:
                EyeTracker._localEDFDir=ioHub.data_paths['NATIVE_DEVICE_DATA']
    
            self._setRuntimeSettings(runtimeSettings)

    ####################################################################################################################


    def _setRuntimeSettings(self,runtimeSettings):
        eyelink=self._eyelink
        for pkey,v in runtimeSettings.iteritems():
            pylink.msecDelay(1)
            if pkey in ['enable_api_without_connection','network_settings']:
                pass
            elif pkey == 'auto_calibration':
                if v is True or v == 1 or v == 'ON':
                    eyelink.enableAutoCalibration()
                elif v is False or v == 0 or v == 'OFF':
                    eyelink.disableAutoCalibration()

            elif pkey == 'auto_calibration_speed': # in seconds.msec
                if isinstance(v,(int,float)):
                    eyelink.setAutoCalibrationPacing(int(v*1000))
                else:
                    ioHub.print2err('ERROR: auto_calibration_speed value must be an int or float: %s'%(str(v)))

            elif pkey == 'default_calibration':
                #  calibrationType:
                #  H3: Horizontal 3-point
                #  HV3: 3-point calibration
                #  HV5: 5-point calibration
                #  HV9: 9-point calibration
                VALID_CALIBRATION_TYPES=dict(NONE='NONE',H3="H3",HV3="HV3",HV5="HV5",HV9="HV9",HV13="HV13")
                if v in VALID_CALIBRATION_TYPES:
                    if v is not 'NONE':
                        eyelink.setCalibrationType(VALID_CALIBRATION_TYPES[v])
                else:
                    ioHub.print2err('ERROR: default_calibration value is unrecognized: %s'%(v))

            elif pkey == 'runtime_filtering':
                self.setDataFilterLevel(**v)

            elif pkey == 'sampling_rate':
                self.setSamplingRate(v)

            elif pkey == 'default_native_data_file_name':
                if isinstance(v,(str,unicode)):
                    r=v.rfind('.')
                    if r>0:
                        if v[r:] == 'edf'.lower():
                            v=v[:r]

                    if len(v)>7:
                        EyeTracker._fullEDFName=v
                        twoDigitRand=np.random.randint(10,99)
                        EyeTracker._remoteEDFName=self._fullEDFName[:3]+twoDigitRand+self._fullEDFName[5:7]
                    else:
                        EyeTracker._fullEDFName=v
                        EyeTracker._remoteEDFName=v
                else:
                    ioHub.print2err("ERROR: default_native_data_file_name must be a string or unicode value")

            elif pkey == 'track_eyes':
                self.setEyesToTrack(v)

            elif pkey == 'vog_settings':
                for pkey,v in runtimeSettings['vog_settings'].iteritems():
                    pylink.msecDelay(1)
                    if pkey == 'pupil_measure_types':
                        if v in ['AREA','DIAMETER']:
                            self._eyelink.sendCommand("pupil_size_diameter %s"%(v))
                        else:
                            ioHub.print2err('ERROR: pupil_measure_types value must be set to AREA or DIAMETER for EyeLink.')
                    elif pkey == 'pupil_center_algorithm':
                        self._setPupilDetection(v)
                    elif pkey == 'tracking_mode':
                        self._setEyeTrackingMode(v)
                    elif pkey == 'pupil_illumination':
                        pass # always dark for eyelink, so skip the param all together.
                    else:
                        ioHub.print2err("WARNING: unhandled eye tracker config setting ( in sub group vog_settings):",pkey,v)
                        ioHub.print2err("")
            else:
                ioHub.print2err("WARNING: unhandled eye tracker config setting:",pkey,v)

        if self._localEDFDir and self._fullEDFName:
            EyeTracker._ACTIVE_EDF_FILE=self._fullEDFName+'.EDF'

        self._eyelink.openDataFile(self._remoteEDFName+'.EDF')


    def _fileTransferProgressUpdate(self,size,received):
        from util.experiment import ProgressBarDialog
        if EyeTracker._fileTransferProgress is None:
            EyeTracker._fileTransferProgress =  ProgressBarDialog("OpenPsycho pyEyeTrackerInterface","Transferring  " + self._fullEDFName+'.EDF to '+self._localEDFDir,100)
        elif received >= size and EyeTracker._fileTransferProgress:
                EyeTracker._fileTransferProgress.close()
                EyeTracker._fileTransferProgress = None
        else:
            perc = int((float(received)/float(size))*100.0)+1
            if perc > 100:
                perc=100
            if perc !=self._fileTransferProgress.getCurrentStatus():
                self._fileTransferProgress.updateStatus(perc)

    
    def experimentStartDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the start of an experiment.
        """
        pylink.flushGetkeyQueue()
        return EyeTrackerConstants.EYETRACKER_OK
 
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
        return EyeTrackerConstants.EYETRACKER_OK

    def trialStartDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the start of an experiment trial.
        """
        
        pylink.flushGetkeyQueue()
        return EyeTrackerConstants.EYETRACKER_OK
         
    def trialEndDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the end of an experiment trial.
        """
        pylink.flushGetkeyQueue()
        return EyeTrackerConstants.EYETRACKER_OK
         
    def blockEndDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the end of an experiment block.
        """
        # Currently does nothing; which is current 'implemented' state.
        pylink.flushGetkeyQueue()
        return EyeTrackerConstants.EYETRACKER_OK

    def experimentEndDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the end of an experiment session.
        """
        pylink.flushGetkeyQueue()
        return EyeTrackerConstants.EYETRACKER_OK
        
    def trackerTime(self):
        """
        Current eye tracker time (in msec for eyelink since host app was last started)
        """
        return self._eyelink.trackerTime()

    def trackerSec(self):
        """
        Current eye tracker time, normalized to sec.msec.
        """
        return self._eyelink.trackerTime()*self.DEVICE_TIMEBASE_TO_SEC

    def setConnectionState(self,*args,**kwargs):
        """
        setConnectionState is used to connect ( setConnectionState(True) ) or disable ( setConnectionState(False) )
        the connection of the pyEyeTrackerInterface to the eyetracker.

        Args:

            enabled (bool): True = enable the connection, False = disable the connection.
            kwargs (dict): any eye tracker specific parameters that should be passed.
        """
        enabled=args[0]

        if 'dummy' in kwargs:
            return self._eyelink.dummy_open()

        if enabled is True or enabled is False:
            if enabled is True and not self._eyelink.isConnected():
                self._eyelink.open()
                pylink.msecDelay(100)
                pylink.flushGetkeyQueue()
                self._eyelink.setOfflineMode()
                return True
            elif enabled is False and self._eyelink.isConnected():
                self._eyelink.setOfflineMode()

                if self._ACTIVE_EDF_FILE:
                    self._eyelink.closeDataFile()
                    # receive(scr,dest)
                    self._eyelink.receiveDataFile(self._remoteEDFName+".EDF",os.path.join(self._localEDFDir,self._ACTIVE_EDF_FILE))

                self._eyelink.close()
                EyeTracker._ACTIVE_EDF_FILE=None
                return EyeTrackerConstants.EYETRACKER_OK
        else:
            return ['EYETRACKER_ERROR','Invalid arguement type','setConnectionState','enabled',enabled,kwargs]
            
    def isConnected(self):
        """
        isConnected returns whether the pyEyeTrackerInterface is connected to the eye tracker (returns True) or not (returns False)
        """
        return self._eyelink.isConnected() != 0
            
    def sendCommand(self, *args, **kwargs):
        """
        sendCommand sends a text command and text command value to the eye tracker. Depending on the command and on the eye trackers
        implementation, when a command is send, the eye tracker may or n=may not response indicating the status of the command. If the
        command is not going to return a response from the eye tracker, the method will return selfRESULT_UNKNOWN.
        Please see the specific eye tracker implementation you are working with for a list of supported command's and value's.

        Args:
           str: command (and value if applicable) all as one string.

        kwargs:
           command (str): line. This can be used 'instead of' the arg option. If it is used, provide the actual command
                                name as the argument key, and the value for the line. i.e. command_name = command_value
           waitForResponse (bool): if bool, True = do not return from function until result of command if known
                                  (if it can be known); False = return immediately after sending the command,
                                  ignoring any possible return value. (if waitForResponse is not specified,
                                  False is assumed)

        Return: the result of the command call, or one of the ReturnCodes Constants ( ReturnCodes.ET_OK, ReturnCodes.ET_RESULT_UNKNOWN, ReturnCodes.ET_NOT_IMPLEMENTED )
        """

        command=None
        waitForResponse=False

        if len(args)>0:
            command=args[0]
            args=args[1:]

        if 'waitForResponse' in kwargs:
            waitForResponse=True
            del kwargs['waitForResponse']

        if command in EyeTracker._COMMAND_TO_FUNCTION:
            EyeTracker._COMMAND_TO_FUNCTION[command](*args)
        else:
            cmdstr=''
            if len(args)==0:
                cmdstr="{0}".format(command)
            else:
                cmdstr="{0} = {1}".format(command,args)

            if waitForResponse:
                yield self._readResultFromTracker(cmdstr)
            else:
                yield self._eyelink.sendCommand(cmdstr)

        for command, value in kwargs.iteritems():
            if command in EyeTracker._COMMAND_TO_FUNCTION:
                cargs=()
                ckwargs={}
                if isinstance(value,dict):
                    ckwargs=value
                elif isinstance(value,list):
                    if len(value)==2:
                        a,b=value
                        if isinstance(a,tuple) and isinstance (b,dict):
                            cargs=a
                            ckwargs=b
                        else:
                            cargs=value
                else:
                    cargs=value

                yield EyeTracker._COMMAND_TO_FUNCTION[command](*cargs,**ckwargs)
            else:
                cmdstr="{0} = {1}".format(command,value)
                if waitForResponse:
                    yield self._readResultFromTracker(cmdstr)
                else:
                    yield self._eyelink.sendCommand(cmdstr)

    def sendMessage(self,*args,**kwargs):
        """
        sendMessage sends a text message to the eye tracker. Depending on the eye trackers implementation, when a message is send,
        the eye tracker may or may not response indicating the message was received. If the
        message is not going to receive a response from the eye tracker, the method will return selfRESULT_UNKNOWN.
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
            return self.RESULT_UNKNOWN
        return r
        
    def runSetupProcedure(self, *args ,**kwargs):
        """
        runSetupProcedure passes the graphics environment over to the eye tracker interface so that it can perform such things
        as camera setup, calibration, etc. This is a blocking call that will not return until the setup procedure is done; at which time
        the graphics environment can be taken back over by psychopy.  See the EyeTrackerSetupGraphics class for more information.

        The graphicsContext argument should likely be the psychopy full screen window instance that has been created
        for the experiment.
        """
        try:
            ioHub.print2err('Starting runSetupProcedure')

            import eyeLinkCoreGraphicsIOHubPsychopy
            EyeLinkCoreGraphicsIOHubPsychopy = eyeLinkCoreGraphicsIOHubPsychopy.EyeLinkCoreGraphicsIOHubPsychopy

            # Optional kwargs that can be passed in to control built in calibration graphics and sound
            targetForegroundColor=kwargs.get('targetForegroundColor',None) # [r,g,b] of outer circle of targets
            targetBackgroundColor=kwargs.get('targetBackgroundColor',None) # [r,g,b] of inner circle of targets
            screenColor=kwargs.get('screenColor',None)                     # [r,g,b] of screen
            targetOuterDiameter=kwargs.get('targetOuterDiameter',None)     # diameter of outer target circle (in px)
            targetInnerDiameter=kwargs.get('targetInnerDiameter',None)     # diameter of inner target circle (in px)
            dc_sounds=kwargs.get('dc_sounds',["","",""])                   # targetS, goodS, errorS for DC. "" ==
                                                                           # use current defaults. "off" or None ==
                                                                           # play no sound
            cal_sounds=kwargs.get('cal_sounds',["","",""])                 # targetS, goodS, errorS for Cal / Val.

            genv=EyeLinkCoreGraphicsIOHubPsychopy(self,targetForegroundColor=targetForegroundColor,
                                                        targetBackgroundColor=targetBackgroundColor,
                                                        screenColor=screenColor,
                                                        targetOuterDiameter=targetOuterDiameter,
                                                        targetInnerDiameter=targetInnerDiameter,
                                                        dc_sounds=dc_sounds, cal_sounds=cal_sounds)


            ioHub.print2err("monitor_event_types for eyelink: ", self.monitor_event_types, EyeTracker.ALL_EVENT_CLASSES)
           # ioHub.print2err("EyeTracker._ioServer: ",EyeTracker._ioServer)
           # genv._registerEventMonitors()
            pylink.openGraphicsEx(genv)

            self._eyelink.doTrackerSetup()

            genv._unregisterEventMonitors() 
            genv.window.close()
            genv.clearAllEventBuffers()

        except:
            ioHub.print2err("Error during runSetupProcedure")
            ioHub.printExceptionDetailsToStdErr()
        return True

    def enableEventReporting(self,enabled=True):
        EyeTrackerInterface.enableEventReporting(self,enabled)
        self.setRecordingState(enabled)

    def setRecordingState(self,*args,**kwargs):
        """
        setRecordingState is used to start or stop the recording of data from the eye tracking device. Use sendCommand() set the necessary information
        for your eye tracker to enable what data you would like saved, send over to the experiment computer during recording, etc.

        args:
           recording (bool): if True, the eye tracker should start recordng data.; false = stop recording data.
        """
        ioHub.print2err()
        if len(args)==0:
            return ('EYETRACKER_ERROR','EyeTracker.setRecordingState','recording(bool) must be provided as a args[0]')
        enable=args[0]
        
        if enable is True and not self.isRecordingEnabled():
            error = self._eyelink.startRecording(1,1,1,1)
            if error:
                return ('EYETRACKER_ERROR','EyeTracker.setRecordingState','Could not start Recording',error)

            if not self._eyelink.waitForBlockStart(100, 1, 0):
                return ('EYETRACKER_ERROR','EyeTracker.setRecordingState','Error in waitForBlockStart')
            else:
                return EyeTrackerConstants.EYETRACKER_OK
        
        elif enable is False and self.isRecordingEnabled():
            self._eyelink.stopRecording()
            pylink.msecDelay(50)
            return EyeTrackerConstants.EYETRACKER_OK

    def isRecordingEnabled(self,*args,**kwargs):
       """
       isRecordingEnabled returns the recording state from the eye tracking device.
       True == the device is recording data
       False == Recording is not occurring
       """
       return self._eyelink.isRecording()  == 0

    def getEyesToTrack(self,*args,**kwargs):
        LEFT_EYE=0
        RIGHT_EYE=1
        BINOCULAR=2

        eye_used = self._eyelink.eyeAvailable() #determine which eye(s) are available

        if eye_used == RIGHT_EYE:
            return EyeTrackerConstants.getName(EyeTrackerConstants.RIGHT_EYE)
        elif eye_used == LEFT_EYE:
            return EyeTrackerConstants.getName(EyeTrackerConstants.LEFT_EYE)
        elif eye_used == BINOCULAR:
            return EyeTrackerConstants.getName(EyeTrackerConstants.BINOCULAR)
        else:
            ioHub.print2err("ERROR: getEyesToTrack: Error in getting the eye information!")
            return ['EYETRACKER_ERROR',"EyeTracker.getEyesToTrack","Error in getting the eye information",eye_used]


    def setEyesToTrack(self,*args,**kwargs):
        r=args[0]

        if isinstance(r,basestring):
            pass
        else:
            r = EyeTrackerConstants.getName(r)

        if r is None:
            ioHub.print2err("** Warning: UNKNOWN EYE CONSTANT, SETTING EYE TO TRACK TO RIGHT. UNKNOWN EYE CONSTANT: ",args[0])
            r='RIGHT'
        elif r in ['RIGHT', EyeTrackerConstants.getName(EyeTrackerConstants.RIGHT_EYE)]:
            r='RIGHT'
        elif r in ['LEFT', EyeTrackerConstants.getName(EyeTrackerConstants.LEFT_EYE)]:
            r='LEFT'
        elif r in ['BOTH', EyeTrackerConstants.getName(EyeTrackerConstants.BINOCULAR)]:
            r='BOTH'
        else:
            ioHub.print2err("** Warning: UNKNOWN EYE CONSTANT, SETTING EYE TO TRACK TO RIGHT. UNKNOWN EYE CONSTANT: ",args[0])
            r='RIGHT'

        srate=self.getSamplingRate()

        self._eyelink.sendCommand("lock_active_eye = NO")

        if r == "BOTH":
            if self._eyelink.getTrackerVersion() == 3:
                if srate>=1000:
                    ioHub.print2err("ERROR: setEyesToTrack: EyeLink can not record binocularly over 500 hz.")
                else:
                    trackerVersion =self._eyelink.getTrackerVersionString().strip()
                    trackerVersion = trackerVersion.split(' ')
                    tv = float(trackerVersion[len(trackerVersion)-1])
                    if tv <= 3:
                        if srate>500:
                            ioHub.print2err("ERROR: setEyesToTrack: Selected sample rate is not supported in binocular mode")
                        else:
                            self._eyelink.sendCommand("binocular_enabled = YES")
                            return True
                    else:
                        rts = []
                        modes = self._readResultFromTracker("read_mode_list")
                        if modes is None or modes.strip() == 'Unknown Variable Name':
                            ioHub.print2err("ERROR: setEyesToTrack: Failed to get supported modes. ")
                        modes = modes.strip().split()

                        for x in modes:
                            if x[-1] == 'B':
                                x =int(x.replace('B',' ').strip())
                                rts.append(x)
                        if srate in rts:
                            self._eyelink.sendCommand("binocular_enabled = YES")
                            return True
                        else:
                            ioHub.print2err("ERROR: setEyesToTrack: Selected sample rate is not supported!")
        elif r in ("EITHER", 'MONO'):
            self.sendCommand("binocular_enabled = NO")
            return True
        else:
            self.sendCommand("binocular_enabled = NO")
            self.sendCommand("active_eye = %s"%(r))
            self.sendCommand("lock_active_eye = YES")



    def getSamplingRate(self,*args,**kwargs):
        if self.isConnected():
            return self._eyelink.getSampleRate()
        return 0

    def setSamplingRate(self,*args,**kwargs):
        if len(args)==1 and self.isConnected():
            srate=int(args[0])
            tracker_version=self._eyelink.getTrackerVersion()
            if tracker_version < 3:
                # eyelink II
                self._eyelink.sendCommand("use_high_speed %d"%(srate==500))
            else:
                trackerVersion =self._eyelink.getTrackerVersionString().strip()
                trackerVersion = trackerVersion.split(' ')
                tv = float(trackerVersion[len(trackerVersion)-1])

                if tv>3:
                    # EyeLink 2000
                    rts = []
                    modes = self._readResultFromTracker("read_mode_list")
                    if modes is None or modes.strip() == 'Unknown Variable Name':
                        raise RuntimeError,"Failed to get supported modes. "
                    modes = modes.strip().split()

                    ioHub.print2err("Modes = ", modes)
                    for x in modes:
                        m = x.replace('B',' ').strip()
                        m = m.replace('R',' ').strip()
                        x =int(m)
                        rts.append(x)
                    if srate in rts:
                        self._eyelink.sendCommand("sample_rate = %d"%(srate))
                else:
                    # EyeLink 1000
                    if srate<=1000:
                        self.sendCommand("sample_rate = %d"%(srate))
            return self.getSamplingRate()
        return False



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
        
        # TODO: Implement getDataFilterLevel for EyeLink
        ioHub.print2err('getDataFilterLevel is not implemented currently.')        
        return EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED

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

        if len(kwargs)>0:
            supportedTypes='ANY','ALL','FILE','ANALOG','NET'
            supportedLevels= False,'LEVEL_1','LEVEL_2'

            for key,value in kwargs.iteritems():
                if key.upper() in supportedTypes and (value is False or value.upper() in supportedLevels):
                    ffilter=0
                    lfilter=0
                    if key.upper() in ['ALL','ANY']:
                        if value is not False:
                            self._eyelink.setHeuristicLinkAndFileFilter(supportedLevels.index(value.upper()),supportedLevels.index(value.upper()))
                        else:
                            self._eyelink.setHeuristicLinkAndFileFilter(0,0)
                        return True
                    elif key.upper() == 'FILE' and value:
                        ffilter=supportedLevels.index(value.upper())
                    elif value:
                        lfilter=supportedLevels.index(value.upper())

            self._eyelink.setHeuristicLinkAndFileFilter(ffilter,lfilter)
            return True
        return False

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

    def drawToHostApplicationWindow(self,*args,**kwargs):
        """
        drawToHostApplicationWindow provides a generic interface for ET devices that support
        having graphics drawn to the Host / Control computer / application gaze overlay area, or other similar
        graphics area functionality.

        The method should return the appropriate return code if successful or if the command failed,
        or if it is unsupported.

        There is no set list of values for any of the arguments for this command, so please refer to the
        ET implementation notes for your device for details.

        In general, the method takes one arg, being a string token for the drawing command to perform. The method
        then takes 0 - N key=value kwargs, providing the necessary named arguements for the drawing command
        being performed.

        EyeLink supported:

        arg: 'TEXT'
        kwargs: text='The text to draw', position=(x,y)
                where x,y is the position to draw the text in calibrated screen coords.

        arg: 'CLEAR'
        kwargs: color = int, between 0 - 15, the color from the EyeLink Host PC palette to use.

        arg: 'LINE'
        kwargs: color= int 0 - 15,  start=(x,y), end=(x,y)
                where x,y are the start and end position to draw the line in calibrated screen coords.

        arg: 'BOX'
        kwargs:  x  = x coordinates for the top-left corner of the rectangle.
                 y  = y coordinates for the top-left corner of the rectangle.
                 width = width of the filled rectangle.
                 height = height of the filled rectangle.
                 color = 0 to 15.
                 filled (optional) = True , then box is filled, False and box is only an outline.

        arg: 'CROSS' - Draws a small "+" to mark a target point.
        kwargs: x = x coordinates for the center point of cross.
                y = y coordinates for the center point of cross.
                color = 0 to 15 (0 for black; 1 for blue; 2 for green; 3 for cyan; 4 for red; 5 for magenta;
                                6 for brown; 7 for light gray; 8 for dark gray; 9 for light blue;
                                10 for light green; 11 for light cyan; 12 for light red;
                                13 for bright magenta; 14 for yellow; 15 for bright white).

        """
        drawingcommand=None
        if len(args)==0:
            return ('EYETRACKER_ERROR','drawToGazeOverlayScreen','args must have length > 0: drawingcommand = args[0]')
        else:
            drawingcommand=args[0]
            
        if drawingcommand is None:
            return ('EYETRACKER_ERROR','drawToGazeOverlayScreen','drawingcommand can not be None.')
        elif drawingcommand=='TEXT':
            if 'text' in kwargs and 'position' in kwargs:
                text=kwargs['text']
                position=kwargs['position']
                return self._eyelink.drawText(str(text),position)
            return ('EYETRACKER_ERROR','drawToGazeOverlayScreen','arg: TEXT','kwargs "text" and "position" are required for this command.')
        elif drawingcommand=='CLEAR':
            if 'color' in kwargs:
                pcolor=int(kwargs['color'])
                if pcolor >=0 and pcolor <= 15:
                    return self._eyelink.clearScreen(pcolor)
            return ('EYETRACKER_ERROR','drawToGazeOverlayScreen','arg: CLEAR','kwargs "color" is required for this command')
        elif drawingcommand=='LINE':
            if 'color' in kwargs and 'start' in kwargs and 'end' in kwargs:
                pcolor=int(kwargs['color'])
                sposition = kwargs['start']
                eposition = kwargs['end']
                if pcolor >=0 and pcolor <= 15 and len(sposition)==2 and len(eposition)==2:
                    return self._eyelink.drawLine(sposition, eposition,pcolor)
            return ('EYETRACKER_ERROR','drawToGazeOverlayScreen','arg: LINE','kwargs "color" and "start" and "end" are required for this command')
        elif drawingcommand=='BOX':
            if 'color' in kwargs and 'x' in kwargs and 'y' in kwargs and 'width' in kwargs and 'height' in kwargs:
                pcolor=kwargs['color']
                x=kwargs['x']
                y=kwargs['y']
                width=kwargs['width']
                height=kwargs['height']
                filled=False
                if filled in kwargs:
                    filled=kwargs['filled']
                if pcolor >=0 and pcolor <= 15:
                    if filled is True:
                        return self._eyelink.drawBox(x, y,width, height, pcolor)
                    else:
                        return self._eyelink.drawFilledBox(x, y,width, height, pcolor)
            return ('EYETRACKER_ERROR','drawToGazeOverlayScreen','arg: BOX','kwargs x, y,width, height, and color are required for this command')
        elif drawingcommand=='CROSS': # Draws a small "+" to mark a target point.  # value must be between 0 - 15 and is the color from the EyeLink Host PC pallette to use.  position must be (x,y)
            if 'color' in kwargs and 'x' in kwargs and 'y' in kwargs:
                pcolor=int(kwargs['color'])
                x = kwargs['x']
                y = kwargs['y']
                if pcolor >=0 and pcolor <= 15:
                    return self._eyelink.drawCross(x,y,pcolor)
            return ('EYETRACKER_ERROR','drawToGazeOverlayScreen','command: CROSS','kwargs "value" and "position" are required for this command')
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
            if self._eyelink is None:
                return
            eyelink=self._eyelink
            DEVICE_TIMEBASE_TO_SEC=EyeTracker.DEVICE_TIMEBASE_TO_SEC
            poll_time=Computer.getTime()
            confidenceInterval=poll_time-self._lastPollTime
            self._lastPollTime=poll_time
            
            #get native events queued up
            nEvents=[]
            while 1:
                ne = eyelink.getNextData()
                if ne == 0 or ne is None:
                    break # no more events / samples to process

                ne=eyelink.getFloatData()
                if ne is None:
                    break

                cltime=Computer.currentSec()
                cttime=self.trackerSec()

                event_timestamp=ne.getTime()*DEVICE_TIMEBASE_TO_SEC
                event_delay=cttime-event_timestamp
                if event_delay < 0:
                    event_delay=0.0

                timestamp=cltime-event_delay

                ne.logged_time=cltime
                ne.event_timestamp=event_timestamp
                ne.timestamp=timestamp
                ne.event_delay=event_delay
                nEvents.append(ne)

            for ne in nEvents:
                if isinstance(ne,pylink.Sample):
                    # now convert from native format to pyEyeTracker  common format

                    ppd=ne.getPPD()

                    # hubtime calculation needs to be finished / improved.
                    # - offset should be an integration of 1% to handle noise / spikes in
                    #   calulation
                    # - need to handle drift between clocks


                    if ne.isBinocular():
                        # binocular sample
                        event_type=EventConstants.BINOC_EYE_SAMPLE
                        myeye=EyeTrackerConstants.BINOCULAR
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

                        binocSample=[
                                     0,
                                     0,
                                     Computer._getNextEventID(),
                                     event_type,
                                     ne.event_timestamp,
                                     ne.logged_time,
                                     ne.timestamp,
                                     confidenceInterval,
                                     ne.event_delay,
                                     0,
                                     myeye,
                                     leftGaze[0],
                                     leftGaze[1],
                                     EyeTrackerConstants.UNDEFINED,
                                     EyeTrackerConstants.UNDEFINED,
                                     EyeTrackerConstants.UNDEFINED,
                                     EyeTrackerConstants.UNDEFINED,
                                     leftHref[0],
                                     leftHref[1],
                                     leftRawPupil[0],
                                     leftRawPupil[1],
                                     leftPupilSize,
                                     EyeTrackerConstants.PUPIL_AREA,
                                     EyeTrackerConstants.UNDEFINED,
                                     EyeTrackerConstants.UNDEFINED,
                                     ppd[0],
                                     ppd[1],
                                     vel_x,
                                     vel_y,
                                     vel_xy,
                                     rightGaze[0],
                                     rightGaze[1],
                                     EyeTrackerConstants.UNDEFINED,
                                     EyeTrackerConstants.UNDEFINED,
                                     EyeTrackerConstants.UNDEFINED,
                                     EyeTrackerConstants.UNDEFINED,
                                     rightHref[0],
                                     rightHref[1],
                                     rightRawPupil[0],
                                     rightRawPupil[1],
                                     rightPupilSize,
                                     EyeTrackerConstants.PUPIL_AREA,
                                     EyeTrackerConstants.UNDEFINED,
                                     EyeTrackerConstants.UNDEFINED,
                                     ppd[0],
                                     ppd[1],
                                     vel_x,
                                     vel_y,
                                     vel_xy,
                                     0
                                     ]

                        EyeTracker._latestSample=binocSample

                        g=[pylink.MISSING_DATA,pylink.MISSING_DATA]
                        for i in range(2):
                            ic=0
                            if leftGaze[i] != pylink.MISSING_DATA:
                                g[i]+=leftGaze[i]
                                ic+=1
                            if rightGaze[i] != pylink.MISSING_DATA:
                                g[i]+=rightGaze[i]
                                ic+=1
                            if ic == 2:
                                g[i]=g[i]/2.0

                        EyeTracker._latestGazePosition=g
                        self._addNativeEventToBuffer(binocSample)

                    else:
                        # monocular sample
                        event_type=EventConstants.EYE_SAMPLE
                        leftEye=ne.isLeftSample()
                        eyeData=None
                        if leftEye == 1:
                            eyeData=ne.getLeftEye()
                            myeye=EyeTrackerConstants.LEFT_EYE
                        else:
                            eyeData=ne.getRightEye()
                            myeye=EyeTrackerConstants.RIGHT_EYE

                        pupilSize=eyeData.getPupilSize()
                        rawPupil=eyeData.getRawPupil()
                        href=eyeData.getHREF()
                        gaze=eyeData.getGaze()

                        # TO DO: EyeLink pyLink does not expose sample velocity fields. Patch and fix.
                        vel_x=-1.0
                        vel_y=-1.0
                        vel_xy=-1.0

                        monoSample=[0,
                                    0,
                                    Computer._getNextEventID(),
                                    event_type,
                                    ne.event_timestamp,
                                    ne.logged_time,
                                    ne.timestamp,
                                    confidenceInterval,
                                    ne.event_delay,
                                    0,
                                    myeye,
                                    gaze[0],
                                    gaze[1],
                                    EyeTrackerConstants.UNDEFINED,
                                    EyeTrackerConstants.UNDEFINED,
                                    EyeTrackerConstants.UNDEFINED,
                                    EyeTrackerConstants.UNDEFINED,
                                    href[0],
                                    href[1],
                                    rawPupil[0],
                                    rawPupil[1],
                                    pupilSize,
                                    EyeTrackerConstants.PUPIL_AREA,
                                    EyeTrackerConstants.UNDEFINED,
                                    EyeTrackerConstants.UNDEFINED,
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
                    etype=EventConstants.FIXATION_END

                    estatus = ne.getStatus()

                    which_eye=ne.getEye()
                    if which_eye:
                        which_eye=EyeTrackerConstants.RIGHT_EYE
                    else:
                        which_eye=EyeTrackerConstants.LEFT_EYE

                    start_event_time= ne.getStartTime()*DEVICE_TIMEBASE_TO_SEC
                    end_event_time = ne.event_timestamp
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

                    fee=[0,
                         0,
                         Computer._getNextEventID(),
                         etype,
                         ne.event_timestamp,
                         ne.logged_time,
                         ne.timestamp,
                         confidenceInterval,
                         ne.event_delay,
                         0,
                        which_eye,
                        event_duration,
                        s_gaze[0],
                        s_gaze[1],
                        EyeTrackerConstants.UNDEFINED,
                        s_href[0],
                        s_href[1],
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        s_pupilsize,
                        EyeTrackerConstants.PUPIL_AREA,
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        s_ppd[0],
                        s_ppd[1],
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        s_vel,
                        e_gaze[0],
                        e_gaze[1],
                        EyeTrackerConstants.UNDEFINED,
                        e_href[0],
                        e_href[1],
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        e_pupilsize,
                        EyeTrackerConstants.PUPIL_AREA,
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        e_ppd[0],
                        e_ppd[1],
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        e_vel,
                        a_gaze[0],
                        a_gaze[1],
                        EyeTrackerConstants.UNDEFINED,
                        a_href[0],
                        a_href[1],
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        a_pupilsize,
                        EyeTrackerConstants.PUPIL_AREA,
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        a_vel,
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        peak_vel,
                        estatus
                        ]
                    #EyeTracker._eventArrayLengths['FIXATION_END']=len(fee)
                    self._addNativeEventToBuffer(fee)

                elif isinstance(ne,pylink.EndSaccadeEvent):
                    etype=EventConstants.SACCADE_END

                    estatus = ne.getStatus()

                    which_eye=ne.getEye()
                    if which_eye:
                        which_eye=EyeTrackerConstants.RIGHT_EYE
                    else:
                        which_eye=EyeTrackerConstants.LEFT_EYE

                    start_event_time= ne.getStartTime()*DEVICE_TIMEBASE_TO_SEC
                    end_event_time = ne.event_timestamp
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
                         Computer._getNextEventID(),
                        etype,
                        ne.event_timestamp,
                        ne.logged_time,
                        ne.timestamp,
                        confidenceInterval,
                        ne.event_delay,
                        0,
                        which_eye,
                        event_duration,
                        e_amp[0],
                        e_amp[1],
                        e_angle,
                        s_gaze[0],
                        s_gaze[1],
                        EyeTrackerConstants.UNDEFINED,
                        s_href[0],
                        s_href[1],
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        s_pupilsize,
                        EyeTrackerConstants.PUPIL_AREA,
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        s_ppd[0],
                        s_ppd[1],
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        s_vel,
                        e_gaze[0],
                        e_gaze[1],
                        EyeTrackerConstants.UNDEFINED,
                        e_href[0],
                        e_href[1],
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        e_pupilsize,
                        EyeTrackerConstants.PUPIL_AREA,
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        e_ppd[0],
                        e_ppd[1],
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        e_vel,
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        a_vel,
                        EyeTrackerConstants.UNDEFINED,
                        EyeTrackerConstants.UNDEFINED,
                        peak_vel,
                        estatus
                        ]
                    self._addNativeEventToBuffer(see)
                elif isinstance(ne,pylink.EndBlinkEvent):
                    etype=EventConstants.BLINK_END

                    estatus = ne.getStatus()

                    which_eye=ne.getEye()
                    if which_eye:
                        which_eye=EyeTrackerConstants.RIGHT_EYE
                    else:
                        which_eye=EyeTrackerConstants.LEFT_EYE

                    start_event_time= ne.getStartTime()*DEVICE_TIMEBASE_TO_SEC
                    end_event_time = ne.event_timestamp
                    event_duration = end_event_time-start_event_time

                    bee=[
                        0,
                        0,
                        Computer._getNextEventID(),
                        etype,
                        ne.event_timestamp,
                        ne.logged_time,
                        ne.timestamp,
                        confidenceInterval,
                        ne.event_delay,
                        0,
                        which_eye,
                        event_duration,
                        estatus
                        ]

                    self._addNativeEventToBuffer(bee)

                elif isinstance(ne,pylink.StartFixationEvent) or isinstance(ne,pylink.StartSaccadeEvent):
                    etype=EventConstants.FIXATION_START

                    if isinstance(ne,pylink.StartSaccadeEvent):
                        etype=EventConstants.SACCADE_START

                    which_eye=ne.getEye()
                    if which_eye:
                        which_eye=EyeTrackerConstants.RIGHT_EYE
                    else:
                        which_eye=EyeTrackerConstants.LEFT_EYE

                    pupil_size=-1
                    if etype == EventConstants.FIXATION_START:
                        pupil_size=ne.getStartPupilSize()
                    gaze=ne.getStartGaze()
                    href=ne.getStartHREF()
                    velocity=ne.getStartVelocity()
                    ppd=ne.getStartPPD()
                    estatus=ne.getStatus()

                    se=[
                        0,                                      # exp ID
                        0,                                      # sess ID
                        Computer._getNextEventID(),              # event ID
                        etype,                                  # event type
                        ne.event_timestamp,
                        ne.logged_time,
                        ne.timestamp,
                        confidenceInterval,
                        ne.event_delay,
                        0,
                        which_eye,                              # eye
                        gaze[0],                                # gaze x
                        gaze[1],                                # gaze y
                        EyeTrackerConstants.UNDEFINED,                                     # gaze z
                        href[0],                                # angle x
                        href[1],                                # angle y
                        EyeTrackerConstants.UNDEFINED,                                   # raw x
                        EyeTrackerConstants.UNDEFINED,                                   # raw y
                        pupil_size,                             # pupil area
                        EyeTrackerConstants.PUPIL_AREA,                    # pupil measure type 1
                        EyeTrackerConstants.UNDEFINED,                                   # pupil measure 2
                        EyeTrackerConstants.UNDEFINED,     # pupil measure 2 type
                        ppd[0],                                 # ppd x
                        ppd[1],                                 # ppd y
                        EyeTrackerConstants.UNDEFINED,                                    # velocity x
                        EyeTrackerConstants.UNDEFINED,                                    # velocity y
                       velocity,                                # velocity xy
                       estatus                                  # status
                        ]

                    self._addNativeEventToBuffer(se)

                elif isinstance(ne,pylink.StartBlinkEvent):
                    etype=EventConstants.BLINK_START

                    estatus = ne.getStatus()

                    which_eye=ne.getEye()
                    if which_eye:
                        which_eye=EyeTrackerConstants.RIGHT_EYE
                    else:
                        which_eye=EyeTrackerConstants.LEFT_EYE

                    bse=[
                        0,
                        0,
                        Computer._getNextEventID(),
                        etype,
                        ne.event_timestamp,
                        ne.logged_time,
                        ne.timestamp,
                        confidenceInterval,
                        ne.event_delay,
                        0,
                        which_eye,
                        estatus
                        ]

                    self._addNativeEventToBuffer(bse)

            pollEndLocalTime=Computer.currentSec()
            self._lastPollTime=pollEndLocalTime
        except Exception:
            ioHub.printExceptionDetailsToStdErr()
    
    def _handleNativeEvent(self,*args,**kwargs):
        pass
    
    def _getIOHubEventObject(self,*args,**kwargs):
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
        """
        
        # CASE 1: Polling is being used to get events:
        #
        if len(args)==1:
            event=args[0]
            
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

    def _eyelinkSetScreenPhysicalData(self):
        eyelink=self._eyelink

        # eye to screen distance
        sdist=EyeTracker._displaySettings.get('default_eye_to_surface_distance',None)
        if sdist:
            if 'surface_center' in sdist:
                eyelink.sendCommand("screen_distance = %d "%(sdist['surface_center'],))
        else:
            ioHub.print2err('ERROR: "default_eye_to_surface_distance":"surface_center" value could not be read from monitor settings')
            return False

        # screen_phys_coords
        sdim=EyeTracker._displaySettings.get('physical_stimulus_area',None)
        if sdim:
            if 'width' in sdim and 'height' in sdim:
                sw=sdim['width']
                sh=sdim['height']
                hsw=sw/2.0
                hsh=sh/2.0

                eyelink.sendCommand("screen_phys_coords = -%.3f, %.3f, %.3f, -%.3f"%(hsw,hsh,hsw,hsh))
        else:
            ioHub.print2err('ERROR: "physical_stimulus_area":"width" or "height" value could not be read from monitor settings')
            return False

        # calibration coord space
        width,height=ioHub.devices.Display.getStimulusScreenResolution()
        bounds=dict(left=-width/2,top=height/2,right=width/2,bottom=-height/2)
        eyelink.sendCommand("screen_pixel_coords %.0f %.0f %.0f %.0f" %(bounds['left'],bounds['top'],bounds['right'],bounds['bottom']))
        eyelink.sendMessage("DISPLAY_COORDS  %.0f %.0f %.0f %.0f" %(bounds['left'],bounds['top'],bounds['right'],bounds['bottom']))

        pylink.msecDelay(1)

    def _eyeLinkHardwareAndSoftwareVersion(self):
        tracker_software_ver = 0
        eyelink_ver = self._eyelink.getTrackerVersion()

        if eyelink_ver == 3:
            tvstr = self._eyelink.getTrackerVersionString()
            vindex = tvstr.find("EYELINK CL")
            tracker_software_ver = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))

        return eyelink_ver, tracker_software_ver

    def _eyelinkSetLinkAndFileContents(self):
        eyelink = self._eyelink

        eyelink_hw_ver, eyelink_sw_ver = self._eyeLinkHardwareAndSoftwareVersion()

        # set EDF file contents
        eyelink.sendCommand("file_event_filter = LEFT, RIGHT, FIXATION, SACCADE, BLINK, MESSAGE, BUTTON, INPUT")
        eyelink.sendCommand("file_event_data = GAZE , GAZERES , HREF , AREA  , VELOCITY , STATUS")

        if eyelink_sw_ver>=4:
            eyelink.sendCommand("file_sample_data = GAZE, GAZERES, HREF , PUPIL , AREA ,STATUS, BUTTON, INPUT, HTARGET")
        else:
            eyelink.sendCommand("file_sample_data = GAZE, GAZERES, HREF , PUPIL , AREA ,STATUS, BUTTON, INPUT")

        pylink.msecDelay(1)

        # set link data
        eyelink.sendCommand("link_event_filter = LEFT, RIGHT, FIXATION, SACCADE , BLINK, BUTTON, MESSAGE, INPUT")
        eyelink.sendCommand("link_event_data = GAZE, GAZERES, HREF , AREA, VELOCITY, STATUS")

        if eyelink_sw_ver>=4:
            eyelink.sendCommand("link_sample_data = GAZE, GAZERES, HREF , PUPIL , AREA ,STATUS, BUTTON, INPUT , HTARGET")
        else:
            eyelink.sendCommand("link_sample_data = GAZE, GAZERES, HREF , PUPIL , AREA ,STATUS, BUTTON, INPUT")

    def _addCommandFunctions(self):
        self._COMMAND_TO_FUNCTION['getTrackerMode']=_getTrackerMode
        self._COMMAND_TO_FUNCTION['doDriftCorrect']=_doDriftCorrect
        self._COMMAND_TO_FUNCTION['eyeAvailable']=_eyeAvailable
        self._COMMAND_TO_FUNCTION['enableDummyOpen']=_dummyOpen
        self._COMMAND_TO_FUNCTION['getLastCalibrationInfo']=_getCalibrationMessage
        self._COMMAND_TO_FUNCTION['applyDriftCorrect']=_applyDriftCorrect
        self._COMMAND_TO_FUNCTION['setIPAddress']=_setIPAddress
        self._COMMAND_TO_FUNCTION['setLockEye']=_setLockEye
        self._COMMAND_TO_FUNCTION['setLocalResultsDir']=_setNativeRecordingFileSaveDir

    def _readResultFromTracker(self,cmd,timeout=200):
        self._eyelink.readRequest(cmd)

        t = pylink.currentTime()
        # Waits for a maximum of timeout msec
        while(pylink.currentTime()-t < timeout):
            rv = self._eyelink.readReply()
            if rv and len(rv) >0:
                return rv
        return None

    def _setPupilDetection(self,pmode):
        if(pmode.upper() == "ELLIPSE"):
            self.sendCommand("use_ellipse_fitter = YES")
        else:
            self.sendCommand("use_ellipse_fitter = NO")

    def _getPupilDetectionModel(self):
        v = self._readResultFromTracker("use_ellipse_fitter")
        if v !="0":
            return "ELLIPSE"
        else:
            return "CENTROID"

    def _setEyeTrackingMode(self,r=0):
        ri=-1
        if r is "PUPIL-ONLY":
            ri=0
        elif r.upper is "PUPIL-CR":
            ri=1
        if ri>=0:
            self.sendCommand("corneal_mode %d"%(ri))
            return True
        return False
#================= Command Functions ==========================================

_EYELINK_HOST_MODES={
    "EL_IDLE_MODE" : 1,  
    "EL_IMAGE_MODE" : 2,  
    "EL_SETUP_MENU_MODE" : 3,  
    "EL_USER_MENU_1" : 5,  
    "EL_USER_MENU_2" : 6,  
    "EL_USER_MENU_3" : 7,  
    "EL_OPTIONS_MENU_MODE" : 8,  
    "EL_OUTPUT_MENU_MODE" : 9,  
    "EL_DEMO_MENU_MODE" : 10,  
    "EL_CALIBRATE_MODE" : 11,  
    "EL_VALIDATE_MODE" : 12,  
    "EL_DRIFT_CORR_MODE" : 13,  
    "EL_RECORD_MODE" : 14,  
    }

_eyeLinkCalibrationResultDict = dict()
_eyeLinkCalibrationResultDict[-1]="OPERATION_FAILED"
_eyeLinkCalibrationResultDict[0]="OPERATION_FAILED"
_eyeLinkCalibrationResultDict[1]="OK_RESULT"
_eyeLinkCalibrationResultDict[27]='ABORTED_BY_USER'

if 1 not in _EYELINK_HOST_MODES:
    t=dict(_EYELINK_HOST_MODES)
    for k,v in t.iteritems():
        _EYELINK_HOST_MODES[v]=k

def _getTrackerMode(*args, **kwargs):
    r=pylink.getEyeLink().getTrackerMode()
    return _EYELINK_HOST_MODES[r]

def _doDriftCorrect(*args,**kwargs):
    if len(args)==4:
        x,y,draw,allow_setup=args
        r=pylink.getEyeLink().doDriftCorrect(x,y,draw,allow_setup) 
        return r
    else:
        ioHub.print2err("doDriftCorrect requires 4 parameters, received: ", args)
        return False

def _applyDriftCorrect():
    r=pylink.getEyeLink().applyDriftCorrect()
    if r == 0:
        return True
    else:
        return ['EYE_TRACKER_ERROR','applyDriftCorrect',r]
        
def _eyeAvailable(*args,**kwargs):
    r=pylink.getEyeLink().eyeAvailable()
    if r== 0:
        return EyeTrackerConstants.getName(EyeTrackerConstants.LEFT_EYE)
    elif r==1:
        return EyeTrackerConstants.getName(EyeTrackerConstants.RIGHT_EYE)
    elif r == 2:
        return EyeTrackerConstants.getName(EyeTrackerConstants.BINOCULAR)
    else:
        return EyeTrackerConstants.UNDEFINED

def _dummyOpen(*args,**kwargs):
    r=pylink.getEyeLink().dummy_open()
    return r
    
def _getCalibrationMessage(*args,**kwargs):
    m=pylink.getEyeLink().getCalibrationMessage()
    r=pylink.getEyeLink().getCalibrationResult()
    if r in _eyeLinkCalibrationResultDict:
        r=_eyeLinkCalibrationResultDict[r]
    else:
        r = 'NO_REPLY'
    rString="Last Calibration Message:\n{0}\n\nLastCalibrationResult:\n{1}".format(m,r)
    return rString
    
def _setIPAddress(*args, **kwargs):
    if len(args)==1:
        ipString=args[0]
        r=pylink.getEyeLink().setAddress(ipString)
        if r == 0:
            return True
    return ['EYE_TRACKER_ERROR','setIPAddress','Could not Parse IP String']

def _setLockEye(*args,**kwargs):
    if len(args)==1:
        enable=args[0]
        r=pylink.getEyeLink().sendCommand("lock_eye_after_calibration %d"%(enable))
        return r
    return ['EYE_TRACKER_ERROR','setLockEye','One argument is required, bool type.']

def _setNativeRecordingFileSaveDir(*args):
    if len(args)>0:
        edfpath=args[0]
        ioHub.print2err("Setting File Save path: ",edfpath)
        EyeTracker._localEDFDir=edfpath