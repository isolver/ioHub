from __future__ import division
"""
ioHub
.. file: ioHub/ioDataStore/__init__.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>

PyTables EMRT File Format v 0.1 ALPHA
=====================================

Root Node == EMRT User / Site Data File
+++++++++++++++++++++++++++++++++++++++

The purpose of this file is to hold all data for a given user, or user group (lab / site). This includes
all experiment data, all experiment collateral. experiment documentation, information of devices available
to the person or lab, etc. This file will be the data storage hub for the EMRT. WE NEED A BACKUP POLICY. ;)

* Node Name = Name of user, or usernam/ site name , lab name

* Node Attributes:

EMRT_File_Format_Version - file format version number itself.

Children Nodes:
+++++++++++++++

* Implementation Node (Group): contains sub groups holding all files and scripts needed to run the experiment.

* Logistics (Group): Contains sub groups and Tables containing user information, site information, device instance data, etc.

* Documentation (Group): Contains HTML formatted documentation about the experiment, how to run it, etc. 
                         index.html is always the starting page. A set of helper files will be provided to make generating 
                         good looking scientific html documentation easier.
                         
* Data Collection (Group): Contains groups and Tables for all the different event types that can occur in an experiment, the 
                         conditions for the experiment trials (dependent and independent variables), data on each session that
                         has been run, and each paricipant, as well as data on the experiment itself. The file can contain data
                         for > 1 experiment, so that needs to considered in all dat tables.

Experiment Table
++++++++++++++++

id - unique experiment id (assigned by system
code - user definable code for experiment
name - full name of experiment, up to X characters long
description - brief desciption of experiment, up to Y characters
experiment_version - version of experiment - string up to Z char 
create_date - date the experiment file was first created
modified_date - date the file was last modified
created_by - member id of user who created the experiment
status - NOT_STARTED, ACTIVE, ON HOLD, COMPLETED, CANCELLED
phase - EXPERIMENT_DESIGN, DATA_COLLECTION, ANALYSIS, WRITE_UP, NONE

PyTables Definition
+++++++++++++++++++

"""

import tables
from tables import *
from tables import parameters
import os, sys, atexit, shutil
import ioHub
import ioHub.devices as D
from ioHub.devices import EventConstants
from log import ExperimentLog,BaseLogLevels
import util
import numpy as N

loggingLevels=BaseLogLevels()

parameters.MAX_NUMEXPR_THREADS=None
"""The maximum number of threads that PyTables should use internally in
Numexpr.  If `None`, it is automatically set to the number of cores in
your machine. In general, it is a good idea to set this to the number of
cores in your machine or, when your machine has many of them (e.g. > 4),
perhaps one less than this. < S. Simpson Note: These are 'not' GIL bound
threads and therefore actually improve performance > """

parameters.MAX_BLOSC_THREADS=None
"""The maximum number of threads that PyTables should use internally in
Blosc.  If `None`, it is automatically set to the number of cores in
your machine. In general, it is a good idea to set this to the number of
cores in your machine or, when your machine has many of them (e.g. > 4),
perhaps one less than this.  < S. Simpson Note: These are 'not' GIL bound
threads and therefore actually improve performance > """

