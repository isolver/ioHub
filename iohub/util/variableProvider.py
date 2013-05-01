__author__ = 'Sol'

import numpy as np
import sys
import json
from psychopy.clock import monotonicClock
from . import OrderedDict,  printExceptionDetailsToStdErr, print2err
getTime=monotonicClock.getTime 
#### Experiment Variable (IV and DV) Condition Management
#
class ConditionSetProvider(object):
    def __init__(self, conditionSetArray, randomize=False):        
        non_empty_count=0
        empty_sets=[]
        for i,c in enumerate(conditionSetArray):
            if type(c)==np.void or c.getCount()!=0:
                non_empty_count+=1
            else:
                empty_sets.append(i)
        
        for i in empty_sets:
            conditionSetArray.pop(i)

        self._conditionSets=conditionSetArray
        self.conditionSetCount=non_empty_count
        self.currentConditionSet=None
        self.currentConditionSetIndex=-1
        self.currentConditionSetIteration=0
        self.randomize=randomize

        self._provideInOrder=range(self.conditionSetCount)
        if self.randomize is True:
            np.random.shuffle(self._provideInOrder)

    def getNextConditionSet(self):
        for i in self._provideInOrder:
            self.currentConditionSetIndex=i
            self.currentConditionSetIteration+=1
            conditionSet=self._conditionSets[i]
            self.currentConditionSet=conditionSet
            yield conditionSet

    def getCurrentConditionSet(self):
        return self.currentConditionSet

    def getConditionSetCount(self):
        return self.conditionSetCount

    def getCount(self):
        return self.conditionSetCount

    def getCurrentConditionSetIndex(self):
        return self.currentConditionSetIndex

    def getCurrentConditionSetIteration(self):
        return self.currentConditionSetIteration

    def getRandomize(self):
        return self.randomize

    def getIterationOrder(self):
        return self._provideInOrder

class BlockSetProvider(ConditionSetProvider):
    def __init__(self, blockSetArray, randomize):
        ConditionSetProvider.__init__(self, blockSetArray, randomize)

class TrialSetProvider(ConditionSetProvider):
    def __init__(self, trialSetArray, randomize):
        ConditionSetProvider.__init__(self, trialSetArray, randomize)

