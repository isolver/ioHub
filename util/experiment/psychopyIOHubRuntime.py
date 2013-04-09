"""
ioHub
.. file: ioHub/util/experiment/psychopyIOHubRuntime.py

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""
from __future__ import division
from psychopy import  core as core, gui

import os,sys
from collections import deque

try:
    from yaml import load
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print "*** Using Python based YAML Parsing"
    from yaml import Loader, Dumper

import ioHub
from ioHub.devices import Computer


_currentSessionInfo=None

class ioHubExperimentRuntime(object):    
    """
    ioHubExperimentRuntime is a utility class that is used to 'bind' the ioHub framework to the PsychoPy API in an easy to use way,
    hiding many of the internal complexities of the implementation and making it as simple to use within a PsychoPy script
    as possible. That is the *intent* anyway.

    The ioHubExperimentRuntime class is intended to be extended in a user script, with the .run() method being implemented with
    the actual contents of the main body of the experiment. As an example, a run.py file could be created and contain
    the following code as a minimal implementation of using the ioHubExperimentRuntime to combine psychopy and ioHub functionality
    to display a window and wait for a key press to close the window and terminate the experiment. The source file and .yaml
    config files for this simple example can be found in ioHub/examples/simple ::

        import ioHub
        from ioHub.experiment import ioHubExperimentRuntime
        
        class ExperimentRuntime(ioHubExperimentRuntime):
            def __init__(self,configFileDirectory, configFile):
                ioHubExperimentRuntime.__init__(self,configFileDirectory,configFile)
        
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
        
        
        ################################## End of Stub Example ioHubExperimentRuntime implementation ###############################
        
        Along with a python file that extends the ioHubExperimentRuntime class, normally you will also need to provide an experiment_config.yaml and ioHub_config.yaml file.
        These files are read by the ioHubExperimentRuntime and the ioHub system and make it much easier for the ioHub and associated devices to be
        configurated than if you needed to do it within a python script. So while at first these files may seem like extra overhead, we hope that they are found to
        actually save time and work in the end. Comments and feedback on this would be highly apprieciated.
        
        The iohub/examples/simple example contains the python file and two .yaml config files needed to run the example.  To run the example simply open
        a command prompt at the ioHub/examples/simple folder and type:
        
            python.exe run.py

    """
    def __init__(self, configFilePath, configFile):
        """
        Initialize the ioHubExperimentRuntime Object, loading the experiment configuration file, initializing and launching
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
        self.hub=None
        self.configFilePath=configFilePath
        self.configFileName=configFile

        # load the experiment config settings from the experiment_config.yaml file.
        # The file must be in the same directory as the experiment script.
        self.configuration=load(file( os.path.join(self.configFilePath,self.configFileName),u'r'), Loader=Loader)

        import random
        random.seed(ioHub.highPrecisionTimer()*1000.123)
        randomInt=random.randint(1,1000)
        self.experimentConfig=dict()
        self._experimentConfigKeys=['title','code','version','description']
        self.experimentConfig.setdefault('title',self.experimentConfig.get('title','A Default Experiment Title'))
        self.experimentConfig.setdefault('code',self.experimentConfig.get('code','EXP_%d'%(randomInt,)))
        self.experimentConfig.setdefault('version',self.experimentConfig.get('version','1.0d'))
        self.experimentConfig.setdefault('description',self.experimentConfig.get('description','A Default Experiment Description'))