EMRT_FILE_VERSION = '0.7 Alpha'
EMRT_SCHEMA_AUTHORS='Sol Simpson'
EMRT_SCHEMA_MODIFIED_DATE='September 26, 2012'

        
class EMRTpyTablesFile():
    
    def __init__(self,fileName,folderPath,fmode='a'):
        self.fileName=fileName
        self.folderPath=folderPath
        self.filePath=os.path.join(folderPath,fileName)
        
        self.active_experiment_id=None
        self.active_session_id=None
        
        self.flushCounter=128        
        self._eventCounter=0
        
        self.TABLES=dict()
        
        self.emrtFile = openFile(self.filePath, mode = fmode)
               
        atexit.register(close_open_data_files, False)
        
        if len(self.emrtFile.title) == 0:
            self.buildOutTemplate()
            self.flush()
        else:
            self.loadTableMappings()
    
    def loadTableMappings(self):
        self.emrtFile.title="EMRT ioDataHub File"
        # create meta-data tables
        self.TABLES['EXPERIMENT_METADETA']=self.emrtFile.root.data_collection.experiment_meta_data
        self.TABLES['SESSION_METADETA']=self.emrtFile.root.data_collection.session_meta_data

        # log table
        self.TABLES['LOG_TABLE']=self.emrtFile.root.logs.ExperimentLog
        
        # create event tables
        self.TABLES['KEYBOARD_KEY']=self.emrtFile.root.data_collection.events.keyboard.KeyboardKeyEvent

        self.TABLES['MOUSE_MOVE']=self.emrtFile.root.data_collection.events.mouse.MouseMoveEvent
        self.TABLES['MOUSE_WHEEL']=self.emrtFile.root.data_collection.events.mouse.MouseWheelEvent
        self.TABLES['MOUSE_BUTTON']=self.emrtFile.root.data_collection.events.mouse.MouseButtonEvent

        self.TABLES['JOYSTICK_BUTTON']=self.emrtFile.root.data_collection.events.joystick.JoystickButtonEvent

        self.TABLES['TTL_INPUT']=self.emrtFile.root.data_collection.events.parallel_port.ParallelPortEvent
       
        #self.TABLES['COMMAND']=self.emrtFile.root.data_collection.events.experiment.Command
        self.TABLES['MESSAGE']=self.emrtFile.root.data_collection.events.experiment.Message

        self.TABLES['EYE_SAMPLE']=self.emrtFile.root.data_collection.events.eye_tracker.MonocularEyeSample     
        self.TABLES['BINOC_EYE_SAMPLE']=self.emrtFile.root.data_collection.events.eye_tracker.BinocularEyeSample     
        self.TABLES['FIXATION_START']=self.emrtFile.root.data_collection.events.eye_tracker.FixationStartEvent     
        #self.TABLES['FIXATION_UPDATE']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.eye_tracker,'FixatonUpdateEvent', D.FixatonUpdateEvent.ndType, title='Fixation Update Events')     
        self.TABLES['FIXATION_END']=self.emrtFile.root.data_collection.events.eye_tracker.FixationEndEvent     
        self.TABLES['SACCADE_START']=self.emrtFile.root.data_collection.events.eye_tracker.SaccadeStartEvent     
        self.TABLES['SACCADE_END']=self.emrtFile.root.data_collection.events.eye_tracker.SaccadeEndEvent     
        self.TABLES['BLINK_START']=self.emrtFile.root.data_collection.events.eye_tracker.BlinkStartEvent     
        self.TABLES['BLINK_END']=self.emrtFile.root.data_collection.events.eye_tracker.BlinkEndEvent     
    
    
    def buildOutTemplate(self): 
        self.emrtFile.title="EMRT ioDataHub File"
        self.emrtFile.root.EMRT_FILE_VER=EMRT_FILE_VERSION
        self.emrtFile.root.SCHEMA_DESIGNER=EMRT_SCHEMA_AUTHORS
        self.emrtFile.root.SCHEMA_MODIFIED=EMRT_SCHEMA_MODIFIED_DATE
        
        #CREATE GROUPS
        self.emrtFile.createGroup(self.emrtFile.root, 'documentation', title='Documents related to how to use the EMRT system and user documents about experiments held within this file')
        self.emrtFile.createGroup(self.emrtFile.root, 'implementation', title='Experiment Source Files and Resources needed to Run Experiments')
        self.emrtFile.createGroup(self.emrtFile.root, 'data_collection', title='Data Collected from Experiment Sessions')
        self.emrtFile.createGroup(self.emrtFile.root, 'analysis', title='Data Analysis Files, notebooks, scripts and saved results tables.')
        self.emrtFile.createGroup(self.emrtFile.root, 'logistics', title='Information on the members and sires involved in the experiments represented in this file.')
        self.emrtFile.createGroup(self.emrtFile.root, 'logs', title='Logging Data')

        self.emrtFile.flush()
 
        self.emrtFile.createGroup(self.emrtFile.root.implementation, 'scripts', title='Source Experiment Script Files')
        self.emrtFile.createGroup(self.emrtFile.root.implementation, 'resources', title='Resource Files Used within the Experiment')

        self.emrtFile.flush()
        
        self.emrtFile.createGroup(self.emrtFile.root.implementation.resources, 'images', title='Images used in the Experiments')
        self.emrtFile.createGroup(self.emrtFile.root.implementation.resources, 'audio', title='Audio files used in the Experiments')
        self.emrtFile.createGroup(self.emrtFile.root.implementation.resources, 'video', title='Video files used in the Experiments')
        self.emrtFile.createGroup(self.emrtFile.root.implementation.resources, 'condition_files', title='Condition Files used in thee experiments.images')
        
        self.emrtFile.flush()
        
        self.emrtFile.createGroup(self.emrtFile.root.data_collection, 'experiments', title='Information about each experiment saved in this file.')
        self.emrtFile.createGroup(self.emrtFile.root.data_collection, 'sessions', title='Information about each experiment session run and saved in this file.')
        self.emrtFile.createGroup(self.emrtFile.root.data_collection, 'participants', title='Information about each participant that was employed in atleast on session in this file.')
        self.emrtFile.createGroup(self.emrtFile.root.data_collection, 'events', title='Events that occurred and were saved during the experiments.')
        
        self.emrtFile.flush()

        self.emrtFile.createGroup(self.emrtFile.root.data_collection.events, 'experiment', title='Experiment Generated Events')
        self.emrtFile.createGroup(self.emrtFile.root.data_collection.events, 'keyboard', title='Keyboard Created Events')
        self.emrtFile.createGroup(self.emrtFile.root.data_collection.events, 'mouse', title='Mouse Device Created Events')
        self.emrtFile.createGroup(self.emrtFile.root.data_collection.events, 'joystick', title='Joystick Created Events')
        self.emrtFile.createGroup(self.emrtFile.root.data_collection.events, 'eye_tracker', title='Eye Tracker Generated Events')
        self.emrtFile.createGroup(self.emrtFile.root.data_collection.events, 'parallel_port', title='Parallel Port Created Events')
        #self.emrtFile.createGroup(self.emrtFile.root.data_collection.events, 'monitor', title='Computer Monitor Created Events')

        # CREATE TABLES
                        
        # create meta-data tables
        self.TABLES['EXPERIMENT_METADETA']=self.emrtFile.createTable(self.emrtFile.root.data_collection,'experiment_meta_data', ExperimentMetaData, title='Different Experiments Paradigms that have been run')
        self.TABLES['SESSION_METADETA']=self.emrtFile.createTable(self.emrtFile.root.data_collection,'session_meta_data', SessionMetaData, title='Session run for the various experiments.')

        # log table
        self.TABLES['LOG_TABLE']=self.emrtFile.createTable(self.emrtFile.root.logs,'ExperimentLog', ExperimentLog, title='Experiment Logging Data')
        
        # create event tables
        self.TABLES['KEYBOARD_KEY']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.keyboard,'KeyboardKeyEvent', D.KeyboardKeyEvent.ndType, title='Keyboard Key Event Logging.')

        self.TABLES['MOUSE_MOVE']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.mouse,'MouseMoveEvent', D.MouseMoveEvent.ndType, title='Mouse Move Event Logging.')
        self.TABLES['MOUSE_WHEEL']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.mouse,'MouseWheelEvent', D.MouseWheelEvent.ndType, title='Mouse Wheel Event Logging.')
        self.TABLES['MOUSE_BUTTON']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.mouse,'MouseButtonEvent', D.MouseButtonEvent.ndType, title='Mouse Button Event Logging.')

        self.TABLES['JOYSTICK_BUTTON']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.joystick,'JoystickButtonEvent', D.JoystickButtonEvent.ndType, title='Joystick Button Event Logging.')

        self.TABLES['TTL_INPUT']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.parallel_port,'ParallelPortEvent', D.ParallelPortEvent.ndType, title='Parallel Port Event Logging.')

        self.TABLES['MESSAGE']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.experiment,'Message', D.MessageEvent.ndType, title='Experiment Message Event Logging.')

        self.TABLES['EYE_SAMPLE']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.eye_tracker,'MonocularEyeSample', D.MonocularEyeSample.ndType, title='Monocular Eye Samples')     
        self.TABLES['BINOC_EYE_SAMPLE']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.eye_tracker,'BinocularEyeSample', D.BinocularEyeSample.ndType, title='Binocular Eye Samples')     
        self.TABLES['FIXATION_START']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.eye_tracker,'FixationStartEvent', D.FixationStartEvent.ndType, title='Fixation Start Events')     
        self.TABLES['FIXATION_END']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.eye_tracker,'FixationEndEvent', D.FixationEndEvent.ndType, title='Fixation End Events')
        self.TABLES['SACCADE_START']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.eye_tracker,'SaccadeStartEvent', D.SaccadeStartEvent.ndType, title='Saccade Start Events')     
        self.TABLES['SACCADE_END']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.eye_tracker,'SaccadeEndEvent', D.SaccadeEndEvent.ndType, title='Saccade End Events')     
        self.TABLES['BLINK_START']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.eye_tracker,'BlinkStartEvent', D.BlinkStartEvent.ndType, title='Blink Start Events')     
        self.TABLES['BLINK_END']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.eye_tracker,'BlinkEndEvent', D.BlinkEndEvent.ndType, title='Blink End Events')     
         

        self.flush()
    
    def log(self,time,text,level=None,experiment_id=0,session_id=0):
        import inspect
        if level is None:
            level=loggingLevels.INFO
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 3)
        caller=calframe[1][3]        
        
        logline=self.TABLES['LOG_TABLE'].row
        
        logline['experiment_id']=experiment_id
        logline['session_id']=session_id
        logline['usec_time']=time
        logline['caller']=caller
        logline['level']=level
        logline['text']=text

        logline.append()
        self.TABLES['LOG_TABLE'].flush()
    
          
    def createOrUpdateExperimentEntry(self,experimentInfoList):
        experiment_metadata=self.TABLES['EXPERIMENT_METADETA']

        result = [ row for row in experiment_metadata.iterrows() if row['code'] == experimentInfoList[1] ]
        if len(result)>0:
            result=result[0]
            self.active_experiment_id=result['experiment_id']
            return self.active_experiment_id
        
        max_id=0
        id_col=experiment_metadata.col('experiment_id')

        if len(id_col) > 0:
            max_id=N.amax(id_col)
            
        self.active_experiment_id=max_id+1
        experimentInfoList[0]=self.active_experiment_id
        experiment_metadata.append([experimentInfoList,])
        self.flush()
        return self.active_experiment_id
    
    def createExperimentSessionEntry(self,sessionInfoDict):
        session_metadata=self.TABLES['SESSION_METADETA']

        max_id=0
        id_col=session_metadata.col('session_id')
        if len(id_col) > 0:
            max_id=N.amax(id_col)
        
        self.active_session_id=int(max_id+1)
        
        values=(self.active_session_id,self.active_experiment_id,sessionInfoDict['code'],sessionInfoDict['name'],sessionInfoDict['comments'],sessionInfoDict['user_variables'])
        session_metadata.append([values,])
        self.flush()

        return self.active_session_id
    
    def addMetaDataToFile(self,metaData):
        pass
    
    def _handleEvent(self, event):
        try:
            if self.active_experiment_id is None or self.active_session_id is None:
                exp_id=self.active_experiment_id
                if exp_id is None:
                    exp_id=0
                sess_id=self.active_session_id
                if sess_id is None:
                    sess_id=0

                self.log(ioHub.highPrecisionTimer(),"Experiment or Session ID is None, event not being saved: "+str(event),loggingLevels.WARNING,exp_id, sess_id)
                return

            eventClass=EventConstants.EVENT_CLASSES[event[3]]

            etable=self.TABLES[eventClass.IOHUB_DATA_TABLE]

            event[0]=self.active_experiment_id
            event[1]=self.active_session_id

            np_array= N.array([tuple(event),],dtype=eventClass.ndType) #event._asNumpyArray()


            etable.append(np_array)

            # if flushCounter threshold is >=0 then do some checks. If it is < 0, then
            # flush only occurs when command is sent to ioHub, so do nothing here.
            if self.flushCounter>=0:
                if self.flushCounter==0:
                    self.emrtFile.flush()
                    return
                if self.flushCounter==self._eventCounter:
                    self.emrtFile.flush()
                    self._eventCounter=0
                    return
                self._eventCounter+=1
        except ioHub.ioHubError, e:
            ioHub.printExceptionDetailsToStdErr()
    def flush(self):
        self.emrtFile.flush()
        
    def close(self):
        self.emrtFile.flush()
        self.emrtFile.close()
        
    def __del__(self):
        try:
            self.close()
        except:
            pass    

