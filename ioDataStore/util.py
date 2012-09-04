import tables
from tables import *
import os

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
    def __init__(self, hdfFilePath, hdfFileName, experimentCodes,mode='r'):
        if isinstance(str,experimentCodes) or isinstance(unicode,experimentCodes):
            self.experimentCodes=[experimentCodes,]
        else:
            self.experimentCodes=experimentCodes
        self.hdfFilePath=hdfFilePath
        self.hdfFileName=hdfFileName
        self.mode=mode
        self.hdfFile=None
        self._tables={}
        try:
            self.hdfFile=openHubFile(hdfFilePath,hdfFileName,mode)
            self._tables['EXPERIMENT_METADATA']=self.hdfFile.root.data_collection.experiment_meta_data
            self._tables['SESSION_METADATA']=self.hdfFile.root.data_collection.session_meta_data
            
        except Exception as e:
            raise ExperimentDataAccessException(e)
    
    def printHubFileMetaData(self):
        if self.hdfFile:
            printHubFileMetaData(self.hdfFile)

    def printHubFileStructure(self):
        if self.hdfFile:
            printHubFileStructure(self.hdfFile)
    
    def getExperimentDetails(self):
        if self.hdfFile:
            
            experimentrows=[]
            exptable=self._tables['EXPERIMENT_METADATA']
            if self.experimentCodes:
                for code in self.experimentCodes:
                    wherecluase='code = "%s"'%(code,)
                    experimentrows.append([row.fetch_all_fields() for row in exptable.where(whereclause)])
            else:
                experimentrows=[row.fetch_all_fields() for row in exptable]
            
            sesstable=self._tables['SESSION_METADATA']
            experimentSessionData=[]
            for exp in experimentrows:
                wherecluase='experiment_id = %d'%(exp[0],)
                sessionrows=[row.fetch_all_fields() for row in sesstable.where(whereclause)]
                experimentSessionData.append((exp,sessionrows))
            
            return experimentSessionData
          
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