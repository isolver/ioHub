"""
ioHub
Common Eye Tracker Interface
.. file: ioHub/devices/eyeTracker/HW/Tobii/TobiiCalibrationGraphics.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

---------------------------------------------------------------------------------------------------------------------
This file uses the pylink module, Copyright (C) SR Research Ltd. License type unknown as it is not provided in the
pylink distribution (atleast when downloaded May 2012). At the time of writing, Pylink is freely avalaible for
download from  www.sr-support.com once you are registered and includes the necessary C DLLs.
---------------------------------------------------------------------------------------------------------------------

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor::
"""

from psychopy import visual

import time, Queue

import ioHub.external_libs
import ioHub.devices
from ioHub.devices import Computer
from ioHub.constants import EventConstants, KeyboardConstants

currentTime=Computer.getTime

class TobiiPsychopyCalibrationGraphics(object):
    IOHUB_HEARTBEAT_INTERVAL=0.050   # seconds between forced run through of
                                     # micro threads, since one is blocking
                                     # on camera setup.
    WINDOW_BACKGROUND_COLOR=(128,128,128)
    CALIBRATION_POINT_OUTER_RADIUS=15.0,15.0
    CALIBRATION_POINT_OUTER_EDGE_COUNT=64
    CALIBRATION_POINT_OUTER_COLOR=(255,255,255)
    CALIBRATION_POINT_INNER_RADIUS=3.0,3.0
    CALIBRATION_POINT_INNER_EDGE_COUNT=32
    CALIBRATION_POINT_INNER_COLOR=(25,25,25)
    CALIBRATION_POINT_LIST=[(0.5, 0.5),(0.1, 0.1),(0.9, 0.1),(0.9, 0.9),(0.1, 0.9),(0.5, 0.5)]

    TEXT_POS=[0,0]
    TEXT_COLOR=[0,0,0]
    TEXT_HEIGHT=48
    
    def __init__(self, eyetrackerInterface, targetForegroundColor=None, 
                 targetBackgroundColor=None, screenColor=None, 
                 targetOuterDiameter=None, targetInnerDiameter=None,
                 calibrationPointList=None):
        ppd_x,ppd_y=ioHub.devices.Display.getPPD()
        self.screenSize = ioHub.devices.Display.getStimulusScreenResolution()
        self._eyetrackerinterface=eyetrackerInterface
        self._tobii = eyetrackerInterface._tobii._eyetracker

        if targetForegroundColor is not None:
            TobiiPsychopyCalibrationGraphics.CALIBRATION_POINT_OUTER_COLOR=targetForegroundColor

        if targetBackgroundColor is not None:
            TobiiPsychopyCalibrationGraphics.CALIBRATION_POINT_INNER_COLOR=targetBackgroundColor

        if screenColor is not None:
            TobiiPsychopyCalibrationGraphics.WINDOW_BACKGROUND_COLOR=screenColor

        if targetOuterDiameter is not None:
            TobiiPsychopyCalibrationGraphics.CALIBRATION_POINT_OUTER_RADIUS=targetOuterDiameter/2.0,targetOuterDiameter/2.0
        else:
            TobiiPsychopyCalibrationGraphics.CALIBRATION_POINT_OUTER_RADIUS=ppd_x/2.0,ppd_y/2.0

        if targetInnerDiameter is not None:
            TobiiPsychopyCalibrationGraphics.CALIBRATION_POINT_INNER_RADIUS=targetInnerDiameter/2.0,targetInnerDiameter/2.0
        else:
            TobiiPsychopyCalibrationGraphics.CALIBRATION_POINT_INNER_RADIUS=ppd_x/6.0,ppd_y/6.0


        if calibrationPointList is not None:
            TobiiPsychopyCalibrationGraphics.CALIBRATION_POINT_LIST=calibrationPointList

        self._msg_queue=Queue.Queue()
        
        self._ioKeyboard=None
        #self._ioMouse=None
        self._ioServer=None
        
        self.width=self.screenSize[0]
        self.height=self.screenSize[1]

        self.window = visual.Window(self.screenSize, monitor="calibrationMonitor", units='pix', fullscr=True, allowGUI=False, screen=ioHub.devices.Display.getStimulusScreenIndex())
        self.window.setColor(self.WINDOW_BACKGROUND_COLOR,'rgb255')        
        self.window.flip(clearBuffer=True)
        self.window.flip(clearBuffer=True)
        
        self._createStim()
        
        self._registerEventMonitors()
        self._lastMsgPumpTime=currentTime()
        
        self.clearAllEventBuffers()

    def clearAllEventBuffers(self):
        self._ioServer.eventBuffer.clear()
        for d in self._ioServer.devices:
            d.clearEvents()

    def _registerEventMonitors(self):
        self._ioServer=self._eyetrackerinterface._ioServer

        if self._ioServer:
            for dev in self._ioServer.devices:
                ioHub.print2err("dev: ",dev.__class__.__name__)
                if dev.__class__.__name__ == 'Keyboard':
                    kbDevice=dev

        if kbDevice:
            self._ioKeyboard=kbDevice
            self._ioKeyboard._addEventListener(self)
        else:
            ioHub.print2err("Warning: Tobii Cal GFX could not connect to Keyboard device for events.")

    def _unregisterEventMonitors(self):
        if self._ioKeyboard:
            self._ioKeyboard._removeEventListener(self)
     
    def _handleEvent(self,ioe):
        event_type_index=ioHub.devices.DeviceEvent.EVENT_TYPE_ID_INDEX
        if ioe[event_type_index] == EventConstants.KEYBOARD_PRESS:
            if ioe[-3] == 'SPACE':
                self._msg_queue.put("SPACE_KEY_ACTION")
                self.clearAllEventBuffers()
            if ioe[-3] == 'ESCAPE':
                self._msg_queue.put("QUIT")
                self.clearAllEventBuffers()

    def MsgPump(self):
        #keep the psychopy window happy ;)
        if currentTime()-self._lastMsgPumpTime>self.IOHUB_HEARTBEAT_INTERVAL:                
            # try to keep ioHub, being blocked. ;(
            if self._ioServer:
                for dm in self._ioServer.deviceMonitors:
                    dm.device._poll()
                self._ioServer._processDeviceEventIteration()
            self._lastMsgPumpTime=currentTime()

    def getNextMsg(self):
        try:
            msg=self._msg_queue.get(block=True,timeout=0.05)
            self._msg_queue.task_done()
            return msg
        except Queue.Empty:
            pass

    def _createStim(self):                
        self.calibrationPointOUTER = visual.Circle(self.window,pos=(0,0) ,lineWidth=0.0,radius=self.CALIBRATION_POINT_OUTER_RADIUS,name='CP_OUTER', units='pix',opacity=1.0, interpolate=False)
        self.calibrationPointINNER = visual.Circle(self.window,pos=(0,0),lineWidth=0.0, radius=self.CALIBRATION_POINT_INNER_RADIUS, name='CP_INNER',units='pix',opacity=1.0, interpolate=False)
        
        self.calibrationPointOUTER.setFillColor(self.CALIBRATION_POINT_OUTER_COLOR,'rgb255')
        self.calibrationPointOUTER.setLineColor(None,'rgb255')
        self.calibrationPointINNER.setFillColor(self.CALIBRATION_POINT_INNER_COLOR,'rgb255')
        self.calibrationPointINNER.setLineColor(None,'rgb255 ')

        instuction_text="Press Space Key to Start".center(32)+'\n'+"Eye Tracker Calibration.".center(32)
        self.startCalibrationTextScreen=visual.TextStim(self.window, text=instuction_text, pos = self.TEXT_POS, height=self.TEXT_HEIGHT, color=self.TEXT_COLOR, colorSpace='rgb255',alignHoriz='center',alignVert='center',wrapWidth=self.width*0.8)
        
    def runCalibration(self):
        import tobii
        
        calibration_sequence_completed=False
        quit_calibration_notified=False
        
        self.window.flip()
        self.startCalibrationTextScreen.draw()
        self.window.flip()
        
        self.clearAllEventBuffers()
 
        stime=currentTime()
        while currentTime()-stime<60*5.0:
            msg=self.getNextMsg()
            if msg == 'SPACE_KEY_ACTION':
                break

            self.MsgPump()

        self.clearAllEventBuffers()
       
        self._tobii.StartCalibration(self.on_start_calibration)   

        i=0
        for pt in self.CALIBRATION_POINT_LIST:
            w,h=self.screenSize
            ioHub.print2err("Screen Size: ",w," ",h)
            self.clearAllEventBuffers()
            pix_pt=int(w*pt[0]-w/2),int(h*(1.0-pt[1])-h/2)
            ioHub.print2err( "Cal point Mapping: ",pt," == ",pix_pt)
            self.drawCalibrationTarget(pix_pt)

            stime=currentTime()
            while currentTime()-stime<2.5:
                msg=self.getNextMsg()
                if msg == 'SPACE_KEY_ACTION':
                    break
                elif msg == 'QUIT':
                    quit_calibration_notified=True
                    
                self.MsgPump()
            
            if quit_calibration_notified:
                break
            
            pt2D=tobii.sdk.types.Point2D(pt[0],pt[1])
            ioHub.print2err(pt2D)
            self._tobii.AddCalibrationPoint(pt2D,self.on_add_calibration_point)
            time.sleep(0.5)            
            self.clearCalibrationWindow()
            self.clearAllEventBuffers()

            i+=1
            if i == len(self.CALIBRATION_POINT_LIST):
                calibration_sequence_completed=True
        
        if calibration_sequence_completed:
            self._tobii.ComputeCalibration(self.on_compute_calibration_result)
 
        msg=1
        while msg is not "CALIBRATION_COMPLETE":        
            msg=self.getNextMsg()
            
        self._tobii.StopCalibration(self.on_stop_calibration)  
        
    def clearCalibrationWindow(self):
        self.window.flip(clearBuffer=True)
        
    def drawCalibrationTarget(self,tp):        
        self.calibrationPointOUTER.setPos(tp)            
        self.calibrationPointINNER.setPos(tp)            
        self.calibrationPointOUTER.draw()          
        self.calibrationPointINNER.draw()            
        self.window.flip(clearBuffer=True)
           
    def on_start_calibration(self,*args,**kwargs):
        ioHub.print2err('on_start_calibration: ',args,kwargs)

    def on_add_calibration_point(self,*args,**kwargs):
        ioHub.print2err('on_add_calibration_point: ',args,kwargs)
        self._msg_queue.put('DRAW_NEXT')

    def on_stop_calibration(self,*args,**kwargs):
        ioHub.print2err('on_stop_calibration: ',args,kwargs)

    def on_compute_calibration_result(self,*args,**kwargs):
        ioHub.print2err('on_compute_calibration_result: ',args,kwargs)
        self._msg_queue.put("CALIBRATION_COMPLETE")