## -------------------- Utility Functions ------------------------ ##

def close_open_data_files(verbose):
    open_files = tables.file._open_files
    are_open_files = len(open_files) > 0
    if verbose and are_open_files:
        print "Closing remaining open data files:"
    for fileh in open_files.keys():
        if verbose:
            print "%s..." % (open_files[fileh].filename,)
        open_files[fileh].close()
        if verbose:
            print "done"

try:
    global registered_close_open_data_files
    if registered_close_open_data_files is True:
        pass
except:
    registered_close_open_data_files = True
    atexit.register(close_open_data_files, False)

## ---------------------- Pytable Definitions ------------------- ##

class ExperimentMetaData(IsDescription):
    experiment_id = UInt32Col(pos=1)
    code = StringCol(8,pos=2)
    title = StringCol(48,pos=3)
    description  = StringCol(256,pos=4)
    version = StringCol(6,pos=5)
    total_sessions_to_run = UInt16Col(pos=9)    
#    status = EnumCol([ 'NOT_STARTED', 'ACTIVE', 'ON_HOLD', 'COMPLETED', 'CANCELLED'],'NOT_STARTED','int16',pos=10)
#    phase = EnumCol([ 'EXPERIMENT_DESIGN', 'TESTING', 'DATA_COLLECTION', 'ANALYSIS', 'WRITE_UP', 'NONE'],'NONE','int16',pos=11)
#    parent_experiment_id = UInt32Col(pos=10)
    
