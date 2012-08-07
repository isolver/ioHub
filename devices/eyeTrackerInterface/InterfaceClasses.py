"""
ioHub Python Module

Copyright (C) 2012 Sol Simpson 
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version). 

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""

import sys
import numpy as N
import ioHub
from .. import Device

from . import RTN_CODES,EYE_CODES,PUPIL_SIZE_MEASURES,DATA_TYPES,\
              ET_MODES,CALIBRATION_TYPES,CALIBRATION_MODES,DATA_STREAMS,\
              DATA_FILTER,USER_SETUP_STATES




class EyeTracker(Device):
    """EyeTracker class is the main class for the pyEyeTrackerInterface module, 
    containing the majority of the eye tracker functionality commonly needed
    for a range of experiments.
       
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

    
    #: A dictionary holding various information about the specific eye tracker that is being usedwith thepyEyeTracker interface.
    DEVICE_INFO={'manufacturer':'Unknown', \
    'model':'unknown', \
    'model_number':'unknown', \
    'hardware_revision': 'unknown', \
    'serial_number':'unknown', \
    'software_version':'unknown', \
    'notes':'unknown' \
    }
    CAL_SURFACE_INFO={'SCREEN_RES':(0,0,1024,768), # L,T,R,B in pixels by default
                       'SCREEN_AREA':(0.0,0.0,0.0,0.0), # L,T,R,B
                       'MONITOR_SIZE':(0.0,0.0), #(w,h) in mm
                       'DEFAULT_EYE_TO_SCREEN_DIST_MM':(600,660) #(mm_dist_top,mm_dist_bottom) or just mm_dist
                       }  
    #: Used by pyEyeTrackerInterface implentations to store relationships between an eye 
    #: trackers command names supported for pyEyeTrackerInterface sendCommand method and  
    #: a private python function to call for that command. This allows an implemetation 
    #: of the interface to expose functions that are not in the core pyEyeTrackerInterface spec 
    #: without have to use the EXT extension class.
    #: Any arguements passed into the sendCommand function are assumed to map
    #: directly to the native function        
    _INSTANCE=None #: Holds the reference to the current instance of the EyeTracker object in use and ensures only one is created.
    _COMMAND_TO_FUNCTION={}                  
    EXT=None  # IF Vendor specific extensioin of API must be done, create an extension of EyeTrackerVendorExtension class and add an instance of it here. 
    _setupGraphics=None # instance of EyeTrackerSetupGraphics class, if supported                                  
    
    dataType = Device.dataType+[]
    attributeNames=[e[0] for e in dataType]
    ndType=N.dtype(dataType)
    fieldCount=ndType.__len__()
    __slots__=attributeNames
    
    categoryTypeString='EYE_TRACKER'
    deviceTypeString='EYE_TRACKER_DEVICE'
    def __init__(self,*args,**kwargs):
        """EyeTracker class. This class is to be extended by each eye tracker specific implemetation
        of the pyEyeTrackerInterface.
        
        Please review the documentation page for the specific eye tracker model that you are using the 
        pyEyeTrackerInterface with to get the appropriate module path for that eye tracker; for example,
        if you are using an interface that supports eye trackers developed by EyeTrackingCompanyET, you
        may initialize the eye tracker object for that manufacturer something similar too :
       
           eyeTracker = hub.eyetrackers.EyeTrackingCompanyET.EyeTracker(**kwargs)
        
        where hub is the instance of the ioHubClient class that has been created for your experiment.
        
        **kwargs are an optional set of named parameters.
        
        **If an instance of EyeTracker has already been created, trying to create a second will raise an exception. Either destroy the first instance and then create the new instance, or use the class method EyeTracker.getInstance() to access the existing instance of the eye tracker object.**
        """
        if EyeTracker._INSTANCE is not None:
            raise "EyeTracker object has already been created; only one instance can exist.\n \
            Delete existing instance before recreating EyeTracker object."
            sys.exit(1)  
        EyeTracker._INSTANCE=self
        
        deviceConfig=kwargs['dconfig']
        deviceSettings={'instance_code':deviceConfig['instance_code'],
            'category_id':ioHub.DEVICE_CATERGORY_ID_LABEL[EyeTracker.categoryTypeString],
            'type_id':ioHub.DEVICE_TYPE_LABEL[EyeTracker.deviceTypeString],
            'device_class':deviceConfig['device_class'],
            'user_label':deviceConfig['name'],
            'os_device_code':'OS_DEV_CODE_NOT_SET',
            'max_event_buffer_length':deviceConfig['event_buffer_size']
            }
        Device.__init__(self,**deviceSettings)
       
        #EyeTracker.CAL_SURFACE_INFO['SCREEN_RES']=experimentContext.SCREEN_RESOLUTION
        #EyeTracker.CAL_SURFACE_INFO['SCREEN_AREA']=experimentContext.SCREEN_AREA
        #EyeTracker.CAL_SURFACE_INFO['MONITOR_SIZE']=experimentContext.MONITOR_DIMENTIONS
        #EyeTracker.CAL_SURFACE_INFO['DEFAULT_EYE_TO_SCREEN_DIST_MM']=experimentContext.DEFAULT_SCREEN_DISTANCE

         
    def _getRPCInterface(self):
        """
        Called by the ioHubClient to get the list of valid RPC methods to call. 
        This is a default implementation.
        An implemetation can extend it's logic, but should not remove existing logic.
        """
        rpcList=[]
        dlist = dir(self)
        for d in dlist:
            if d[0] is not '_' and not d.startswith('I_'):
                if callable(getattr(self,d)):
                    rpcList.append(d)
        return rpcList
        
    def experimentStartDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the start of an experiment.  
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
 
    def blockStartDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the start of an experiment block.  
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def trialStartDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the start of an experiment trial.  
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
         
    def trialEndDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the end of an experiment trial.  
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
         
    def blockEndDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the end of an experiment block.  
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def experimentEndDefaultLogic(self,*args,**kwargs):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the end of an experiment sessio.  
        """       
        return RTN_CODES.ET_NOT_IMPLEMENTED
        
    def trackerTime(self):
        """
        Current usec time of the EYE TRACKER in EYE TRACKER TIMESPACE. 
        Should be accurate to within +/- 500 usec to meet pyEyeTrackerInterface specification.
        If this can not be met, accuracy and resolution should be specified.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED # *self.DEVICE_TIMEBASE_TO_USEC
   
    def setConnectionState(self,enabled,**kwargs):
        """
        setConnectionState is used to connect ( setConnectionState(True) ) or disable ( setConnectionState(False) )
        the connection of the pyEyeTrackerInterface to the eyetracker.
        
        Args:
        
            enabled (bool): True = enable the connection, False = disable the connection.
            kwargs (dict): any eye tracker specific parameters that should be passed.
        """
        if enabled is True or enabled is False:
            return RTN_CODES.ET_NOT_IMPLEMENTED
        else:
            raise BaseException("enableConnection state must be a bool of True or False")
            
    def isConnected(self):
        """
        isConnected returns whether the pyEyeTrackerInterface is connected to the eye tracker (returns True) or not (returns False)
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
            
    def sendCommand(self, command, value, wait=True, **kwargs):
        """
        sendCommand sends a text command and text command value to the eye tracker. Depending on the command and on the eye trackers
        implementation, when a command is send, the eye tracker may or n=may not response indicating the status of the command. If the
        command is not going to return a response from the eye tracker, the method will return RTN_CODES.ET_RESULT_UNKNOWN.
        Please see the specific eye tracker implementation you are working with for a list of supported command's and value's.
        
        Args:
        
           command (str): string command to send to the eye tracker. See the specific eye tracker documentation for pyEyeTracker for a list of valid commands.
           value (str): the string form of the value of the command to send.
           wait (bool or callable) *NOT CURRENTLY SUPPORTED; FUNCTIONS AS ALWAYS == TRUE*: if bool, True = do not return from function until result of command if known (if it can be known); False = return immediately after sending the command, ignoring any possible return value. If wait is a callable, then wait fould be a reference to the callback function you want called when the return value is available. If no return value is possible for the command, wait is ignorded and RTN_CODES.ET_RESULT_UNKNOWN is returned immediately..           
        
        Return: the result of the command call, or one of the ReturnCodes Constants ( ReturnCodes.ET_OK, ReturnCodes.ET_RESULT_UNKNOWN, ReturnCodes.ET_NOT_IMPLEMENTED ) 
        """
        if command in EyeTracker.COMMAND_TO_FUNCTIONS:
            return EyeTracker.COMMAND_TO_FUNCTIONS[command](value,**kwargs)
        return RTN_CODES.ET_NOT_IMPLEMENTED
        
    def sendMessage(self, message, time_offset=0,**kwargs):
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
           time_offset (int): number of int msec that the time stamp of the message should be offset by. This can be used so that a message can be sent for a display change **BEFORE** or **AFTER** the aftual flip occurred (usually before), by sending the message, say 4 msec prior to when you know the next trace will occur, entering -4 into the offset field of the message, and then send it and calling flip() 4 msec before the retrace to ensure that the message time stampe and flip are both sent and schuled in advance. (4 msec is quite large buffer even on windows these days with morern hardware BTW)
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
        
    def createRecordingFile(self, **kwargs):
        """
        createRecordingFile instructs the eye tracker to open a new file on the eye tracker computer to save data collected to
        during the recording. If recording is started and stopped multiple times while a single recording file is open, each 
        start/stop recording pair will be represented within the single file. A recording file is closed by calling
        closeRecordingFile(). Normally you would open a rtecoring file at the start of an experimental session and close it
        at the end of the experiment; starting and stopping recording of eye data between trials of the experiment.
        
        Args:
           fileName (str): Name of the recording file to save on the eye tracker. This does *not* include the path to the file. Some eye trackers have limitations to the length of their file name, so please refer to the specific implemtations documenation for any caviates.
           path (str): This optional parameter can be used to specify the path to the recording file that should be saved. The path must already exist. If this paramemter is not specified, then the defualt file location is used. 
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
        
    def closeRecordingFile(self,**kwargs):
        """
        closeRecordingFile is used to close the currently open file that is being used to save data from the eye track to the eye tracker computer. 
        Once a file has been closed, getFile(localFileName,fileToTransfer) can be used to transfer the file from the eye tracker computer to the 
        experiment computer at the end of the experiment session.
        
        Args:
           fileName (str): Name of the recording file to save on the eye tracker. This does *not* include the path to the file. Some eye trackers have limitations to the length of their file name, so please refer to the specific implemtations documenation for any caviates.
           path (str): This optional parameter can be used to specify the path to the recording file that should be saved. The path must already exist. If this paramemter is not specified, then the defualt file location is used. 
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def getFile(self,localFileName,fileToTransfer, **kwargs):
        """
        getFile is used to transfer the file from the eye tracker computer to the experiment computer at the end of the experiment session.

        Args:
        
           localFileName (str): Name of the recording file to experiment computer.
           fileToTransfer (str): Name of the recording file to transfer from the eye tracker.
        """   
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def runSetupProcedure(self, graphicsContext=None ,**kwargs):
        """
        runSetupProcedure passes the graphics environment over to the eye tracker interface so that it can perform such things
        as camera setup, calibration, etc. This is a blocking call that will not return until the setup procedure is done; at which time
        the graphics environment can be taken back over by psychopy.  See the EyeTrackerSetupGraphics class for more information.
        
        The graphicsContext arguement should likely be the psychopy full screen window instance that has been created 
        for the experiment.
        """
        if self._setupGraphics is None:
            self._setupGraphics=EyeTrackerSetupGraphics(graphicsContext=graphicsContext,**kwargs)
        return self._setupGraphics.run()

    def stopSetupProcedure(self):
        """
        stopSetupProcedure allows a user to cancel the ongoing eye tracker setup procedure. Given runSetupProcedure is a blocking
        call, the only way this will happen is if the user has another thread that makes the call, perhaps a watch dog type thread.
        So in practice, calling this method is not very likely I do not think.
        """
        result=None
        if self._setupGraphics is not None:
            result = self._setupGraphics.stop()
        return result
                
    def setRecordingState(self,recording=False,**kwargs):
        """
        setRecordingState is used to start or stop the recording of data from the eye tracking device. Use sendCommand() set the necessary information 
        for your eye tracker to enable what data you would like saved, send over to the experiment computer during recording, etc.
        
        Args:
           recording (bool): if True, the eye tracker should start recordng data.; false = stop recording data.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def isRecordingEnabled(self,**kwargs):
       """
       isRecordingEnabled returns the recording state from the eye tracking device.
       True == the device is recording data
       False == Recording is not occurring
       """
       return RTN_CODES.ET_NOT_IMPLEMENTED
     
    def getDataFilteringLevel(self,data_stream=DATA_STREAMS.ALL,**kwargs):
        """
        getDataFilteringLevel returns the numerical code the current device side filter level 
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
        return RTN_CODES.ET_NOT_IMPLEMENTED

    def setDataFilteringLevel(self,level,data_stream=DATA_STREAMS.ALL,**args):
        """
        setDataFilteringLevel sets the numerical code for current ET device side filter level 
        for the specific data_stream. 
        
        Currently, filter levels 0 (meaning no filter) through 
        5 (highest filter level) can be specified via the pyEyeTrackerInterface.
        They are defined in ET_FILTERS.
        
        data_streams specifies what output the filter is being applied to by the device. The
        currently defined output streams are defined in ET_DATA_STREAMS, and are
        ALL,FILE,NET,SERIAL,ANALOG. ALL indicates that the filter level should be applied to all 
        available output streams,
        
        If an ET device supports setting one filter level for all available output streams, 
        then setting using filter_level only should be done.
        
        If a stream type that is not supported by the device for individual filtering is specified, 
        an error should be generated.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def drawToGazeOverlayScreen(self, drawingcommand='UNIMPLEMENTED', position=None,  value=None, **args):
        """
        drawToGazeOverlayScreen provides a generic interface for ET devices that support
        having graphics drawn to the Host / Control computer gaze overlay area, or other similar
        graphics area functionality.
        
        The method should return the appropriate return code if successful or if the command failed,
        or if it is unsupported.
        
        There is no set list of values for any of the arguements for this command, so please refer to the
        ET imlpementation notes for your device for details. Hypothetical examples may be:
        
        # clear the overlay area to black
        eyetracker.drawToGazeOverlayScreen(drawingcommand='CLEAR',  value="BLACK")

        # draw some white text centered on the overlay area
        eyetracker.drawToGazeOverlayScreen(drawingcommand='TEXT', position=('CENTER',512,387),  value="This is my Text To Show", color='WHITE')

        # draw an image on the overlay area
        eyetracker.drawToGazeOverlayScreen(drawingcommand='IMAGE',  value="picture.png", position=('CENTER',512,387))
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def getDigitalPortState(self, port, **args):
        """
        getDigitalPortState returns the current value of the specified digital port on the ET computer. 
        This can be used to read the parallel port or idigial lines on the ET host PC if the ET has such functionality.

        port = the address to read from on the host PC. Consult your ET device documentation for appropriate values.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
 
    def setDigitalPortState(self, port, value, **args):
        """
        setDigitalPortState sets the value of the specified digital port on the ET computer. 
        This can be used to write to the parallel port or idigial lines on the ET Host / Operator PC if the ET
        has such functionality.

        port = the address to write to on the host PC. Consult your ET device documentation for appropriate values.
        """
        return RTN_CODES.ET_NOT_IMPLEMENTED
    
    def getEventHandler(self):
        return self.eventHandler
        
    def __del__(self):
        """
        Do any final cleanup of the eye tracker before the object is destroyed. Users should not call or change this method. It is for implemetaion by interface creators and is autoatically called when an object is destroyed by the interpreter.
        """
        EyeTracker._INSTANCE=None
        
 
class EyeTrackerSetupGraphics(object):
    '''
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
    '''
    def __init__(self,graphicsContext,**kwargs):
        '''
        The EyeTrackerSetupGraphics instance is created the first time eyetracker.runSetupProcedure(graphicsContext)
        is called. The class instance is then reused in future calls. 
        graphicsContext object type is dependent on the graphics environment being used.
        Since psychopy normalizes everything in this regard to psychopy.visual.Window (regardless of
        whether pyglet or pygame backend is being used), then likely graphicsContext should be the instance of
        Window that has been created for your psychopy experiment. For an eye tracking experiment
        this would normally be a single 'full screen' window.
        '''
        self.graphicsContext=graphicsContext
        
    def run(self,*args,**kwargs):
        print "EyeTrackerSetupGraphics.run is not implemented."
        return _handleDefaultState(*args,**kwargs)   

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
