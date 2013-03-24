"""
ioHub Python Module

Copyright (C) 2012  Stefan Wiedemann (Interactive Minds Dresden GmbH), Markus Joos (Interactive Minds Dresden GmbH), Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""

import sys,gc
import numpy as N
import ioHub
from ..... import Device, Computer
from ....eye_events import *

from .... import RTN_CODES, EYE_CODES, PUPIL_SIZE_MEASURES, DATA_TYPES, \
              ET_MODES, CALIBRATION_TYPES, CALIBRATION_MODES, DATA_STREAMS, \
              DATA_FILTER, USER_SETUP_STATES

from ctypes import *
from lctigazeapi import  *

class EyeTracker(Device):
    '''EyeTracker class is the main class for the pyEyeTrackerInterface module,
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
    '''
    # >>> implementation specific private class attributes
    _lctigazeAPI = None
    sample_rate = None
    egc= stEgControl()

    DEVICE_TIMEBASE_TO_SEC=0.00001
    EVENT_CLASS_NAMES=['BinocularEyeSampleEvent',]
    __slots__=[]
    def __init__(self,*args,**kwargs):
        '''
        EyeTracker class. This class is to be extended by each eye tracker specific implemetation
        of the pyEyeTrackerInterface.

        Please review the documentation page for the specific eye tracker model that you are using the
        pyEyeTrackerInterface with to get the appropriate module path for that eye tracker; for example,
        if you are using an interface that supports eye trackers developed by EyeTrackingCompanyET, you
        may initialize the eye tracker object for that manufacturer something similar too :

           eyeTracker = hub.eyetrackers.EyeTrackingCompanyET.EyeTracker(**kwargs)

        where hub is the instance of the ioHubClient class that has been created for your experiment.

        **kwargs are an optional set of named parameters.

        **If an instance of EyeTracker has already been created, trying to create a second will raise an exception. Either destroy the first instance and then create the new instance, or use the class method EyeTracker.getInstance() to access the existing instance of the eye tracker object.**
        '''

        Device.__init__(self,*args,**kwargs)

        EyeTracker._lctigazeAPI = cdll.LoadLibrary("lctigaze.dll")

        EyeTracker.sample_rate = c_int(_lctigazeAPI.lctNVisionSystems()) * 60


    def experimentStartDefaultLogic(self,*args,**kwargs):
        '''
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the start of an experiment.
        '''

        egc.iNDataSetsInRingBuffer=100
        egc.bTrackingActive=False
        egc.iScreenWidthPix=1920   # must ne filled with proper data
        egc.iScreenHeightPix=1080  # must ne filled with proper data
        egc.bEgCameraDisplayActive=0
        egc.iCommType=EG_COMM_TYPE_LOCAL
        egc.iVisionSelect=0
        egc.pszCommName=u''

        res = self.setConnectionState(True)
        res = self.setRecordingState(True)

        return RTN_CODES.ET_OK  # this should return the result of the setConnectionState call

    def blockStartDefaultLogic(self,*args,**kwargs):
        '''
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the start of an experiment block.
        '''
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def trialStartDefaultLogic(self,*args,**kwargs):
        '''
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the start of an experiment trial.
        '''
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def trialEndDefaultLogic(self,*args,**kwargs):
        '''
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the end of an experiment trial.
        '''
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def blockEndDefaultLogic(self,*args,**kwargs):
        '''
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the end of an experiment block.
        '''
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def experimentEndDefaultLogic(self,*args,**kwargs):
        '''
        Experiment Centered Generic method that can be used to perform a set of
        eye tracker default code associated with the end of an experiment session.
        '''
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def trackerTime(self):
        '''
        Current eye tracker time (timebase is eye tracker dependent)
        '''
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def trackerUsecTimeSinceDeviceInit(self):
        '''
        Current eye tracker time, normalized. (in usec for since ioHub initialized Device)
        '''
        return RTN_CODES.ET_NOT_IMPLEMENTED


    def setConnectionState(self,*args,**kwargs):
        '''
        setConnectionState is used to connect ( setConnectionState(True) ) or disable ( setConnectionState(False) )
        the connection of the pyEyeTrackerInterface to the eyetracker.

        args:
            enabled (bool): True = enable the connection, False = disable the connection.
        kwargs (dict): any eye tracker specific parameters that should be passed.
        '''
        enabled=None
        if len(args)>0:
            enabled=args[0]
        if enabled is True:
            return = c_int(EyeTracker._lctigazeAPI.EgInit(byRef(egc)))
        elif enabled is False:
            return = c_int(EyeTracker._lctigazeAPI.EgExit(byRef(egc)))
        else:
            return ['EYETRACKER_ERROR','Invalid arguement type','setConnectionState','enabled',enabled,args]

    def isConnected(self):
        '''
        isConnected returns whether the pyEyeTrackerInterface is connected to the eye tracker (returns True) or not (returns False)
        '''
        return return RTN_CODES.ET_NOT_IMPLEMENTED

    def sendCommand(self, *args, **kwargs):
        '''
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
        '''
        if len(args)>=2:
            command=args[0]
            value=args[1]
        else:
            return ('EYETRACKER_ERROR','EyeTracker.sendCommand','requires args of length >=2, command==args[0],value==args[1]')
        wait=False
        if wait in kwargs:
            wait=kwargs['wait']

        return RTN_CODES.ET_NOT_IMPLEMENTED

    def sendMessage(self,*args,**kwargs):
        '''
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
        '''
        message=args[0]

        time_offset=0
        if time_offset in kwargs:
            time_offset=kwargs['time_offset']

        return RTN_CODES.ET_NOT_IMPLEMENTED

    def createRecordingFile(self, *args,**kwargs):
        '''
        createRecordingFile instructs the eye tracker to open a new file on the eye tracker computer to save data collected to
        during the recording. If recording is started and stopped multiple times while a single recording file is open, each
        start/stop recording pair will be represented within the single file. A recording file is closed by calling
        closeRecordingFile(). Normally you would open a rtecoring file at the start of an experimental session and close it
        at the end of the experiment; starting and stopping recording of eye data between trials of the experiment.

        kwargs:
           fileName (str): Name of the recording file to save on the eye tracker. This does *not* include the path to the file. Some eye trackers have limitations to the length of their file name, so please refer to the specific implemtations documenation for any caviates.
           path (str): This optional parameter can be used to specify the path to the recording file that should be saved. The path must already exist. If this paramemter is not specified, then the defualt file location is used.
        '''
        fileName=None
        if fileName in kwargs:
            fileName= kwargs['fileName']
        else:
            return ('EYETRACKER_ERROR','EyeTracker.createRecordingFile','fileName must be provided as a kwarg')

        return RTN_CODES.ET_NOT_IMPLEMENTED

    def closeRecordingFile(self,*args,**kwargs):
        '''
        closeRecordingFile is used to close the currently open file that is being used to save data from the eye track to the eye tracker computer.
        Once a file has been closed, getFile(localFileName,fileToTransfer) can be used to transfer the file from the eye tracker computer to the
        experiment computer at the end of the experiment session.

        kwargs:
           fileName (str): Name of the recording file to save on the eye tracker. This does *not* include the path to the file. Some eye trackers have limitations to the length of their file name, so please refer to the specific implemtations documenation for any caviates.
           path (str): This optional parameter can be used to specify the path to the recording file that should be saved. The path must already exist. If this paramemter is not specified, then the defualt file location is used.
        '''
        return RTN_CODES.ET_NOT_IMPLEMENTED


    def getFile(self,*args,**kwargs):
        '''
        getFile is used to transfer the file from the eye tracker computer to the experiment computer at the end of the experiment session.

        kwargs:
           localFileName (str): Name of the recording file to experiment computer.
           fileToTransfer (str): Name of the recording file to transfer from the eye tracker.
        '''

        fileToTransfer=None
        if fileToTransfer in kwargs:
            fileToTransfer=kwargs['fileToTransfer']

        localFileName=None
        if localFileName in kwargs:
            localFileName=kwargs['localFileName']

        return RTN_CODES.ET_NOT_IMPLEMENTED


    def runSetupProcedure(self, *args ,**kwargs):
        '''
        runSetupProcedure passes the graphics environment over to the eye tracker interface so that it can perform such things
        as camera setup, calibration, etc. This is a blocking call that will not return until the setup procedure is done; at which time
        the graphics environment can be taken back over by psychopy.  See the EyeTrackerSetupGraphics class for more information.

        The graphicsContext arguement should likely be the psychopy full screen window instance that has been created
        for the experiment.
        '''
        graphicsContext=None
        if len(args)>0:
            graphicsContext=args[0]
        else:
            return ['EYETRACKER_ERROR','runSetupProcedure requires graphicsContext==args[0]']

        if self._setupGraphics is None:
            self._setupGraphics=EyeTrackerSetupGraphics(graphicsContext=graphicsContext,**kwargs)
        r=self._setupGraphics.run()
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def stopSetupProcedure(self):
        '''
        stopSetupProcedure allows a user to cancel the ongoing eye tracker setup procedure. Given runSetupProcedure is a blocking
        call, the only way this will happen is if the user has another thread that makes the call, perhaps a watch dog type thread.
        So in practice, calling this method is not very likely I do not think.
        '''
        result=None
        if self._setupGraphics is not None:
            result = self._setupGraphics.stop()
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def setRecordingState(self,*args,**kwargs):
        '''
        setRecordingState is used to start or stop the recording of data from the eye tracking device. Use sendCommand() set the necessary information
        for your eye tracker to enable what data you would like saved, send over to the experiment computer during recording, etc.

        args:
           recording (bool): if True, the eye tracker should start recordng data.; false = stop recording data.
        '''
        if len(args)==0:
            return ('EYETRACKER_ERROR','EyeTracker.setRecordingState','recording(bool) must be provided as a args[0]')
        enable=args[0]
        if enable = True:
            egc.bTrackingActive = True
            EyeTracker.recording = True
            return True
        else if enable = False:
            egc.bTrackingActive = False
            EyeTracker.recording = False
            return False
        else:
            return ['EYETRACKER_ERROR', 'Invalid argument type', 'setConnectionState', 'enabled', recording, kwargs]

    def isRecordingEnabled(self,*args,**kwargs):
       '''
       isRecordingEnabled returns the recording state from the eye tracking device.
       True == the device is recording data
       False == Recording is not occurring
       '''
       return RTN_CODES.ET_NOT_IMPLEMENTED

    def getDataFilterLevel(self,*args,**kwargs):
        '''
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
        '''
        data_stream=DATA_STREAMS.ALL
        if 'data_stream' in kwargs:
            data_stream=kwargs['data_stream']
        elif len(args)>0:
            data_stream=args[0]

        return RTN_CODES.ET_NOT_IMPLEMENTED

    def setDataFilterLevel(self,*args,**kwargs):
        '''
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
        '''
        if len(args)==0:
            return ['EYETRACKER_ERROR',"EyeTracker.setDataFilterLevel", "level = args[0], but no args provided")
        level=args[0]

        # example code below......
        supportedLevels=(DATA_FILTER.OFF,DATA_FILTER.LEVEL_1,DATA_FILTER.LEVEL_2)
        if level not in supportedLevels:
            return ['EYETRACKER_ERROR',"EyeTracker.setDataFilterLevel", "Invalid level value provided; must be one of (DATA_FILTER.OFF,DATA_FILTER.LEVEL_1,DATA_FILTER.LEVEL_2)")

        data_stream=DATA_FILTER.ALL
        if data_stream in kwargs:
            data_stream=kwargs['data_stream']
        supportedFilterStreams=(DATA_STREAMS.ALL,DATA_STREAMS.NET,DATA_STREAMS.ANALOG)
        if data_stream not in supportedFilterStreams:
            return ['EYETRACKER_ERROR',"EyeTracker.setDataFilterLevel", "Invalid data_stream value provided; must be one of (DATA_STREAMS.ALL,DATA_STREAMS.NET,DATA_STREAMS.ANALOG)")

        lindex = supportedLevels.index(level)

        return RTN_CODES.ET_NOT_IMPLEMENTED

    def getLatestSample(self, *args, **kwargs):
        '''
        Returns the latest sample retieved from the eye tracker device.
        '''
        return RTN_CODES.ET_NOT_IMPLEMENTED #return self._latestSample

    def drawToGazeOverlayScreen(self,*args,**kwargs):
        '''
        drawToGazeOverlayScreen provides a generic interface for ET devices that support
        having graphics drawn to the Host / Control computer gaze overlay area, or other similar
        graphics area functionality.

        The method should return the appropriate return code if successful or if the command failed,
        or if it is unsupported.

        There is no set list of values for any of the arguements for this command, so please refer to the
        ET imlpementation notes for your device for details. Hypothetical examples may be:
        '''
        drawingcommand=None
        if len(args)==0:
            return ('EYETRACKER_ERROR','drawToGazeOverlayScreen','args must have length > 0: drawingcommand = args[0]')
        else:
            drawingcommand=args[0]

        return RTN_CODES.ET_NOT_IMPLEMENTED

    def getDigitalPortState(self, *args, **kwargs):
        '''
        getDigitalPortState returns the current value of the specified digital port on the ET computer.
        This can be used to read the parallel port or idigial lines on the ET host PC if the ET has such functionality.

        args:
            port = the address to read from on the host PC. Consult your ET device documentation for appropriate values.
        '''
        if len(args)==0:
            return ('EYETRACKER_ERROR','getDigitalPortState','port=args[0] is required.')
        port = int(args[0])
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def setDigitalPortState(self, *args, **kwargs):
        '''
        setDigitalPortState sets the value of the specified digital port on the ET computer.
        This can be used to write to the parallel port or idigial lines on the ET Host / Operator PC if the ET
        has such functionality.

        args:
            port = the address to write to on the host PC. Consult your ET device documentation for appropriate values.
            value = value to assign to port
        '''
        if len(args)<2:
            return ('EYETRACKER_ERROR','setDigitalPortState','port=args[0] and value=args[1] are required.')
        port = int(args[0])
        value = int(args[1])
        return RTN_CODES.ET_NOT_IMPLEMENTED

