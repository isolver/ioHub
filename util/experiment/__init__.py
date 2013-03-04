# -*- coding: utf-8 -*-
"""
Created on Sat Nov 03 19:09:25 2012

@author: Sol
"""
import platform

if platform.system() == 'Windows':
    import pythoncom
    
    def pumpLocalMessageQueue():
        """
        Pumps the Experiment Process Windows Message Queue so the PsychoPy Window does not appear to be 'dead' to the
        OS. If you are not flipping regularly (say because you do not need to and do not want to block frequently,
        you can call this, which will not block waiting for messages, but only pump out what is in the que already.
        On an i7 desktop, this call method taking between 10 and 90 usec.
        """
        if pythoncom.PumpWaitingMessages() == 1:
            raise KeyboardInterrupt()

from variableProvider import ExperimentVariableProvider

from visualStimUtil import generatedPointGrid, Rotate2D, SinusoidalMotion

from screenState import ScreenState, ClearScreen, InstructionScreen, ImageScreen, DeviceEventTrigger

from psychopyIOHubRuntime import ioHubExperimentRuntime

from dialogs import ProgressBarDialog, MessageDialog, FileDialog

