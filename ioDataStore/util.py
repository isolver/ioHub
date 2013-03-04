"""
ioHub
.. file: ioHub/ioDataStore/util.py

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

import ioHub
from tables import *
import os
from pprint import pprint
from collections import namedtuple
from ioHub.constants import EventConstants
import numpy

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
    for group in hubFile.walkGroups("/"):
        for table in hubFile.listNodes(group, classname='Table'):
            if table.name == tableName:
                print '------------------'
                print "Path:", table
                print "Table name:", table.name
                print "Number of rows in table:", table.nrows
                print "Number of cols in table:", len(table.colnames)
                print "Attribute name := type, shape:"
                for name in table.colnames:
                    print '\t',name, ':= %s, %s' % (table.coldtypes[name], table.coldtypes[name].shape)
                print '------------------'
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


def qtOpenFileDialog():
    from PyQt4 import QtGui
    import sys

    app = QtGui.QApplication(sys.argv)

    fname = QtGui.QFileDialog.getOpenFileName(None, 'Open file', '.')

    if fname:
        filePath, fileName = os.path.split(str(fname))
        experimentData = ExperimentDataAccessUtility(filePath, fileName)
        return experimentData
    app.quit()
    return None


def qtDisplayConditionVariablesTable(experimentData):
    from PyQt4 import QtGui
    import sys

    app = QtGui.QApplication(sys.argv)

    entries = []
    tableWidget = QtGui.QTableWidget()
    cvNames=[]
    if isinstance(experimentData, ExperimentDataAccessUtility):
        condition_variables_table = experimentData.hdfFile.root.data_collection.condition_variables.EXP_CV_1
        cvNames=experimentData.getConditionVariableNames()    
        entries = [row[:] for row in condition_variables_table]
    else:
        entries = [row.condition_set[:] for row in experimentData]
        cvNames=experimentData[0].condition_set._fields 
        
    tableWidget.setRowCount(len(entries))
    tableWidget.setColumnCount(len(entries[0]))

    tableWidget.setHorizontalHeaderLabels(cvNames)

    for i, row in enumerate(entries):
        for j, col in enumerate(row):
            col = str(col)
            item = QtGui.QTableWidgetItem(col)
            tableWidget.setItem(i, j, item)

    tableWidget.show()
    app.exec_()

########### Experiment / Experiment Session Based Data Access #################

class ExperimentDataAccessUtility(object):

    def __init__(self, hdfFilePath, hdfFileName, experimentCode=None,sessionCodes=[],mode='r'):
        self.hdfFilePath=hdfFilePath
        self.hdfFileName=hdfFileName
        self.mode=mode
        self.hdfFile=None

        self._experimentCode=experimentCode
        self._sessionCodes=sessionCodes
        self._lastWhereClause=None

        try:
            self.hdfFile=openHubFile(hdfFilePath,hdfFileName,mode)
        except Exception as e:
            print e
            raise ExperimentDataAccessException(e)

        self.getExperimentMetaData()

    def printTableStructure(self,tableName):
        if self.hdfFile:
            printHubFileMetaData(self.hdfFile,tableName)

    def printHubFileStructure(self):
        if self.hdfFile:
            printHubFileStructure(self.hdfFile)
    
    def getExperimentMetaData(self):
        if self.hdfFile:
            expcols=self.hdfFile.root.data_collection.experiment_meta_data.colnames
            if 'sessions' not in expcols:
                expcols.append('sessions')
            ExperimentMetaDataInstance = namedtuple('ExperimentMetaDataInstance', expcols)
            experiments=[]
            for e in self.hdfFile.root.data_collection.experiment_meta_data:
                self._experimentID=e['experiment_id']
                a_exp=list(e[:])
                a_exp.append(self.getSessionMetaData())
                experiments.append(ExperimentMetaDataInstance(*a_exp))
            return experiments

    def getSessionMetaData(self,sessions=None):
        if self.hdfFile:
            if sessions == None:
                sessions=[]

            sessionCodes=self._sessionCodes
            sesscols=self.hdfFile.root.data_collection.session_meta_data.colnames
            SessionMetaDataInstance = namedtuple('SessionMetaDataInstance', sesscols)
            for r in self.hdfFile.root.data_collection.session_meta_data:
                if (len(sessionCodes) == 0 or r['code'] in sessionCodes) and r['experiment_id']==self._experimentID:
                    sessions.append(SessionMetaDataInstance(*r[:]))
            return sessions

    def getConditionVariableNames(self):
        cv_group=self.hdfFile.root.data_collection.condition_variables
        ecv="EXP_CV_%d"%(self._experimentID,)
        if ecv in cv_group._v_leaves:
            ecvTable=cv_group._v_leaves[ecv]
            return ecvTable.colnames
        return None

    def getConditionVariables(self,filter=None):
        if filter is None:
            session_ids=[]
            for s in self.getExperimentMetaData()[0].sessions:
                session_ids.append(s.session_id)
            filter=dict(session_id=(' in ',session_ids))

        ConditionSetInstance=None

        for conditionVarName, conditionVarComparitor in filter.iteritems():
            avComparison, value = conditionVarComparitor

            cv_group=self.hdfFile.root.data_collection.condition_variables
            cvrows=[]
            ecv="EXP_CV_%d"%(self._experimentID,)
            if ecv in cv_group._v_leaves:
                ecvTable=cv_group._v_leaves[ecv]

                if ConditionSetInstance is None:
                    colnam=ecvTable.colnames
                    ConditionSetInstance = namedtuple('ConditionSetInstance', colnam)

                cvrows.extend([ConditionSetInstance(*r[:]) for r in ecvTable if all([eval("{0} {1} {2}".format(r[conditionVarName],conditionVarComparitor[0],conditionVarComparitor[1])) for conditionVarName, conditionVarComparitor in filter.iteritems()])])
        return cvrows
     
    def getValuesForVariables(self,cv, value, cvNames):
        if isinstance(value,(list,tuple)):
            resolvedValues=[]
            for v in value:
                if isinstance(value,basestring) and value.startswith('@') and value.endswith('@'):
                    value=value[1:-1]
                    if value in cvNames:
                        resolvedValues.append(getattr(cv,v))
                    else:
                        raise ExperimentDataAccessException("getEventAttributeValues: {0} is not a valid attribute name in {1}".format(v,cvNames))
                        return None
                elif isinstance(value,basestring):
                    resolvedValues.append(value)
            return resolvedValues
        elif isinstance(value,basestring) and value.startswith('@') and value.endswith('@'):
            value=value[1:-1]
            if value in cvNames:
                return getattr(cv,value)
            else:                
                raise ExperimentDataAccessException("getEventAttributeValues: {0} is not a valid attribute name in {1}".format(value,cvNames))
                return None
        else:
            raise ExperimentDataAccessException("Unhandled value type !: {0} is not a valid type for value {1}".format(type(value),value))



            
    def getEventAttributeValues(self,event_type_id,event_attribute_names,filter_id=None, conditionVariablesFilter=None, startConditions=None,endConditions=None):
        if self.hdfFile:
            klassTables=self.hdfFile.root.class_table_mapping

            deviceEventTable=None

            result=[row.fetch_all_fields() for row in klassTables.where('(class_id == %d) & (class_type_id == 1)'%(event_type_id))]
            if len(result) is not 1:
                raise ExperimentDataAccessException("event_type_id passed to getEventAttribute should only return one row from CLASS_MAPPINGS.")
            tablePathString=result[0][3]
            deviceEventTable=self.hdfFile.getNode(tablePathString)
  
            for ename in event_attribute_names:
                if ename not in deviceEventTable.colnames:
                    raise ExperimentDataAccessException("getEventAttribute: %s does not have a column named %s"%(deviceEventTable.title,event_attribute_names))
                    return None
          
            resultSetList=[]            

            csier=list(event_attribute_names)
            csier.append('query_string')
            csier.append('condition_set')            
            EventAttributeResults=namedtuple('EventAttributeResults',csier)
            
            if deviceEventTable is not None:
                if not isinstance(event_attribute_names, (list,tuple)):
                    event_attribute_names=[event_attribute_names,]

                filteredConditionVariableList=None
                if conditionVariablesFilter is None:
                    filteredConditionVariableList= self.getConditionVariables()
                else:
                    filteredConditionVariableList=self.getConditionVariables(conditionVariablesFilter)
                
                cvNames=self.getConditionVariableNames()

                # no futher where clause building needed; get reseults and return
                if startConditions is None and endConditions is None:
                    for cv in filteredConditionVariableList:    
                
                        wclause="( experiment_id == {0} ) & ( session_id == {1} )".format(self._experimentID,cv.session_id)
        
                        wclause+=" & ( type == {0} ) ".format(event_type_id)
        
                        if filter_id is not None:
                            wclause += "& ( filter_id == {0} ) ".format(filter_id)

                        resultSetList.append([])

                        for ename in event_attribute_names:
                            resultSetList[-1].append(deviceEventTable.readWhere(wclause, field=ename))
                        resultSetList[-1].append(wclause)
                        resultSetList[-1].append(cv)

                        eventAttributeResults=EventAttributeResults(*resultSetList[-1])
                        resultSetList[-1]=eventAttributeResults
                        
                    return resultSetList

                #start or end conditions exist....
                for cv in filteredConditionVariableList:    
                    resultSetList.append([])

                    wclause="( experiment_id == {0} ) & ( session_id == {1} )".format(self._experimentID,cv.session_id)
    
                    wclause+=" & ( type == {0} ) ".format(event_type_id)
    
                    if filter_id is not None:
                        wclause += "& ( filter_id == {0} ) ".format(filter_id)
                        
                    # start Conditions need to be added to where clause
                    if startConditions is not None:
                        wclause += "& ("
                        for conditionAttributeName, conditionAttributeComparitor in startConditions.iteritems():
                            avComparison,value=conditionAttributeComparitor
                            value=self.getValuesForVariables(cv,value, cvNames)                                    
                            wclause += " ( {0} {1} {2} ) & ".format(conditionAttributeName,avComparison,value)
                        wclause=wclause[:-3]
                        wclause+=" ) "
    
                    # end Conditions need to be added to where clause
                    if endConditions is not None:
                        wclause += " & ("
                        for conditionAttributeName, conditionAttributeComparitor in endConditions.iteritems():
                            avComparison,value=conditionAttributeComparitor
                            value=self.getValuesForVariables(cv,value, cvNames)                                                                        
                            wclause += " ( {0} {1} {2} ) & ".format(conditionAttributeName,avComparison,value)
                        wclause=wclause[:-3]
                        wclause+=" ) "

                    for ename in event_attribute_names:
                        resultSetList[-1].append(deviceEventTable.readWhere(wclause, field=ename))
                    resultSetList[-1].append(wclause)
                    resultSetList[-1].append(cv)

                    eventAttributeResults=EventAttributeResults(*resultSetList[-1])
                    resultSetList[-1]=eventAttributeResults
                    
                return resultSetList

            return None

    def close(self):
        closeHubFile(self.hdfFile)

        
        self.experimentCodes=None
        self.hdfFilePath=None
        self.hdfFileName=None
        self.mode=None
        self.hdfFile=None
    
    def __del__(self):
        try:
            self.close()
        except:
            pass
        
class ExperimentDataAccessException(Exception):
    pass