"""
pyLCTEyeTracker: LC Technologies interface implemtation of pyEyeTracker

Part of the pyEyeTracker library 
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version). 

 
.. moduleauthor:: ??????? + contributors, please see credits section of documentation.
"""
from ... import EyeTracker

from ... import ET_RTN_CODES,ET_EYE_CODES,\
                    ET_PUPIL_SIZE_MEASURES,ET_DATA_TYPES,ET_MODES,ET_CALIBRATION_TYPES,\
                    ET_CALIBRATION_MODES,ET_DATA_STREAMS,ET_REALTIME_FILTERS
import time
import gc
import sys
import logging
import os

class LCTechEyeTracker(EyeTracker):
    """LCTechEyeTracker class is the implementation of the pyEyeTracker
    common eye tracker interface for the LC Technologies EyeTracker eye trackers
    .. note:: 
        Only **one** instance of LCTechEyeTracker can be created within an experiment. Attempting to create > 1 instance will raise an exception. 
        To get the current instance of the EyeTracker you can call the class method EyeTracker.getInstance(); this is useful as it saves needing 
        to pass an eyeTracker instance variable around your code. 
    """    
    _OPEN_FILE=None

    def __init__(self,experimentContext):
        """iViewXEyeTracker class. 
        """
        if LCTechEyeTracker._INSTANCE is None:
            EyeTracker.__init__(self,experimentContext)
            self.eventHandler=LCTechEventHandler(self)  
        else:
            raise "LCTechEyeTracker instance already exists. del it or access it via getEyeTracker()"
            
    def experimentStartDefaultLogic(self,**args):
        """
        Experiment Centered Generics 
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED #ET_OK
         
    def blockStartDefaultLogic(self,**args):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the start of an experiment block.  
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
        

    def trialStartDefaultLogic(self,**args):
        """
        Experiment Centered Generic 
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
        Experiment Centered Generic for end of experiment
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
        
    def trackerTime(self):
        """
        Current iViewXEyeTracker Host PC time
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED #*iViewXEyeTracker.TRACKER_TIMEBASE_TO_MSEC
 
    def experimentTime(self):
        """
        Current msec.usec time of the EXPERIMENT / STIMULUS PC CLOCK
        """
        return self.localTime()*iViewXEyeTracker.EXP_TIMEBASE_TO_MSEC
  
    def enableConnection(self,state,**args):
        """
        enableConnection
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED 
            
    def isConnected(self):
        """
        isConnected returns whether the pyEyeTracker is connected to the eye tracker (returns True) or not (returns False)
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED 
            
    def sendCommand(self, command, value, wait=True):
        """
        sendCommand
        """
        r=None
        if command in self._COMMAND_TO_FUNCTION:
            print "Command",command,"maps to function", value," . That is not implemented yet."
            return ET_RTN_CODES.ET_NOT_IMPLEMENTED 
        else:
            return ET_RTN_CODES.ET_NOT_IMPLEMENTED 
        
        if wait is True:
            print "LCTechEyeTracker.sendCommand wait param not implemented"
        
        return ET_RTN_CODES.ET_RESULT_UNKNOWN
        
    def sendMessage(self, message, time_offset=0):
        """
        sendMessage
        """
        if time_offset:
            return ET_RTN_CODES.ET_NOT_IMPLEMENTED 
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED 
        
    def createRecordingFile(self, fileName):
        """
        createRecordingFile
        """
        print 'createRecordingFile ',fileName
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED 
        
    def closeRecordingFile(self,**args):
        """
        closeRecordingFile
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED 
    
    def getFile(self,localFileName,fileToTransfer=None, **args):
        """
        getFile
        """   
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED 
 
    def runCalibrationProcedure(self, eyeTracker, calibrationType=ET_CALIBRATION_TYPES.HV9, targetPoints=None, randomizePoints=False, customCalibrationHandlerClass=None,**args):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED 
    
    def cancelCalibration(self,**args):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
                
    def enableRecording(self,enable=False,**args):
        """
        enableRecording
        """
        if enable is True:
            return ET_RTN_CODES.ET_NOT_IMPLEMENTED 
        elif  enable is False:
            return ET_RTN_CODES.ET_NOT_IMPLEMENTED 
        
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def isRecordingEnabled(self):
        """
        isRecordingEnabled
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED 
    
    def getDataFilteringLevel(self,data_stream=ET_DATA_STREAMS.ALL,**args):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def setDataFilteringLevel(self,level,data_stream=ET_DATA_STREAMS.ALL,**args):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
      
    def drawToGazeOverlayScreen(self, drawingcommand=None, position=None, value=None, **args):
        if drawingcommand is None:
            return ET_RTN_CODES.ET_ERROR
        elif drawingcommand:
            return ET_RTN_CODES.ET_NOT_IMPLEMENTED
            
    
    def getDigitalPortState(self, port, **args):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
 
    def setDigitalPortState(self, port, value, **args):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
      
    def __del__(self):
        """
        Do any final cleanup of the eye tracker before the object is destroyed. Users should not call or change this method. It is for implemetaion by interface creators and is autoatically called when an object is destroyed by the interpreter.
        """
        EyeTracker._INSTANCE=None
        self.eventHandler=None

from ... import EyeTrackerEventHandler

class LCTechEventHandler(EyeTrackerEventHandler):
    tracker=None
    def __init__(self, eyetracker, userEventHandler=None):
        EyeTrackerEventHandler.__init__(self, eyetracker)
        
        LCTechEventHandler.tracker=eyetracker
              
    def getLatestEvent(self,peak=False):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
     
    def updateTimeBaseOffset(self):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
        
    def getConvertedNativeEvents(self):
        # get events from eye tracker, create appropriate evnt type for each
        # and set the correct localTime based on the current offset.
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

from ... import EyeTrackerVendorExtension

class LCTechExtension(EyeTrackerVendorExtension):
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
