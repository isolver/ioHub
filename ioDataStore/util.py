"""
ioHub
.. file: ioHub/ioDataStore/util.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

from tables import *
import os
import json
import ioHub.devices 
EventConstants = ioHub.devices.EventConstants

global _hubFiles

try:
    len(_hubFiles)
except:
    _hubFiles=[]
    
def openHubFile(filepath,filename,mode):
    global _hubFiles
    hubFile=openFile(os.path.join(filepath,filename), mode)
    _hubFiles.append(hubFile)
    return hubFile

def closeHubFile(hubFile):
    global _hubFiles
    if hubFile in _hubFiles:
        _hubFiles.remove(hubFile)
    hubFile.close()

def closeAllFiles():
    global _hubFiles
    for t in _hubFiles:
        t.close()
    _hubFiles[:]=[None,]*len(_h5files)
    _hubFiles=[]

def printHubFileStructure(hubFile):
    print hubFile
    
def printHubFileMetaData(hubFile,tableName,parentName=None):
    found=False
    for group in hubFile.walkGroups("/"):
        for table in hubFile.listNodes(group, classname='Table'):
            if table.name == tableName:
                found=True
                print "Object:", table
                print "Table name:", table.name
                print "Number of rows in table:", table.nrows
                print "Number of cols in table:", len(table.colnames)
                print "Table variable names with their type and shape:"
                for name in table.colnames:
                    print '\t',name, ':= %s, %s' % (table.coldtypes[name], table.coldtypes[name].shape)
                return
            
def getTableFromHubFile(hubFile,tableName,parentName=None):
    for group in hubFile.walkGroups("/"):
        for table in hubFile.listNodes(group, classname='Table'):
            if table.name == tableName:
                return table
    return None
    
def hubTableToExcel(filePath, fileName, tableName, experiment_id=0,session_id=0):
    from openpyxl import Workbook
    
    hf=openHubFile(filePath, fileName, 'r')

    hfTable=getTableFromHubFile(hf,tableName)
    nrows=hfTable.nrows

    wb = Workbook(optimized_write = True)
    ws = wb.create_sheet()
    ws.title = tableName
   
    ws.append(hfTable.colnames)

    #result=[row for row in hfTable if (row['experiment_id'] == 0 and row['session_id'] == 0)]
    for r in hfTable:    
        ws.append(r[:])

    wb.save(fileName+'.xlsx') # don't forget to save !
    
    closeHubFile(hf)
    
    return nrows
    
########### Experiment / Experiment Session Based Data Access #################

class ExperimentDataAccessUtility(object):
    EventConstants=EventConstants
    def __init__(self, hdfFilePath, hdfFileName, experimentCode=None,sessionCodes=[], mode='r'):
        self.hdfFilePath=hdfFilePath
        self.hdfFileName=hdfFileName
        self.mode=mode
        self.hdfFile=None
        self._tables={}
        self._experimentCodeList=[]
        self.experimentDicts=None


        try:
            self.hdfFile=openHubFile(hdfFilePath,hdfFileName,mode)
            self._tables['EXPERIMENT_METADATA']=self.hdfFile.root.data_collection.experiment_meta_data
            self._tables['SESSION_METADATA']=self.hdfFile.root.data_collection.session_meta_data
            self._tables['CLASS_MAPPINGS']=self.hdfFile.root.class_table_mapping            
            
        except Exception as e:
            print e
            raise ExperimentDataAccessException(e)
        
        self.getExperimentData(experimentCode,sessionCodes)

    def printHubFileMetaData(self):
        if self.hdfFile:
            printHubFileMetaData(self.hdfFile)

    def printHubFileStructure(self):
        if self.hdfFile:
            printHubFileStructure(self.hdfFile)
    
    def getExperimentData(self,experimentCode=None, sessionCodes=[]):
        if self.hdfFile:

            if experimentCode and self.experimentDicts and experimentCode in self._experimentCodeList:

                if sessionCodes is None or len(sessionCodes) == 0:
                    return self.experimentDicts[experimentCode]
                else:
                    print "getExperimentSessionData: NOT IMPLEMENTED: need to handle case of re-requesting sessionCodes for a given experiment code"
                    print "** returning ALL stored sessions for now"
                    return self.experimentDicts[experimentCode]

            if experimentCode is not None and not isinstance(experimentCode,(str,unicode)):
                raise ExperimentDataAccessException("getExperimentSessionData: experimentCode must be of type string or unicode")
    
            if sessionCodes is None:
                sessionCodes=[]
                
            if isinstance(sessionCodes,(list,tuple)):
                for s in sessionCodes:
                    if not isinstance(s,(str,unicode)):
                        raise ExperimentDataAccessException("getExperimentSessionData: each element of sessionCodes must be of type string or unicode")
            elif isinstance(sessionCodes,(str,unicode)):
                sessionCodes=[sessionCodes,]
            else:
                raise ExperimentDataAccessException("getExperimentSessionData: sessionCode must be of type string or unicode")
    
            if self.experimentDicts is None:
                self.experimentDicts=dict()

            experimentrows=None
            
            if experimentCode is None:
                experimentrows=[row[:] for row in self._tables['EXPERIMENT_METADATA'].where('(experiment_id >= 0)')]
                experimentCode=[]
                for r in experimentrows:
                    experimentCode.append(r[1])
                    self._experimentCodeList.extend(experimentCode)
            else:        
                self._experimentCodeList.append(experimentCode)
                experimentrows=[row[:] for row in self._tables['EXPERIMENT_METADATA'].where('(code == "%s")'%(experimentCode))]
            
            for erow in experimentrows:
                if erow[1] in self.experimentDicts.keys():
                    edict=self.experimentDicts[erow[1]]
                else:
                    edict={'experiment_id':erow[0], 'experiment_code':erow[1], 'title':erow[2], 'description':erow[3], 'version':erow[4], 'total_sessions_to_run':erow[5], 'session_codes':[], 'sessions': {}}
                    self.experimentDicts[erow[1]]=edict
                
                whereclause= '(experiment_id == %d)'%(erow[0])
                if len(sessionCodes)>0:
                    scode_clause=''
                    for scode in sessionCodes:
                        if scode not in edict['session_codes']: 
                            scode_clause+=' (code == "%s") |'%(scode)
                    if len(scode_clause)>0:      
                        whereclause=whereclause+' & ('+scode_clause[:-1]+')'
                sessionrows=[row[:] for row in self._tables['SESSION_METADATA'].where(whereclause)]
                    
                for srow in sessionrows:
                    if srow[2] not in edict['session_codes']:
                        edict['session_codes'].append(srow[2])
                        edict['sessions'][srow[0]]={'session_id':srow[0], 'experiment_id':srow[1], 'code':srow[2], 'name':srow[3], 'comments':srow[4], 'user_variables':json.loads(srow[5])}
            
            if len(experimentCode) ==1:
                return self.experimentDicts[experimentCode[0]]
            
            r=dict()
            for ec in experimentCode:
                if ec in self.experimentDicts:
                    r[ec]=self.experimentDicts[ec]
            return r
            
    def getEventAttributeValues(self,event_type_id,event_attribute_name,experiment_codes=None,session_codes=None):
        if self.hdfFile and self.experimentDicts:
            ctable=None            
            if event_type_id in self._tables.keys():
                ctable=self._tables[event_type_id]
            else:
                result=[row.fetch_all_fields() for row in self._tables['CLASS_MAPPINGS'].where('(class_id == %d) & (class_type_id == 1)'%(event_type_id))]

                if len(result) is not 1:
                    raise ExperimentDataAccessException("event_type_id passed to getEventAttribute should only return one row from CLASS_MAPPINGS.")
                tablePathString=result[0][3]
                self._tables[event_type_id]=self.hdfFile.getNode(tablePathString)
                ctable=self._tables[event_type_id]

            if ctable:
                if event_attribute_name not in ctable.colnames:
                    raise ExperimentDataAccessException("getEventAttribute: %s does not have a column named %s"%(ctable.title,event_attribute_name))    

                exp_ids_session_ids_lists=[]
                                
                if experiment_codes is None or len(experiment_codes)==0:
                    experiment_codes=self._experimentCodeList
                else:
                    experiment_codes=[experiment_codes,]                
                
                for ecode in self._experimentCodeList:
                    edict = self.experimentDicts[ecode]
                    exp_ids_session_ids_lists.append([edict['experiment_id'],[]])
                    if session_codes is None or len(session_codes)==0:
                        print '-------------'
                        session_ids=edict['sessions'].keys()
                        print 'session_ids:',session_ids
                        exp_ids_session_ids_lists[-1][1].extend(session_ids)
                    else: 
                        for scode in session_codes:
                            if scode in edict['session_codes']:
                                for sess in edict['sessions'].itervalues():
                                    if sess['code'] == scode:        
                                        exp_ids_session_ids_lists[-1][1].append(sess['session_id'])
                                        break
                            
                whereclause= ''
                for eid, sid_list in exp_ids_session_ids_lists:               
                    whereclause+= '( (experiment_id == %d)'%(eid)
                    if len(sid_list)>0:
                        sid_clause=''
                        for sid in sid_list:
                            sid_clause+=' (session_id == %d) |'%(sid)
                        whereclause=whereclause+' & ('+sid_clause[:-1]+') ) &'
                whereclause=whereclause[:-1]
                                
                return ctable.readWhere(whereclause, field=event_attribute_name)
          
    def close(self):
        closeHubFile(self.hdfFile)
        keys = self._tables.keys()
        for key in keys:
            del self._tables[key]
        self._tables=dict()
        
        self.experimentCodes=None
        self.hdfFilePath=None
        self.hdfFileName=None
        self.mode=None
        self.hdfFile=None
    
    def __del__(self):
        self.close()

        
class ExperimentDataAccessException(Exception):
    pass