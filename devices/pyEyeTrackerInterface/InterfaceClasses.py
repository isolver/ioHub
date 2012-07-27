"""
pyEyeTracker: common Python interface for multiple eye tracking devices.

Part of the pyEyeTracker library 
Copyright (C) 2012 Sol Simpson 
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version). 

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""

from collections import deque, Counter
import sys

from . import ET_RTN_CODES,ET_EYE_CODES,\
                    ET_PUPIL_SIZE_MEASURES,ET_DATA_TYPES,ET_MODES,ET_CALIBRATION_TYPES,\
                    ET_CALIBRATION_MODES,ET_DATA_STREAMS,ET_REALTIME_FILTERS,ET_USER_SETUP_STATES



class EyeTracker(object):
    """EyeTracker class is the main class for the pyEyeTracker module, 
    containing the majority of the eye tracker functionality commonly needed
    for a range of experiments experiment.
       
    Not every eye tracker implemenation of the pyEyeTracker specification will
    support all of the specifications functionality. This is to be expected and
    pyEyeTracker has been designed to handle this case. When a specific
    implementation does not support a given method, if that method is called, 
    a default *not supported* behaviour is built into the base implemetation.
       
    On the other hand, some eye trackers offer very specialized functionality that
    is not of widespread interest or use across the eye tracking field. In these cases,
    the specific eye tracker implemetation can expose the non core pyEyeTracker 
    functionality for their device by adding extra sendCommand command types to the
    sendCommand method, or as a last resort. via the *EyeTracker.EXT* attribute of the class.

    .. note:: 
    
        Only **one** instance of EyeTracker can be created within an experiment. Attempting to create > 1 instance will raise an exception. To get the current instance of the EyeTracker you can call the class method EyeTracker.getInstance(); this is useful as it saves needing to pass an eyeTracker instance variable around your code. 
        
    Methods are broken down into several categories within the EyeTracker class:
    
    #. Eye Tracker Initalization / State Setting    
    #. Ability to Define the Graphics Layer for the Eye Tracker to Use During Calibration
    #. Starting and Stopping of Data Recording
    #. Sending Syncronization messages to the Eye Tracker
    #. Accessing the Eye Tracker Timebase
    #. Accessing Eye Tracker Data During Recording
    #. Syncronizing the Local Experiment timebase with the Eye Tracker Timebase, so Eye Tracker events can be provided with local time stamps when that is appropriate.
    #. Experiment Flow Generics 
    """    

    _INSTANCE=None #: Holds the reference to the current instance of the EyeTracker object in use and ensures only one is created.
    
    #: A dictionary holding various information about the specific eye tracker that is being usedwith thepyEyeTracker interface.
    _INFO={'manufacturer':'Unknown', \
    'model':'unknown', \
    'model_number':'unknown', \
    'hardware_revision': 'unknown', \
    'serial_number':'unknown', \
    'software_version':'unknown', \
    'notes':'unknown' \
    }
    
    _CAL_SURFACE_INFO={'SCREEN_RES':(0,0,1024,768), # L,T,R,B in pixels by default
                       'SCREEN_AREA':(0.0,0.0,0.0,0.0), # L,T,R,B
                       'MONITOR_SIZE':(0.0,0.0), #(w,h) in mm
                       'DEFAULT_EYE_TO_SCREEN_DIST_MM':(600,660) #(mm_dist_top,mm_dist_bottom) or just mm_dist
                       }
    
    #: Used by pyEyeTracker interface implemtations to store relationship between an eye 
    #: trackers command names supported for pyEyeTracker sendCommand method and the actual 
    #: 'native' tracker API function to call for that command. This allows an implemetation 
    #: of the interface to exposes functions that are not in the core pyEyeTracker spec 
    #: without have to use the EXT extension class.
    #: Any arguements passed into the sendCommand function are assumed to map
    #: directly to the native function        
    _COMMAND_TO_FUNCTION={}
    
    LAST_ERROR=ET_RTN_CODES.ET_NOT_IMPLEMENTED
    LAST_WARNING=ET_RTN_CODES.ET_NOT_IMPLEMENTED
    LAST_RETURN_VALUE=ET_RTN_CODES.ET_NOT_IMPLEMENTED
    
    _ERROR_CODES_TO_STRINGS={}
             
    RESULTS_DIR=None
    
    EXP_TIMEBASE_TO_MSEC=1.0
    TRACKER_TIMEBASE_TO_MSEC=1.0
    
    def __init__(self,experimentContext):
        """EyeTracker class. This class is to be extended by each eye tracker specific implemetation of the pyEyeTracker interface.
        
        Please review the documentation page for the specific eye tracker model that you are using the pyEyeTracker interface with to get
        the appropriate class name for that eye tracker; for example, if you are using an interface that supports eye trackers developed by
        EyeTrackingCompanyET, you may initialize the eye tracker object for that manufacturer something similar too ::
       
           eyeTracker = pyEyeTracker.EyeTrackingCompanyET.EyeTrackerInterface(core.Clock().getTime)

        Args:
           timebase_function (function reference): Reference to the function / method that should be called to get the current **experiment / stimulus computer** time. So::
              t=timebase_function()
              print t  # should print the current experiment computer high resolution time.
           
           **args (dict): dictionary of optional eye tracker specific arguements for use in this method.
           
        **If an instance of EyeTracker has already been created, trying to create a second will raise an exception. Either destroy the first instance and then create the new instance, or use the class method EyeTracker.getInstance() to access the existing instance of the ey tracker object.**
        """
        if EyeTracker._INSTANCE is not None:
            raise "pyEyeTracker object has already been created; only one instance can exist.\n \
            Delete existing instance before recreating pyEyeTracker object."
            sys.exit(1)  
        EyeTracker._INSTANCE=self
        
        EyeTracker._CAL_SURFACE_INFO['SCREEN_RES']=experimentContext.SCREEN_RESOLUTION
        EyeTracker._CAL_SURFACE_INFO['SCREEN_AREA']=experimentContext.SCREEN_AREA
        EyeTracker._CAL_SURFACE_INFO['MONITOR_SIZE']=experimentContext.MONITOR_DIMENTIONS
        EyeTracker._CAL_SURFACE_INFO['DEFAULT_EYE_TO_SCREEN_DIST_MM']=experimentContext.DEFAULT_SCREEN_DISTANCE

        EyeTracker.RESULTS_DIR=experimentContext.RESULTS_DIR
        
        self.localTime= experimentContext.GC_FUNC
        
        self.lastPollTime=None
        self.eventHandler=None
        
        self.SETUP_GRAPHICS=None # CETI Implementor to extend EyeTrackerSetupGraphics object for 
                                 # specific implementation; assign object instance to this attribute.
                                 
        self.EXT=None  # IF Vendor specific extensioin of API must be done, create an extension of EyeTrackerVendorExtension class and add an instance of it here. 
    
    @classmethod
    def getInstance(cls):
        """
        Returns the currently created instance the of EyeTracker object.
        """
        return EyeTracker._INSTANCE
    
    def experimentStartDefaultLogic(self,**args):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the start of an experiment.  
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
 
    def blockStartDefaultLogic(self,**args):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the start of an experiment block.  
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def trialStartDefaultLogic(self,**args):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the start of an experiment trial.  
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
         
    def trialEndDefaultLogic(self,**args):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the end of an experiment trial.  
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
         
    def blockEndDefaultLogic(self,**args):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the end of an experiment block.  
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def experimentEndDefaultLogic(self,**args):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the end of an experiment sessio.  
        """       
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def poll(self):
        """
        poll should be called on a regular basis (atleast once a refresh, ideally, once every msec or so). This allows the backend
        implementation of the interface to perform any necessary processing and housekeeping in a timely and regular fashion.
        
        In psychopy as of 1.7 atleast I believe), it is written around a refresh rate based blocking model, which means that when the user calls 
        win.flip() in their code, the user script blocks until the start of the next retrace. This has been implemeted in psychopy because the 
        blocking method of detecting the upcoming retrace start is simplier to implement, does not require different code to be written per platform,
        and is agruably more robust that the abailable non-blocking techniques. However there are some negative ramificatiosn to this approach when the whole
        design, as it stands now, is considered:
        
        #. user code only really has the oppertunity to be called once per refresh. In general this is not ideal for gaze contingent paradigms where
        the total delay from eye movement to screen update whould be as small as possible. Therefore, you need to use a system with a short sample 
        delay but also wait as long as possible before you pick the sample to base the screen change on before you can win.flip(). There is not much advantage
        to having a 1000 + Hz eye tracker for your gaze contingent work if you are using a sample that is 10 msec earlier in time than it needed to be.  
        to get the nost recebased on that data is as small as possible.

        #. Further more, if the underlying eye tracker backend is not performing buffering of incoming eye tracker data in a native seperate library 
        thread that is not GIL bound, then you will likely loose some eye tracker data in high sampling rate systems. In these cases, the interface 
        implementors should use a seperate thread that connects the native eye tracker interface to the pyEyeTracker interface. A python queue object
        (or two) can be used as a simple way to syncronize data access between the main thread and the eye tracker native interface thread. Several 
        manufacturers already handle sample buffering when you use their native library as the interface ( as examples SR Research, Tobii )
        however some do not ( as an example SMI UDP direct, however SMI C library (parrallel to the SR Research library) does buffer, but we plan 
        on using the UDP direct as the interface to the SMI for pyEyeTracker based on the existing python library written by Michael et al)  
        
        Respectfully to the great work done by the developers of psychopy, in my opinion, the blocking methodology is unnecessary given the negatives. 
        An asyncronous, threadless, approach to checking retrace state would address a fundamental issue with the current implementation. 
        I hope to be able to show how such an implementation could work, and work reliably, so that this could be improved.  While the above is not 
        ideal by any means, it is likely the best option until the general issue is resolved or until some extra functionality is added to pyEyeTracker
        to at least address the issue the blocking nature of the psychopy loop has on high sample rate data collection of non-buffered native eye 
        tracking data interfaces.

        As another related, but not duplicate effort, that I have been working on prototyping is a 'data center hub' concept that would integrate 
        all the inputs for an experiment as a seperate process running on the experiment PC, or even a seperate PC all together if desired, 
        perform some of the workload related to those inputs ( timebase coversion and alignment, etc ), and act as a service that could
        be subscribed to by the experiment, with events from all inputs being streamed to the experiment from the data hub. Other clients could
        also subscribe to the data hub for other purposed; for example as a way to feed the current status of the experiment and all related 
        devices to experiment monitoring device (a.k.a a tablet, or web browser on a lab computer). A more mundain, but immediately practical use
        for multiple client access would be to have a data storage client accessing the data stream, saving the data for offline analysis.
        
        ** This is a longer term project, but has multiple applications is unique as far as I am aware. **
        """
        
        self.eventHandler.poll()
        self.lastPollTime=self.localTime()
        
    def trackerTime(self):
        """
        Current msec.usec time of the EYE TRACKER in EYE TRACKER TIMESPACE. 
        Should be accurate to within +/- 0.5 msec to meet pyEyeTracker specification.
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
 
    def experimentTime(self):
        """
        Current msec.usec time of the EXPERIMENT / STIMULUS PC CLOCK that was passed into the constructor of EyeTracker.
        This is simply the return value of the timer_base function handle that was passed into the EyeTracker object 
        when the instance was created. 
        Should be accurate to within +/- 0.05 msec to meet pyEyeTracker specification.
        """
        return self.localTime()*EXP_TIMEBASE_TO_MSEC
  
    def enableConnection(self,state,**args):
        """
        enableConnection is used to connect ( enableConnection(True) ) or disable ( enableConnection(False) )
        the connection of the pyEyeTracker software to the eyetracker.
        
        Args:
        
            state (bool): True = enable the connection, False = disable the connection.
            args (dict): any eye tracker specific parameters that should be passed.
        """
        if state is True or state is False:
            return ET_RTN_CODES.ET_NOT_IMPLEMENTED
        else:
            raise BaseException("enableConnection state must be a bool of True or False")
            
    def isConnected(self):
        """
        isConnected returns whether the pyEyeTracker is connected to the eye tracker (returns True) or not (returns False)
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
            
    def sendCommand(self, command, value, wait=True, **args):
        """
        sendCommand sends a text command and text command value to the eye tracker. Depending on the command and on the eye trackers
        implementation, when a command is send, the eye tracker may or n=may not response indicating the status of the command. If the
        command is not going to return a response from the eye tracker, the method will return ET_RTN_CODES.ET_RESULT_UNKNOWN.
        Please see the specific eye tracker implementation you are working with for a list of supported command's and value's.
        
        Args:
        
           command (str): string command to send to the eye tracker. See the specific eye tracker documentation for pyEyeTracker for a list of valid commands.
           value (str): the string form of the value of the command to send.
           wait (bool or callable): if bool, True = do not rteurn from function until result of command if know (if it can be known); False = return immediately after sending the command, ignoring any possible return value. If wait is a callable, then wait fould be a reference to the callback function you want called when the return value is available. If no return value is possible for the command, wait is ignorded and ET_RTN_CODES.ET_RESULT_UNKNOWN is returned immediately..           
        
        Return: a value from et_constants.ET_RTN_CODES. 
        #. If the return value is "ET_RTN_VALUE", call EyeTracker.getLastCommandReturnValue() for the value returned.
        #. If the return value is "ET_ERROR", call EyeTracker.getLastErrorString() for the description of the error.
        #. If the return value is "ET_WARNING", call getLastWarningString() for the description of the warning.      
        """
        if command in EyeTracker.COMMAND_TO_FUNCTIONS:
            pass
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
        
    def sendMessage(self, message, time_offset=0,**args):
        """
        sendMessage sends a text message to the eye tracker. Depending on the eye trackers implementation, when a message is send,
        the eye tracker may or may not response indicating the message was received. If the
        message is not going to receive a response from the eye tracker, the method will return ET_RTN_CODES.ET_RESULT_UNKNOWN.
        Messages are generally used to send general text information you want saved with the eye data file  but more importantly
        are often used to syncronize stimulus changes in the experiment with the eye data stream. This means that the sendMessage 
        implementation needs to perform in real-time, with a delay of <1 msec from when a message is sent to when it is logged in
        the eye tracker data file, for it to be accurate in this regard. If this standard can not be met, the expected delay and
        message precision (variability) should be provided in the eye tracker's implementation notes for the pyEyeTRacker interface.  
        
        Args:
        
           message (str): string command to send to the eye tracker. The default maximum length of a message string is 128 characters.
           time_offset (int): number of int msec that the timestampe of the message should be offset by. This can be used so that a message can be sent for a display change **BEFORE** or **AFTER** the aftual flip occurred (usually before), by sending the message, say 4 msec prior to when you know the next trace will occur, entering -4 into the offset field of the message, and then send it and calling flip() 4 msec before the retrace to ensure that the message time stampe and flip are both sent and schuled in advance. (4 msec is quite large buffer even on windows these days with morern hardware BTW)
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
        
    def createRecordingFile(self, fileName, path=None, **args):
        """
        createRecordingFile instructs the eye tracker to open a new file on the eye tracker computer to save data collected to
        during the recording. If recording is started and stopped multiple times while a single recording file is open, each 
        start/stop recording pair will be represented within the single single file. A recording file is closed by calling
        closeRecordingFile(). Normally you would open a rtecoring file at the start of an experimental session and close it
        at the end of the experiment; starting and stopping recording of eye data between trials of the experiment.
        
        Args:
        
           fileName (str): Name of the recording file to save on the eye tracker. This does *not* include the path to the file. Some eye trackers have limitations to the length of their file name, so please refer to the specific implemtations documenation for any caviates.
           path (str): This optional parameter can be used to specify the path to the recording file that should be saved. The path must already exist. If this paramemter is not specified, then the defualt file location is used. 
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
        
    def closeRecordingFile(self,**args):
        """
        closeRecordingFile is used to close the currently open file that is being used to save data from the eye track to the eye tracker computer. 
        Once a file has been closed, getFile(localFileName,fileToTransfer) can be used to transfer the file from the eye tracker computer to the 
        experiment computer at the end of the experiment session.
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
    
    def getFile(self,localFileName,fileToTransfer, **args):
        """
        getFile is used to transfer the file from the eye tracker computer to the experiment computer at the end of the experiment session.

        Args:
        
           localFileName (str): Name of the recording file to experiment computer.
           fileToTransfer (str): Name of the recording file to transfer from the eye tracker.
        """   
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
    
    def runSetupProcedure(self, mode=ET_SETUP_STATES.DEFAULT, calibrationType=ET_CALIBRATION_TYPES.HV9, targetPoints=None, randomizePoints=False,**kwargs):
        if self.SETUP_GRAPHICS is not None:
            result = self.SETUP_GRAPHICS.run(mode,calibrationType,targetPoints,randomizePoints,**kwargs)
            return result 
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def stopSetupProcedure(self,**args):
        if self.SETUP_GRAPHICS is not None:
            result = self.SETUP_GRAPHICS.stop()
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
                
    def enableRecording(self,enable=False,**args):
        """
        enableRecording is used to start or stop the recording of data from the eye tracking device. Use sendCommand() set sned the necessary information 
        for your eye tracker to enable who data you would like saved, send over to the experiment computer during recording, etc.
        
        Args:
           enable (bool): if True, the eye tracker should start recordng data.; false = stop recording data.
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def isRecordingEnabled(self,**args):
       """
       enableRecording is used to start or stop the recording of data from the eye tracking device. Use sendCommand() set sned the necessary information 
       for your eye tracker to enable who data you would like saved, send over to the experiment computer during recording, etc.
        
       Return: a value from et_constants.ET_RTN_CODES. 
       #. If the return value is "ET_RTN_VALUE", call EyeTracker.getLastReturnValue() for the value returned; True = the eye tracker is recording; False = it is not
       #. If the return value is "ET_ERROR", call EyeTracker.getLastErrorString() for the description of the error.
       #. If the return value is "ET_WARNING", call getLastWarningString() for the description of the warning.      
       """
       return ET_RTN_CODES.ET_NOT_IMPLEMENTED
     
    def getDataFilteringLevel(self,data_stream=ET_DATA_STREAMS.ALL,**args):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def setDataFilteringLevel(self,level,data_stream=ET_DATA_STREAMS.ALL,**args):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
    
    def drawToGazeOverlayScreen(self, drawingcommand='UNIMPLEMENTED', position=None,  value=None, **args):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
    
    def getDigitalPortState(self, port, **args):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
 
    def setDigitalPortState(self, port, value, **args):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
    
    def getEventHandler(self):
        return self.eventHandler
    
    @classmethod
    def _ERROR(_class,value):
        _class.LAST_ERROR=value
        return value

    @classmethod
    def _WARNING(_class,value):
        _class.LAST_WARNING=value
        return value

    @classmethod
    def _OK(_class,value):
        _class.LAST_RETURN_VALUE=value
        return value
     
    @classmethod
    def getLastError(_class, clearState=False):
        r= _class.LAST_ERROR
        if clearState==True:
            _class.LAST_ERROR=None 
        return _class.LAST_ERROR
    
    @classmethod   
    def getLastWarning(_class, clearState=False):
        r= _class.LAST_WARNING
        if clearState==True:
            _class.LAST_WARNING=None 
        return _class.LAST_WARNING
    
    @classmethod 
    def getLastReturnValue(_class, clearState=False):
        r= _class.LAST_RETURN_VALUE
        if clearState==True:
            _class.LAST_RETURN_VALUE=None 
        return _class.LAST_RETURN_VALUE
        
    def __del__(self):
        """
        Do any final cleanup of the eye tracker before the object is destroyed. Users should not call or change this method. It is for implemetaion by interface creators and is autoatically called when an object is destroyed by the interpreter.
        """
        EyeTracker._INSTANCE=None
        self.eventHandler=None
        
