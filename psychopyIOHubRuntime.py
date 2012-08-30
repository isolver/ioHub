from __future__ import division
import psychopy
from psychopy import logging, core, visual
import os,gc,psutil
from collections import deque
import time
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print "*** Using Python based YAML Parsing"
    from yaml import Loader, Dumper

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
            global typeCodeToClass
            import ioHub
            import ioHub.devices
            ioHub.devices.buildTypeCodeToClassDict()
            from ioHub.devices import typeCodeToClass
            
            from ioHub.client import ioHubClient
            
            # start up ioHub using subprocess module so you can have it run for duration of experiment only
            import subprocess

            ioHubConfigFileName=self.configuration['ioHub']['config']
            configAbsPath=os.path.join(self.configFilePath,ioHubConfigFileName)
            subprocessArgLIst=["%s"%self.configuration['runtime']['python_exe'], '%s\ioHub\server.py'%self.configuration['ioHub']['ioHub_path'],"%s"%configAbsPath]
            self.hub_pid = subprocess.Popen(subprocessArgLIst).pid
            print "started subprocess %d"%self.hub_pid
           
            # for now just giving hub 5 seconds to spin up; 
            # this is logged as a bug; ioHub to notify client
            # when ready to accept requests.            
            import time
            time.sleep(5)
                        
            ioHubConfig=load(file(configAbsPath,'r'), Loader=Loader)
            self.ioHubConfig=ioHubConfig
            
            self.hub=ioHubClient(ioHubConfig['ipcCoder'])
 
            # Is ioHub configured to be run in experiment?
            if self.hub: 
                # check if a connection can be made to the hub
                r=self.hub.getDeviceList()
                if r is None:
                    print " ** ioHub Server could not be started. Is it running, check for already running python instances in the task manager? **"
                    sys.exit(1)
                else:
                    dlist=r[0][2]
                    self.hub.createDeviceList(dlist)                   
                        
                    
                self.allEvents=deque(maxlen=self.configuration['eventBufferLength'])
        else:
            print "** ioHub is Disabled (or should be) **"
            
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
    
    @staticmethod    
    def printExceptionDetails():
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
                
                events=self.hub.getEvents()[0][1]
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
    
    def getEvents(self,deviceLabel=None,asType='list'):
        if self.hub:
            r=None
            if deviceLabel is None:
                events=self.hub.getEvents()[0][1]
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
        eclass=typeCodeToClass[eventValueList[3]]
        combo = zip(eclass.attributeNames,eventValueList)
        kwargs = dict(combo)
        return eclass(**kwargs)

    @staticmethod
    def eventListToDict(eventValueList):
        eclass=typeCodeToClass[eventValueList[3]]
        combo = zip(eclass.attributeNames,eventValueList)
        return dict(combo)
         
    def run(self,*args,**kwargs):
        pass

class IOHubClientError(Exception):
    """Base class for exceptions raised by SimpleIOHubRuntime class."""
    pass        