class SessionMetaData(IsDescription):
    session_id = UInt32Col(pos=1)
    experiment_id = UInt32Col(pos=2)
    code = StringCol(8,pos=3)
    name = StringCol(16,pos=4)
    comments  = StringCol(128,pos=5)
    user_variables = StringCol(512,pos=6) # will hold json encoded version of user variable dict for session
#    date = Time64Col(pos=6)
#    participant_id=UInt32Col(pos=8)
#    member_id=UInt32Col(pos=7)
#    completion_status=EnumCol([ 'FULLY_COMPLETED', 'PARTIAL_COMPLETION', 'NOT_ABLE_TO_START','N/A'],'N/A','uint8',pos=9)
#    data_rating=EnumCol([ 'EXCELLENT', 'VERY_GOOD', 'ABOVE_AVERAGE', 'AVERAGE', 'BELOW_AVERAGE', 'POOR', 'NOT_SATISFACTORY','N/A'],'N/A','uint8',pos=10)


# NEEDS TO BE COMPLETED    
class ParticipantMetaData(IsDescription):
    participant_id = UInt32Col(pos=1) 
    participant_code = StringCol(8,pos=2)

# NEEDS TO BE COMPLETED       
class SiteMetaData(IsDescription):
    site_id = UInt32Col(pos=1) 
    site_code = StringCol(8,pos=2)

# NEEDS TO BE COMPLETED       
class MemberMetaData(IsDescription):
    member_id =UInt32Col(pos=1) 
    username = StringCol(16,pos=2)
    password = StringCol(16,pos=3)
    email = StringCol(32,pos=4)
    secretPhrase = StringCol(64,pos=5)
    dateAdded = Int64Col(pos=6)

# NEEDS TO BE COMPLETED       
class DeviceInformation(IsDescription):
    device_id = UInt32Col(pos=1) 
    device_code = StringCol(7,pos=2)
    name =StringCol(32,pos=3)
    manufacturer =StringCol(32,pos=3)

# NEEDS TO BE COMPLETED       
class CalibrationAreaInformation(IsDescription):
    cal_id = UInt32Col(pos=1)

# NEEDS TO BE COMPLETED       
class EyeTrackerInformation(IsDescription):
    et_id = UInt32Col(pos=1)

# NEEDS TO BE COMPLETED   
class EyeTrackerSessionConfiguration(IsDescription):
    et_config_id = UInt32Col(pos=1)

# NEEDS TO BE COMPLETED       
class ApparatusSetupMetaData(IsDescription):
    app_setup_id = UInt32Col(pos=1)
    
