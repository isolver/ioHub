import numpy as N
from collections import namedtuple

#-----------------------------------------------------------------------

_CURRENT_TRIAL_INDEX=-1

ORD_B=ord('b')
ORD_R=ord('r')
#-----------------------------------------------------------------------

TRIAL_BORDER_MSG_TOKEN = ("displayFixationPoint : FP1 :",len("displayFixationPoint : FP1 :"))

TARGET2_DISPLAY_TIME=(") : [0, 0, 0, 255] : FP2_INITIAL_DISPLAY",len(") : [0, 0, 0, 255] : FP2_INITIAL_DISPLAY"))

TARGET_COLOR_TOKENS=(('[0, 0, 255, 255] : FP2_COLOR_CHANGE_START','b'),
                     ('[255, 0, 0, 255] : FP2_COLOR_CHANGE_START','r'))

TARGET_COLOR_CHANGE_END= "] : FP2_COLOR_CHANGE_END"

RESPONSE_TOKENS=(("b') : [0, 0, 0, 255]",len("b') : [0, 0, 0, 255]")),
                ("r') : [0, 0, 0, 255]",len("r') : [0, 0, 0, 255]")))

#-----------------------------------------------------------------------

def e2n(fname):
    samples, trials = createDataPointLists()
                         
    myrecarray = parseEyeLinkAscii(fname,trials,samples)
    #print '=================================='
    #print "Trial Count: ", len(trials.trial_id.values)
    #print "Sample Count: ", len(samples.trial_id.values)
    #print _CURRENT_TRIAL_INDEX
    #print '----------------------------------'
    reportMissingDataColumns(trials)
    reportMissingDataColumns(samples)
    trials_numpy=convertNamedTupleColumnsToNumPyTypes(trials)
    samples_numpy=convertNamedTupleColumnsToNumPyTypes(samples)
    #print '=================================='
    #print "Trial Count: ", len(trials_numpy.trial_id.values),len(trials.trial_id.values)
    #print "Sample Count: ", len(samples_numpy.trial_id.values),len(samples.trial_id.values)
    #print trials_numpy
    #print '----------------------------------'
    return trials_numpy, samples_numpy

#-----------------------------------------------------------------------

def createDataPointLists():
    DataPointList = namedtuple('DataPointList', 'label numpyType values calculateValue')

    sample_trial_id = DataPointList('trial_id','uint16',[],None)
    edf_time = DataPointList('edf_time','uint32',[],None)
    gaze_x = DataPointList('gaze_x','float32',[],None)
    gaze_y = DataPointList('gaze_y','float32',[],None)
    pupil_size= DataPointList('pupil_size', 'uint16',[],None)
    ppd_x = DataPointList('ppd_x', 'float16', [],None)
    ppd_y = DataPointList('ppd_y', 'float16', [],None)
    sample_flags = DataPointList('sample_flags', 'uint8', [],None)

    trial_id = DataPointList('trial_id','uint16',[],None)
    trial_start_time = DataPointList('trial_start_time','uint32',[],None)
    trial_end_time = DataPointList('trial_end_time','uint32',[],None)
    trial_duration = DataPointList('trial_duration','uint16',[],None)
    first_sample_index = DataPointList('first_sample_index','uint32',[],None)
    last_sample_index = DataPointList('last_sample_index','uint32',[],None)
    target1_onset = DataPointList('target1_onset','uint32',[],None)
    target1_x = DataPointList('target1_x','int16',[],None)
    target1_y = DataPointList('target1_y','int16',[],None)
    target2_onset = DataPointList('target2_onset','uint32',[],None)
    target2_x = DataPointList('target2_x','int16',[],None)
    target2_y = DataPointList('target2_y','int16',[],None)
    target2_change_onset = DataPointList('target2_change_onset','uint32',[],None)
    target2_change_off = DataPointList('target2_change_off','uint32',[],None)
    response = DataPointList('response','uint8',[],None)
    correct_response = DataPointList('correct_response','uint8',[],None)
    correct = DataPointList('correct','bool',[],None)
    keypress_msg_time = DataPointList('keypress_msg_time','uint32',[],None)
    
   
    SampleData=namedtuple("SampleData","trial_id edf_time gaze_x gaze_y \
                        pupil_size ppd_x ppd_y sample_flags")
                      
    samples=SampleData(sample_trial_id,edf_time,gaze_x,gaze_y,pupil_size, ppd_x, \
                    ppd_y,sample_flags)

    TrialData=namedtuple("TrialData","trial_id trial_start_time \
                        trial_end_time trial_duration first_sample_index\
                        last_sample_index target1_onset target1_x \
                        target1_y target2_onset target2_x target2_y \
                        target2_change_onset target2_change_off \
                        response correct_response correct keypress_msg_time")

    trials=TrialData(trial_id,trial_start_time,
                        trial_end_time,trial_duration,first_sample_index,
                        last_sample_index,target1_onset,target1_x,
                        target1_y,target2_onset,target2_x,target2_y,
                        target2_change_onset,target2_change_off,
                        response,correct_response,correct, keypress_msg_time)

    return samples, trials

#-----------------------------------------------------------------------

def parseEyeLinkAscii(eyelinkAsiiFile, trialsNamedTuple, samplesNamedTuple):
    """ Parses a monocular eyelink ascii file ( edf2asc - res my.edf my.asc ) 
    into a namedtuple respresenting trial level data, and another 
    representating the sample columns from the ascii file prepended
    with a trial_id colunm.
    """
    global _CURRENT_TRIAL_INDEX
    _CURRENT_TRIAL_INDEX=-1

    for line in open(eyelinkAsiiFile, 'r'):
        if _CURRENT_TRIAL_INDEX>-1 and line[0:3].isdigit():
            processSample(line,trialsNamedTuple,samplesNamedTuple)
        elif line[0:3]=='MSG':
            processMessage(line,trialsNamedTuple,samplesNamedTuple)
    finalizeCurrentTrial(trialsNamedTuple,samplesNamedTuple) 

     