class EyeTrackerEventHandler:
    _PY_EYETRACKER=None
    
    def __init__(self,eyetracker, userEventHandler=None):
                
        # event queue point back to pyEyeTracker dataQueue 
        self.processedDataBuffer=dequeue(2048)

        self.eventCounts=Counter(ET_DATA_TYPES.ENUM_LIST)
        
        EyeTrackerEventHandler._PY_EYETRACKER=eyetracker
        
        self.userEventHandler=userEventHandler
        
        self.latestSample=None
         
        self.localTimeFunction=eyetracker.experimentTime  # function pointer to timer to use for converting eye tracker 
                                # time stamps to local / experiment time. should provide time 
                                # as msec.usec floats 
        
        self.eyetrackerTimeFunction=eyetracker.trackerTime
        
        self.timebaseOffset=0  # offset / different between API and EYE_TRACKER time
                                # this should be calulated when pyEyeTracker instance is created
                                # and use best mention available to underlying interface to get an accurate, 
                                # precise offset. Notethat the offset could be updated every second to adjust
                                # for slow drift between the the two clocks.
    
        self.updateTimeBaseOffset()
        self.lastTimeBaseUpdate=self.localTimeFunction()
        
        self.lastPollTime=self.lastTimeBaseUpdate
    
    def setUserEventHandler(self, userEventHandler):
        self.userEventHandler=userEventHandler     
    
    def poll(self):
        '''
        poll should be called on a regular basis so that processing and housekeeping can occur 
        by the _eyetrackerEventProcessor class.
        '''        
        self.lastPollTime=self.localTimeFunction()
        
        #update timebase delta every 1000 msec
        if self.lastPollTime - self.lastTimeBaseUpdate >= 1000.0:
            self.updateTimeBaseOffset()
            self.lastTimeBaseUpdate=self.lastPollTime
       
        newEyeTrackerEvents=self.getConvertedNativeEvents()
        if newEyeTrackerEvents is not ET_RTN_CODES.ET_NOT_IMPLEMENTED:
            self.processedDataBuffer.extend(newEyeTrackerEvents)
        
        newUserEvents=[]
        if self.userEventHandler:
            newUserEvents=self.userEventHandler.poll()
            if newUserEvents is not ET_RTN_CODES.ET_NOT_IMPLEMENTED:
                self.processedDataBuffer.extend(newUserEvents)
        
             
    def getLocalTime(self):
        return self.localTimeBaseFunction()
        
    def getEyeTrackerTime(self):
        return self.eyeTrackerTimeFunction()
        
    def getLatestSample(self):
        return self.latestSample
        
    def getLatestEvent(self,peak=False):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def getBufferedData(self,filter=None,clear=True):
        elist=[]
        while len(self.processedDataBuffer)>0:
            elist.append(self.processedDataBuffer.popleft())
        if filter is None:
            if clear is True:
                self.processedDataBuffer.clear()
            return elist
        else:
            return ET_RTN_CODES.ET_NOT_IMPLEMENTED
    
    def clearDataBuffer(self):
        self.processedDataBuffer.clear()
    
    def updateTimeBaseOffset(self, **args):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
        
    def getConvertedNativeEvents(self):
        # get events from eye tracker, create appropriate evnt type for each
        # and set the correct localTime based on the current offset.
        nevents=list((ET_RTN_CODES.ET_NOT_IMPLEMENTED,))        
        return nevents
        
    def __del__(self):
        try:
            self.close()
        except:
            pass
            