#        self.experimentConfig.setdefault('total_sessions_to_run',self.experimentConfig.get('total_sessions_to_run',0))

        for key in self._experimentConfigKeys:
            if key in self.configuration:
                self.experimentConfig[key]=self.configuration[key]
 
        self.experimentSessionDefaults=self.configuration['session_defaults']
        self.sessionUserVariables=self.experimentSessionDefaults.get('user_variables',None)
        if self.sessionUserVariables is not None:
            del self.experimentSessionDefaults['user_variables']
        else:
            self.sessionUserVariables={}

        # initialize the experiment object based on the configuration settings.
        self.hub=self._initalizeConfiguration()

        self.devices=self.hub.devices
        self.devices.computer=Computer

    def getExperimentConfiguration(self):
        '''
        Returns the full YAML parsing of experiment_config.
        '''
        return self.configuration

    def getSavedExperimentParameters(self):
        '''
        Returns the experiment parameters saved to the DataStore.
        These are also displayed in the read-only Experiment Dialog.
        '''
        return self.experimentConfig

    def getSavedSessionParameters(self):
        '''
        Returns the experiment session parameters saved to the DataStore.
        These are also displayed in the Session Dialog. These do 'not' include
        user defined parameters.
        '''
        return self.experimentSessionDefaults

    def getSavedUserDefinedParameters(self):
        '''
        Returns the experiment session user defined parameters saved to the DataStore.
        These are also displayed in the Session Dialog.
        '''
        return self.sessionUserVariables


    def isSessionCodeNotInUse(self,current_sess_code):
        r=self.hub.sendToHubServer(('RPC','checkIfSessionCodeExists',(current_sess_code,)))
        return r[2]
                    
    def _initalizeConfiguration(self):
        global _currentSessionInfo
        """
        Based on the configuration data in the experiment_config.yaml and iohub_config.yaml,
        configure the experiment environment and ioHub process environments. This mehtod is called by the class init
        and should not be called directly.
        """
        display_experiment_dialog=self.configuration.get("display_experiment_dialog",False)
        display_session_dialog=self.configuration.get("display_session_dialog",True)
        
        
        if display_experiment_dialog is True:        
            # display a read only dialog verifying the experiment parameters
            # (based on the experiment .yaml file) to be run. User can hit OK to continue,
            # or Cancel to end the experiment session if the wrong experiment was started.
            exitExperiment=self._displayExperimentSettingsDialog()
            if exitExperiment:
                print "User Cancelled Experiment Launch."
                self._close()
                sys.exit(1)

        self.experimentConfig=self.prePostExperimentVariableCallback(self.experimentConfig)

        ioHubInfo= self.configuration.get('ioHub',{})
        
        if ioHubInfo is None:
            print 'ioHub section of configuration file could not be found. Exiting.....'
            self._close()
            sys.exit(1)
        else:
            from ioHub.client import ioHubConnection

            ioHubConfigFileName=unicode(ioHubInfo.get('config','iohub_config.yaml'))
            ioHubConfigAbsPath=os.path.join(self.configFilePath,unicode(ioHubConfigFileName))
            self.hub=ioHubConnection(None,ioHubConfigAbsPath)

            #print 'ioHubExperimentRuntime.hub: {0}'.format(self.hub)
            # A circular buffer used to hold events retrieved from self.getEvents() during
            # self.delay() calls. self.getEvents() appends any events in the allEvents
            # buffer to the result of the hub.getEvents() call that is made.
            self.hub.allEvents=deque(maxlen=self.configuration.get('event_buffer_length',256))

            #print 'ioHubExperimentRuntime sending experiment config.....'
            # send experiment info and set exp. id
            self.hub._sendExperimentInfo(self.experimentConfig)

            #print 'ioHubExperimentRuntime SENT experiment config.'
           
            allSessionDialogVariables = dict(self.experimentSessionDefaults, **self.sessionUserVariables)
            sessionVariableOrder=self.configuration['session_variable_order']
            if 'user_variables' in allSessionDialogVariables:
                del allSessionDialogVariables['user_variables']
    
            if display_session_dialog is True:
                # display session dialog
                r=True
                while r is True:
                    # display editable session variable dialog displaying the ioHub required session variables
                    # and any user defined session variables (as specified in the experiment config .yaml file)
                    # User can enter correct values and hit OK to continue, or Cancel to end the experiment session.
    
                    allSessionDialogVariables = dict(self.experimentSessionDefaults, **self.sessionUserVariables)
                    sessionVariableOrder=self.configuration['session_variable_order']
                    if 'user_variables' in allSessionDialogVariables:
                        del allSessionDialogVariables['user_variables']
         
                    tempdict=self._displayExperimentSessionSettingsDialog(allSessionDialogVariables,sessionVariableOrder)
                    if tempdict is None:
                        print "User Cancelled Experiment Launch."
                        self._close()
                        sys.exit(1)
                
                    tempdict['user_variables']=self.sessionUserVariables
    
                    r=self.isSessionCodeNotInUse(tempdict['code'])
                     
                    if r is True:
                        display_device=self.hub.getDevice('display')
                        display_id=0
                        if display_device:
                            display_id=display_device.getIndex()
                        msg_dialog=ioHub.util.experiment.dialogs.MessageDialog(
                                        "Session Code {0} is already in use by the experiment.\nPlease enter a new Session Code".format(tempdict['code']),
                                        "Session Code In Use",
                                        dialogType=ioHub.util.experiment.dialogs.MessageDialog.ERROR_DIALOG,
                                        allowCancel=False,
                                        display_index=display_id)
                        msg_dialog.show()
            else:
                tempdict=allSessionDialogVariables
                tempdict['user_variables']=self.sessionUserVariables

            for key,value in allSessionDialogVariables.iteritems():
                if key in self.experimentSessionDefaults:
                    self.experimentSessionDefaults[key]=value#(u''+value).encode('utf-8')
                elif  key in self.sessionUserVariables:
                    self.sessionUserVariables[key]=value#(u''+value).encode('utf-8')      


            tempdict=self.prePostSessionVariableCallback(tempdict)
            tempdict['user_variables']=self.sessionUserVariables

            _currentSessionInfo=self.experimentSessionDefaults

            self.hub._sendSessionInfo(tempdict)

            # create necessary paths based on yaml settings,
            self.paths=PathMapping(self.configFilePath,self.configuration.get('paths',None))
    
            self.paths.saveToJson()
        

            self._setInitialProcessAffinities(ioHubInfo)

            return self.hub

    def _setInitialProcessAffinities(self,ioHubInfo):
            # set process affinities based on config file settings
            cpus=range(Computer.processingUnitCount)
            experiment_process_affinity=cpus
            other_process_affinity=cpus
            iohub_process_affinity=cpus
    
            experiment_process_affinity=self.configuration.get('process_affinity',[])
            if len(experiment_process_affinity) == 0:
                experiment_process_affinity=cpus
                    
            other_process_affinity=self.configuration.get('remaining_processes_affinity',[])
            if len(other_process_affinity) == 0:
                other_process_affinity=cpus
            
            iohub_process_affinity=ioHubInfo.get('process_affinity',[])
            if len(iohub_process_affinity) == 0:
                iohub_process_affinity=cpus
    
            if len(experiment_process_affinity) < len(cpus) and len(iohub_process_affinity) < len(cpus):
                Computer.setProcessAffinities(experiment_process_affinity,iohub_process_affinity)
    
            if len(other_process_affinity) < len(cpus):
                ignore=[Computer.currentProcessID,Computer.ioHubServerProcessID]
                Computer.setAllOtherProcessesAffinity(other_process_affinity,ignore)
        

    def run(self,*args,**kwargs):
        """
        The run method is what gets calls when the ioHubExperimentRuntime.start method is called. The run method is intended
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
        except ioHub.ioHubError, e:
            print e
        except:
            ioHub.printExceptionDetailsToStdErr()
        finally:
            # _close ioHub, shut down ioHub process, clean-up.....
            self._close()


    def prePostExperimentVariableCallback(self,expVarDict):
        return expVarDict

    def prePostSessionVariableCallback(self,sessionVarDict):
        sess_code=sessionVarDict['code']
        scount=1
        while self.isSessionCodeNotInUse(sess_code) is True:
            sess_code='%s-%d'%(sessionVarDict['code'],scount)
            scount+=1
        sessionVarDict['code']=sess_code
        return sessionVarDict
        
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
        #print 'self.experimentConfig:', self.experimentConfig
        #print 'self._experimentConfigKeys:',self._experimentConfigKeys

        experimentDlg=gui.DlgFromDict(self.experimentConfig, 'Experiment Launcher', self._experimentConfigKeys, self._experimentConfigKeys, {})
        if experimentDlg.OK:
            result= False
        else:
            result= True

            
        return result

    def _displayExperimentSessionSettingsDialog(self,allSessionDialogVariables,sessionVariableOrder):
        """
        Display an editable dialog showing the experiment session setting retrieved from the configuration file.
        This includes the few mandatory ioHub experiment session attributes, as well as any user defined experiment session
        attributes that have been defined in the experiment configuration file. If OK is selected in the dialog,
        the experiment logic continues, otherwise the experiment session is terminated.
        """
        
        sessionDlg=gui.DlgFromDict(allSessionDialogVariables, 'Experiment Session Settings', [], sessionVariableOrder)

        result=None        
        if sessionDlg.OK:
            result=allSessionDialogVariables

            
        return result
        
    @staticmethod    
    def printExceptionDetails():
        """
        Prints out stack trace info for the last exception in multiple ways.
        No idea if all of this is needed, in fact I know it is not. But for now why not.
        Taken straight from the python 2.7.3 manual on Exceptions.
        """
        import traceback
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
 

class PathDir(object):
    def __init__(self, physicalAbsPath, fileFilter=None):
        self._extensions=None
        self._fileTypes=None
        self._path=physicalAbsPath

        if fileFilter is not None:
            if len(fileFilter)==2:
                self._fileTypes,self._extensions=fileFilter

        if self._fileTypes:
            for ft in self._fileTypes:
                if ft in PathMapping._FILE_TYPES:
                    if ft not in PathMapping._fileTypeToPath:
                        PathMapping._fileTypeToPath[ft]=self
    
    def getPath(self):
        return self._path
    
    def getExtensions(self):    
        return self._extensions

    def getFileTypes(self):    
        return self._fileTypes
    
class PathMapping(object):
    _FILE_TYPES=dict(CONDITION_FILES='CONDITION_FILES',
                    IMAGE_FILES='IMAGE_FILES',
                    AUDIO_FILES='AUDIO_FILES',
                    VIDEO_FILES='VIDEO_FILES',
                    IOHUB_DATA='IOHUB_DATA',
                    LOGS='LOGS',
                    SYS_INFO='SYS_INFO',
                    USER_FILES='USER_FILES',
                    NATIVE_DEVICE_DATA='NATIVE_DEVICE_DATA',)
    _fileTypeToPath={}
    def __init__(self, top, pathSettings):
        self.experimentSourceDir=os.path.abspath(top)
        self.pythonPath=sys.path
        self.workingDir=os.getcwdu()

        self.structure=PathDir(os.path.abspath(top))

        # build the structure

        if pathSettings is None:
            self._fileTypeToPath['*']=self.structure
            self._fileTypeToPath['SYS_INFO']=self.structure
            self._fileTypeToPath['IOHUB_DATA']=self.structure
            self._fileTypeToPath['NATIVE_DEVICE_DATA']=self.structure
            self.SYS_INFO=self.structure
            self.IOHUB_DATA=self.structure
        else:
            def buildOutPath(root,pathDict):

                for subdir,info in pathDict.iteritems():
                    isSubjectDir=False
                    if subdir == 'session_defaults.code':
                        subdir=_currentSessionInfo['code']
                        isSubjectDir=True

                    newDir=os.path.join(root._path,subdir)
                    if os.path.exists(newDir):
                        if isSubjectDir:
                            #TODO Show dialog asking if they want subject dir to be removed / overwritten.
                            print "#TODO Show dialog asking if they want subject dir to be removed / overwritten."
                    else:
                        os.makedirs(newDir)

                    if isinstance(info,dict):
                        newPath=PathDir(newDir)
                        setattr(root,subdir,newPath)
                        buildOutPath(newPath,info)
                    else:
                        newPath=PathDir(newDir,info)
                        for ft in newPath._fileTypes:
                            if not hasattr(self,ft):
                                setattr(self,ft,newPath)
                        setattr(root,subdir,newPath)


            buildOutPath(self.structure,pathSettings)

    def getPathForFile(self,fileName=None,fileExtension=None,fileType=None):
        if fileExtension in self._fileTypeToPath:
            return self._fileTypeToPath[fileExtension]
        if fileType in self._fileTypeToPath:
            return self._fileTypeToPath[fileType]
        if isinstance(fileName,(str,unicode)):
            i=fileName.rfind('.')
            if i > 0:
                ext = fileName.strip()[i+1:]
                if ext in self._fileTypeToPath:
                    return self._fileTypeToPath[ext]
        return self._fileTypeToPath['*']

    def saveToJson(self):
        import ujson
        mappings={}
        for v in self._FILE_TYPES.values():
            if v in self._fileTypeToPath:
                mappings[v]=self._fileTypeToPath[v]._path

        f=open(os.path.join(self.experimentSourceDir,'exp.paths'),'w')
        f.write(ujson.dumps(mappings))
        f.flush()
        f.close()
       
class ioHubExperimentRuntimeError(Exception):
    """Base class for exceptions raised by ioHubExperimentRuntime class."""
    pass        