def processSample(line,trialsNamedTuple, samplesNamedTuple):
    global _CURRENT_TRIAL_INDEX
    samplesNamedTuple.trial_id.values.append(_CURRENT_TRIAL_INDEX)
    
    fields = line.strip().split()
    for f,a1 in itertools.izip(fields,samplesNamedTuple[1:]):
        a1.values.append(tryeval(f))
        
     
        
def processMessage(line, trialsNamedTuple,samplesNamedTuple):
    fields = line.strip().split('\t')
    temp=fields[-1]
    if temp.startswith(TRIAL_BORDER_MSG_TOKEN[0]):
        if _CURRENT_TRIAL_INDEX>=0:
            finalizeCurrentTrial(trialsNamedTuple,samplesNamedTuple)
        startNextTrial(fields,trialsNamedTuple,samplesNamedTuple)
        return

    if temp.endswith(TARGET2_DISPLAY_TIME[0]):
        trialsNamedTuple.target2_onset.values.append(int(fields[1].split()[0]))
        temp=temp[:-TARGET2_DISPLAY_TIME[1]].split()
        trialsNamedTuple.target2_x.values.append(float(temp[-2][1:-1]))
        trialsNamedTuple.target2_y.values.append(float(temp[-1]))
        return
        
    if temp.endswith(TARGET_COLOR_TOKENS[0][0]):
        trialsNamedTuple.correct_response.values.append(ORD_B)
        trialsNamedTuple.target2_change_onset.values.append(int(fields[1].split()[0]))
        return
    
    if temp.endswith(TARGET_COLOR_TOKENS[1][0]):
        trialsNamedTuple.correct_response.values.append(ORD_R)
        trialsNamedTuple.target2_change_onset.values.append(int(fields[1].split()[0]))
        return
        
    if temp.endswith(TARGET_COLOR_CHANGE_END):
        v=int(fields[1].split()[0])
        trialsNamedTuple.target2_change_off.values.append(v)
        return

    if temp.endswith(RESPONSE_TOKENS[0][0]): # b
        trialsNamedTuple.response.values.append(ORD_B)
        trialsNamedTuple.keypress_msg_time.values.append(int(fields[1].split()[0]))
        return
    
    if temp.endswith(RESPONSE_TOKENS[1][0]): # r
        trialsNamedTuple.response.values.append(ORD_R)
        trialsNamedTuple.keypress_msg_time.values.append(int(fields[1].split()[0]))
        return

def startNextTrial(fields,trialsNamedTuple,samplesNamedTuple):
    global _CURRENT_TRIAL_INDEX
    stime,msgSentTime=fields[1][:-2].split()
    _CURRENT_TRIAL_INDEX+=1            
    trialsNamedTuple.trial_id.values.append(_CURRENT_TRIAL_INDEX)
    trialsNamedTuple.trial_start_time.values.append(int(stime))
    trialsNamedTuple.target1_onset.values.append(int(stime))
    
    fields2=fields[-1][TRIAL_BORDER_MSG_TOKEN[1]:].split()
    trialsNamedTuple.target1_x.values.append(float(fields2[0][1:-2]))
    trialsNamedTuple.target1_y.values.append(float(fields2[1][:-2]))
    
    trialsNamedTuple.first_sample_index.values.append(len(samplesNamedTuple.edf_time.values))


def finalizeCurrentTrial(trialsNamedTuple,samplesNamedTuple):
    trialsNamedTuple.trial_end_time.values.append(samplesNamedTuple.edf_time.values[-1])
    trialsNamedTuple.trial_duration.values.append(trialsNamedTuple.trial_end_time.values[-1]-trialsNamedTuple.trial_start_time.values[-1])
    r=trialsNamedTuple.correct_response.values[-1] == trialsNamedTuple.response.values[-1]
    trialsNamedTuple.correct.values.append(r)

    if len(trialsNamedTuple.last_sample_index.values)==samplesNamedTuple.trial_id.values[-1]:
        trialsNamedTuple.last_sample_index.values.append(len(samplesNamedTuple.trial_id.values)-1)
 #-----------------------------------------------------------------------

def reportMissingDataColumns(namedTuple):
    for a in namedTuple:
        if len(a.values) == 0:
            print "Column [ %s ] has no data."%(a.label,)
        else:
            print "Column [ %s ] has %d rows."%(a.label,len(a.values))

def convertNamedTupleColumnsToNumPyTypes(namedTuple):
    cast = N.cast
    dtype=N.dtype([a[0:2] for a in namedTuple])
    numpy_namedTuple_fields={}
    for i,a in enumerate(namedTuple):
         numpy_namedTuple_fields[a.label]=a._replace(values=cast[dtype[i]](a.values))
    return namedTuple._replace(**numpy_namedTuple_fields)
    
## >>>
# from http://stackoverflow.com/questions/2859674/converting-python-list-of-strings-to-their-type
# modified by Sol Simpson, May 25th, 2012
 
import ast,itertools
cvalues=[1,2,4,8,16,32,64,128]
def tryeval(val):
  try:
    return ast.literal_eval(val)
  except:
    val=str(val)
    r=0
    for c,i in itertools.izip(cvalues,xrange(len(val))):
        if val[i] is not '.': r+=c
    return r
#
## <<<  
        
#-----------------------------------------------------------------------

if __name__=="__main__":
    e2n()
