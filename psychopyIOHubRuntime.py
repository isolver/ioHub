"""
ioHub
.. file: ioHub/psychopyIOHubRuntime.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

from __future__ import division
from __builtin__ import unicode, file, repr, dict, object, staticmethod, zip, str
from exceptions import Exception, ImportError
import psychopy
#noinspection PyUnresolvedReferences
from psychopy import  core, gui, visual
import os,gc,psutil
from collections import deque
import time
from yaml import load
import ioHub
from ioHub.devices import computer,highPrecisionTimer,EventConstants

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print "*** Using Python based YAML Parsing"
    from yaml import Loader, Dumper


class SimpleIOHubRuntime(object):
    """
    SimpleIOHubRuntime is a utility class that is used to 'bind' the ioHub framework to psychopy in an easy to use way,
    hiding many of the internal complexities of the implementation and making it as easy to use within a psychopy script
    as possible.

    The SimpleIOHubRuntime class is intended to be extended in a user script, with the .run() method being implemented with
    the actual contents of the main body of the experiment. As an example, a simpleExperiment.py file could be created and contain
    the following code as a minimal implementation of using the SimpleIOHubRuntime to combine psychopy and ioHub functionality
    to display a window and wait for a key press to _close the window and terminate the experminent. The source file and .yaml
    config files for this simple example can be found in ioHub/examples/simple :

import ioHub
from ioHub.psychopyIOHubRuntime import SimpleIOHubRuntime, visual

class ExperimentRuntime(SimpleIOHubRuntime):
    def __init__(self,configFileDirectory, configFile):
        SimpleIOHubRuntime.__init__(self,configFileDirectory,configFile)

    def run(self,*args,**kwargs):
        ###
        #
        # Your experiment logic start here. You can do anything you would in a standard psychopy script.
        # You can even import a psychopy script and just call a fucntion in it to run it if you wanted
        #

        #
        # See ioHub/examples/simple/simpleTest.py for an example implementation of the contents for a run method.
        #

        ### End run method / end of experiment logic

##################################################################

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
    #
    # Using if __name__ == "__main__": ensures that this logic will only be run if the file is run from a commond prompt
    # or from executed from an interactive shell. If the file is imported as a module the code will not run. i.e. the experiment will not run.
    #
    configurationDirectory=ioHub.module_directory(main)
    main(configurationDirectory)

################################## End of Stub Example SimpleIOHubRuntime implementation ###############################

Along with a python file that extends the SimpleIOHubRuntime class, normally you will also need to provide an experiment_config.yaml and ioHub_config.yaml file.
These files are read by the SimpleIOHubRuntime and the ioHub system and make it much easier for the ioHub and associated devices to be
configurated than if you needed to do it within a python script. So while at first these files may seem like extra overhead, we hope that they are found to
actually save time and work in the end. Comments and feedback on this would be highly apprieciated.