class ExperimentVariableProvider(object):
    _randomGeneratorSeed=None
    def __init__(self,fileNameWithPath,blockingVariableLabel,practiceBlockValues=None,randomizeBlocks=False,randomizeTrials=True,randSeed=None):
        self.fileNameWithPath=fileNameWithPath
        self.blockingVariableLabel=blockingVariableLabel
        self.practiceBlockValues=practiceBlockValues

        self.randomizeBlocks=randomizeBlocks
        self.randomizeTrials=randomizeTrials

        if ExperimentVariableProvider._randomGeneratorSeed is None:
            if randSeed is None:
                randSeed=int(getTime()*1000.0)
            ExperimentVariableProvider._randomGeneratorSeed = randSeed
            np.random.seed(ExperimentVariableProvider._randomGeneratorSeed)

        self.variableNames=[]
        self.totalColumnCount=None
        self.totalRowCount=None
        self._numpyConditionVariableDescriptor=None
        self.data=None

        self.practiceBlocks=BlockSetProvider([TrialSetProvider([],self.randomizeTrials),],self.randomizeBlocks)
        self.experimentBlocks=BlockSetProvider([TrialSetProvider([],self.randomizeTrials),],self.randomizeBlocks)

        self._readConditionVariableFile()


        # not implemented yet
        #self.recycleCount={} # dict of trialID: recyledTimes

    def getData(self):
        return self.data

    def getExperimentBlocks(self):
        """
        Blocks are simply returned as a numpy ndarray of ndarrays. Blocks are grouped based on the
        value of the blocking variable column. The top level is the block set,
        the second level within each block is a ndarray of trial condition variable. Each trial is an nd array
        of the condition variable values for that iteration.
        Supported variable types are:
            
             * unicode
             * color ( a string in an xls file of format [r,g,b,a] or (r,g,b,a). a is optional. It is converted to a
             * ndarray for the cell [(r,'u8'),(g,'u8'),(b,'u8'),(a,'u8')]
             * int
             * float
        """
        return self.experimentBlocks

    def getPracticeBlocks(self):
        return self.practiceBlocks

    def _readConditionVariableFile(self):
        import xlrd
        workbook = xlrd.open_workbook(self.fileNameWithPath)
        worksheet = workbook.sheet_by_index(0)

        self.variableNames=['ROW_ID',]
        self.variableNames.extend(worksheet.row_values(0))
        self.variableNames=tuple(self.variableNames)

        self.totalColumnCount=len(self.variableNames)
        self.totalRowCount=worksheet.nrows

        np_dtype=[]

        # returns true if number is a full integer (i.e. 3.0 == FALSE, 3 == TRUE)
        def is_integer(n):
            return (float(n)-int(n)).as_integer_ratio()[1] == 1

        #Assume 1st row represents type for all rows
        row_types=[2,]
        row_types.extend(worksheet.row_types(1))

        row_values=[0,]
        row_values.extend(worksheet.row_values(1))

        # create a 2D numpy ndarray representing spreadsheet data
        # we add one column to start of table, 'ROW_ID'
        color_column_indexes=[]
        for i,cname in enumerate(self.variableNames):
            cname=str(cname)
            rtype=row_types[i]
            rvalue=row_values[i]
            if rtype==1:
                # need to check if string should be considered a color or a string
                if (rvalue[0] in ('[','(')) and (rvalue[-1] in (']',')')) and (rvalue.count(',') in (2,3)):
                    try:
                        rgbList=json.loads(rvalue)
                        if len(rgbList) == 3:
                            np_dtype.append((cname,[('r','u1'),('g','u1'),('b','u1')]))
                        else:
                            np_dtype.append((cname,[('r','u1'),('g','u1'),('b','u1'),('a','u1')]))
                        color_column_indexes.append(i)
                    except:
                        print2err("*** ERROR HANDLING COLOR COLUMN: ",cname,". Setting to 64 char string.")
                        printExceptionDetailsToStdErr()
                        np_dtype.append((cname,'S',64))
                else:
                    np_dtype.append((cname,'S',64))
            elif rtype==2:
                # need to check between floats and ints
                if is_integer(rvalue):
                    np_dtype.append((cname,'i4'))
                else:
                    np_dtype.append((cname,'f4'))
            else:
                print2err("*** ERROR HANDLING COLUMN: ",cname," bad type: ",rtype,". Setting to 8 bit unsigned int")
                np_dtype.append((cname,'u1'))

        temp_rows=[]
        for r in xrange(1,worksheet.nrows):
            rowValues=[r,]
            rowValues.extend(worksheet.row_values(r))
            for i in color_column_indexes:
                rowValues[i]=tuple(json.loads(rowValues[i]))
            temp_rows.append(tuple(rowValues))

        self._numpyConditionVariableDescriptor=np_dtype

        self.data=np.array(temp_rows,dtype=np_dtype)

        # break trial variable arrays into blocks.
        tempBlockDict=OrderedDict()
        if self.blockingVariableLabel in self.variableNames:
            u=np.unique(self.data[:][self.blockingVariableLabel])
            for v in u:
                tempBlockDict[v]=self.data[self.data[:][self.blockingVariableLabel] == v]

        if self.practiceBlockValues is not None:
            if isinstance(self.practiceBlockValues,(str,unicode)):
                self.practiceBlockValues=[self.practiceBlockValues,]


            blockList=[]
            for pbn in self.practiceBlockValues:
                if pbn in tempBlockDict.keys():
                    blockList.append(TrialSetProvider(tempBlockDict[pbn],self.randomizeTrials))
                    del tempBlockDict[pbn]
            self.practiceBlocks=BlockSetProvider(blockList, False)


        blockList=[]
        for pbv in tempBlockDict.values():
            blockList.append(TrialSetProvider(pbv,self.randomizeTrials))
        self.experimentBlocks=BlockSetProvider(blockList,self.randomizeBlocks)

        tempBlockDict.clear()
        del tempBlockDict

    def recycleTrial(self):
        # not implemented
        pass
