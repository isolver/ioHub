"""
ioHub
Common Eye Tracker Interface
.. file: iohub/devices/eyetracker/hw/sr_research/eyelink/eyetracker.py

Copyright (C) 2012-2013 iSolver Software Solutions

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

---------------------------------------------------------------------------------------------------------------------
This file uses the pylink module, Copyright (C) SR Research Ltd. License type unknown as it is not provided in the
pylink distribution (atleast when downloaded May 2012). At the time of writing, Pylink is freely avalaible for
download from  www.sr-support.com once you are registered and includes the necessary C DLLs.

EyeLink is also a registered trademark of SR Research Ltd, Ontario, Canada.
---------------------------------------------------------------------------------------------------------------------

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

import os
import numpy as np
from gevent import sleep
import pylink

from ...... import print2err,printExceptionDetailsToStdErr
from ......constants import EventConstants, EyeTrackerConstants
from ......util.experiment import ProgressBarDialog
from ..... import Computer
from .... import EyeTrackerDevice
from ....eye_events import *
from ......server import createErrorResult

try:
    pylink.enableUTF8EyeLinkMessages()
except:
    pass

class EyeTracker(EyeTrackerDevice):
    """The EyeLink EyeTracker class implements support of the SR Research EyeLink 1000 and EyeLink II
    for the ioHub Common Eye Tracker Interface. 
    
    Please see the  eyetracker/hw/sr_research/eyelink/eyetracker/EyeTracker.py documentation page for 
    details on the supported ioHub configuration settings, implementation notes regarding 
    the EyeLink implementation of the Common Eye Tracker Interface API, and other
    useful information.
    
    The EyeLink implementation of the ioHub Common Eye Tracker Interface is currently supported under
    Windows XP and Windows 7. Linux support is likely also available, 
    however it has not been tested at this time.
    """

    # >>> Constants:
    EYELINK=1
    EYELINK_II=2
    EYELINK_1000=3

    # >>> Custom class attributes
    _eyelink=None
    _local_edf_dir='.'
    _full_edf_name='temp'
    _host_edf_name=None
    _active_edf_file=None
    _file_transfer_progress_dialog=None
    # <<<

    # >>> Overwritten class attributes
    DEVICE_TIMEBASE_TO_SEC=0.001
    EVENT_CLASS_NAMES=['MonocularEyeSampleEvent','BinocularEyeSampleEvent','FixationStartEvent',
                         'FixationEndEvent', 'SaccadeStartEvent', 'SaccadeEndEvent',
                         'BlinkStartEvent', 'BlinkEndEvent']
    __slots__=[]
    # <<<

    def __init__(self, *args,**kwargs):
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

        EyeTrackerDevice.__init__(self,*args,**kwargs)
        
        EyeTracker._eyelink=None
       
        try:                
            tracker_config=self.getConfiguration()

            dummyModeEnabled=tracker_config.get('enable_interface_without_connection')
            if dummyModeEnabled:
                self._eyelink.dummy_open()
    
            host_pc_ip_address=tracker_config.get('network_settings')

            EyeTracker._eyelink=pylink.EyeLink(host_pc_ip_address)
            
            self._eyelink.setOfflineMode()

            EyeTracker._eyelink.progressUpdate=self._fileTransferProgressUpdate

            self._addCommandFunctions()

            self._eyelinkSetScreenPhysicalData()

            self._eyelink.sendCommand("button_function 5 'accept_target_fixation'")

            # Set whether to run in mouse simulation mode or not.
            simulation_mode=host_pc_ip_address=tracker_config.get('simulation_mode',False)
            if simulation_mode is True:
                self._eyelink.sendCommand("aux_mouse_simulation = YES")
            else:
                self._eyelink.sendCommand("aux_mouse_simulation = NO")
                
                
            import iohub
            if iohub.data_paths is None:
                EyeTracker._local_edf_dir=os.path.abspath('.')
            else:
                EyeTracker._local_edf_dir=iohub.data_paths['NATIVE_DEVICE_DATA']

            self._setRuntimeSettings(self._runtime_settings)

            # calibration related settings
            eyelink=self._eyelink
            calibration_config=tracker_config.get('calibration',None)
            if calibration_config:
                for cal_key,cal_val in calibration_config.iteritems():
                    if cal_key == 'auto_pace':
                        if cal_val is True:
                            eyelink.enableAutoCalibration()
                        elif cal_val is False:
                            eyelink.disableAutoCalibration()        
                    elif cal_key == 'pacing_speed': # in seconds.msec
                        eyelink.setAutoCalibrationPacing(int(cal_val*1000))        
                    elif cal_key == 'type':
                        VALID_CALIBRATION_TYPES=dict(THREE_POINTS="HV3",FIVE_POINTS="HV5",NINE_POINTS="HV9",THIRTEEN_POINTS="HV13")
                        eyelink.setCalibrationType(VALID_CALIBRATION_TYPES[cal_val])
                    elif cal_key == 'target_type': 
                        pass
                    elif cal_key == 'screen_background_color':
                        pass
                    elif cal_key == 'target_attributes':
                        pass
                    else:
                        print2err("WARNING: unhandled eye tracker calibration setting: {0}, value: {1}".format(cal_key,cal_val))

            # native data recording file
            
            default_native_data_file_name=tracker_config.get('default_native_data_file_name',None)
            if default_native_data_file_name:
                if isinstance(default_native_data_file_name,(str,unicode)):
                    r=default_native_data_file_name.rfind('.')
                    if default_native_data_file_name>0:
                        if default_native_data_file_name[r:] == 'edf'.lower():
                            default_native_data_file_name=default_native_data_file_name[:r]

                    if len(default_native_data_file_name)>7:
                        EyeTracker._full_edf_name=default_native_data_file_name
                        twoDigitRand=np.random.randint(10,99)
                        EyeTracker._host_edf_name=self._full_edf_name[:3]+twoDigitRand+self._full_edf_name[5:7]
                    else:
                        EyeTracker._full_edf_name=default_native_data_file_name
                        EyeTracker._host_edf_name=default_native_data_file_name
                else:
                    print2err("ERROR: default_native_data_file_name must be a string or unicode value")

            if self._local_edf_dir and self._full_edf_name:
                EyeTracker._active_edf_file=self._full_edf_name+'.EDF'    
            self._eyelink.openDataFile(self._host_edf_name+'.EDF')
        except:
            print2err(" ---- Error during EyeLink EyeTracker Initialization ---- ")
            printExceptionDetailsToStdErr()
            print2err(" ---- Error during EyeLink EyeTracker Initialization ---- ")
                    
    def trackerTime(self):
        """
        """
        return self._eyelink.trackerTime()

    def trackerSec(self):
        """
        """
        return self._eyelink.trackerTime()*self.DEVICE_TIMEBASE_TO_SEC

    def setConnectionState(self,enable):
        """
        """
        print2err("EyeLink Interface Warning: setConnectionState is not Handling DUMMY yet.")
        try:
            if enable is True or enable is False:
                if enable is True and not self._eyelink.isConnected():
                    self._eyelink.open()
                    sleep(0.001)
                    pylink.flushGetkeyQueue()
                    self._eyelink.setOfflineMode()
                    return True
                elif enable is False and self._eyelink.isConnected():
                    self._eyelink.setOfflineMode()
    
                    if self._active_edf_file:
                        self._eyelink.closeDataFile()
                        # receive(scr,dest)
                        self._eyelink.receiveDataFile(self._host_edf_name+".EDF",os.path.join(self._local_edf_dir,self._active_edf_file))
    
                    self._eyelink.close()
                    EyeTracker._active_edf_file=None
                    return False
            else:
                return createErrorResult("INVALID_METHOD_ARGUMENT_VALUE",error_message="The enable arguement value provided is not recognized",method="EyeTracker.setConnectionState",arguement='enable', value=enable)            
        except Exception,e:
                return createErrorResult("IOHUB_DEVICE_EXCEPTION",error_message="An unhandled exception occurred on the ioHub Server Process.",method="EyeTracker.setConnectionState",arguement='enable', value=enable, error=e)            
            
            
            
    def isConnected(self):
        """
        """
        try:
            return self._eyelink.isConnected() != 0
        except Exception, e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker.isConnected", error=e)            
            
    def sendCommand(self, key, value=None):
        """
        """
        try:
            if key in EyeTracker._COMMAND_TO_FUNCTION:
                yield EyeTracker._COMMAND_TO_FUNCTION[key](*value)
            else:
                cmdstr=''
                if value is None:
                    cmdstr="{0}".format(key)
                else:
                    cmdstr="{0} = {1}".format(key,value)
    
                yield self._readResultFromTracker(cmdstr)
        except Exception, e:
            yield createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker.sendCommand", key=key,value=value, error=e)            
        
    def sendMessage(self,message_contents,time_offset=None):
        """
        """
        try:        
            if time_offset:            
                r = self._eyelink.sendMessage("\t%d\t%s"%(time_offset,message_contents))
            else:
                r = self._eyelink.sendMessage(message_contents)
    
            if r == 0:
                return EyeTrackerConstants.EYETRACKER_OK
            return r
        except Exception, e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker.sendMessage", message_contents=message_contents,time_offset=time_offset, error=e)            

    def runSetupProcedure(self,starting_state=EyeTrackerConstants.DEFAULT_SETUP_PROCEDURE):
        """
        """
        if starting_state!=EyeTrackerConstants.DEFAULT_SETUP_PROCEDURE:
            return createErrorResult("INVALID_METHOD_ARGUMENT_VALUE",
                error_message="The starting_state arguement value provided is not recognized",
                method="EyeTracker.runSetupProcedure",arguement='starting_state', value=starting_state)            
            
        try:
            #ioHub.print2err('Starting runSetupProcedure')

            import eyeLinkCoreGraphicsIOHubPsychopy
            EyeLinkCoreGraphicsIOHubPsychopy = eyeLinkCoreGraphicsIOHubPsychopy.EyeLinkCoreGraphicsIOHubPsychopy
            
            calibration_properties=self.getConfiguration().get('calibration')
            circle_attributes=calibration_properties.get('target_attributes')
            targetForegroundColor=circle_attributes.get('outer_color') # [r,g,b] of outer circle of targets
            targetBackgroundColor=circle_attributes.get('inner_color') # [r,g,b] of inner circle of targets
            screenColor=calibration_properties.get('screen_background_color')                     # [r,g,b] of screen
            targetOuterDiameter=circle_attributes.get('outer_diameter')     # diameter of outer target circle (in px)
            targetInnerDiameter=circle_attributes.get('inner_diameter')     # diameter of inner target circle (in px)
            
            dc_sounds=calibration_properties.get('dc_sounds',["","",""])                   # targetS, goodS, errorS for DC. "" ==
                                                                           # use current defaults. "off" or None ==
                                                                           # play no sound
            cal_sounds=calibration_properties.get('cal_sounds',["","",""])                 # targetS, goodS, errorS for Cal / Val.

            genv=EyeLinkCoreGraphicsIOHubPsychopy(self,targetForegroundColor=targetForegroundColor,
                                                        targetBackgroundColor=targetBackgroundColor,
                                                        screenColor=screenColor,
                                                        targetOuterDiameter=targetOuterDiameter,
                                                        targetInnerDiameter=targetInnerDiameter,
                                                        dc_sounds=dc_sounds, cal_sounds=cal_sounds)


           # ioHub.print2err("monitor_event_types for eyelink: ", self.monitor_event_types, EyeTracker.ALL_EVENT_CLASSES)
           # ioHub.print2err("self._iohub_server: ",self._iohub_server)
           # genv._registerEventMonitors()
            pylink.openGraphicsEx(genv)

            self._eyelink.doTrackerSetup()

            genv._unregisterEventMonitors() 
            genv.window.close()
            genv.clearAllEventBuffers()

        except Exception,e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker.runSetupProcedure", 
                    starting_state=starting_state,
                    error=e)            

    def isRecordingEnabled(self,*args,**kwargs):
        """
        """
        try:
            return self._eyelink.isRecording()  == 0
        except Exception, e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker.isRecordingEnabled", error=e)

    def enableEventReporting(self,enabled=True):
        """
        """
        try:        
            enabled=EyeTrackerDevice.enableEventReporting(self,enabled)
            return self.setRecordingState(enabled)
        except Exception, e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker.enableEventReporting", error=e)            

    def setRecordingState(self,recording):
        """
        """
        try:
            if not isinstance(recording,bool):
                return createErrorResult("INVALID_METHOD_ARGUMENT_VALUE",
                    error_message="The recording arguement value provided is not a boolean.",
                    method="EyeTracker.setRecordingState",arguement='recording', value=recording)
             
            if recording is True and not self.isRecordingEnabled():                
                error = self._eyelink.startRecording(1,1,1,1)
                if error:
                    return createErrorResult("EYETRACKER_START_RECORD_EXCEPTION",
                            error_message="An error occurred when the eye tracker tried to start recording data.",
                            method="EyeTracker.setRecordingState", eyelink_call='_eyelink.startRecording(1,1,1,1)',
                            recording=recording, error=error)            
    
                if not self._eyelink.waitForBlockStart(100, 1, 0):
                    return createErrorResult("EYETRACKER_START_RECORD_EXCEPTION",
                            error_message="An error occurred when the eye tracker tried to start recording data.",
                            method="EyeTracker.setRecordingState", eyelink_call='_eyelink.waitForBlockStart(100, 1, 0)',
                            recording=recording, error=error)            
                
                EyeTrackerDevice.enableEventReporting(self,True)
                return self.isRecordingEnabled()
            
            elif recording is False and self.isRecordingEnabled():
                self._eyelink.stopRecording()
                EyeTrackerDevice.enableEventReporting(self,False)
                sleep(0.05)

                self._latest_sample=None
                self._latest_gaze_position=None
                return self.isRecordingEnabled()
        except Exception, e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker.setRecordingState", error=e)            

    def getLastSample(self):
        """
        """
        try:
            return self._latest_sample
        except Exception, e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker.getLastSample", error=e)            

    def getLastGazePosition(self):
        """
        """
        try:
            return self._latest_gaze_position
        except Exception, e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker.getLastGazePosition", error=e)             
    
    def _poll(self):
        try:
            if self._eyelink is None:
                return
            eyelink=self._eyelink
            DEVICE_TIMEBASE_TO_SEC=EyeTracker.DEVICE_TIMEBASE_TO_SEC
            poll_time=Computer.getTime()
            confidenceInterval=poll_time-self._last_poll_time
            self._last_poll_time=poll_time
            
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
                        event_type=EventConstants.BINOCULAR_EYE_SAMPLE
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
                                     0, #device id (not currently used)
                                     Computer._getNextEventID(),
                                     event_type,
                                     ne.event_timestamp,
                                     ne.logged_time,
                                     ne.timestamp,
                                     confidenceInterval,
                                     ne.event_delay,
                                     0,
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

                        self._latest_sample=binocSample

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

                        self._latest_gaze_position=g
                        self._addNativeEventToBuffer(binocSample)

                    else:
                        # monocular sample
                        event_type=EventConstants.MONOCULAR_EYE_SAMPLE
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
                                    0, #device id (not currently used)
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
                        self._latest_gaze_position=gaze
                        self._latest_sample=monoSample
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
                         0, #device id (not currently used)
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
                         0, #device id (not currently used)
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
                        0, #device id (not currently used)
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
                        0, #device id (not currently used)
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

        except Exception:
            print2err("ERROR occurred during poll:")
            printExceptionDetailsToStdErr()
                

    def _eyeTrackerToDisplayCoords(self,eyetracker_point):
        """
        """
        try:
            return eyetracker_point
        except Exception,e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker._eyeTrackerToDisplayCoords", 
                    error=e)            
        
    def _displayToEyeTrackerCoords(self,display_x,display_y):
        """
        """
        try:            
            return display_x,display_y
        except Exception,e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker._displayToEyeTrackerCoords", 
                    error=e)            

    def _setRuntimeSettings(self,runtimeSettings):
        for pkey,v in runtimeSettings.iteritems():
            sleep(0.001)

            if pkey == 'sample_filtering':
                all_filters=dict()                
                #ioHub.print2err("sample_filtering: {0}".format(v))
                for filter_type, filter_level in v.iteritems():
                    if filter_type in ['FILTER_ALL','FILTER_FILE','FILTER_ONLINE']:
                        if filter_level in  ['FILTER_LEVEL_OFF','FILTER_LEVEL_1','FILTER_LEVEL_2']:
                            all_filters[filter_type]=filter_level
                self._setSampleFilterLevel(all_filters)
            elif pkey == 'sampling_rate':
                self._setSamplingRate(v)
            elif pkey == 'track_eyes':
                self._setEyesToTrack(v)
            elif pkey == 'vog_settings':
                for vog_key,vog_val in v.iteritems():
                    sleep(0.001)
                    if vog_key == 'pupil_measure_types':
                        self._eyelink.sendCommand("pupil_size_diameter %s"%(vog_val.split('_')[1]))
                    elif vog_key == 'pupil_center_algorithm':
                        self._setPupilDetection(vog_val)
                    elif vog_key == 'tracking_mode':
                        self._setEyeTrackingMode(vog_val)
                    else:
                        print2err("WARNING: unhandled eye tracker config setting ( in sub group vog_settings):",vog_key,vog_val)
                        print2err("")
            else:
                print2err("WARNING: unhandled eye tracker config setting:",pkey,v)

    def _fileTransferProgressUpdate(self,size,received):
        if EyeTracker._file_transfer_progress_dialog is None:
            EyeTracker._file_transfer_progress_dialog =  ProgressBarDialog(
                    "OpenPsycho pyEyeTrackerInterface",
                    "Transferring  " + self._full_edf_name+'.EDF to '+self._local_edf_dir,
                    100,display_index=self._display_device.getIndex())
        elif received >= size and EyeTracker._file_transfer_progress_dialog:
                EyeTracker._file_transfer_progress_dialog.close()
                EyeTracker._file_transfer_progress_dialog = None
        else:
            perc = int((float(received)/float(size))*100.0)+1
            if perc > 100:
                perc=100
            if perc !=self._file_transfer_progress_dialog.getCurrentStatus():
                self._file_transfer_progress_dialog.updateStatus(perc)

    def _setEyesToTrack(self,track_eyes):
        """
        """
        try:
            if isinstance(track_eyes,basestring):
                pass
            else:
                track_eyes = EyeTrackerConstants.getName(track_eyes)
    
            if track_eyes is None:
                print2err("** Warning: UNKNOWN EYE CONSTANT, SETTING EYE TO TRACK TO RIGHT. UNKNOWN EYE CONSTANT: ",track_eyes)
                track_eyes='RIGHT'
            elif track_eyes in ['RIGHT', EyeTrackerConstants.getName(EyeTrackerConstants.RIGHT_EYE)]:
                track_eyes='RIGHT'
            elif track_eyes in ['LEFT', EyeTrackerConstants.getName(EyeTrackerConstants.LEFT_EYE)]:
                track_eyes='LEFT'
            elif r in ['BOTH', EyeTrackerConstants.getName(EyeTrackerConstants.BINOCULAR)]:
                track_eyes='BOTH'
            else:
                print2err("** Warning: UNKNOWN EYE CONSTANT, SETTING EYE TO TRACK TO RIGHT. UNKNOWN EYE CONSTANT: ",track_eyes)
                track_eyes='RIGHT'
    
            srate=self._getSamplingRate()
    
            self._eyelink.sendCommand("lock_active_eye = NO")
    
            if track_eyes == "BOTH":
                if self._eyelink.getTrackerVersion() == 3:
                    if srate>=1000:
                        print2err("ERROR: setEyesToTrack: EyeLink can not record binocularly over 500 hz.")
                    else:
                        trackerVersion =self._eyelink.getTrackerVersionString().strip()
                        trackerVersion = trackerVersion.split(' ')
                        tv = float(trackerVersion[len(trackerVersion)-1])
                        if tv <= 3:
                            if srate>500:
                                print2err("ERROR: setEyesToTrack: Selected sample rate is not supported in binocular mode")
                            else:
                                self._eyelink.sendCommand("binocular_enabled = YES")
                                return True
                        else:
                            rts = []
                            modes = self._readResultFromTracker("read_mode_list")
                            if modes is None or modes.strip() == 'Unknown Variable Name':
                                print2err("ERROR: setEyesToTrack: Failed to get supported modes. ")
                            modes = modes.strip().split()
    
                            for x in modes:
                                if x[-1] == 'B':
                                    x =int(x.replace('B',' ').strip())
                                    rts.append(x)
                            if srate in rts:
                                self._eyelink.sendCommand("binocular_enabled = YES")
                                return True
                            else:
                                print2err("ERROR: setEyesToTrack: Selected sample rate is not supported!")
            elif track_eyes in ("LEFT", 'RIGHT'):
                self.sendCommand("binocular_enabled = NO")
                return True
            else:
                self.sendCommand("binocular_enabled = NO")
                self.sendCommand("active_eye = %s"%(track_eyes))
                self.sendCommand("lock_active_eye = YES")
        except Exception, e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker.setEyesToTrack", error=e)            


    def _setSamplingRate(self,sampling_rate):
        """
        """
        try:        
            if self.isConnected():
                srate=sampling_rate
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
                            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                                    error_message="Error: Could not retrieve sample rate modes from EyeLink Host.",
                                    method="EyeTracker.setSamplingRate", error=e)            
                        modes = modes.strip().split()
    
                        #ioHub.print2err("Modes = ", modes)
                        for x in modes:
                            m = x.replace('B',' ').strip()
                            m = m.replace('R',' ').strip()
                            x =int(m)
                            rts.append(x)
                        if srate in rts:
                            self._eyelink.sendCommand("sample_rate = %d"%(srate))
                    else:
                        if srate<=1000:
                            self.sendCommand("sample_rate = %d"%(srate))
                return self._getSamplingRate()
            return EyeTrackerConstants.EYETRACKER_ERROR
        except Exception, e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker._getSamplingRate", error=e)            

    def _setSampleFilterLevel(self,filter_settings_dict):
        """
        """
        try:
            if len(filter_settings_dict)>0:
                supportedTypes='FILTER_ALL','FILTER_FILE','FILTER_ONLINE'
                supportedLevels= 'FILTER_LEVEL_OFF','FILTER_LEVEL_1','FILTER_LEVEL_2'

                ffilter=0
                lfilter=0
                update_filter=False
                for key,value in filter_settings_dict.iteritems():
                    if key in supportedTypes and value in supportedLevels:
                        if key == 'FILTER_ALL':
                            self._eyelink.setHeuristicLinkAndFileFilter(getattr(EyeTrackerConstants,value),getattr(EyeTrackerConstants,value))
                            return EyeTrackerConstants.EYETRACKER_OK
                        elif key == 'FILTER_FILE':
                            ffilter=getattr(EyeTrackerConstants,value)
                            update_filter=True
                        elif key == 'FILTER_ONLINE':
                            lfilter=getattr(EyeTrackerConstants,value)
                            update_filter=True
                    else:
                        return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                                error_message="Unsupported eyetracker sample filter type or filter level.",
                                filter_type=key, filter_level=value, 
                                supported_types=supportedTypes,
                                supported_levels=supportedLevels)            
                        
                if update_filter:  
                    self._eyelink.setHeuristicLinkAndFileFilter(ffilter,lfilter)
                    return EyeTrackerConstants.EYETRACKER_OK
                    
            return EyeTrackerConstants.EYETRACKER_ERROR
        except Exception, e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker.setDataFilterLevel", error=e)            

    def _eyelinkSetScreenPhysicalData(self):
        try:        
            eyelink=self._eyelink
    
            # eye to screen distance
            sdist=self._display_device.getConfiguration().get('default_eye_distance',None)
            if sdist:
                if 'surface_center' in sdist:
                    eyelink.sendCommand("screen_distance = %d "%(sdist['surface_center'],))
            else:
                print2err('ERROR: "default_eye_distance":"surface_center" value could not be read from monitor settings')
                return False
    
            # screen_phys_coords
            sdim=self._display_device.getConfiguration().get('physical_dimensions',None)
            if sdim:
                if 'width' in sdim and 'height' in sdim:
                    sw=sdim['width']
                    sh=sdim['height']
                    hsw=sw/2.0
                    hsh=sh/2.0
    
                    eyelink.sendCommand("screen_phys_coords = -%.3f, %.3f, %.3f, -%.3f"%(hsw,hsh,hsw,hsh))
            else:
                print2err('ERROR: "physical_stimudisplay_x,display_ylus_area":"width" or "height" value could not be read from monitor settings')
                return False
    
            # calibration coord space
            l,t,r,b=self._display_device.getCoordBounds()
            eyelink.sendCommand("screen_pixel_coords %.5f %.5f %.5f %.5f" %(l,t,r,b))
            eyelink.sendMessage("DISPLAY_COORDS  %.0f %.0f %.0f %.0f" %(l,t,r,b))
    
            sleep(0.001)
        except Exception,e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker._eyelinkSetScreenPhysicalData", 
                    error=e)            


    def _eyeLinkHardwareAndSoftwareVersion(self):
        try:        
            tracker_software_ver = 0
            eyelink_ver = self._eyelink.getTrackerVersion()
    
            if eyelink_ver == 3:
                tvstr = self._eyelink.getTrackerVersionString()
                vindex = tvstr.find("EYELINK CL")
                tracker_software_ver = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))
    
            return eyelink_ver, tracker_software_ver
        except Exception,e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker._eyeLinkHardwareAndSoftwareVersion", 
                    error=e)            

    def _eyelinkSetLinkAndFileContents(self):
        try:
            eyelink = self._eyelink
    
            eyelink_hw_ver, eyelink_sw_ver = self._eyeLinkHardwareAndSoftwareVersion()
    
            # set EDF file contents
            eyelink.sendCommand("file_event_filter = LEFT, RIGHT, FIXATION, SACCADE, BLINK, MESSAGE, BUTTON, INPUT")
            eyelink.sendCommand("file_event_data = GAZE , GAZERES , HREF , AREA  , VELOCITY , STATUS")
    
            if eyelink_sw_ver>=4:
                eyelink.sendCommand("file_sample_data = GAZE, GAZERES, HREF , PUPIL , AREA ,STATUS, BUTTON, INPUT, HTARGET")
            else:
                eyelink.sendCommand("file_sample_data = GAZE, GAZERES, HREF , PUPIL , AREA ,STATUS, BUTTON, INPUT")
    
            sleep(0.001)
    
    
            # set link data
            eyelink.sendCommand("link_event_filter = LEFT, RIGHT, FIXATION, SACCADE , BLINK, BUTTON, MESSAGE, INPUT")
            eyelink.sendCommand("link_event_data = GAZE, GAZERES, HREF , AREA, VELOCITY, STATUS")
    
            if eyelink_sw_ver>=4:
                eyelink.sendCommand("link_sample_data = GAZE, GAZERES, HREF , PUPIL , AREA ,STATUS, BUTTON, INPUT , HTARGET")
            else:
                eyelink.sendCommand("link_sample_data = GAZE, GAZERES, HREF , PUPIL , AREA ,STATUS, BUTTON, INPUT")
        except Exception,e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker._eyelinkSetLinkAndFileContents", 
                    error=e)            

    def _addCommandFunctions(self):
        try:
            self._COMMAND_TO_FUNCTION['getTrackerMode']=_getTrackerMode
            self._COMMAND_TO_FUNCTION['doDriftCorrect']=_doDriftCorrect
            self._COMMAND_TO_FUNCTION['eyeAvailable']=_eyeAvailable
            self._COMMAND_TO_FUNCTION['enableDummyOpen']=_dummyOpen
            self._COMMAND_TO_FUNCTION['getLastCalibrationInfo']=_getCalibrationMessage
            self._COMMAND_TO_FUNCTION['applyDriftCorrect']=_applyDriftCorrect
            self._COMMAND_TO_FUNCTION['setIPAddress']=_setIPAddress
            self._COMMAND_TO_FUNCTION['setLockEye']=_setLockEye
            self._COMMAND_TO_FUNCTION['setLocalResultsDir']=_setNativeRecordingFileSaveDir
        except Exception,e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker._addCommandFunctions", 
                    error=e)            

    def _readResultFromTracker(self,cmd,timeout=200):
        try:
            self._eyelink.readRequest(cmd)
    
            t = pylink.currentTime()
            # Waits for a maximum of timeout msec
            while(pylink.currentTime()-t < timeout):
                rv = self._eyelink.readReply()
                if rv and len(rv) >0:
                    return rv
            return None
        except Exception,e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker._readResultFromTracker", 
                    error=e)            

    def _setPupilDetection(self,pmode):
        try:
            if(pmode.upper() == "ELLIPSE"):
                self.sendCommand("use_ellipse_fitter = YES")
            else:
                self.sendCommand("use_ellipse_fitter = NO")
        except Exception,e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker._setPupilDetection", 
                    error=e)            
        
    def _getPupilDetectionModel(self):
        try:
            v = self._readResultFromTracker("use_ellipse_fitter")
            if v !="0":
                return "ELLIPSE"
            else:
                return "CENTROID"
        except Exception,e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker._getPupilDetectionModel", 
                    error=e)            

    def _setEyeTrackingMode(self,r=0):
        try:
            ri=-1
            if r is "PUPIL-ONLY":
                ri=0
            elif r.upper is "PUPIL-CR":
                ri=1
            if ri>=0:
                self.sendCommand("corneal_mode %d"%(ri))
                return True
            return False
        except Exception,e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker._setEyeTrackingMode", 
                    error=e)            
        
    def _getSamplingRate(self):
        """
        """
        try:        
            if self.isConnected():
                return self._eyelink.getSampleRate()
            return EyeTrackerConstants.EYETRACKER_ERROR
        except Exception, e:
            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                    error_message="An unhandled exception occurred on the ioHub Server Process.",
                    method="EyeTracker.getSamplingRate", error=e)            

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
    try:
        r=pylink.getEyeLink().getTrackerMode()
        return _EYELINK_HOST_MODES[r]
    except Exception,e:
        return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                error_message="An unhandled exception occurred on the ioHub Server Process.",
                method="_getTrackerMode", 
                error=e)            

def _doDriftCorrect(*args,**kwargs):
    try:
        if len(args)==4:
            x,y,draw,allow_setup=args
            r=pylink.getEyeLink().doDriftCorrect(x,y,draw,allow_setup) 
            return r
        else:
            print2err("doDriftCorrect requires 4 parameters, received: ", args)
            return False
    except Exception,e:
        return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                error_message="An unhandled exception occurred on the ioHub Server Process.",
                method="_doDriftCorrect", 
                error=e)            

def _applyDriftCorrect():
    try:
        r=pylink.getEyeLink().applyDriftCorrect()
        if r == 0:
            return True
        else:
            return ['EYE_TRACKER_ERROR','applyDriftCorrect',r]
    except Exception,e:
        return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                error_message="An unhandled exception occurred on the ioHub Server Process.",
                method="_applyDriftCorrect", 
                error=e)            
        
def _eyeAvailable(*args,**kwargs):
    try:
        r=pylink.getEyeLink().eyeAvailable()
        if r== 0:
            return EyeTrackerConstants.getName(EyeTrackerConstants.LEFT_EYE)
        elif r==1:
            return EyeTrackerConstants.getName(EyeTrackerConstants.RIGHT_EYE)
        elif r == 2:
            return EyeTrackerConstants.getName(EyeTrackerConstants.BINOCULAR)
        else:
            return EyeTrackerConstants.UNDEFINED
    except Exception,e:
        return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                error_message="An unhandled exception occurred on the ioHub Server Process.",
                method="_eyeAvailable", 
                error=e)            

def _dummyOpen(*args,**kwargs):
    try:
        r=pylink.getEyeLink().dummy_open()
        return r
    except Exception,e:
        return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                error_message="An unhandled exception occurred on the ioHub Server Process.",
                method="_dummyOpen", 
                error=e)            
    
def _getCalibrationMessage(*args,**kwargs):
    try:
        m=pylink.getEyeLink().getCalibrationMessage()
        r=pylink.getEyeLink().getCalibrationResult()
        if r in _eyeLinkCalibrationResultDict:
            r=_eyeLinkCalibrationResultDict[r]
        else:
            r = 'NO_REPLY'
        rString="Last Calibration Message:\n{0}\n\nLastCalibrationResult:\n{1}".format(m,r)
        return rString
    except Exception,e:
        return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                error_message="An unhandled exception occurred on the ioHub Server Process.",
                method="_getCalibrationMessage", 
                error=e)            
        
def _setIPAddress(*args, **kwargs):
    try:
        if len(args)==1:
            ipString=args[0]
            r=pylink.getEyeLink().setAddress(ipString)
            if r == 0:
                return True
        return ['EYE_TRACKER_ERROR','setIPAddress','Could not Parse IP String']
    except Exception,e:
        return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                error_message="An unhandled exception occurred on the ioHub Server Process.",
                method="_setIPAddress", 
                error=e)            

def _setLockEye(*args,**kwargs):
    try:
        if len(args)==1:
            enable=args[0]
            r=pylink.getEyeLink().sendCommand("lock_eye_after_calibration %d"%(enable))
            return r
        return ['EYE_TRACKER_ERROR','setLockEye','One argument is required, bool type.']
    except Exception,e:
        return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                error_message="An unhandled exception occurred on the ioHub Server Process.",
                method="_setLockEye", 
                error=e)            

def _setNativeRecordingFileSaveDir(*args):
    try:
        if len(args)>0:
            edfpath=args[0]
            print2err("Setting File Save path: ",edfpath)
            EyeTracker._local_edf_dir=edfpath
    except Exception,e:
        return createErrorResult("IOHUB_DEVICE_EXCEPTION",
                error_message="An unhandled exception occurred on the ioHub Server Process.",
                method="_setNativeRecordingFileSaveDir", 
                error=e)            
                
#    def drawToHostApplicationWindow(self,graphic_type,**graphic_attributes):
#        """
#        EyeLink supported:
#
#        graphic_type: EyeTrackerConstants.TEXT_GRAPHIC
#        graphic_attributes: text='The text to draw', position=(x,y)
#                where x,y is the position to draw the text in calibrated screen coords.
#
#        graphic_type: EyeTrackerConstants.CLEAR_GRAPHICS
#        graphic_attributes: color = int, between 0 - 15, the color from the EyeLink Host PC palette to use.
#
#        graphic_type: EyeTrackerConstants.LINE_GRAPHIC
#        graphic_attributes: color= int 0 - 15,  start=(x,y), end=(x,y)
#                where x,y are the start and end position to draw the line in calibrated screen coords.
#
#        graphic_type: EyeTrackerConstants.RECTANGLE_GRAPHIC
#        graphic_attributes:  x  = x coordinates for the top-left corner of the rectangle.
#                 y  = y coordinates for the top-left corner of the rectangle.
#                 width = width of the filled rectangle.
#                 height = height of the filled rectangle.
#                 color = 0 to 15.
#                 filled (optional) = True , then box is filled, False and box is only an outline.
#        """
#        try:
#            if graphic_type==EyeTrackerConstants.TEXT_GRAPHIC:
#                if 'text' in graphic_attributes and 'position' in graphic_attributes:
#                    text=graphic_attributes['text']
#                    position=graphic_attributes['position']
#                    return self._eyelink.drawText(str(text),position)
#                return createErrorResult("INVALID_METHOD_ARGUMENT_VALUE",
#                    error_message="The graphic_attributes arguement kwargs provided is not complete.",
#                    method="EyeTracker.drawToHostApplicationWindow",arguement='graphic_attributes', value=graphic_attributes)
#            elif graphic_type==EyeTrackerConstants.CLEAR_GRAPHICS:
#                if 'color' in graphic_attributes:
#                    pcolor=int(graphic_attributes['color'])
#                    if pcolor >=0 and pcolor <= 15:
#                        return self._eyelink.clearScreen(pcolor)
#                return createErrorResult("INVALID_METHOD_ARGUMENT_VALUE",
#                    error_message="The graphic_attributes arguement kwargs provided is not complete.",
#                    method="EyeTracker.drawToHostApplicationWindow",arguement='graphic_attributes', value=graphic_attributes)
#            elif graphic_type==EyeTrackerConstants.LINE_GRAPHIC:
#                if 'color' in graphic_attributes and 'start' in graphic_attributes and 'end' in graphic_attributes:
#                    pcolor=int(graphic_attributes['color'])
#                    sposition = graphic_attributes['start']
#                    eposition = graphic_attributes['end']
#                    if pcolor >=0 and pcolor <= 15 and len(sposition)==2 and len(eposition)==2:
#                        return self._eyelink.drawLine(sposition, eposition,pcolor)
#                return createErrorResult("INVALID_METHOD_ARGUMENT_VALUE",
#                    error_message="The graphic_attributes arguement kwargs provided is not complete.",
#                    method="EyeTracker.drawToHostApplicationWindow",arguement='graphic_attributes', value=graphic_attributes)
#            elif graphic_type==EyeTrackerConstants.RECTANGLE_GRAPHIC:
#                if 'color' in kwargs and 'x' in kwargs and 'y' in kwargs and 'width' in kwargs and 'height' in kwargs:
#                    pcolor=kwargs['color']
#                    x=kwargs['x']
#                    y=kwargs['y']
#                    width=kwargs['width']
#                    height=kwargs['height']
#                    filled=False
#                    if filled in kwargs:
#                        filled=kwargs['filled']
#                    if pcolor >=0 and pcolor <= 15:
#                        if filled is True:
#                            return self._eyelink.drawBox(x, y,width, height, pcolor)
#                        else:
#                            return self._eyelink.drawFilledBox(x, y,width, height, pcolor)
#                return createErrorResult("INVALID_METHOD_ARGUMENT_VALUE",
#                    error_message="The graphic_attributes arguement kwargs provided is not complete.",
#                    method="EyeTracker.drawToHostApplicationWindow",arguement='graphic_attributes', value=graphic_attributes)
#        except Exception, e:
#            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
#                    error_message="An unhandled exception occurred on the ioHub Server Process.",
#                    method="EyeTracker.drawToHostApplicationWindow", 
#                    graphic_type=graphic_type,graphic_attributes=graphic_attributes,error=e)            
#
#    def getDigitalPortState(self, port):
#        """
#        """
#        try:
#            return self._eyelink.readIOPort(port)
#        except Exception, e:
#            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
#                    error_message="An unhandled exception occurred on the ioHub Server Process.",
#                    method="EyeTracker.getDigitalPortState", 
#                    port=port,error=e)            
#         
#    def setDigitalPortState(self, port, value):
#        """
#        """
#        try:
#            return self._eyelink.writeIOPort(port, value)
#        except Exception, e:
#            return createErrorResult("IOHUB_DEVICE_EXCEPTION",
#                    error_message="An unhandled exception occurred on the ioHub Server Process.",
#                    method="EyeTracker.setDigitalPortState", 
#                    port=port,error=e)           