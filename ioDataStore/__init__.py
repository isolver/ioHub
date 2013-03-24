from __future__ import division
"""
ioHub
.. file: ioHub/ioDataStore/__init__.py

Copyright (C) 2012-2013 iSolver Software Solutions
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
import os, atexit

import tables
from tables import *
from tables import parameters

import numpy as N

import ioHub
import ioHub.devices as D
from ioHub.devices import  loadedDeviceClasses,DeviceEvent
from ioHub.constants import EventConstants
from log import ExperimentLog,BaseLogLevels

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

DATA_FILE_TITLE="ioHub Experiment Data File"
FILE_VERSION = '0.8 Alpha'
SCHEMA_AUTHORS='Sol Simpson'
SCHEMA_MODIFIED_DATE='October 1st, 2012'

        
class ioHubpyTablesFile():
    
    def __init__(self,fileName,folderPath,fmode='a',ioHubsettings=None):
        self.fileName=fileName
        self.folderPath=folderPath
        self.filePath=os.path.join(folderPath,fileName)

        self.settings=ioHubsettings

        self.active_experiment_id=None
        self.active_session_id=None
        
        self.flushCounter=self.settings.get('flush_interval',32)
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
        # create meta-data tables
        self.TABLES['EXPERIMENT_METADETA']=self.emrtFile.root.data_collection.experiment_meta_data
        self.TABLES['SESSION_METADETA']=self.emrtFile.root.data_collection.session_meta_data

        # log table
        self.TABLES['LOG_TABLE']=self.emrtFile.root.logs.ExperimentLog
        
        class_constant_strings=loadedDeviceClasses.keys()
        # create event tables
        if 'KEYBOARD' in class_constant_strings:
            self.TABLES['KEYBOARD_KEY']=self.emrtFile.root.data_collection.events.keyboard.KeyboardKeyEvent
            self.TABLES['KEYBOARD_CHAR']=self.emrtFile.root.data_collection.events.keyboard.KeyboardCharEvent

        if 'MOUSE' in class_constant_strings:
            self.TABLES['MOUSE_INPUT']=self.emrtFile.root.data_collection.events.mouse.MouseInputEvent

        if 'GAMEPAD' in class_constant_strings:
            self.TABLES['GAMEPAD_STATE_CHANGE']=self.emrtFile.root.data_collection.events.gamepad.GamePadStateChangeEvent

        if 'EXPERIMENT' in class_constant_strings:
            self.TABLES['MESSAGE']=self.emrtFile.root.data_collection.events.experiment.Message

        if 'ANALOGINPUT' in class_constant_strings:
            self.TABLES['MULTI_CHANNEL_ANALOG_INPUT']=self.emrtFile.root.data_collection.events.analog_input.MultiChannelAnalogInputEvent

        if 'EYETRACKER' in class_constant_strings:
            self.TABLES['MONOCULAR_EYE_SAMPLE']=self.emrtFile.root.data_collection.events.eyetracker.MonocularEyeSampleEvent
            self.TABLES['BINOCULAR_EYE_SAMPLE']=self.emrtFile.root.data_collection.events.eyetracker.BinocularEyeSampleEvent
            self.TABLES['FIXATION_START']=self.emrtFile.root.data_collection.events.eyetracker.FixationStartEvent
            self.TABLES['FIXATION_END']=self.emrtFile.root.data_collection.events.eyetracker.FixationEndEvent
            self.TABLES['SACCADE_START']=self.emrtFile.root.data_collection.events.eyetracker.SaccadeStartEvent
            self.TABLES['SACCADE_END']=self.emrtFile.root.data_collection.events.eyetracker.SaccadeEndEvent
            self.TABLES['BLINK_START']=self.emrtFile.root.data_collection.events.eyetracker.BlinkStartEvent
            self.TABLES['BLINK_END']=self.emrtFile.root.data_collection.events.eyetracker.BlinkEndEvent
    
        #ioHub.print2err('loadTableMappings complete. TABLES: {0}'.format(self.TABLES.keys()))
        
    def buildOutTemplate(self): 
        self.emrtFile.title=DATA_FILE_TITLE
        self.emrtFile.FILE_VERSION=FILE_VERSION
        self.emrtFile.SCHEMA_DESIGNER=SCHEMA_AUTHORS
        self.emrtFile.SCHEMA_MODIFIED=SCHEMA_MODIFIED_DATE
        
        #CREATE GROUPS

        self.emrtFile.createGroup(self.emrtFile.root, 'analysis', title='Data Analysis Files, notebooks, scripts and saved results tables.')
        self.emrtFile.createGroup(self.emrtFile.root, 'data_collection', title='Data Collected from Experiment Sessions')
        self.flush()

        self.emrtFile.createGroup(self.emrtFile.root.data_collection, 'events', title='Events that occurred and were saved during the experiments.')

        self.emrtFile.createGroup(self.emrtFile.root.data_collection, 'condition_variables', title='Experiment DV and IVs used during and experiment session, or calculated and stored. In general, each row represents one trial of an experiment session.')
        self.flush()

        # CREATE TABLES

        dfilter = Filters(complevel=0, complib='zlib', shuffle=False, fletcher32=False)
        #  filters = Filters(complevel=1, complib='blosc', shuffle=True, fletcher32=False)
        # create meta-data tables
        self.TABLES['CLASS_TABLE_MAPPINGS']=self.emrtFile.createTable(self.emrtFile.root,'class_table_mapping', ClassTableMappings, title='Mapping of ioObjects Classes to ioHub tables')
        
        self.TABLES['EXPERIMENT_METADETA']=self.emrtFile.createTable(self.emrtFile.root.data_collection,'experiment_meta_data', ExperimentMetaData, title='Different Experiments Paradigms that have been run')
        self.TABLES['SESSION_METADETA']=self.emrtFile.createTable(self.emrtFile.root.data_collection,'session_meta_data', SessionMetaData, title='Session run for the various experiments.')
        self.flush()

        # log table
        self.emrtFile.createGroup(self.emrtFile.root, 'logs', title='Logging Data')
        self.flush()
        self.TABLES['LOG_TABLE']=self.emrtFile.createTable(self.emrtFile.root.logs,'ExperimentLog', ExperimentLog, title='Experiment Logging Data')

        class_constant_strings=loadedDeviceClasses.keys()
        
        if 'KEYBOARD' in class_constant_strings:
            # create event tables
            self.emrtFile.createGroup(self.emrtFile.root.data_collection.events, 'keyboard', title='Keyboard Created Events')
            self.flush()
            self.TABLES['KEYBOARD_KEY']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.keyboard,'KeyboardKeyEvent', D.KeyboardKeyEvent.NUMPY_DTYPE, title='Keyboard Key Event Logging.', filters=dfilter.copy())
            self.TABLES['KEYBOARD_CHAR']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.keyboard,'KeyboardCharEvent', D.KeyboardCharEvent.NUMPY_DTYPE, title='Keyboard Char Event Logging.', filters=dfilter.copy())
            self.flush()
            self.addClassMapping(D.KeyboardPressEvent,self.TABLES['KEYBOARD_KEY'])
            self.addClassMapping(D.KeyboardReleaseEvent,self.TABLES['KEYBOARD_KEY'])
            self.addClassMapping(D.KeyboardCharEvent,self.TABLES['KEYBOARD_CHAR'])
            
        if 'MOUSE' in class_constant_strings:
            self.emrtFile.createGroup(self.emrtFile.root.data_collection.events, 'mouse', title='Mouse Device Created Events')
            self.flush()
            self.TABLES['MOUSE_INPUT']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.mouse,'MouseInputEvent', D.MouseInputEvent.NUMPY_DTYPE, title='Mouse Event Logging.', filters=dfilter.copy())
            self.addClassMapping(D.MouseMoveEvent,self.TABLES['MOUSE_INPUT'])
            self.addClassMapping(D.MouseWheelUpEvent,self.TABLES['MOUSE_INPUT'])
            self.addClassMapping(D.MouseWheelDownEvent,self.TABLES['MOUSE_INPUT'])
            self.addClassMapping(D.MouseButtonReleaseEvent,self.TABLES['MOUSE_INPUT'])
            self.addClassMapping(D.MouseButtonPressEvent,self.TABLES['MOUSE_INPUT'])
            self.addClassMapping(D.MouseDoubleClickEvent,self.TABLES['MOUSE_INPUT'])
        
        if 'GAMEPAD' in class_constant_strings:
            self.emrtFile.createGroup(self.emrtFile.root.data_collection.events, 'gamepad', title='GamePad Created Events')
            self.flush()

            self.TABLES['GAMEPAD_STATE_CHANGE']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.gamepad,'GamePadStateChangeEvent', D.GamepadStateChangeEvent.NUMPY_DTYPE, title='GamePad Multi-State Change Event Logging.')
            self.addClassMapping(D.GamepadStateChangeEvent,self.TABLES['GAMEPAD_STATE_CHANGE'])
            self.addClassMapping(D.GamepadDisconnectEvent,self.TABLES['GAMEPAD_STATE_CHANGE'])

        if 'ANALOGINPUT' in class_constant_strings:
            self.emrtFile.createGroup(self.emrtFile.root.data_collection.events, 'analog_input', title='AnalogInput Device Created Events')
            self.flush()
            self.TABLES['MULTI_CHANNEL_ANALOG_INPUT']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.analog_input,'MultiChannelAnalogInputEvent', D.MultiChannelAnalogInputEvent.NUMPY_DTYPE, title='Multiple Channel Analog Input Event Logging.',expectedrows=3637200000, filters=dfilter.copy()) # 20 hours of 1000 Hz samples
            self.flush()
            #self.addClassMapping(D.DASingleChannelInputEvent,self.TABLES['DA_SINGLE_CHANNEL_INPUT'])
            self.addClassMapping(D.MultiChannelAnalogInputEvent,self.TABLES['MULTI_CHANNEL_ANALOG_INPUT'])
            
        if 'EXPERIMENT' in class_constant_strings:
            self.emrtFile.createGroup(self.emrtFile.root.data_collection.events, 'experiment', title='Experiment Generated Events')
            self.flush()
            self.TABLES['MESSAGE']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.experiment,'Message', D.MessageEvent.NUMPY_DTYPE, title='Experiment Message Event Logging.', filters=dfilter.copy())
            self.addClassMapping(D.MessageEvent,self.TABLES['MESSAGE']) 
            
        if 'EYETRACKER' in class_constant_strings:
            self.emrtFile.createGroup(self.emrtFile.root.data_collection.events, 'eyetracker', title='Eye Tracker Generated Events')
            self.flush()
            self.TABLES['MONOCULAR_EYE_SAMPLE']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.eyetracker,'MonocularEyeSampleEvent', D.MonocularEyeSampleEvent.NUMPY_DTYPE, title='Monocular Eye Samples',expectedrows=3637200000, filters=dfilter.copy())
            self.TABLES['BINOCULAR_EYE_SAMPLE']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.eyetracker,'BinocularEyeSampleEvent', D.BinocularEyeSampleEvent.NUMPY_DTYPE, title='Binocular Eye Samples',expectedrows=3637200000, filters=dfilter.copy())
            self.TABLES['FIXATION_START']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.eyetracker,'FixationStartEvent', D.FixationStartEvent.NUMPY_DTYPE, title='Fixation Start Events', filters=dfilter.copy())
            self.TABLES['FIXATION_END']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.eyetracker,'FixationEndEvent', D.FixationEndEvent.NUMPY_DTYPE, title='Fixation End Events', filters=dfilter.copy())
            self.TABLES['SACCADE_START']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.eyetracker,'SaccadeStartEvent', D.SaccadeStartEvent.NUMPY_DTYPE, title='Saccade Start Events', filters=dfilter.copy())
            self.TABLES['SACCADE_END']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.eyetracker,'SaccadeEndEvent', D.SaccadeEndEvent.NUMPY_DTYPE, title='Saccade End Events', filters=dfilter.copy())
            self.TABLES['BLINK_START']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.eyetracker,'BlinkStartEvent', D.BlinkStartEvent.NUMPY_DTYPE, title='Blink Start Events', filters=dfilter.copy())
            self.TABLES['BLINK_END']=self.emrtFile.createTable(self.emrtFile.root.data_collection.events.eyetracker,'BlinkEndEvent', D.BlinkEndEvent.NUMPY_DTYPE, title='Blink End Events', filters=dfilter.copy())
            self.addClassMapping(D.MonocularEyeSampleEvent,self.TABLES['MONOCULAR_EYE_SAMPLE']) 
            self.addClassMapping(D.BinocularEyeSampleEvent,self.TABLES['BINOCULAR_EYE_SAMPLE']) 
            self.addClassMapping(D.FixationStartEvent,self.TABLES['FIXATION_START']) 
            self.addClassMapping(D.FixationEndEvent,self.TABLES['FIXATION_END']) 
            self.addClassMapping(D.SaccadeStartEvent,self.TABLES['SACCADE_START']) 
            self.addClassMapping(D.SaccadeEndEvent,self.TABLES['SACCADE_END']) 
            self.addClassMapping(D.BlinkStartEvent,self.TABLES['BLINK_START']) 
            self.addClassMapping(D.BlinkEndEvent,self.TABLES['BLINK_END']) 
            
        self.flush()
        #ioHub.print2err('buildOutTemplate complete. TABLES: {0}'.format(self.TABLES.keys()))
    
    def addClassMapping(self,ioClass,ctable):
        trow=self.TABLES['CLASS_TABLE_MAPPINGS'].row
        trow['class_id']=ioClass.EVENT_TYPE_ID
        trow['class_type_id'] = 1 # Device or Event etc.
        trow['class_name'] = ioClass.__name__
        trow['table_path']  = ctable._v_pathname
        trow.append()            
        self.flush()
        
    def log(self,time,text,level=None,experiment_id=0,session_id=0):
        import inspect
        if level is None:
            level=loggingLevels.INFO
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 3)
        caller=calframe[1][3]        
        
        if experiment_id==0 and self.active_experiment_id:
            experiment_id=self.active_experiment_id

        if session_id==0 and self.active_session_id:
            session_id=self.active_session_id
            
        logline=self.TABLES['LOG_TABLE'].row
        
        logline['experiment_id']=experiment_id
        logline['session_id']=session_id
        logline['sec_time']=float(time)
        logline['caller']=caller
        logline['level']=level
        logline['text']=text

        logline.append()
        self.flush()
    
          
    def createOrUpdateExperimentEntry(self,experimentInfoList):
        #ioHub.print2err("createOrUpdateExperimentEntry called with: ",experimentInfoList)
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
        #ioHub.print2err("Experiment ID set to: ",self.active_experiment_id)
        return self.active_experiment_id
    
    def createExperimentSessionEntry(self,sessionInfoDict):
        #ioHub.print2err("createExperimentSessionEntry called with: ",sessionInfoDict)
        session_metadata=self.TABLES['SESSION_METADETA']

        max_id=0
        id_col=session_metadata.col('session_id')
        if len(id_col) > 0:
            max_id=N.amax(id_col)
        
        self.active_session_id=int(max_id+1)
        
        values=(self.active_session_id,self.active_experiment_id,sessionInfoDict['code'],sessionInfoDict['name'],sessionInfoDict['comments'],sessionInfoDict['user_variables'])
        session_metadata.append([values,])
        self.flush()

        #ioHub.print2err("Session ID set to: ",self.active_session_id)
        return self.active_session_id

    def _initializeConditionVariableTable(self,experiment_id,np_dtype):
        experimentConditionVariableTable=None
        self._EXP_COND_DTYPE=N.dtype(np_dtype)
        try:
            expCondTableName="EXP_CV_%d"%(experiment_id)
            experimentConditionVariableTable=self.emrtFile.root.data_collection.condition_variables._f_getChild(expCondTableName)
            self.TABLES['EXP_CV']=experimentConditionVariableTable
        except NoSuchNodeError, nsne:
            try:
                experimentConditionVariableTable=self.emrtFile.createTable(self.emrtFile.root.data_collection.condition_variables,expCondTableName,self._EXP_COND_DTYPE,title='Condition Variables for Experiment id %d'%(experiment_id))
                self.TABLES['EXP_CV']=experimentConditionVariableTable
                self.emrtFile.flush()
            except:
                ioHub.printExceptionDetailsToStdErr()
                return False
        except Exception:
            ioHub.print2err('Error getting experimentConditionVariableTable for experiment %d, table name: %s'%(experiment_id,expCondTableName))
            ioHub.printExceptionDetailsToStdErr()
            return False
        self._activeRunTimeConditionVariableTable=experimentConditionVariableTable
        return True

    def _addRowToConditionVariableTable(self,session_id,data):
        if self.emrtFile and 'EXP_CV' in self.TABLES and self._EXP_COND_DTYPE is not None:
            try:
                etable=self.TABLES['EXP_CV']

                for i,d in enumerate(data):
                    if isinstance(d,(list,tuple)):
                        data[i]=tuple(d)

                np_array= N.array([tuple(data),],dtype=self._EXP_COND_DTYPE)
                etable.append(np_array)

                self.bufferedFlush()
                return True

            except:
                ioHub.printExceptionDetailsToStdErr()
        return False

    def addMetaDataToFile(self,metaData):
        pass

    def checkForExperimentAndSessionIDs(self,event=None):
        if self.active_experiment_id is None or self.active_session_id is None:
            exp_id=self.active_experiment_id
            if exp_id is None:
                exp_id=0
            sess_id=self.active_session_id
            if sess_id is None:
                sess_id=0

            self.log(ioHub.devices.Computer.getTime(),"Experiment or Session ID is None, event not being saved: "+str(event),loggingLevels.WARNING,exp_id, sess_id)
            return False
        return True
        
    def checkIfSessionCodeExists(self,sessionCode):
        if self.emrtFile:
            sessionsForExperiment=self.emrtFile.root.data_collection.session_meta_data.where("experiment_id == %d"%(self.active_experiment_id,))
            sessionCodeMatch=[sess for sess in sessionsForExperiment if sess['code'] == sessionCode]
            if len(sessionCodeMatch)>0:
                return True
            return False
            
    def _handleEvent(self, event):
        try:
            if self.checkForExperimentAndSessionIDs(event) is False:
                return False

            etype=event[DeviceEvent.EVENT_TYPE_ID_INDEX]

            eventClass=EventConstants.getClass(etype)
            etable=self.TABLES[eventClass.IOHUB_DATA_TABLE]
            event[DeviceEvent.EVENT_EXPERIMENT_ID_INDEX]=self.active_experiment_id
            event[DeviceEvent.EVENT_SESSION_ID_INDEX]=self.active_session_id

            np_array= N.array([tuple(event),],dtype=eventClass.NUMPY_DTYPE)
            etable.append(np_array)

            self.bufferedFlush()

        except ioHub.ioHubError, e:
            ioHub.print2err(e)
        except:
            ioHub.printExceptionDetailsToStdErr()

    def _handleEvents(self, events):
        # saves many events to pytables table at once.
        # EVENTS MUST ALL BE OF SAME TYPE!!!!!
        try:
            #ioHub.print2err("_handleEvent: ",self.active_experiment_id,self.active_session_id)

            if self.checkForExperimentAndSessionIDs(len(events)) is False:
                return False

            event=events[0]

            etype=event[DeviceEvent.EVENT_TYPE_ID_INDEX]
            #ioHub.print2err("etype: ",etype)
            eventClass=EventConstants.getClass(etype)
            etable=self.TABLES[eventClass.IOHUB_DATA_TABLE]
            #ioHub.print2err("eventClass: etable",eventClass,etable)

            np_events=[]
            for event in events:
                event[DeviceEvent.EVENT_EXPERIMENT_ID_INDEX]=self.active_experiment_id
                event[DeviceEvent.EVENT_SESSION_ID_INDEX]=self.active_session_id
                np_events.append(tuple(event))

            np_array= N.array(np_events,dtype=eventClass.NUMPY_DTYPE)
            #ioHub.print2err('np_array:',np_array)
            etable.append(np_array)

            self.bufferedFlush(len(np_events))

        except ioHub.ioHubError, e:
            ioHub.print2err(e)
        except:
            ioHub.printExceptionDetailsToStdErr()

    def bufferedFlush(self,eventCount=1):
        # if flushCounter threshold is >=0 then do some checks. If it is < 0, then
        # flush only occurs when command is sent to ioHub, so do nothing here.
        if self.flushCounter>=0:
            if self.flushCounter==0:
                self.flush()
                return True
            if self.flushCounter<=self._eventCounter:
                self.flush()
                self._eventCounter=0
                return True
            self._eventCounter+=eventCount
            return False


    def flush(self):
        try:
            if self.emrtFile:
                self.emrtFile.flush()
        except ClosedFileError:
            pass
        except:
            ioHub.printExceptionDetailsToStdErr()

    def close(self):
        self.flush()
        self._activeRunTimeConditionVariableTable=None
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
class ClassTableMappings(IsDescription):
    class_id = UInt32Col(pos=1)
    class_type_id = UInt32Col(pos=2) # Device or Event etc.
    class_name = StringCol(32,pos=3)
    table_path  = StringCol(128,pos=4)


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


"""
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
    
"""