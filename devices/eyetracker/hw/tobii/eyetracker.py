"""
ioHub
Common Eye Tracker Interface
.. file: ioHub/devices/eyetracker/hw/tobii/eyetracker.py

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: ??
.. fileauthor:: ??
"""

import numpy as np 
import ioHub
from ioHub.constants import EventConstants, EyeTrackerConstants


from .... import Computer
from ... import EyeTrackerDevice
from ...eye_events import *
from ioHub.server import createErrorResult

try:
    from tobiiclasses  import *
    from tobiiCalibrationGraphics import TobiiPsychopyCalibrationGraphics
except:
    pass

class EyeTracker(EyeTrackerDevice):
    """
    """
    _tobii=None

    DEVICE_TIMEBASE_TO_SEC=0.000001
    EVENT_CLASS_NAMES=['MonocularEyeSampleEvent','BinocularEyeSampleEvent','FixationStartEvent',
                         'FixationEndEvent', 'SaccadeStartEvent', 'SaccadeEndEvent',
                         'BlinkStartEvent', 'BlinkEndEvent']
    __slots__=[]

    def __init__(self,*args,**kwargs):
        """
        EyeTracker class. This class is to be extended by each eye tracker specific implementation
        of the ioHub Common Eye Tracker Interface.
        """
        
        EyeTrackerDevice.__init__(self,*args,**kwargs)

        model_name=self.model_name
        serial_num=self.serial_number
        
        if model_name and len(model_name)==0:
            model_name = None
        if serial_num and len(serial_num)==0:
            serial_num = None
                
        
        EyeTracker._tobii=None
        try:
            EyeTracker._tobii=TobiiTracker(product_id=serial_num,model=model_name)
        except:
            pass
        
        if self._tobii and self._runtime_settings['sampling_rate'] and self._runtime_settings['sampling_rate'] in self._tobii.getAvailableSamplingRates():
            #ioHub.print2err('Settings Tobii sampling rate to %f.'%self._runtime_settings['sampling_rate'])
            self._tobii.setSamplingRate(self._runtime_settings['sampling_rate'])
    
        self._latest_sample=None
        self._latest_gaze_position=None
        
    def trackerTime(self):
        """
        Current eye tracker time in native time base. The Tobii system uses a 
        usec timebase.
        """
        if self._tobii:
            return self._tobii.getCurrentEyeTrackerTime()
        return EyeTrackerConstants.EYETRACKER_ERROR
        
    def trackerSec(self):
        """
        Current eye tracker time, normalized to sec.msec.
        """
        if self._tobii:
            return self._tobii.getCurrentEyeTrackerTime()*self.DEVICE_TIMEBASE_TO_SEC
        return EyeTrackerConstants.EYETRACKER_ERROR

    def setConnectionState(self,enable):
        """
        setConnectionState is a no-op when using the Tobii system, as the 
        connection is established when the Tobii EyeTracker class is created, and remains
        active until the program ends, or a error occurs resulting in the loss
        of the tracker connection.
        """
        if self._tobii:
            return self._tobii.getTrackerDetails().get('status',False)=='OK'
        return False
            
    def isConnected(self):
        """
        isConnected returns whether the Tobii is connected to the experiment PC
        and if the tracker state is valid. Returns True if the tracker can be 
        put into Record mode, etc and False if there is an error with the tracker
        or tracker connection with the experiment PC.
        """
        if self._tobii:
            return self._tobii.getTrackerDetails().get('status',False)=='OK'
        return False
            
    def sendCommand(self, key, value=None):
        """
        The Tobii has several custom commands that can be sent to set or get
        information about the eye tracker that is specific to Tobii
        systems. Valid command tokens and associated possible valid command values
        are as follows:
        
        TO DO: complete based on these tracker object methods
            - getTrackerDetails
            - getName
            - setName
            - getHeadBox
            - setXSeriesPhysicalPlacement (no-op if tracker is not an X series system)
            - getEyeTrackerPhysicalPlacement
            - getAvailableExtensions
            - getEnabledExtensions
            - enableExtension
            - ....
            
        Commands always return their result at the end of the command call, if
        there is any result to return. Otherwise EyeTrackerConstants.EYETRACKER_OK
        is returned.
        """
        EyeTrackerConstants.FUNCTIONALITY_NOT_SUPPORTED

    def runSetupProcedure(self,starting_state=EyeTrackerConstants.DEFAULT_SETUP_PROCEDURE):
        """
        runSetupProcedure passes the graphics environment over to the eye tracker interface so that it can perform such things
        as camera setup, calibration, etc. This is a blocking call that will not return until the setup procedure is done; at which time
        the graphics environment can be taken back over by psychopy.  See the EyeTrackerSetupGraphics class for more information.

        The graphicsContext argument should likely be the psychopy full screen window instance that has been created
        for the experiment.
        
        Result:
            bool: True if setup / calibration procedue passed, False otherwise. If false, should likely exit experiment.
        """
        try:
            calibration_properties=self._runtime_settings.get('calibration')
            circle_attributes=calibration_properties.get('circle_attributes')
            targetForegroundColor=circle_attributes.get('outer_color') # [r,g,b] of outer circle of targets
            targetBackgroundColor=circle_attributes.get('inner_color') # [r,g,b] of inner circle of targets
            screenColor=calibration_properties.get('screen_background_color')                     # [r,g,b] of screen
            targetOuterDiameter=circle_attributes.get('outer_diameter')     # diameter of outer target circle (in px)
            targetInnerDiameter=circle_attributes.get('inner_diameter')     # diameter of inner target circle (in px)

            genv=TobiiPsychopyCalibrationGraphics(self,
                                                  targetForegroundColor=targetForegroundColor,
                                                  targetBackgroundColor=targetBackgroundColor,
                                                  screenColor=screenColor,
                                                  targetOuterDiameter=targetOuterDiameter,
                                                  targetInnerDiameter=targetInnerDiameter)


            calibrationOK=genv.runCalibration()
            genv.window.close()
            
            genv._unregisterEventMonitors() 
            genv.clearAllEventBuffers()
            
            return calibrationOK
            
        except:
            ioHub.print2err("Error during runSetupProcedure")
            ioHub.printExceptionDetailsToStdErr()
        return EyeTrackerConstants.EYETRACKER_ERROR

    def enableEventReporting(self,enabled=True):
        try:        
            enabled=EyeTrackerDevice.enableEventReporting(self,enabled)
            self.setRecordingState(enabled)
            return enabled
        except Exception, e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker.enableEventReporting", error=e)

    def setRecordingState(self,recording):
        """
        setRecordingState is used to start or stop the recording of data from 
        the eye tracking device.
        
        args:
           recording (bool): if True, the eye tracker will start recordng available
              eye data and sending it to the experiment program if data streaming
              was enabled for the device. If recording == False, then the eye
              tracker stops recording eye data and streaming it to the experiment.
              
        If the eye tracker is already recording, and setRecordingState(True) is
        called, the eye tracker will simple continue recording and the method call
        is a no-op. Likewise if the system has already stopped recording and 
        setRecordingState(False) is called again.
        """
        if self._tobii and recording is True and not self.isRecordingEnabled():
            #ioHub.print2err("Starting Tracking... ")
            self._tobii.startTracking(self._handleNativeEvent)
            return EyeTrackerDevice.enableEventReporting(self,True)
            

        
        elif self._tobii and recording is False and self.isRecordingEnabled():
            self._tobii.stopTracking()            
            #ioHub.print2err("STopping Tracking... ")
            self._latest_sample=None
            self._latest_gaze_position=None

            return  EyeTrackerDevice.enableEventReporting(self,False)


        return self.isRecordingEnabled() 

    def isRecordingEnabled(self):
        """
        isRecordingEnabled returns the recording state from the eye tracking device.
        True == the device is recording data
        False == Recording is not occurring
        """
        if self._tobii:      
            return self._tobii._isRecording
        return False
        
    def _setSamplingRate(self,sampling_rate):
        return self._tobii.setSamplingRate(sampling_rate)

        
    def getLastSample(self):
        """
        Returns the latest sample retrieved from the Tobii device. The Tobii
        system always using the BinocularSample Evenet type. The following fields
        of this ioHub event type are supported:
            
            TO DO: give list of fields used in binoc. sample event and a meaning
            for each field that is relevent for the Tobii system.
        """
        return self._latest_sample

    def getLastGazePosition(self):
        """
        Returns the latest 2D eye gaze position retrieved from the Tobii device.
        This represents where on the calibrated surface the eye tracker is 
        reporting each eyes gaze vector is intersecting.
        
        In general, the y or vertical component of each eyes gaze position should
        be the same value, since in typical user populations the two eyes are
        yoked vertically when they move. Therefore any difference between the 
        two eyes in the y dimention is likely due to eye tracker error.
        
        Differences between the x, or horizontal component of the gaze position,
        indicate that the participant is being reported as looking behind or
        in front of the calibrated plane. When a user is looking at the 
        calibration surface , the x component of the two eyes gaze position should be the same.
        Differences between the x value for each eye either indicates that the
        user is not focussing at the calibrated depth, or that there is error in the eye data.
        
        The above remarks are true for any eye tracker in general.
        
        """
        return self._latest_gaze_position
    
    def _poll(self):
        """
        The Tobii system uses a callback approach to providing new eye data as 
        it becomes available, so polling (and therefore this method) are not used.
        """
        pass
    
    def _handleNativeEvent(self,*args,**kwargs):
        """
        This method is called every time there is new eye data available from
        the Tobii system, which will be roughly equal to the sampling rate eye 
        data is being recorded at. The callback needs to return as quickly as 
        possible so there is no chance of overlapping calls being made to the
        callback. Therefore this method simply puts the event data received from 
        the eye tracker device, and the local ioHub time the callback was
        called, into a buffer for processing by the ioHub event system.
        """
        if self.isReportingEvents():
            try:
                eye_data_event=args[1]
                logged_time_iohub_usec=Computer.getTime()/self.DEVICE_TIMEBASE_TO_SEC
                logged_time_tobii_local_usec=self._tobii._getTobiiClockTime()        
                data_time_in_tobii_local_time=self._tobii._sync_manager.convert_from_remote_to_local(eye_data_event.Timestamp)
                
                data_delay=logged_time_tobii_local_usec-data_time_in_tobii_local_time
                
                logged_time=logged_time_iohub_usec*self.DEVICE_TIMEBASE_TO_SEC
                device_event_time=data_time_in_tobii_local_time*self.DEVICE_TIMEBASE_TO_SEC
                iohub_event_time=(logged_time_iohub_usec-data_delay)*self.DEVICE_TIMEBASE_TO_SEC # in sec.msec_usec
                data_delay=data_delay*self.DEVICE_TIMEBASE_TO_SEC
                
                self._addNativeEventToBuffer((logged_time,device_event_time,iohub_event_time,data_delay,eye_data_event))
                return True
            except:
                ioHub.print2err("ERROR IN _handleNativeEvent")
                ioHub.printExceptionDetailsToStdErr()
        else:
            ioHub.print2err("self._handleNativeEvent called but isReportingEvents == false")
   
    def _getIOHubEventObject(self,native_event_data):
        """
        The _getIOHubEventObject method is called by the ioHub Server to convert 
        new native device event objects that have been received to the appropriate 
        ioHub Event type representation. 
        
        If the ioHub Device has been implemented to use the _poll() method of checking for
        new events, then this method simply should return what it is passed, and is the
        default implmentation for the method.
        
        If the ioHub Device has been implemented to use the evnt callback method
        to register new native device events with the ioHub Server, then this method should be
        overwritten by the Device subclass to convert the native event data into
        an appropriate ioHub Event representation. See the implementation of the 
        Keyboard or Mouse device classes for an example of such an implementation.
        
        Args:
            native_event_data: object or tuple of (callback_time, native_event_object)
           
        Returns:
            tuple: The appropriate ioHub Event type in list form.
        """
        try:
            logged_time,device_event_time,iohub_event_time,data_delay,eye_data_event=native_event_data
            
            # TO DO: Convert the middle layer representation of a Tobii data event to 
            # the array format needed by ioHub for the appropriete data type.        
            # TO DO: integrate data into ioHub event handling
            
    #        eyes[LEFT]['gaze_mm'][0]=eye_data_event.LeftGazePoint3D.x
    #        eyes[LEFT]['gaze_mm'][1]=eye_data_event.LeftGazePoint3D.y
    #        eyes[LEFT]['gaze_mm'][2]=eye_data_event.LeftGazePoint3D.z
    #        eyes[LEFT]['eye_location_norm'][0]=eye_data_event.LeftEyePosition3DRelative.x
    #        eyes[LEFT]['eye_location_norm'][1]=eye_data_event.LeftEyePosition3DRelative.y
    #        eyes[LEFT]['eye_location_norm'][2]=eye_data_event.LeftEyePosition3DRelative.z
    #        eyes[RIGHT]['gaze_mm'][0]=eye_data_event.RightGazePoint3D.x
    #        eyes[RIGHT]['gaze_mm'][1]=eye_data_event.RightGazePoint3D.y
    #        eyes[RIGHT]['gaze_mm'][2]=eye_data_event.RightGazePoint3D.z
    #        eyes[RIGHT]['eye_location_norm'][0]=eye_data_event.RightEyePosition3DRelative.x
    #        eyes[RIGHT]['eye_location_norm'][1]=eye_data_event.RightEyePosition3DRelative.y
    #        eyes[RIGHT]['eye_location_norm'][2]=eye_data_event.RightEyePosition3DRelative.z
    
            event_type=EventConstants.BINOCULAR_EYE_SAMPLE
    
            left_gaze_x=eye_data_event.LeftGazePoint2D.x
            left_gaze_y=eye_data_event.LeftGazePoint2D.y
            right_gaze_x=eye_data_event.RightGazePoint2D.x
            right_gaze_y=eye_data_event.RightGazePoint2D.y
    
            if left_gaze_x != -1 and left_gaze_y != -1:
                left_gaze_x,left_gaze_y=self._eyeTrackerToDisplayCoords((left_gaze_x,left_gaze_y))
            if right_gaze_x != -1 and right_gaze_y != -1:
                right_gaze_x,right_gaze_y=self._eyeTrackerToDisplayCoords((right_gaze_x,right_gaze_y))
            # TO DO: Set CI to be equal to current time error stated in Tobii Sync manager
            confidenceInterval=0.0 
            binocSample=[
                         0,
                         0,
                         Computer._getNextEventID(),
                         event_type,
                         device_event_time,
                         logged_time,
                         iohub_event_time,
                         confidenceInterval,
                         data_delay,
                         0, # filtered id (always 0 right now)
                         left_gaze_x,
                         left_gaze_y,
                         EyeTrackerConstants.UNDEFINED, # Left Eye Angle z
                         eye_data_event.LeftEyePosition3D.x,
                         eye_data_event.LeftEyePosition3D.y,
                         eye_data_event.LeftEyePosition3D.z,
                         EyeTrackerConstants.UNDEFINED, # Left Eye Angle x
                         EyeTrackerConstants.UNDEFINED, # Left Eye Angle y
                         EyeTrackerConstants.UNDEFINED, # Left Camera Sensor position x
                         EyeTrackerConstants.UNDEFINED, # Left Camera Sensor position y
                         eye_data_event.LeftPupil,
                         EyeTrackerConstants.PUPIL_DIAMETER,
                         EyeTrackerConstants.UNDEFINED, # Left pupil size measure 2
                         EyeTrackerConstants.UNDEFINED, # Left pupil size measure 2 type
                         EyeTrackerConstants.UNDEFINED, # Left PPD x
                         EyeTrackerConstants.UNDEFINED, # Left PPD y
                         EyeTrackerConstants.UNDEFINED, # Left velocity x
                         EyeTrackerConstants.UNDEFINED, # Left velocity y
                         EyeTrackerConstants.UNDEFINED, # Left velocity xy
                         right_gaze_x,
                         right_gaze_y,
                         EyeTrackerConstants.UNDEFINED, # Right Eye Angle z 
                         eye_data_event.RightEyePosition3D.x,
                         eye_data_event.RightEyePosition3D.y,
                         eye_data_event.RightEyePosition3D.z,
                         EyeTrackerConstants.UNDEFINED, # Right Eye Angle x
                         EyeTrackerConstants.UNDEFINED, # Right Eye Angle y
                         EyeTrackerConstants.UNDEFINED, #Right Camera Sensor position x
                         EyeTrackerConstants.UNDEFINED, #Right Camera Sensor position y
                         eye_data_event.RightPupil,
                         EyeTrackerConstants.PUPIL_DIAMETER,
                         EyeTrackerConstants.UNDEFINED, # Right pupil size measure 2
                         EyeTrackerConstants.UNDEFINED, # Right pupil size measure 2 type
                         EyeTrackerConstants.UNDEFINED, # Right PPD x
                         EyeTrackerConstants.UNDEFINED, # Right PPD y
                         EyeTrackerConstants.UNDEFINED, # right velocity x
                         EyeTrackerConstants.UNDEFINED, # right velocity y
                         EyeTrackerConstants.UNDEFINED, # right velocity xy
                         int(str(eye_data_event.LeftValidity)+str(eye_data_event.RightValidity))
                         ]
    
            self._latest_sample=binocSample
            
            if eye_data_event.LeftValidity>=2 and eye_data_event.RightValidity >=2:
                self._latest_gaze_position=None
            elif eye_data_event.LeftValidity<2 and eye_data_event.RightValidity<2:
                self._latest_gaze_position=[(right_gaze_x+left_gaze_x)/2.0,
                                                (right_gaze_y+left_gaze_y)/2.0]
            elif eye_data_event.LeftValidity<2:
                self._latest_gaze_position=[left_gaze_x,left_gaze_y]
            elif eye_data_event.RightValidity<2:
                self._latest_gaze_position=[right_gaze_x,right_gaze_y]
    
            self._last_callback_time=logged_time
            
            return binocSample
        except:
            ioHub.printExceptionDetailsToStdErr()
        return None
        
    def _eyeTrackerToDisplayCoords(self,eyetracker_point):
        """
        For eye tracker that have a static or fixed type internal mapping,
        this method is used to convert from eye tracker units to display units.
        Default implementation is to just pass the data through untouched.
        """
        gaze_x=eyetracker_point[0]
        gaze_y=eyetracker_point[1]
        left,top,right,bottom=self._display_device.getCoordBounds()
        w,h=right-left,bottom-top
        # For the Tobii, the data used for screen gaze position is represented
        # as a normalized value between 0.0 and 1.0. Therefore, this method
        # needs to convert that to screen pixel coordinates based on the
        # current screen resolution and settings in the Display device. 
        display_x=gaze_x*w+left
        display_y=gaze_y*h+top
        return display_x,display_y
        
    def _displayToEyeTrackerCoords(self,display_x,display_y):
        """
        For eye tracker that have a static or fixed type internal mapping,
        this method is used to convert from display units to eye tracker units.
        Default implementation is to just pass the data through untouched.

        For the Tobii system, this means converting from the screen coordinate
        space to a normalized value between 0.0 and 1.0. 0.0 is top-left of
        screen, 1.0 is bottom-right.
        """
        
        left,top,right,bottom=self._display_device.getCoordBounds()

        gaze_x=(display_x-left)/(right-left)
        gaze_y=(display_y-top)/(bottom-top)
        
        return gaze_x,gaze_y

    def _close(self):
        if self._tobii:
            self._tobii.disconnect()
        EyeTrackerDevice._close(self)