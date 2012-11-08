"""
ioHub
.. file: ioHub/examples/sequentialFixationTask/experimentResources.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: ioHub Team
"""


import ioHub
from ioHub.experiment import psychopyVisual, ScreenState

import json
from collections import OrderedDict
import numpy as np

from shapely.geometry import Point

class TargetScreen(ScreenState):
    TARGET_OUTER_RADIUS=15
    TARGET_INNER_RADIUS=5
    TARGET_OUTER_COLOR=[255,255,255]
    TARGET_INNER_COLOR=[255,255,255]
    WITHIN_AOI_SAMPLE_COUNT_THRESHOLD=5
    def __init__(self,experimentRuntime, deviceEventTriggers=None, timeout=None):
        ScreenState.__init__(self,experimentRuntime, deviceEventTriggers, timeout)
        self.stim['OUTER_POINT']=psychopyVisual.Circle(self.window(),radius=(self.TARGET_OUTER_RADIUS,self.TARGET_OUTER_RADIUS),lineWidth=0, lineColor=None, lineColorSpace='rgb255', name='FP_OUTER', opacity=1.0, interpolate=False, units='pix',pos=(0,0))
        self.stimNames.append('OUTER_POINT')
        self.stim['OUTER_POINT'].setFillColor(self.TARGET_OUTER_COLOR,'rgb255')

        self.stim['INNER_POINT']=psychopyVisual.Circle(self.window(),radius=(self.TARGET_INNER_RADIUS,self.TARGET_INNER_RADIUS),lineWidth=0, lineColor=None, lineColorSpace='rgb255', name='FP_INNER', opacity=1.0, interpolate=False, units='pix', pos=(0,0))
        self.stimNames.append('INNER_POINT')
        self.stim['INNER_POINT'].setFillColor(self.TARGET_INNER_COLOR,'rgb255')

        self._showDynamicStim=False
        self.dynamicStimPositionFuncPtr=None
        self.stim['DYNAMIC_STIM']=psychopyVisual.GratingStim(self.window(),tex=None, mask="gauss", pos=[0,0],size=experimentRuntime.devices.display.getPPD(),color='purple',opacity=0.0)
        self.stimNames.append('DYNAMIC_STIM')
        
        self.nextAreaOfInterest=None
        self.aoiTriggeredTime=None
        self.aoiTriggeredID=None

    def setTargetOuterColor(self,rgbColor):
        self.stim['OUTER_POINT'].setFillColor(rgbColor,'rgb255')
        self.dirty=True

    def setTargetInnerColor(self,rgbColor):
        self.stim['INNER_POINT'].setFillColor(rgbColor,'rgb255')
        self.dirty=True

    def setTargetOuterSize(self,r):
        self.stim['OUTER_POINT'].setRadius(r)
        self.dirty=True

    def setTargetInnerSize(self,r):
        self.stim['INNER_POINT'].setRadius(r)
        self.dirty=True

    def setTargetPosition(self,pos):
        self.stim['OUTER_POINT'].setPos(pos)
        self.stim['INNER_POINT'].setPos(pos)
        self.dirty=True
        self.aoiTriggeredTime=None
        self.aoiTriggeredID=None
        self.withinAOIcount=0
        self.aoiBestGaze=None
        self._mindist=100000.0
        
    def toggleDynamicStimVisibility(self,flipTime,stateDuration,event):
        self._showDynamicStim=not self._showDynamicStim
        if self._showDynamicStim is True:
            self.stim['DYNAMIC_STIM'].setOpacity(1.0)
        else:
            self.stim['DYNAMIC_STIM'].setOpacity(0.0)
        self.flip()
        self.dirty=True
        return False

    def setDynamicStimPosition(self,flipTime,stateDuration,event):
        if self.dynamicStimPositionFuncPtr:
            x,y=self.dynamicStimPositionFuncPtr()
            
            if self.nextAreaOfInterest:
                p=Point(x,y)
                if self.nextAreaOfInterest.contains(p):                         
                    self.withinAOIcount+=1
                    if self.withinAOIcount>=self.WITHIN_AOI_SAMPLE_COUNT_THRESHOLD:
                        if self.aoiTriggeredID is None:                        
                            self.aoiTriggeredTime=event['hub_time']
                            self.aoiTriggeredID=event['event_id']
                            cdist=self.nextAreaOfInterest.centroid.distance(p)
                            if cdist<self._mindist:
                                self._mindist=cdist
                                self.aoiBestGaze=x,y
                else:
                    self.withinAOIcount=0
                del p
                    
            if self._showDynamicStim is True:
                self.stim['DYNAMIC_STIM'].setPos((x,y))
                self.dirty=True
                self.flip()
        return False

    def flip(self, text=''):
        if text is not None:
            text="TARGET_SCREEN SYNC: [%s] [%s] "%(str(self.stim['OUTER_POINT'].pos),text)
        return ScreenState.flip(self,text)

#### Experiment Variable (IV and DV) Condition Management
class ConditionSetProvider(object):
    def __init__(self, conditionSetArray, randomize=False):
        self._conditionSets=conditionSetArray
        self.conditionSetCount=len(conditionSetArray)
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
                randSeed=int(ioHub.highPrecisionTimer()*1000.0)
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
             - unicode
             - color ( a string in an xls file of format [r,g,b,a] or (r,g,b,a). a is optional. It is converted to a
             - ndarray for the cell [(r,'u8'),(g,'u8'),(b,'u8'),(a,'u8')]
             - int
             - float
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
                        ioHub.print2err("*** ERROR HANDLING COLOR COLUMN: ",cname)
                        ioHub.printExceptionDetailsToStdErr()
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
                ioHub.print2err("*** ERROR HANDLING COLUMN: ",cname," bad type: ",rtype)
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


def getAutoGeneratedTargetPositions(pixel_width,pixel_height,width_scalar=1.0, 
                                    height_scalar=1.0, horiz_points=7, vert_points=7):
    swidth=int(pixel_width*width_scalar)
    sheight=int(pixel_height*height_scalar)
    hstep=int(swidth/(horiz_points+1))
    vstep=int(sheight/(vert_points+1))
    hsteps=np.arange(hstep,swidth-hstep+1,hstep)
    vsteps=np.arange(vstep,sheight-vstep+1,vstep)
    # center 0 on screen center
    hpoints = hsteps-int(swidth/2)
    vpoints = vsteps-int(sheight/2)

    # create horiz_points X vert_points X 2 array of all pixel positions (XY)
    # 0,0 is center of screen
    X, Y = np.meshgrid(hpoints, vpoints)
    XY=np.vstack(([X.T], [Y.T])).T

    # convert it to a 2D array, horiz_points*vert_points,2
    POINTS=XY.reshape(horiz_points*vert_points,2)
    
    return POINTS


