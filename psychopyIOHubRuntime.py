from __future__ import division
import psychopy
from psychopy import logging, core, visual, gui
import os,gc,psutil
from collections import deque
import time
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print "*** Using Python based YAML Parsing"
    from yaml import Loader, Dumper
from ioHub.devices import EventConstants
            
class SimpleIOHubRuntime(object):
    def __init__(self, configFilePath, configFile):
        '''
        Initialize the Experiment Object. 
        ''' 
        # as of 2.7, timeit.default_timer correctly selects the best clock based on OS
        # for high precision timing. < 2.7, you need to check the OS version yourself
        # and select; or use the psychopy clocks since it does the work for you. ;)
        import timeit
        self.currentTime=timeit.default_timer

        self.configFilePath=configFilePath
        self.configFileName=configFile
        
        # load the experiment config settings from the experiment_config.yaml file.
        # The file must be in the same directory as the experiment script.
        self.configuration=load(file(os.path.join(configFilePath,configFile),'r'), Loader=Loader)

        self.experimentConfig=dict()
        self._experimentConfigKeys=['title','code','version','description','total_sessions_to_run']
        for key in self._experimentConfigKeys:
            if key in self.configuration:
                self.experimentConfig[key]=self.configuration[key]
 
        self.experimentSessionDefaults=self.configuration['session_defaults']
        self.sessionUserVariables=self.experimentSessionDefaults['user_variables']
        del self.experimentSessionDefaults['user_variables']
        
        # self.hub will hold the reference to the ioHubClient object, used to access the ioHubServer
        # process and devices.
        self.hub=None
        # holds events collected from the ioHub during periods like msecWait()
        self.allEvents=None
        
        # indicates if the experiment is in high priority mode or not. Do not set directly.
        # See enableHighPriority() and disableHighPriority()
        self._inHighPriorityMode=False
        
        # initialize the experiment object based on the configuration settings.
        self.initalizeConfiguration()
        
    def initalizeConfiguration(self):
        '''
        Based on the configuration data in the experiment_config.yaml and iohub_config.yaml,
        configure the experiment environment.
        '''
        if 'ioHub' in self.configuration and self.configuration['ioHub']['enable'] is True:
            import ioHub
            from ioHub.client import ioHubClient       

            ioHubConfigFileName=self.configuration['ioHub']['config']
            configAbsPath=os.path.join(self.configFilePath,ioHubConfigFileName)
            self.ioHubConfig=load(file(configAbsPath,'r'), Loader=Loader)
            
            self.hub=ioHubClient(self.ioHubConfig,configAbsPath)
 
            self.hub.startServer()
            
            # Is ioHub configured to be run in experiment?
            if self.hub:
            
                # display a read only dialog verifying the experiment parameters 
                # (based on the experiment .yaml file) to be run. User can hit OK to continue,
                # or Cancel to end the experiment session if the wrong experiment was started.
                exitExperiment=self.displayExperimentSettingsDialog()
                if exitExperiment:
                    print "User Cancelled Experiment Launch."
                    self.close()
                    import sys
                    sys.exit(1)
            
            
                # send experiment info and set exp. id
                self.hub.sendExperimentInfo(self.experimentConfig)
                
                # display editable session variable dialog displaying the ioHub required session variables
                # and any user defined session variables (as specified in the experiment config .yaml file)
                # User can enter correct values and hit OK to continue, or Cancel to end the experiment session.
                exitExperiment=self.displayExperimentSessionSettingsDialog()
                if exitExperiment:
                    print "User Cancelled Experiment Launch."
                    self.close()
                    import sys
                    sys.exit(1)
                
                # send session data to ioHub and get session ID (self.hub.sessionID)
                tempdict=(self.experimentSessionDefaults)
                tempdict['user_variables']=self.sessionUserVariables
                self.hub.sendSessionInfo(tempdict)
                
                # get the list of devices regigisted with the ioHub
                dlist=self.hub.getDeviceList()

                # create a local 'thin' representation of the registered ioHub devices,
                # allowing such things as device level event access (if supported) 
                # and transparent IPC calls of public device methods and return value access.
                # Devices are available as hub.devices.[device_name] , where device_name
                # is the name given to the device in the ioHub .yaml config file to be access;
                # i.e. hub.devices.ExperimentPCkeyboard would access the experiment PC keyboard
                # device if the default name was being used.
                self.hub.createDeviceList(dlist)                   
                        
                # A circular buffer used to hold events retrieved from self.getEvents() during 
                # self.delay() calls. self.getEvents() appends any events in the allEvents
                # buffer to the result of the hub.getEvents() call that is made.                
                self.allEvents=deque(maxlen=self.configuration['event_buffer_length'])
        else:
            print "** ioHub is Disabled (or should be). Why are you using this utility class then? ;) **"
            
        return self.hub
    
    def enableHighPriority(self,disable_gc=True):
        '''
        sets the priority of the experiment process to high prority
        and optionally (default is true) disable the python GC. This is very
        useful for the duration of a trial, for example, where you enable at
        start of trial and disable at end of trial. Improves Windows 
        sloppyness greatly in general.
        '''
        if self._inHighPriorityMode is False:
            if disable_gc:
                gc.disable()
            p = psutil.Process(os.getpid())
            p.nice=psutil.HIGH_PRIORITY_CLASS
            self._inHighPriorityMode=True

    def disableHighPriority(self):
        '''
        sets the priority of the experiment process back to normal prority
        and enables the python GC. This is very useful for the duration of a trial,
        for example, where you call enableHighPriority() at
        start of trial and call disableHighPriority() at end of trial. 
        Improves Windows sloppyness greatly in general.
        '''        
        if self._inHighPriorityMode is True:
            gc.enable()
            p = psutil.Process(os.getpid())
            p.nice=psutil.NORMAL_PRIORITY_CLASS
            self._inHighPriorityMode=False
    
    def currentMsec(self):
        return self.currentTime()*1000.0
        
    def msecDelay(self,msecDelay,checkHubInterval=10):
        stime=self.currentMsec()
        targetEndTime=stime+msecDelay

        if checkHubInterval < 0:
            raise IOHubClientError("checkHubInterval parameter for msecDelay method must be a >= 0 msec.")        
        
        if self.hub and checkHubInterval > 0:
            remainingMsec=targetEndTime-self.currentMsec()
            while remainingMsec >= 1.0:
                if remainingMsec < checkHubInterval:
                    time.sleep((remainingMsec-1.0)/1000.0)
                else:
                    time.sleep(checkHubInterval/1000.0)
                
                events=self.hub.getEvents()
                if events:
                    self.allEvents.extend(events)
                
                remainingMsec=targetEndTime-self.currentMsec()
            
            while targetEndTime-self.currentMsec()>0.0:
                pass
        else:
            time.sleep((msecDelay-1.0)/1000.0)
            while targetEndTime-self.currentMsec()>0.0:
                pass
                
        return self.currentMsec()-stime
    
    def getEvents(self,deviceLabel=None,asType='dict'):
        if self.hub:
            r=None
            if deviceLabel is None:
                events=self.hub.getEvents()
                if events is None:
                    r=self.allEvents    
                else:
                    self.allEvents.extend(events)
                    r=self.allEvents
                self.allEvents=[]
            else:
                d=self.hub.deviceByLabel[deviceLabel]
                r=d.getEvents()
  
            if r:
                if asType == 'list':
                    return r
                else:
                    conversionMethod=None
                    if asType == 'dict':
                        conversionMethod=self.eventListToDict
                    elif asType == 'object':
                        conversionMethod=self.eventListToObject
                    
                    if conversionMethod:                    
                        events=[]
                        for el in r:
                            events.append(conversionMethod(el))
                        return events
                    
                    return r
                
    def clearEvents(self,deviceLabel=None):
        if self.hub:
            if deviceLabel is None:
                self.hub.sendToHub(('RPC','clearEventBuffer'))
                self.allEvents=[]
            else:
                d=self.hub.deviceByLabel[deviceLabel]
                d.clearEvents()
    
    @staticmethod
    def eventListToObject(eventValueList):
        eclass=EventConstants.eventTypeCodeToClass[eventValueList[3]]
        combo = zip(eclass.attributeNames,eventValueList)
        kwargs = dict(combo)
        return eclass(**kwargs)

    @staticmethod
    def eventListToDict(eventValueList):
        eclass=EventConstants.eventTypeCodeToClass[eventValueList[3]]
        combo = zip(eclass.attributeNames,eventValueList)
        return dict(combo)
         
    def run(self,*args,**kwargs):
        pass
    
    def close(self):
        # terminate the ioServer
        if self.hub:
            self.hub.shutDownServer()
            
        # terminate psychopy
        core.quit()
        
    def displayExperimentSettingsDialog(self):
        experimentDlg=psychopy.gui.DlgFromDict(self.experimentConfig, 'Experiment Launcher', self._experimentConfigKeys, self._experimentConfigKeys, {})
        if experimentDlg.OK:
            return False
        return True

    def displayExperimentSessionSettingsDialog(self):
        allSessionDialogVariables = dict(self.experimentSessionDefaults, **self.sessionUserVariables)
        sessionVariableOrder=self.configuration['session_variable_order']
        if 'user_variables' in allSessionDialogVariables:
            del allSessionDialogVariables['user_variables']
        
        sessionDlg=psychopy.gui.DlgFromDict(allSessionDialogVariables, 'Experiment Session Settings', [], sessionVariableOrder)
        
        if sessionDlg.OK:
            for key,value in allSessionDialogVariables.iteritems():
                if key in self.experimentSessionDefaults:
                    self.experimentSessionDefaults[key]=str(value)
                elif  key in self.sessionUserVariables:
                    self.sessionUserVariables[key]=str(value)   
            return False
        return True

    @staticmethod    
    def printExceptionDetails():
        '''
        No idea if all of this is needed, infact I know it is not. But for now why not. 
        Taken straight from the python manual on Exceptions.
        '''
        import sys, traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print "*** print_tb:"
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        print "*** print_exception:"
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=2, file=sys.stdout)
        print "*** print_exc:"
        traceback.print_exc()
        print "*** format_exc, first and last line:"
        formatted_lines = traceback.format_exc().splitlines()
        print formatted_lines[0]
        print formatted_lines[-1]
        print "*** format_exception:"
        print repr(traceback.format_exception(exc_type, exc_value,
                                              exc_traceback))
        print "*** extract_tb:"
        print repr(traceback.extract_tb(exc_traceback))
        print "*** format_tb:"
        print repr(traceback.format_tb(exc_traceback))
        print "*** tb_lineno:", exc_traceback.tb_lineno
        
class SimpleIOHubRuntimeError(Exception):
    """Base class for exceptions raised by SimpleIOHubRuntime class."""
    pass        
