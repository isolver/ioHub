"""
pyEyeLinkEyeTracker: SR Research EyeLink interface implemtation of pyEyeTracker

Part of the pyEyeTracker library 
Copyright (C) 2012 Sol Simpson 
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version). 

pyEyeLinkEyeTracker uses the pyLink module with Copyright (C) SR Research Ltd and is to be 
used by owners of the EyeLink eye tracking systems only.
 
.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""
from ... import ET_RTN_CODES,ET_EYE_CODES,\
                    ET_PUPIL_SIZE_MEASURES,ET_DATA_TYPES,ET_MODES,ET_CALIBRATION_TYPES,\
                    ET_CALIBRATION_MODES,ET_DATA_STREAMS,ET_REALTIME_FILTERS
                    
from ... import EyeTracker

import pylink

import time
import gc
import sys
import logging
import os

class EyeLinkEyeTracker(EyeTracker):
    """EyeLinkEyeTracker class is the implementation of the pyEyeTracker
    common eye tracker interface for the SR Research EyeLink II and
    EyeLink 1000 eye trackers.
    .. note:: 
        Only **one** instance of EyeLinkEyeTracker can be created within an experiment. Attempting to create > 1 instance will raise an exception. To get the current instance of the EyeTracker you can call the class method EyeTracker.getInstance(); this is useful as it saves needing to pass an eyeTracker instance variable around your code. 
    """    
    _OPEN_EDF=None
    _EYELINK=None
    
    def __init__(self,experimentContext):
        """EyeLinkEyeTracker class. 
        """
        if EyeLinkEyeTracker._INSTANCE is None:
            EyeTracker.__init__(self,experimentContext)
            EyeLinkEyeTracker._EYELINK = pylink.EyeLink()
            self.eventHandler=EyeLinkEventHandler(self)  
        else:
            raise "EyeLinkEyeTracker instance already exists. del it or access it via getEyeTracker()"
            
    def experimentStartDefaultLogic(self,**args):
        """
        Experiment Centered Generics 
        """
        EyeLinkEyeTracker._EYELINK.setOfflineMode();                          

        #Gets the display surface and sends a mesage to EDF file;
        EyeLinkEyeTracker._EYELINK.sendCommand("screen_pixel_coords =  %d %d %d %d" %self._CAL_SURFACE_INFO['SCREEN_AREA'])
        EyeLinkEyeTracker._EYELINK.sendMessage("DISPLAY_COORDS  %d %d %d %d" %self._CAL_SURFACE_INFO['SCREEN_AREA'])
         
        tracker_software_ver = 0
        eyelink_ver = EyeLinkEyeTracker._EYELINK.getTrackerVersion()
        if eyelink_ver == 3:
            tvstr = EyeLinkEyeTracker._EYELINK.getTrackerVersionString()
            vindex = tvstr.find("EYELINK CL")
            tracker_software_ver = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))

        # set EDF file contents 
        self.sendCommand("file_event_data"," = GAZE , GAZERES ,HREF ,AREA ,VELOCITY ,STATUS")
        self.sendCommand("file_event_filter"," = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT")

        if tracker_software_ver>=4:
            self.sendCommand("file_sample_data","  = LEFT,RIGHT,GAZE, GAZERES, HREF , PUPIL ,AREA ,STATUS, BUTTON, INPUT,HTARGET")
        else:
            self.sendCommand("file_sample_data","  = LEFT,RIGHT, GAZE, GAZERES, HREF , PUPIL ,AREA ,STATUS, BUTTON, INPUT")

        # set link data (used for gaze cursor) 
        self.sendCommand("link_event_filter"," = LEFT,RIGHT,FIXATION,FIXUPDATE,SACCADE,BLINK,BUTTON,MESSAGE,INPUT")
        self.sendCommand("link_event_data"," = GAZE , GAZERES ,HREF ,AREA ,VELOCITY ,STATUS ")
        
        if tracker_software_ver>=4:
            #TODO FIX, should be link sample filter info
            self.sendCommand("link_sample_data","  = GAZE, GAZERES, HREF , PUPIL ,AREA ,STATUS, BUTTON, INPUT , HTARGET")
        else:
            self.sendCommand("link_sample_data","  = GAZE, GAZERES, HREF , PUPIL ,AREA ,STATUS, BUTTON, INPUT")
        self.sendCommand("button_function"," 5 'accept_target_fixation'");
        
        self.setDataFilteringLevel(0,ET_DATA_STREAMS.FILE)
        self.setDataFilteringLevel(0,ET_DATA_STREAMS.LINK)
        
        if 'fileName' in args:
            self.createRecordingFile(args['fileName'])
        pylink.flushGetkeyQueue(); 
        return ET_RTN_CODES.ET_OK
         
    def blockStartDefaultLogic(self,**args):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the start of an experiment block.  
        """
        pylink.flushGetkeyQueue(); 
        return ET_RTN_CODES.ET_OK
        

    def trialStartDefaultLogic(self,**args):
        """
        Experiment Centered Generic 
        """
        pylink.flushGetkeyQueue(); 
        gc.disable();
        #begin the realtime mode
        pylink.beginRealTimeMode(100)
        
        return ET_RTN_CODES.ET_OK
         
    def trialEndDefaultLogic(self,**args):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the end of an experiment trial.  
        """
        
        pylink.endRealTimeMode();
        gc.enable();

        return ET_RTN_CODES.ET_RESULT_UNKNOWN
         
    def blockEndDefaultLogic(self,**args):
        """
        Experiment Centered Generic method that can be used to perform a set of eye tracker default code associated with the end of an experiment block.  
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def experimentEndDefaultLogic(self,**args):
        """
        Experiment Centered Generic for end of experiment
        """
        if EyeLinkEyeTracker._EYELINK != None:
            # File transfer and cleanup!
            
            EyeLinkEyeTracker._EYELINK.setOfflineMode();                          
            pylink.msecDelay(250);                 

            #Close the file and transfer it to Display PC
            if EyeLinkEyeTracker._OPEN_EDF is not None:
                self.closeRecordingFile()
                self.getFile(os.path.join(self.RESULTS_DIR,EyeLinkEyeTracker._OPEN_EDF))
            
            self.enableConnection(False);
 
            return ET_RTN_CODES.ET_OK

        
    def trackerTime(self):
        """
        Current EYELINK Host PC time
        """
        return EyeLinkEyeTracker._EYELINK.trackerTime()
 
    def experimentTime(self):
        """
        Current msec.usec time of the EXPERIMENT / STIMULUS PC CLOCK
        """
        return self.localTime()*EyeLinkEyeTracker.EXP_TIMEBASE_TO_MSEC
  
    def enableConnection(self,state,**args):
        """
        enableConnection
        """
        if state is True or state is False:
            if state is True:
                EyeLinkEyeTracker._EYELINK.connect()
            else:
                EyeLinkEyeTracker._EYELINK.setOfflineMode();                          
                pylink.msecDelay(250);
                EyeLinkEyeTracker._EYELINK.reset()

        else:
            raise BaseException("enableConnection state must be a bool of True or False")
            
    def isConnected(self):
        """
        isConnected returns whether the pyEyeTracker is connected to the eye tracker (returns True) or not (returns False)
        """
        return EyeLinkEyeTracker._EYELINK.isConnected()
            
    def sendCommand(self, command, value, wait=True):
        """
        sendCommand
        """
        r=None
        if command in self._COMMAND_TO_FUNCTION:
            print "Command",command,"maps to function", value," . That is not implemented yet."
        else:
            r=EyeLinkEyeTracker._EYELINK.sendCommand(str(command)+" "+str(value))
        
        if r is None:
            return ET_RTN_CODES.ET_RESULT_UNKNOWN
            
        if wait is True:
            print "EyeLinkEyeTracker.sendCommand wait param not implemented"
            return ET_RTN_CODES.ET_RESULT_UNKNOWN
        
    def sendMessage(self, message, time_offset=0):
        """
        sendMessage
        """
        if time_offset:
            return EyeLinkEyeTracker._EYELINK.sendMessage("\\t%d\\t%s"%(message,time_offset))
        return EyeLinkEyeTracker._EYELINK.sendMessage(message)
        
    def createRecordingFile(self, fileName):
        """
        createRecordingFile
        """
        print 'createRecordingFile ',fileName
        
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
            print "EyeLinkEyeTracker.createRecordingFile filename must be ion 7.3 format. Sorry! Changing name to ",fileName
        
        EyeLinkEyeTracker._EYELINK.openDataFile(fileName)	
        EyeLinkEyeTracker._OPEN_EDF=fileName
        return ET_RTN_CODES.ET_RESULT_UNKNOWN
        
    def closeRecordingFile(self,**args):
        """
        closeRecordingFile
        """
        EyeLinkEyeTracker._EYELINK.closeDataFile()
        return ET_RTN_CODES.ET_OK
    
    def getFile(self,localFileName,fileToTransfer=None, **args):
        """
        getFile
        """   
        if fileToTransfer is None and EyeLinkEyeTracker._OPEN_EDF:
            fileToTransfer=EyeLinkEyeTracker._OPEN_EDF
            EyeLinkEyeTracker._OPEN_EDF=None
        return EyeLinkEyeTracker._EYELINK.receiveDataFile(fileToTransfer,localFileName)
 
    
    def set2DCalibrationCoordinateSpace(self,l,t,b,r,**args):
        """
        set2DCalibrationCoordinateSpace sets the boundinds area that defines the ralibration surface to use used by the eye tracker. 
        Units are often in pixels, but can technically be any unit space that makes most sense for your experiment; piles, dgrees, cm's, percentage)
        
        Args:
           l (number):  left side of calibration plain
           t (number):  top side of calibration plain
           r (number):  right side of calibration plain
           b (number):  bottom side of calibration plain          
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def get2DCalibrationCoordinateSpace(self):
        """
        get2DCalibrationCoordinateSpace gets the boundinds area that defines the ralibration surface to use used by the eye tracker. 
        Units are often in pixels, but can technically be any unit space that makes most sense for your experiment; piles, dgrees, cm's, percentage)
        
        Returns:
           (l, t, r, b) (tuple):  where
           l (number):  left side of calibration plain
           t (number):  top side of calibration plain
           r (number):  right side of calibration plain
           b (number):  bottom side of calibration plain          
        """
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
   
    def runCalibrationProcedure(self, calibrationType, calibrationPoints=None, validationPoints=None, randomizeCalibrationPoints=None, randomizeValidationPoints=None, customCalibrationHandlerClass=None,**args):
        return EyeLinkEyeTracker._EYELINK.doTrackerSetup()

    def cancelCalibration(self,**args):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
                
    def enableRecording(self,enable=False,**args):
        """
        enableRecording
        """
        if enable is True:
            error = EyeLinkEyeTracker._EYELINK.startRecording(1,1,1,1)
            if error:
                print "Error starting eyelink recording", error
                return  ET_RTN_CODES.ET_ERROR
                
            if not EyeLinkEyeTracker._EYELINK.waitForBlockStart(100, 1, 0):
                print "ERROR: No link samples received!";
                return ET_RTN_CODES.ET_ERROR;
            else:
                return ET_RTN_CODES.ET_OK;
        elif  enable is False:
            EyeLinkEyeTracker._EYELINK.stopRecording()
        
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED

    def isRecordingEnabled(self):
       """
       isRecordingEnabled
       """
       return EyeLinkEyeTracker._EYELINK.isRecording()  
     
    def getDataFilteringLevel(self, data_stream=ET_DATA_STREAMS.ALL,**args):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
        
    def setDataFilteringLevel(self, level,data_stream=ET_DATA_STREAMS.ALL,**args):
        #ET_DATA_STREAMS = etEyeTrackerDataStreams(["FILE","LINK, ANALOG"])
        print "** ET_REALTIME_FILTERS: ", ET_REALTIME_FILTERS
        if level not in ET_REALTIME_FILTERS:
            BaseException("EyeTracker.setDataFilteringLevel invalid value provided; must be from ET_REALTIME_FILTERS")
        if data_stream == ET_DATA_STREAMS.ALL:
            return EyeLinkEyeTracker._EYELINK.setHeuristicLinkAndFileFilter(level,level)
        elif data_stream == ET_DATA_STREAMS.LINK or data_stream == ET_DATA_STREAMS.ANALOG:
            return EyeLinkEyeTracker._EYELINK.setHeuristicLinkAndFileFilter(level)
        elif data_stream == ET_DATA_STREAMS.FILE:
            return EyeLinkEyeTracker._EYELINK.setHeuristicLinkAndFileFilter(0,level)
     
    def drawToGazeOverlayScreen(self, drawingcommand=None, position=None, value=None, **args):
        if drawingcommand is None:
            return ET_RTN_CODES.ET_ERROR
        elif drawingcommand=='TEXT':
            return self._EYELINK.drawText(str(value),position) # value = text to display. position = (-1,-1), or position in gaze orders to draw text.
        elif drawingcommand=='CLEAR':
            return self._EYELINK.clearScreen(int(value)) # value must be between 0 - 15 and is the color from the EyeLink Host PC pallette to use.
        elif drawingcommand=='LINE': # value must be between 0 - 15 and is the color from the EyeLink Host PC pallette to use. position must be [(x1,y1),(x2,y2)]
             return self._EYELINK.drawLine(position[0], position[1],int(value))
        elif drawingcommand=='BOX':# value must be between 0 - 15 and is the color from the EyeLink Host PC pallette to use.  position must be (x,y,width,height) 
             return self._EYELINK.drawBox(position[0], position[1],position[2], position[3], int(value))
        elif drawingcommand=='CROSS': # Draws a small "+" to mark a target point.  # value must be between 0 - 15 and is the color from the EyeLink Host PC pallette to use.  position must be (x,y)
             return self._EYELINK.drawBox(position[0], position[1], int(value))
        elif drawingcommand=='FILLEDBOX':
             return self._EYELINK.drawBox(position[0], position[1],position[2], position[3], int(value))
        return ET_RTN_CODES.ET_ERROR
    
    def getDigitalPortState(self, port, **args):
        return self._EYELINK.readIOPort(port)
 
    def setDigitalPortState(self, port, value, **args):
        return self._EYELINK.writeIOPort(port, value)
      
    def __del__(self):
        """
        Do any final cleanup of the eye tracker before the object is destroyed. Users should not call or change this method. It is for implemetaion by interface creators and is autoatically called when an object is destroyed by the interpreter.
        """
        EyeLinkEyeTracker._EYELINK.close()
        EyeLinkEyeTracker._EYELINK=None
        EyeTracker._INSTANCE.close()
        EyeTracker._INSTANCE=None
        self.eventHandler=None

from ... import EyeTrackerEventHandler

class EyeLinkEventHandler(EyeTrackerEventHandler):
    _EYELINK=None
    
    def __init__(self, eyetracker, userEventHandler=None):
        EyeTrackerEventHandler.__init__(self, eyetracker, userEventHandler)
        
        EyeLinkEventHandler._EYELINK=eyetracker._EYELINK
              
    def getLatestEvent(self,peak=False):
        return ET_RTN_CODES.ET_NOT_IMPLEMENTED
     
    def updateTimeBaseOffset(self):
        if self._EYELINK:
            return self._EYELINK.trackerTimeOffset()  #msec diff between stim and host PC, adjusted for drift automatically by eyelink system, 
        
    def getConvertedNativeEvents(self):
        # get events from eye tracker, create appropriate evnt type for each
        # and set the correct localTime based on the current offset.
        
        nevents=list()
        
        #get native events queued up
        while 1:    
            ne = self._EYELINK.getNextData()
            if ne == 0 or ne is None:
                break
            ne= self._EYELINK.getFloatData()

            # possible native pylink class types
            
            #Sample 
            #StartBlinkEvent 
            #EndBlinkEvent      
            #StartSacadeEvent 
            #EndSacadeEvent 
            #StartFixationEvent         
            #EndFixationEvent 
            #FixUpdateEvent 
            #IOEvent 
            #MessageEvent 
            
            # now convert from native format to pyEyeTracker  common format
            # TODO : not yet done, returns native events.
            pe=ne

            if isinstance(pe,pylink.Sample):
                self.latestSample=pe
              
            if isinstance (pe, pylink.StartSaccadeEvent):
                pass#print 'saccade:', dir(pe)
            # add processed event to dequeue
            nevents.append(pe)
            
        return nevents

from ... import EyeTrackerVendorExtension

class EyeLinkExtension(EyeTrackerVendorExtension):
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
