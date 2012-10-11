"""
ioHub
.. file: ioHub/psychopyIOHubRuntime.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

from __future__ import division
import psychopy
from psychopy import  core, gui, visual
import pythoncom
import os
from collections import deque
import time
import ioHub
from ioHub.devices import Computer,EventConstants, DeviceEvent

try:
    from yaml import load
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print "*** Using Python based YAML Parsing"
    from yaml import Loader, Dumper


class SimpleIOHubRuntime(object):
    """
    SimpleIOHubRuntime is a utility class that is used to 'bind' the ioHub framework to the PsychoPy API in an easy to use way,
    hiding many of the internal complexities of the implementation and making it as simple to use within a PsychoPy script
    as possible. That is the *intent* anyway.

    The SimpleIOHubRuntime class is intended to be extended in a user script, with the .run() method being implemented with
    the actual contents of the main body of the experiment. As an example, a run.py file could be created and contain
    the following code as a minimal implementation of using the SimpleIOHubRuntime to combine psychopy and ioHub functionality
    to display a window and wait for a key press to close the window and terminate the experiment. The source file and .yaml
    config files for this simple example can be found in ioHub/examples/simple :

import ioHub
from ioHub.psychopyIOHubRuntime import SimpleIOHubRuntime

class ExperimentRuntime(SimpleIOHubRuntime):
    def __init__(self,configFileDirectory, configFile):
        SimpleIOHubRuntime.__init__(self,configFileDirectory,configFile)

    def run(self,*args,**kwargs):
        ###
        #
        # Your experiment logic start here. You can do anything you would in a standard psychopy script.
        # You can even import a psychopy script and just call a function in it to run it if you wanted
        #

        #
        # See ioHub/examples/simple/run.py for an example implementation of the contents for a run method.
        #

        print "Starting Experiment Script..."

        # ....

        print "Completed Experiment Script..."

        ### End run method / end of experiment logic

def main(configurationDirectory):
    #
    # Main function simply checks for a command line arg and assumes it is the name of the experiment config file if
    # it was provided, otherwise it uses "experiment_config.yaml" by default
    # An instance of ExperimentRuntime is created and the start method is called for it, which calls the .run method you
    # implemented for your experiment.

    import sys
    if len(sys.argv)>1:
        configFile=unicode(sys.argv[1])
        runtime=ExperimentRuntime(configurationDirectory, configFile)
    else:
        runtime=ExperimentRuntime(configurationDirectory, "experiment_config.yaml")

    runtime.start()

if __name__ == "__main__":
    # This code only gets called when the python file is executed, not if it is loaded as a module by another python file
    #
    # The module_directory function determines what the current directory is of the function that is passed to it. It is
    # more reliable when running scripts via IDEs etc in terms of reporting the true file location.
    configurationDirectory=ioHub.module_directory(main)

    # run the main function, which starts the experiment runtime
    main(configurationDirectory)


################################## End of Stub Example SimpleIOHubRuntime implementation ###############################

Along with a python file that extends the SimpleIOHubRuntime class, normally you will also need to provide an experiment_config.yaml and ioHub_config.yaml file.
These files are read by the SimpleIOHubRuntime and the ioHub system and make it much easier for the ioHub and associated devices to be
configurated than if you needed to do it within a python script. So while at first these files may seem like extra overhead, we hope that they are found to
actually save time and work in the end. Comments and feedback on this would be highly apprieciated.