class UserEventHandler:
    def __init__(self, localTimeFunction, eventTypes, callback, callbackData=None):
        self.callback=callback
        self.eventTypes=eventTypes
        self.callbackData=callbackData
        self.localTimeFunction=localTimeFunction
        
    def poll(self):        
        newUserEvents=list()        
        newUserEvents = self.callback(self.localTimeFunction, self.callbackData)
        
        return newUserEvents
 
class EyeTrackerSetupGraphics(object):
    '''
    EyeTrackerUserSetupGraphics provides a minimalistic standard 'public' interface
    that can be used for taking conrol of the experiment runtime graphics environment
    and keyboard / mouse by the eye tracker interface during 'black box' modes such as
    camera setup, calibration, validation, etc. 

    Developers of eye tracker interfaces for CETI can extend this class and implement 
    the specifics necessary to have the eye tracker perform whatever functionality is 
    supported by the eye tracker in terms of user facing graphics for these types of tasks.
    
    * Users 'enter' the graphics mode provided by the EyeTrackerUserCalibrationGraphics class by 
      calling a method of the eyetracker object from their experiment script:

      runUserSetupProcedure(mode=ET_USER_SETUP_STATES.DEFAULT, calibrationType=ET_CALIBRATION_TYPES.HV9, targetPoints=None, randomizePoints=False,**kwargs):

      which in turn calls 
    * This call blocks the user script, handing over control of the graphics state to the eye tracker. 
      The user script will remail blocked until you call the objects returnToUserSpace() method, or the user
      manages to call the eyetracker.cancelCalibration() method.
      
    * Devlopers can access keyboard and mouse events occurring on the experiment computer by calling:
    
      events = getKeyboardMouseEvents() # returns all keyboard and mouse events since the last call or since
      the last time clearKeyboardAndMouseEvents() was called.
      
    
    '''
    def __init__(self):
        pass
        
    def run(self,mode, calibrationType, targetPoints, randomizePoints,**kwargs):
        print "EyeTrackerSetupGraphics.run is not implemented."
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED    
        
    def stop(self, returnMessage):
        print "EyeTrackerSetupGraphics.stop is not implemented."
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def getKeyboardMouseEvents(self):
        print "EyeTrackerSetupGraphics.getKeyboardMouseEvents is not implemented."
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
    
class EyeTrackerVendorExtension(object):
    '''
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
    '''
    
    def __init__(self):
        pass