The iohub/examples/simple example contains the python file and two .yaml config files needed to run the example.  To run the example simply open
a command prompt at the ioHub/examples/simple folder and type:

    python.exe simpleTest.py

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

        self.currentTime=computer.currentSec

        self.configFilePath=configFilePath
        self.configFileName=configFile

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
        
        # self.hub will hold the reference to the ioHubClient object, used to access the ioHubServer
        # process and devices.
        self.hub=None
        # holds events collected from the ioHub during periods like msecWait()
        self.allEvents=None
        
        # indicates if the experiment is in high priority mode or not. Do not set directly.
        # See enableHighPriority() and disableHighPriority()
        self._inHighPriorityMode=False

        self.sysutil=ioHub.devices.computer

        # initialize the experiment object based on the configuration settings.
        self._initalizeConfiguration()

        
    def _initalizeConfiguration(self):
        """
        Based on the configuration data in the experiment_config.yaml and iohub_config.yaml,
        configure the experiment environment and ioHub process environments. This mehtod is called by the class init
        and should not be called directly.
        """
        if 'ioHub' in self.configuration and self.configuration['ioHub']['enable'] is True:
            from ioHub.client import ioHubClient

            ioHubConfigFileName=unicode(self.configuration['ioHub']['config'])
            ioHubConfigAbsPath=os.path.join(self.configFilePath,unicode(ioHubConfigFileName))
            self.ioHubConfig=load(file(ioHubConfigAbsPath,u'r'), Loader=Loader)


            self.hub=ioHubClient(self.ioHubConfig,ioHubConfigAbsPath)
 
            self.hub.startServer()
            self.hub._calculateClientServerTimeOffset(500)
            # Is ioHub configured to be run in experiment?
            if self.hub:
            
                # display a read only dialog verifying the experiment parameters 
                # (based on the experiment .yaml file) to be run. User can hit OK to continue,
                # or Cancel to end the experiment session if the wrong experiment was started.
                exitExperiment=self.displayExperimentSettingsDialog()
                if exitExperiment:
                    print "User Cancelled Experiment Launch."
                    self._close()
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
                    self._close()
                    import sys
                    sys.exit(1)
                
                # send session data to ioHub and get session ID (self.hub.sessionID)
                tempdict= self.experimentSessionDefaults
                tempdict['user_variables']=self.sessionUserVariables
                self.hub.sendSessionInfo(tempdict)
                
                # get the list of devices regigisted with the ioHub
                dlist=self.hub._getDeviceList()

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

        # set process affinities based on config file settings
        cpus=range(computer.cpuCount)
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
            ignore=[computer.currentProcessID,]
            if self.hub:
                ignore.append(self.hub.server_pid)
            computer.setAllOtherProcessesAffinity(other_process_affinity,ignore)

        return self.hub

    def enableHighPriority(self,disable_gc=True,ioHubServerToo=False):
        """
        sets the priority of the experiment process to high prority
        and optionally (default is true) disable the python GC. This is very
        useful for the duration of a trial, for example, where you enable at
        start of trial and disable at end of trial. Improves Windows
        sloppyness greatly in general.
        """
        self.sysutil.enableHighPriority(disable_gc)
        if self.hub and ioHubServerToo is True:
            self.hub.sendToHub(('RPC','enableHighPriority'))

    def disableHighPriority(self,ioHubServerToo=False):
        """
        Sets the priority of the experiment process back to normal prority
        and enables the python GC. This is very useful for the duration of a trial,
        for example, where you call enableHighPriority() at
        start of trial and call disableHighPriority() at end of trial.
        Improves Windows sloppyness greatly in general.
        """
        self.sysutil.disableHighPriority()
        if self.hub and ioHubServerToo is True:
            self.hub.sendToHub(('RPC','disableHighPriority'))

    def getSystemProcessorCount(self):
        """
        Returns the number of parallel processes the computer can carry out at once. I say 'parallel processes' because
        this number includes cpu count, cores per cpu, and hyperthreads per cpu (which is at most 2 I believe). So If you
        have an i5 dual core system with hyperthreading enabled, this method will report 2x2=4 for the count. So 'getSystemProcessorCount'
         really = cpu_count * cores_per_cpu * hypertheads_per_core

        If you have a dual CPU, quad core hyperthreaded system (first, can I be your friend) and second, this method
        would report 2 x 4 x 2 = 16 for the count.

        It is true that all of these levels of 'parallel processing' can not perform processing in parallel at all times,
        particularly hyperthreads, and multiple cores and even cpus can be blocked if a shared i/o resource is being used by one,
        blocking the other. (Very simply put I am sure) ;)
        """
        return self.sysutil.cpuCount

    def getProcessAffinities(self):
        """
        Returns the experimentProcessAffinity , ioHubProcessAffinity; each as a list of 'processor' id's (from 0 to getSystemProcessorCount()-1)
        that the relevent process is able to run on.

        For example, on a 2 core CPU with typerthreading, the possible 'processor' list would be [0,1,2,3], and by default both the
        experiment and ioHub server processes can run on any of these 'processors', so the method would return:

          [0,1,2,3], [0,1,2,3]

        If setProcessAffinities was used to set the experiment process to core 1 (index 0) and the ioHub server process to
        core 2 (index 1), with each using both hyper threads of the given core, the set call would look like:

          setProcessAffinities([0,1],[2,3])

        and and subsequent call to getProcessAffinities() would return:

          [0,1],[2,3]

        assuming the set was successful.

        If the ioHub is not being used, then only the experiment process affinity list will be returned and None will be
        returned for the ioHub process affinity: i.e.

          [0,1,2,3], None

        But in this case, why are you using this utility class? ;)
        """
        if self.hub is None:
            return self.sysutil.getCurrentProcessAffinity(),None
        return self.sysutil.getCurrentProcessAffinity(),self.hub._psutil_server_process.get_cpu_affinity()

    def setProcessAffinities(self,experimentProcessorList, ioHubProcessList=None):
        """
        Sets the experimentProcessAffinity , ioHubProcessAffinity; each as a list of 'processor' id's (from 0 to getSystemProcessorCount()-1)
        that the relevent process is able to run on.

        For example, on a 2 core CPU with typerthreading, the possible 'processor' list would be [0,1,2,3], and by default both the
        experiment and ioHub server processes can run on any of these 'processors', so to have both processes have all processors available
        (which is the default), you would call:

          setProcessAffinities([0,1,2,3], [0,1,2,3])

        based on the above CPU example.

        If setProcessAffinities was used to set the experiment process to core 1 (index 0) and the ioHub server process to
        core 2 (index 1), with each using both hyper threads of the given core, the set call would look like:

          setProcessAffinities([0,1],[2,3])
        """
        self.sysutil.setCurrentProcessAffinity(experimentProcessorList)
        if self.hub and ioHubProcessList:
            self.hub._psutil_server_process.set_cpu_affinity(ioHubProcessList)

    def autoAssignAffinities(self):
        """
        Auto sets the experiment process and ioHub server process processor affinities based on same very simple logic.
        It is not known at this time if the implementation of this method makes any sense in terms of actually improving
        performance. Field tests and feedaback will to occur, based on which the algorithm can be improved.

        Currently, if the system is detected to have 1 processing unit or greater than 8 processing units, nothing is done
        by the method.
        For a system that has two processing units, the experiment process is assigned to index 0, ioHub Server assigned to 1.
        For a system that has four processing units, the experiment process is assigned to index's 0,1, ioHub Server assigned to 1,2.
        For a system that has eight processing units, the experiment process is assigned to index 2,3 ioHub Server assigned to 4,5
        and all other processes are attempted to be assigned to indexes 0,1,6,7
        """
        cpu_count=self.sysutil.cpuCount
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
            self.sysutil.setAllOtherProcessesAffinity([0,1,6,7],[self.sysutil.currentProcessID,self.hub.server_pid])
        else:
            print "autoAssignAffinities does not support %d processors."%(cpu_count,)

    def currentSec(self):
        """
        Returns the current sec.msec time of the system. On Windows this is implemented by directly calling the Windows
        QPC fucntions in ctypes (TODO: move to clib for max performance). This is done so that no offset is allied to the
        timebase based on when the first call to the python time function was called, which will differer between processes
        since they do not start at exactly the same time. By having a 0 offset timebase, both interpreters have a totally
        common bimebase to share.

        For other OS's, right now the timeit.base_timer fucntion is used, which as of python 2.7 correctly selects the
        best high resolution clock for the OS the interpreter is running on.
        """
        return self.currentTime()

    def currentMsec(self):
        """
        Returns the current msec.usec time. This is simply calling currentTime()*1000.0 as a convience method.
        """
        return self.currentTime()*1000.0

    def currentUsec(self):
        """
        Returns the current usec.nsec time. This is simply calling currentTime()*1000000.0 as a convience method.
        """
        return self.currentTime()*1000000.0

    def msecDelay(self,msecDelay,checkHubInterval=10):
        """
        Pause the experiment execution for msec.usec interval, will checking the ioHub for any new events and rerieving
        them every 'checkHubInterval' msec during the delay. Any events that are gathered during the delay period will
        be handed to the experiment the next time self.getEvents() is called, unless self.clearEvents() before name.

        It is important to allow the ioHub server to be monitored for events during long delaying in program execution,
        as if a getEvents() request is made that contains too many events to fit in the maximum UDP patcket size of the
        system, an error will occur and the events will be lost. (TODO: Support multipacket UDP messages, already in bug tracker)
        """
        stime=self.currentMsec()
        targetEndTime=stime+msecDelay

        if checkHubInterval < 0:
            raise SimpleIOHubRuntimeError("checkHubInterval parameter for msecDelay method must be a >= 0 msec.")
        
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
        """
        Retrieve any events that have been collected by the ioHub server from monitored devices since the last call to getEvents
        or since the last call to clearEvents(). By defaults all events for all monitored devices are returned, with each
        event being represented as a dictionary of event attributes. When events are retieved from an event buffer,
        they are removed from the buffer as well.

        Args:
            deviceLabel (str): if specified, indicates to only retieve events for the device with the associated label name. None returns all device events.
            asType (str): indicated how events should be represnted when they are returned.
            Natively, events are sent from the ioHub server as lists or ordered attributes. This is the most efficient
            for data transmission, but not for readability. If you do want events to be kept in list form, set asType = 'list'.
            asType = 'dict' (the default) converts the events lists to event dictionaries. This process is quite fast so the
            conversion time is usually worth if given the huge benifit in usability within your program.
            asType = 'object' converts the events to their ioHub DeviceObject form. This can take a bit of time if the event list
            is long and currently there is not much benifit in doing so vs. treating events as dictionaries. This may change in
            the future. For now, it is suggested that the default, asType='dict' setting be used.
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
        Clears all events from the global event buffer, or if deviceLabel is not None, clears the events only from a specific device event buffer.
        When the global event buffer is cleared, device level event buffers are not effected.

        Args:
            devicelabel: name of the device which should have it's event buffer cleared. If None (the default), the device
            wide event buffer is cleared and device level event buffers are not changed.
        """
        if self.hub:
            if deviceLabel is None:
                self.hub.sendToHub(('RPC','clearEventBuffer'))
                self.allEvents=[]
            else:
                d=self.hub.deviceByLabel[deviceLabel]
                d.clearEvents()
    
    @staticmethod
    def _eventListToObject(eventValueList):
        """
        Convert an ioHub event that is current represented as an orderded list of values, and return the correct
        ioHub.devices.DeviceEvent subclass for the given event type.
        """
        eclass=EventConstants.EVENT_CLASSES[eventValueList[3]]
        combo = zip(eclass.attributeNames,eventValueList)
        kwargs = dict(combo)
        return eclass(**kwargs)

    @staticmethod
    def _eventListToDict(eventValueList):
        """
        Convert an ioHub event that is current represented as an orderded list of values, and return the event as a
        dictionary of attribute name, attribute values for the object.
        """
        eclass=EventConstants.EVENT_CLASSES[eventValueList[3]]
        combo = zip(eclass.attributeNames,eventValueList)
        return dict(combo)
         
    def run(self,*args,**kwargs):
        """
        The run method is what gets calls when the SimpleIOHubRuntime.start method is called. The run method is intended
        to be over written by your extension class and shound include your experiment / program logic. By default it does nothing.
        """
        pass

    def start(self):
        """
        The start method should be called by the main prtion of your experiment script. This method simply wraps a call
        to the run method in an exception handler that tries to ensure any error that occurs is printed out in detail,
        and that the ioHub server process is terminates even in the case of an expection have may not been handled
        explicitedly in your scipt.
        """
        try:
            self.run()
        except ioHub.ioHubError("Error running experimeniment."):
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
            self.hub.shutDownServer()
        # terminate psychopy
        core.quit()
        
    def displayExperimentSettingsDialog(self):
        """
        Display a read-only dialog showing the experiment setting retrieved from the configuration file. This gives the
        experiment operator a chance to ensure the correct configuration file was loaded for the script being run. If OK
        is selected in the dialog, the experiment logic continues, otherwise the experiment session is terminated.
        """
        experimentDlg=psychopy.gui.DlgFromDict(self.experimentConfig, 'Experiment Launcher', self._experimentConfigKeys, self._experimentConfigKeys, {})
        if experimentDlg.OK:
            return False
        return True

    def displayExperimentSessionSettingsDialog(self):
        """
        Display an editable dialog showing the experiment session setting retrieved from the configuration file.
        This includes the few manditory ioHub experiment session attributes, as well as any user defined experiment session
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
        prints out stack stace info for an excption in multiple ways.
        No idea if all of this is needed, infact I know it is not. But for now why not.
        Taken straight from the python manual on Exceptions.
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