The iohub/examples/simple example contains the python file and two .yaml config files needed to run the example.  To run the example simply open
a command prompt at the ioHub/examples/simple folder and type:

    python.exe run.py

    """
    def __init__(self, configFilePath, configFile):
        """
        Initialize the SimpleIOHubRuntime Object, loading the experiment configuration file, initializing and launching
        the ioHub server process, and creating the client side device interface to the ioHub devices that have been created.

        Currently the ioHub timer uses a ctypes implementation of direct access to the Windows QPC functions in win32
        (so no python interpreter start time offset is applied between processes) and timeit.default_timer is used for
        all other platforms at this time. The advantage of not having a first read offset applied per python interpreter is that
        it means the both the psychopy process and the ioHub process are using the exact same timebase without a different
        offset that is hard to exactly determine due to the variablility in IPC request-reponses. By the two processes using
        the exact same time space, including offset, getTime() for the the ioHub client in psychopy == the current time of the ioHub server
        process, greatly simplifying some aspects of synconization. This only holds as long as both processes are running
        on the same PC of course.

        Note on timeit.default_timer: As of 2.7, timeit.default_timer correctly selects the best clock based on OS for high
        precision timing. < 2.7, you need to check the OS version yourself and select; or use the psychopy clocks since
        it does the work for you. ;)

        Args:
            configFilePath (str): The absolute path to the experiment configuration .yaml file, which is automatically assigned
            to the path the experiment script is running from by default.
            configFile (str): The name of the experiment configuration .yaml file, which has a default value of 'experiment_config.yaml'

            Return: None
        """

        self.currentTime=Computer.currentSec

        self.configFilePath=configFilePath
        self.configFileName=configFile

        sysInfoFile=open(os.path.join(self.configFilePath,'systemInfo.txt'),'w')
        from util.systemInfo import printSystemInfo
        printSystemInfo(sysInfoFile)
        sysInfoFile.close()

        self.fullPath= os.path.join(self.configFilePath,self.configFileName)

        # load the experiment config settings from the experiment_config.yaml file.
        # The file must be in the same directory as the experiment script.
        self.configuration=load(file(self.fullPath,u'r'), Loader=Loader)

        self.experimentConfig=dict()
        self._experimentConfigKeys=['title','code','version','description','total_sessions_to_run']
        for key in self._experimentConfigKeys:
            if key in self.configuration:
                self.experimentConfig[key]=self.configuration[key]
 
        self.experimentSessionDefaults=self.configuration['session_defaults']
        self.sessionUserVariables=self.experimentSessionDefaults['user_variables']
        del self.experimentSessionDefaults['user_variables']
        
        # self.hub will hold the reference to the ioHubConnection object, used to access the ioHubServer
        # process and devices.
        self.hub=None
        # holds events collected from the ioHub during periods like msecWait()
        self.allEvents=None
        
        # indicates if the experiment is in high priority mode or not. Do not set directly.
        # See enableHighPriority() and disableHighPriority()
        self._inHighPriorityMode=False

        self.computer=ioHub.devices.Computer

        # initialize the experiment object based on the configuration settings.
        self._initalizeConfiguration()

        
    def _initalizeConfiguration(self):
        """
        Based on the configuration data in the experiment_config.yaml and iohub_config.yaml,
        configure the experiment environment and ioHub process environments. This mehtod is called by the class init
        and should not be called directly.
        """
        if 'ioHub' in self.configuration and self.configuration['ioHub']['enable'] is True:
            from ioHub.client import ioHubConnection

            ioHubConfigFileName=unicode(self.configuration['ioHub']['config'])
            ioHubConfigAbsPath=os.path.join(self.configFilePath,unicode(ioHubConfigFileName))
            self.ioHubConfig=load(file(ioHubConfigAbsPath,u'r'), Loader=Loader)


            self.hub=ioHubConnection(self.ioHubConfig,ioHubConfigAbsPath)
 
            self.hub._startServer()
            #self.hub._calculateClientServerTimeOffset(500)
            # Is ioHub configured to be run in experiment?
            if self.hub:
            
                # display a read only dialog verifying the experiment parameters 
                # (based on the experiment .yaml file) to be run. User can hit OK to continue,
                # or Cancel to end the experiment session if the wrong experiment was started.
                exitExperiment=self._displayExperimentSettingsDialog()
                if exitExperiment:
                    print "User Cancelled Experiment Launch."
                    self._close()
                    import sys
                    sys.exit(1)
            
            
                # send experiment info and set exp. id
                self.hub._sendExperimentInfo(self.experimentConfig)
                
                # display editable session variable dialog displaying the ioHub required session variables
                # and any user defined session variables (as specified in the experiment config .yaml file)
                # User can enter correct values and hit OK to continue, or Cancel to end the experiment session.
                exitExperiment=self._displayExperimentSessionSettingsDialog()
                if exitExperiment:
                    print "User Cancelled Experiment Launch."
                    self._close()
                    import sys
                    sys.exit(1)
                
                # send session data to ioHub and get session ID (self.hub.sessionID)
                tempdict= self.experimentSessionDefaults
                tempdict['user_variables']=self.sessionUserVariables
                self.hub._sendSessionInfo(tempdict)

                # create a local 'thin' representation of the registered ioHub devices,
                # allowing such things as device level event access (if supported) 
                # and transparent IPC calls of public device methods and return value access.
                # Devices are available as hub.devices.[device_name] , where device_name
                # is the name given to the device in the ioHub .yaml config file to be access;
                # i.e. hub.devices.ExperimentPCkeyboard would access the experiment PC keyboard
                # device if the default name was being used.
                self.hub._createDeviceList()
                        
                # A circular buffer used to hold events retrieved from self.getEvents() during 
                # self.delay() calls. self.getEvents() appends any events in the allEvents
                # buffer to the result of the hub.getEvents() call that is made.                
                self.allEvents=deque(maxlen=self.configuration['event_buffer_length'])
        else:
            print "** ioHub is Disabled (or should be). Why are you using this utility class then? ;) **"

        # set process affinities based on config file settings
        cpus=range(Computer.cpuCount)
        experiment_process_affinity=cpus
        other_process_affinity=cpus
        iohub_process_affinity=cpus

        if 'process_affinity' in self.configuration:
            experiment_process_affinity=self.configuration['process_affinity']
            if len(experiment_process_affinity) == 0:
                experiment_process_affinity=cpus
        if 'remaining_processes_affinity' in self.configuration:
            other_process_affinity=self.configuration['remaining_processes_affinity']
            if len(other_process_affinity) == 0:
                other_process_affinity=cpus
        if self.hub and 'process_affinity' in self.configuration['ioHub']:
            iohub_process_affinity=self.configuration['ioHub']['process_affinity']
            if len(iohub_process_affinity) == 0:
                iohub_process_affinity=cpus

        if len(experiment_process_affinity) < len(cpus) or len(iohub_process_affinity) < len(cpus):
            self.setProcessAffinities(experiment_process_affinity,iohub_process_affinity)

        if len(other_process_affinity) < len(cpus):
            ignore=[Computer.currentProcessID,]
            if self.hub:
                ignore.append(self.hub.server_pid)
            Computer.setAllOtherProcessesAffinity(other_process_affinity,ignore)

        return self.hub

    def enableHighPriority(self,disable_gc=True,ioHubServerToo=False):
        """
        Sets the priority of the experiment process to high priority
        and optionally (default is true) disable the python GC. This is very
        useful for the duration of a trial, for example, where you enable at
        start of trial and disable at end of trial. Improves Windows
        sloppiness greatly in general.

        Args:
            disable_gc(bool): True = Turn of the Python Garbage Collector. False = Leave the Garbage Collector running.
                              Default: True
            ioHubServerToo(bool): True = Also set the ioHub Process to High Priority. False = Do not change the ioHub Process Priority.
                              Default: False

        Return: None
        """
        self.computer.enableHighPriority(disable_gc)
        if self.hub and ioHubServerToo is True:
            self.hub.sendToHubServer(('RPC','enableHighPriority'))

    def disableHighPriority(self,ioHubServerToo=False):
        """
        Sets the priority of the Experiment Process back to normal priority
        and enables the python GC. In general you would call enableHighPriority() at
        start of trial and call disableHighPriority() at end of trial.

        Args:
            ioHubServerToo(bool): True = Also set the ioHub Process to High Priority.
                                  False = Do not change the ioHub Process Priority.
                                  Default: False

        Return: None
        """
        self.computer.disableHighPriority()
        if self.hub and ioHubServerToo is True:
            self.hub.sendToHubServer(('RPC','disableHighPriority'))

    def getSystemProcessorCount(self):
        """
        Returns the number of parallel processes the computer can carry out at once.
        I say 'parallel processes' because this number includes cpu count, cores per cpu,
        and hyper-threads per cpu (which is at most 2 I believe). So perhaps it would be better to
        call this method *getSystemProcessingUnitCount*. For example, if you have an i5 dual core
        system with hyper-threading enabled, this method will report 2x2=4 for the count. So
        *getSystemProcessorCount* really = cpu_count * cores_per_cpu * hypertheads_per_core

        If you have a dual CPU, quad core hyper-threaded system (first, can I be your friend)
        and second, this method would report 2 x 4 x 2 = 16 for the count.

        It is true that all of these levels of 'parallel processing' can not perform processing
        in parallel at all times, particularly hyper-threads. Even multiple cores and cpu's can
        blocked each other if a shared i/o resource is being used by one,
        blocking the other. (Very simply put I am sure) ;)

        Args: None

        Return: (int) The number of processing units the current computer has.

        """
        return self.computer.cpuCount

    def getProcessAffinities(self):
        """
        Returns the experiment Process Affinity list, ioHub Process Affinity list. Each as a list of
        'processor' id's (from 0 to getSystemProcessorCount()-1) that the relevant process is able to
        run on.

        For example, on a 2 core CPU with hyper-threading, the possible 'processor' list would be
        [0,1,2,3], and by default both the experiment and ioHub processes can run on any of these
        'processors', so:


            psychoCPUs,ioHubCPUS=self.getProcessAffinities()
            print psychoCPUs,ioHubCPUS

            >> [0,1,2,3], [0,1,2,3]


        If setProcessAffinities was used to set the experiment process to core 1 (index 0 and 1)
        and the ioHub server process to core 2 (index 2 and 3), with each using both hyper threads
        of the given core, the set call would look like:


            self.setProcessAffinities([0,1],[2,3])

            psychoCPUs,ioHubCPUS=self.getProcessAffinities()
            print psychoCPUs,ioHubCPUS

            >> [0,1], [2,3]


        If the ioHub is not being used (i.e self.hub == None), then only the experiment
        process affinity list will be returned and None will be returned for the
        ioHub process affinity:

            psychoCPUs,ioHubCPUS=self.getProcessAffinities()
            print psychoCPUs,ioHubCPUS

            >> [0,1,2,3], None

        But in this case, why are you using this utility class? ;)

        Args: None
        Return (tuple,tuple): the current experiment Process Affinity list, ioHub Process Affinity list
        """
        if self.hub is None:
            return self.computer.getCurrentProcessAffinity(),None
        return self.computer.getCurrentProcessAffinity(),self.hub._psutil_server_process.get_cpu_affinity()

    def setProcessAffinities(self,experimentProcessorList, ioHubProcessorList=None):
        """
        Sets the experimentProcessAffinity , ioHubProcessAffinity; each as a list of 'processor' id's
        (from 0 to getSystemProcessorCount()-1) that the relevant process is able to run on.

        For example, on a 2 core CPU with hyper-threading, the possible 'processor' list would be [0,1,2,3],
        and by default both the experiment and ioHub server processes can run on any of these 'processors',
        so to have both processes have all processors available (which is the default), you would call:

            self.setProcessAffinities([0,1,2,3], [0,1,2,3])

            # check the process affinities
            psychoCPUs,ioHubCPUS=self.getProcessAffinities()
            print psychoCPUs,ioHubCPUS

            >> [0,1,2,3], [0,1,2,3]

        based on the above CPU example.

        If setProcessAffinities was used to set the experiment process to core 1 (index 0,1) and the ioHub server
        process to core 2 (index 2,3), with each using both hyper threads of the given core,
        the set call would look like:

            self.setProcessAffinities([0,1],[2,3])

            # check the process affinities
            psychoCPUs,ioHubCPUS=self.getProcessAffinities()
            print psychoCPUs,ioHubCPUS

            >> [0,1], [2,3]

        Args:
            experimentProcessorList(tuple): set the experiment process affinity based on processing unit indexes
            ioHubProcessorList(tuple): set the ioHub process affinity based on processing unit indexes. Default for ioHubProcessorList
                                       is None, which means do not set the ioHub process affinity.

        Return: None
        """
        self.computer.setCurrentProcessAffinity(experimentProcessorList)
        if self.hub and ioHubProcessorList:
            self.hub._psutil_server_process.set_cpu_affinity(ioHubProcessorList)

    def autoAssignAffinities(self):
        """
        Auto sets the experiment process and ioHub process processor affinities based on some
        very simple logic.

        It is not known at this time if the implementation of this method makes any sense in terms of
        actually improving performance. Field tests and feedback will need to occur, based on which
        the algorithm can be improved.

        Currently, if the system is detected to have 1 processing unit, or greater than 8 processing units,
        nothing is done by the method.

        For a system that has two processing units, the PsychoPy Process is assigned to index 0,
        ioHub Process assigned to 1.

        For a system that has four processing units, the Experiment Process is assigned to index's 0,1
        and the ioHub Process assigned to 2,3.

        For a system that has eight processing units, the PsychoPy Process is assigned to index 2,3
        ioHub Server assigned to 4,5. All other processes running on the OS are attempted to be
        assigned to indexes 0,1,6,7.

        Args: None
        Return: None
        """
        cpu_count=self.computer.cpuCount
        print "System processor count:", cpu_count
        if cpu_count == 2 and self.hub:
            print 'Assigning experiment process to CPU 0, ioHubServer process to CPU 1'
            self.setProcessAffinities([0,],[1,])
        elif cpu_count == 4 and self.hub:
            print 'Assigning experiment process to CPU 0,1, ioHubServer process to CPU 2,3'
            self.setProcessAffinities([0,1],[2,3])
        elif cpu_count == 8 and self.hub:
            print 'Assigning experiment process to CPU 2,3, ioHubServer process to CPU 4,5, attempting to assign all others to 0,1,6,7'
            self.setProcessAffinities([2,3],[4,5])
            self.computer.setAllOtherProcessesAffinity([0,1,6,7],[self.computer.currentProcessID,self.hub.server_pid])
        else:
            print "autoAssignAffinities does not support %d processors."%(cpu_count,)

    def getTime(self):
        """
        Returns the current sec.msec-msec time of the system. On Windows this is implemented by directly
        calling the Windows QPC functions using ctypes (TODO: move to clib for max performance).
        This is done so that no offset is applied to the timebase based on when the first call to the
        python time function was called, which will differed between PsychoPy and ioHub Processes
        since they do not start at exactly the same time.
        By having a 0 offset time-base, both interpreters have a totally common / shared time-base to use.
        This means that either process knows the current time of the other process,
        since they are the same. ;)

        For other OS's, right now the timeit.base_timer function is used, which as of python 2.7
        correctly selects the best high resolution clock for the OS the interpreter is running on.

        Args: None
        Returns (float/double): sec.msec-usec time
        """
        return self.currentTime()

    def currentSec(self):
        """
        Returns the current sec.msec-msec time of the system. On Windows this is implemented by directly
        calling the Windows QPC functions using ctypes (TODO: move to clib for max performance).
        This is done so that no offset is applied to the timebase based on when the first call to the
        python time function was called, which will differed between PsychoPy and ioHub Processes
        since they do not start at exactly the same time.
        By having a 0 offset time-base, both interpreters have a totally common / shared time-base to use.
        This means that either process knows the current time of the other process,
        since they are the same. ;)

        For other OS's, right now the timeit.base_timer function is used, which as of python 2.7
        correctly selects the best high resolution clock for the OS the interpreter is running on.

        Args: None
        Returns (float/double): sec.msec-usec time
        """
        return self.currentTime()

    def delay(self,delay,checkHubInterval=0.01):
        """
        Pause the experiment execution for msec.usec interval, while checking the ioHub for
        any new events and retrieving them every 'checkHubInterval' msec during the delay. Any events
        that are gathered during the delay period will be handed to the experiment the next time
        self.getEvents() is called, unless self.clearEvents() beforehand.

        It is important to allow the PyschoPy Process to periodically either call self.getEvents() events
        during long delaying in program execution, as if a self.getEvents() request is made that
        results in too many events being sent in the reply to fit in the maximum UDP packet size of the
        system, an error will occur and the events will be lost.

        Another option is to call self.clearEvents() after any long delays between calls to
        self.getEvents() or self.clearEvents() if you do not need any events received by the
        ioHub prior to the call. This will clear the ioHub event buffer so the next call to
        self.getEvents() will not overflow.

        (TODO: Support multi-packet UDP messages, already in bug tracker, so that this issue
        will never occur.)

        Args:
            delay (float/double): the sec.msec_usec period that the PsychoPy Process should wait
                              before returning from the function call.
            checkHubInterval (float/double): the sec.msec_usec interval after which any ioHub
                              events will be retrieved (by calling self.getEvents) and stored
                              in a local buffer. This is repeated every checkHubInterval sec.msec_usec until
                              the method completes. Default is every 0.01 sec ( 10.0 msec ).

        Return(float/double): actual duration of delay in sec.msec_usec format.
        """
        stime=self.currentTime()
        targetEndTime=stime+delay

        if checkHubInterval < 0:
            raise SimpleIOHubRuntimeError("checkHubInterval parameter for delay method must be a >= 0 sec.msec.")
        
        if self.hub and checkHubInterval > 0:
            remainingSec=targetEndTime-self.currentTime()
            while remainingSec >= 0.001:
                if remainingSec < checkHubInterval+0.001:
                    time.sleep(remainingSec)
                else:
                    time.sleep(checkHubInterval)
                
                events=self.hub.getEvents()
                if events:
                    self.allEvents.extend(events)
                
                remainingSec=targetEndTime-self.currentTime()
            
            while (targetEndTime-self.currentTime())>0.0:
                pass
        else:
            time.sleep(delay-0.001)
            while (targetEndTime-self.currentTime())>0.0:
                pass
                
        return self.currentTime()-stime

    def getEvents(self,deviceLabel=None,asType='dict'):
        """
        Retrieve any events that have been collected by the ioHub server from monitored devices
        since the last call to getEvents() or since the last call to clearEvents().

        By default all events for all monitored devices are returned, with each event being
        represented as a dictionary of event attributes. When events are retrieved from an event buffer,
        they are removed from the buffer as well.

        Args:
            deviceLabel (str): optional : if specified, indicates to only retrieve events for
                         the device with the associated label name. None (default) returns
                         all device events.
            asType (str): optional : indicated how events should be represented when they are returned.
                         Default: 'dict'
                Events are sent from the ioHub Process as lists of ordered attributes. This is the most
                efficient for data transmission, but not for readability.

                If you do want events to be kept in list form, set asType = 'list'.

                Setting asType = 'dict' (the default) converts the events lists to event dictionaries.
                This process is quite fast so the small conversion time is usually worth it given the
                huge benefit in usability within your program.

                Setting asType = 'object' converts the events to their ioHub DeviceEvent class form.
                This can take a bit of time if the event list is long and currently there is not much
                benefit in doing so vs. treating events as dictionaries. This may change in
                the future. For now, it is suggested that the default, asType='dict' setting be kept.

        Return (tuple): returns a list of event objects, where the object type is defined by the
                'asType' parameter.
        """
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
                        conversionMethod=self._eventListToDict
                    elif asType == 'object':
                        conversionMethod=self._eventListToObject
                    
                    if conversionMethod:                    
                        events=[]
                        for el in r:
                            events.append(conversionMethod(el))
                        return events
                    
                    return r

    def clearEvents(self,deviceLabel=None):
        """
        Clears all events from the global event buffer, or if deviceLabel is not None,
        clears the events only from a specific device event buffer.
        When the global event buffer is cleared, device level event buffers are not effected.

        Args:
            devicelabel (str): name of the device that should have it's event buffer cleared.
                         If None (the default), the device wide event buffer is cleared
                         and device level event buffers are not changed.
        Return: None
        """
        if self.hub:
            if deviceLabel is None:
                self.hub.sendToHubServer(('RPC','clearEventBuffer'))
                self.allEvents=[]
            else:
                d=self.hub.deviceByLabel[deviceLabel]
                d.clearEvents()

    @staticmethod
    def pumpLocalMessageQueue():
        """
        Pumps the Experiment Process Windows Message Queue so the PsychoPy Window does not appear to be 'dead' to the
        OS. If you are not flipping regularly (say because you do not need to and do not want to block frequently,
        you can call this, which will not block waiting for messages, but only pump out what is in the que already.
        On an i7 desktop, this call method taking between 10 and 90 usec.
        """
        if pythoncom.PumpWaitingMessages() == 1:
            raise KeyboardInterrupt()

    @staticmethod
    def _eventListToObject(eventValueList):
        """
        Convert an ioHub event that is current represented as an orderded list of values, and return the correct
        ioHub.devices.DeviceEvent subclass for the given event type.
        """
        eclass=EventConstants.EVENT_CLASSES[eventValueList[3]]
        combo = zip(eclass.CLASS_ATTRIBUTE_NAMES,eventValueList)
        kwargs = dict(combo)
        return eclass(**kwargs)

    @staticmethod
    def _eventListToDict(eventValueList):
        """
        Convert an ioHub event that is current represented as an ordered list of values, and return the event as a
        dictionary of attribute name, attribute values for the object.
        """
        try:
            eclass=EventConstants.EVENT_CLASSES[eventValueList[DeviceEvent.EVENT_TYPE_ID_INDEX]]
            combo = zip(eclass.CLASS_ATTRIBUTE_NAMES,eventValueList)
            return dict(combo)
        except:
            print '---------------'
            print "ERROR: eventValueList: "+eventValueList
            print '---------------'
    def run(self,*args,**kwargs):
        """
        The run method is what gets calls when the SimpleIOHubRuntime.start method is called. The run method is intended
        to be over written by your extension class and should include your experiment / program logic. By default it does nothing.

        Args:
            *args: list of unnamed input variables passed to method
            **kwargs: dictionary of named variables passed to method. Variable names are the dict keys.

        Return: None
        """
        pass

    def start(self):
        """
        The start method should be called by the main portion of your experiment script.
        This method simply wraps a call to self.run() in an exception handler that tries to
        ensure any error that occurs is printed out in detail, and that the ioHub server process
        is terminates even in the case of an exception that may not have been handled explicitly
        in your script.

        Args: None
        Return: None
        """
        try:
            self.run()
        except ioHub.ioHubError, ioe:
            print 'ioHub.ioHubError:',str(ioe)
            self.printExceptionDetails()
        except:
            self.printExceptionDetails()
        finally:
            # _close ioHub, shut down ioHub process, clean-up.....
            self._close()


    def _close(self):
        """
        Close the experiment runtime and the ioHub server process.
        """
        # terminate the ioServer
        if self.hub:
            self.hub._shutDownServer()
        # terminate psychopy
        core.quit()
        
    def _displayExperimentSettingsDialog(self):
        """
        Display a read-only dialog showing the experiment setting retrieved from the configuration file. This gives the
        experiment operator a chance to ensure the correct configuration file was loaded for the script being run. If OK
        is selected in the dialog, the experiment logic continues, otherwise the experiment session is terminated.
        """
        experimentDlg=psychopy.gui.DlgFromDict(self.experimentConfig, 'Experiment Launcher', self._experimentConfigKeys, self._experimentConfigKeys, {})
        if experimentDlg.OK:
            return False
        return True

    def _displayExperimentSessionSettingsDialog(self):
        """
        Display an editable dialog showing the experiment session setting retrieved from the configuration file.
        This includes the few mandatory ioHub experiment session attributes, as well as any user defined experiment session
        attributes that have been defined in the experiment configuration file. If OK is selected in the dialog,
        the experiment logic continues, otherwise the experiment session is terminated.
        """
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
        """
        Prints out stack trace info for the last exception in multiple ways.
        No idea if all of this is needed, in fact I know it is not. But for now why not.
        Taken straight from the python 2.7.3 manual on Exceptions.
        """
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
