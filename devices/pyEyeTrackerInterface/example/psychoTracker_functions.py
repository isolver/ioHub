from __future__ import division

# author and version are used in the demo, in the way you might in your experiment.
# They expected to be at the top of the script that calls RunTimeInfo()), with a string literal assigned to them (no variables).
__author__ = """COGAIN ET Data Quality Standards Implementation Team""" ## double-quotes will be silently removed, single quotes will be left, eg, O'Connor
__version__ = "v0.1.a#'''" ## in-line comments are ignored, but comment characters within strings are retained

import psychopy
from psychopy import visual
from psychopy import core,  gui, data, info, event ,monitors
from numpy import random
import pyeyetracker as ET
import datetime
import time
import os, shutil

# a clock that returns the high res timer as msec.usec instead of sec.msecusec
class MsecClock(core.Clock):
    def __init__(self):
        core.Clock.__init__(self)

    def getTime(self):
        return core.Clock.getTime(self)*1000.0

# a class that only exists to hold a whole whack of glocal like variables. 
# having then in a class means you just need to make the class declared and instantiated
# are the module level and it is accessable everywhere.
class ExperimentConstants(object):
    # clock to use everywhere for local / experiment PC time
    GLOBAL_CLOCK=MsecClock()
    
    # save a couple .'s by holding a direct refernce to the actual class method
    # that gives you msec.usec time
    GC_FUNC=None

    SCREEN_RESOLUTION=None # w,h in pix
    SCREEN_AREA=None #l,t,r,b
    MONITOR_DIMENTIONS=None #mm width, mm height 
    DEFAULT_SCREEN_DISTANCE=None #mm_dicstance or mm_screan_top, mm_screen_bottom
    

    # the eye tracker, if being used.
    TRACKER=None
    
    # the window object. A window is full screen for the experiments ad borderless.
    WINDOW=None
    
    # the monitor you want the window to use. If you have 2 or more monitors, you can specify
    # which to use. Note that this is OK for testing, but is not suggested for actual data collection. 
    # Only 1 monitor should be connected to the video card, otherwise timeing maybe negatively impacted. 
    MONITOR=None
    
    # the path and name of the psychopy monitor calibration filemode
    MONITOR_CAL_FILE=None
    
    # a mouse object, used to get mouse button events.
    MOUSE=None
    
    #general default settings for the prebuilt cans stimuli,
    STIMULUS_SETTINGS=None
    
    # SS is just a shorthand for STIMULUS_SETTINGS
    SS=None
    
    PREBUILT_STIM={}
    PPD=None
    USER_TERMINATE_EXPERIMENT=False
    MAIN_LOG=None
    BLOCKING_COLUMN=u"BLOCK_LABEL"
    N_BLOCKS=0
    BLOCKS={}
    BLOCK_LABEL_LIST=[]
    RANDOMIZE_BLOCKS=False
    PRACTICE_BLOCK=None
    IV_HEADER=None
    RANDOMIZE_TRIALS=True
    
    EYE_TRACKER_INFO={}
    PARTICIPANT_INFO={}
    ENVIRONMENT_INFO={}
    TASK_INFO={}
    
    EXP_XINFO = {"exp_name":'COGAIN ET TEST',
                        "subject_id":"test",
                        "calibration_cm_distance":60,
                        "calibration_cm_width":50,
                        "calibration_cm_height":50/(16.0/9.0),
                        "calibration_width_unit_count":1920,
                        "calibration_height_unit_count":1080,
 #                       'sceen_area_coordinates':(-(1920/2),1080/2,1920/2,-(1080/2)), # l,t,r,b , so pixel 0,0 is screen center
                        "monitor_settings_file":'std1920x1080_50w_60d',
                        "date_run":str(datetime.datetime.utcnow())}
    CONDITION_FILE_DIR=None
    RESULTS_DIR=None
    CONDITIONS_FILE=None
    
    def __init__(self):
        if ExperimentConstants.STIMULUS_SETTINGS is not None:
            return 
        
        ExperimentConstants.GC_FUNC=ExperimentConstants.GLOBAL_CLOCK.getTime
       
        ExperimentConstants.SCREEN_RESOLUTION=(ExperimentConstants.EXP_XINFO["calibration_width_unit_count"],ExperimentConstants.EXP_XINFO["calibration_height_unit_count"])
        ExperimentConstants.SCREEN_AREA=(-(ExperimentConstants.SCREEN_RESOLUTION[0]/2),-(ExperimentConstants.SCREEN_RESOLUTION[1]/2),(ExperimentConstants.SCREEN_RESOLUTION[0]/2),(ExperimentConstants.SCREEN_RESOLUTION[1]/2))
        ExperimentConstants.MONITOR_DIMENTIONS=(ExperimentConstants.EXP_XINFO["calibration_cm_width"],ExperimentConstants.EXP_XINFO["calibration_cm_height"]) 
        ExperimentConstants.DEFAULT_SCREEN_DISTANCE=ExperimentConstants.EXP_XINFO["calibration_cm_distance"] #mm_dicstance or mm_screan_top, mm_screen_bottom
    
        # When creating an experiment, first define your window (& monitor):
        ExperimentConstants.MONITOR = monitors.Monitor(ExperimentConstants.EXP_XINFO["monitor_settings_file"])#fetch the most recent calib for this monitor
        ExperimentConstants.MONITOR.setDistance(ExperimentConstants.EXP_XINFO["calibration_cm_distance"])
        ExperimentConstants.MONITOR.setWidth(ExperimentConstants.EXP_XINFO["calibration_cm_width"])
        ExperimentConstants.MONITOR.setSizePix((ExperimentConstants.EXP_XINFO["calibration_width_unit_count"],ExperimentConstants.EXP_XINFO["calibration_height_unit_count"]))
        
        ExperimentConstants.STIMULUS_SETTINGS={}
        ExperimentConstants.STIMULUS_SETTINGS["SCREEN_BACKGROUND"]=(25,25,25)
        ExperimentConstants.STIMULUS_SETTINGS["FP1_OUTER_RADIUS"]=0.5
        ExperimentConstants.STIMULUS_SETTINGS["FP1_INNER_RADIUS"]=0.125
        ExperimentConstants.STIMULUS_SETTINGS["FP1_OUTER_FILL"]=(0,0,0,255)
        ExperimentConstants.STIMULUS_SETTINGS["FP1_INNER_FILL"]=(255,255,255)
        ExperimentConstants.STIMULUS_SETTINGS["FP1_POSITION"]=(0,0)
        ExperimentConstants.STIMULUS_SETTINGS["FP2_OUTER_RADIUS"]=0.5
        ExperimentConstants.STIMULUS_SETTINGS["FP2_INNER_RADIUS"]=0.125
        ExperimentConstants.STIMULUS_SETTINGS["FP2_OUTER_FILL"]=(0,0,0,255)
        ExperimentConstants.STIMULUS_SETTINGS["FP2_INNER_FILL"]=(255,255,255)
        ExperimentConstants.STIMULUS_SETTINGS["FP2_POSITION"]=(5,5)
        ExperimentConstants.SS= ExperimentConstants.STIMULUS_SETTINGS

        head,tail=os.path.split(__file__)
        ExperimentConstants.CONDITION_FILE_DIR=head+"\\condition_files"
        ExperimentConstants.RESULTS_DIR=os.path.join(head,"results")
        
        if not os.path.exists(ExperimentConstants.CONDITION_FILE_DIR):
             os.makedirs(ExperimentConstants.CONDITION_FILE_DIR)
        if not os.path.exists(ExperimentConstants.RESULTS_DIR):
             os.makedirs(ExperimentConstants.RESULTS_DIR)
             
             
    @classmethod
    def msecTime(cls):
        return ExperimentConstants.GC_FUNC()

EC = ExperimentConstants()

#-----------------------------------------------------------------------

from psychopy import logging
# change the default clock from a sec. msec to a msec.usec clock
# TODO: It seems that this causes issues with retrace detection  error
# reporting (psychopy now thinks everything is 1000x more msec than it is. ;)
# If that is the only issue, no biggie, but should post the question to see
# if there are others.
logging.setDefaultClock(ExperimentConstants.GLOBAL_CLOCK)

#-----------------------------------------------------------------------

def intializeTimerAndLogging(logFileName='logLastRun.log',loggingLevel=logging.INFO, overwrite=True):
    """
    intializeTimerAndLogging setting the experiment clock to use the high precision based timer (i.e. on Windows the one that calls the QPC functions). 
    The function also defines what logging  file to use for general logging to file ( 'logLastRun.log' ) and the minimum loggnig level that will get reported into this file.
    The defaults are logFileName='logLastRun.log',loggingLevel=logging.INFO, overwrite=True. overwrite indicates that each time the experiment is run, this file will be recreated.
    
    """
    fileMode='a' # append to existing log file if it exists
    if overwrite is True:
            fileMode='w' # create new log file if it exists
            
    logging.setDefaultClock(EC.GLOBAL_CLOCK)

    EC.MAIN_LOG=logging.LogFile(logFileName,
        filemode=fileMode,
        level=loggingLevel)
        
    logging.console.setLevel(logging.WARNING)

    ET.eyetracker.logging=logging

#-----------------------------------------------------------------------

def inializeGraphicsAndStim():
    
    
    pw,ph=EC.SCREEN_RESOLUTION
    
    EC.WINDOW = visual.Window(size=EC.SCREEN_RESOLUTION, fullscr=True, winType='pyglet', units='pix', \
    monitor=EC.MONITOR, allowGUI=False, waitBlanking=True)
    EC.WINDOW.setColor(EC.STIMULUS_SETTINGS["SCREEN_BACKGROUND"],'rgb255') # set color of 
    

    aw=psychopy.misc.pix2deg(pw, EC.MONITOR)
    ah=psychopy.misc.pix2deg(ph, EC.MONITOR)
    lstr="Monitor dimentions in degrees: %f\t%f"%(aw,ah)
    logging.info(lstr)

    aw=psychopy.misc.deg2pix(1.0, EC.MONITOR)
    ah=psychopy.misc.deg2pix(1.0, EC.MONITOR)
    EC.PPD=(aw,ah)
    lstr="PPD w : h: %.3f : %.3f"%EC.PPD
    logging.info(lstr)
    ## Create prebuilt stim
    
    #clear the front and back buffers
    EC.WINDOW.flip()
    EC.WINDOW.flip()

    EC.PREBUILT_STIM['BACKGROUND'] = visual.Rect(EC.WINDOW, EC.SCREEN_RESOLUTION[0],EC.SCREEN_RESOLUTION[1], units='pix')
    EC.PREBUILT_STIM['BACKGROUND'].setFillColor(EC.STIMULUS_SETTINGS["SCREEN_BACKGROUND"],'rgb255')
    EC.PREBUILT_STIM['BACKGROUND'].setLineColor(EC.STIMULUS_SETTINGS["SCREEN_BACKGROUND"],'rgb255')
    
    
    EC.PREBUILT_STIM['MESSAGE_TEXT'] = visual.TextStim(EC.WINDOW, text='Experiment Loading. Please wait...', name='MESSAGE_TEXT', units='pix')

    EC.PREBUILT_STIM['FP1'] = {'OUTER':visual.Circle(EC.WINDOW,pos=(0,0) , lineWidth=1.0,radius=(EC.STIMULUS_SETTINGS["FP1_OUTER_RADIUS"]*EC.PPD[0],EC.STIMULUS_SETTINGS["FP1_OUTER_RADIUS"]*EC.PPD[1]),edges=64,name='FP1_OUTER', units='pix'),
                                  'INNER':visual.Circle(EC.WINDOW,pos=(0,0),lineWidth=1.0, radius=(EC.STIMULUS_SETTINGS["FP1_INNER_RADIUS"]*EC.PPD[0],EC.STIMULUS_SETTINGS["FP1_INNER_RADIUS"]*EC.PPD[1]), edges=32, name='FP1_INNER',units='pix')
                                 }
    EC.PREBUILT_STIM['FP1']['OUTER'].setFillColor(EC.STIMULUS_SETTINGS["FP1_OUTER_FILL"],'rgb255')
    EC.PREBUILT_STIM['FP1']['OUTER'].setLineColor(EC.STIMULUS_SETTINGS["FP1_OUTER_FILL"],'rgb255')
    EC.PREBUILT_STIM['FP1']['INNER'].setFillColor(EC.STIMULUS_SETTINGS["FP1_INNER_FILL"],'rgb255')
    EC.PREBUILT_STIM['FP1']['INNER'].setLineColor(EC.STIMULUS_SETTINGS["FP1_INNER_FILL"],'rgb255')

    
    EC.PREBUILT_STIM['FP2'] = {'OUTER':visual.Circle(EC.WINDOW,pos=(0,0), lineWidth=0.125,radius=(EC.STIMULUS_SETTINGS["FP2_OUTER_RADIUS"]*EC.PPD[0],EC.STIMULUS_SETTINGS["FP2_OUTER_RADIUS"]*EC.PPD[1]),edges=64,name='FP2_OUTER', units='pix'),
                                  'INNER':visual.Circle(EC.WINDOW,pos=(0,0),lineWidth=0.125, radius=(EC.STIMULUS_SETTINGS["FP1_INNER_RADIUS"]*EC.PPD[0],EC.STIMULUS_SETTINGS["FP1_INNER_RADIUS"]*EC.PPD[1]), edges=32, name='FP2_INNER', units='pix')
                                 }
    EC.PREBUILT_STIM['FP2']['OUTER'].setFillColor(EC.STIMULUS_SETTINGS["FP2_OUTER_FILL"],'rgb255')
    EC.PREBUILT_STIM['FP2']['OUTER'].setLineColor(EC.STIMULUS_SETTINGS["FP2_OUTER_FILL"],'rgb255')
    EC.PREBUILT_STIM['FP2']['INNER'].setFillColor(EC.STIMULUS_SETTINGS["FP2_INNER_FILL"],'rgb255')
    EC.PREBUILT_STIM['FP2']['INNER'].setLineColor(EC.STIMULUS_SETTINGS["FP2_INNER_FILL"],'rgb255')

#-----------------------------------------------------------------------

def testSystemCapabilitiesAndStatus():
    # Then gather run-time info. All parameters are optional:
    runInfo = info.RunTimeInfo(
            # if you specify author and version here, it overrides the automatic detection of __author__ and __version__ in your script
            #author='<your name goes here, plus whatever you like, e.g., your lab or contact info>',
            #version="<your experiment version info>",
            win=EC.WINDOW,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
            refreshTest='True', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
            verbose=True, ## True means report on everything 
            userProcsDetailed=True,  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
            randomSeed='set:time', ## a way to record, and optionally set, a random seed of type str for making reproducible random sequences
                ## None -> default 
                ## 'time' will use experimentRuntime.epoch as the value for the seed, different value each time the script is run
                ##'set:time' --> seed value is set to experimentRuntime.epoch, and initialized: random.seed(info['randomSeed'])
                ##'set:42' --> set & initialize to str('42'), and will give the same sequence of random.random() for all runs of the script
            )
    for key in runInfo:
        lstr="RUN_INFO %s: %s"%(key,str(runInfo[key]))
        logging.info(lstr)
    
     #process condition file

    EC.WINDOW.flip()

#-----------------------------------------------------------------------
def openConditionVariableFile():
    selectedFile=openDialog=gui.fileOpenDlg(tryFilePath= ExperimentConstants.CONDITION_FILE_DIR,allowed='*.xlsx')
    if selectedFile is None:
        import sys
        sys.exit(1);
    return selectedFile[0]

#-----------------------------------------------------------------------

def inializeExperimentData():
    EC.MOUSE = event.Mouse(visible=False)
    
    dlg = gui.DlgFromDict(EC.EXP_XINFO, title=EC.EXP_XINFO['exp_name'], fixed=['date_run','exp_name'])
    if dlg.OK:
        pass #misc.toFile('lastParams.pickle', expInfo)#save params to file for next time
    else:
        core.quit()#the user hit cancel so exit                
    
    conditionFile=openConditionVariableFile()
    logging.log(level=logging.EXP,msg="conditionFile: %s"%(conditionFile,))
    
    EC.CONDITIONS_FILE=conditionFile
    
    EC.RESULTS_DIR=os.path.join(EC.RESULTS_DIR,EC.EXP_XINFO['subject_id'])
    if not os.path.exists(EC.RESULTS_DIR):
        os.makedirs(EC.RESULTS_DIR)
    print 'EC.RESULTS_DIR: ', EC.RESULTS_DIR
    fname="%s"%(EC.EXP_XINFO['subject_id'],)
    print "FNAME:",fname
    EC.EXP_HANDLER = data.ExperimentHandler(name='COGAIN ET TEST',
                        version='0.1',
                        extraInfo=EC.EXP_XINFO,
                        runtimeInfo=None,
                        originPath=None,
                        savePickle=True,
                        saveWideText=True,
                        dataFileName=os.path.join(EC.RESULTS_DIR,fname))
    trials, header=data.importConditions(conditionFile, returnFieldNames=True)
   
    if EC.IV_HEADER is None:
        EC.IV_HEADER=header
   
    for t in trials:
        if EC.BLOCKING_COLUMN not in t:
            raise  EC.BLOCKING_COLUMN+" not a column or condition variable file"
        else:
            if t[EC.BLOCKING_COLUMN] not in EC.BLOCKS:
                EC.BLOCK_LABEL_LIST.append(t[EC.BLOCKING_COLUMN])
                EC.BLOCKS[t[EC.BLOCKING_COLUMN]]=[]
            EC.BLOCKS[t[EC.BLOCKING_COLUMN]].append(t)
        
    print "BLOCK COUNT: ",len(EC.BLOCKS)
    EC.N_BLOCKS=len(EC.BLOCKS)

def createTrialHandlerForBlock(trials):
    rand=None
    if EC.RANDOMIZE_TRIALS is True:
        rand='random'

    return data.TrialHandler(trialList=trials, 
                    nReps=1,
                    method=rand,
                    dataTypes=None,
                    extraInfo=EC.EXP_XINFO,
                    seed=int(EC.msecTime()*1000))

#----------------------------------------------------------------------   

def displayTextScreenWaitForKeypress(text,keyList=None,maxWait=None):
    EC.PREBUILT_STIM['BACKGROUND'].draw()
    EC.PREBUILT_STIM['MESSAGE_TEXT'].setText(text)
    EC.PREBUILT_STIM['MESSAGE_TEXT'].draw()
    
    EC.WINDOW.logOnFlip('displayTextScreenWaitForKeypress:',level=logging.EXP,obj=EC.PREBUILT_STIM['MESSAGE_TEXT'])
    EC.WINDOW.flip()
    sendTrackerMsg("displayTextScreen : %s"%(text,),True)
    logging.flush()
    
    event.waitKeys(maxWait,keyList)

#----------------------------------------------------------------------   
                    
def endExperiment():
    logging.flush()
    EC.WINDOW.close()
    del EC.TRACKER
    EC.TRACKER=None

#----------------------------------------------------------------------   
def clearScreen(color=None,msg=None):
    if color is not None:
        #EC.WINDOW.setColor(color)
        EC.PREBUILT_STIM['BACKGROUND'].setColor(color,'rgb255')
    
    EC.PREBUILT_STIM['BACKGROUND'].draw()
    
    if msg is not None:
        EC. WINDOW.logOnFlip('CLEAR_SCREEN %s'%(msg,),level=logging.EXP)
    
    EC.WINDOW.flip()
    sendTrackerMsg("clearScreen : %s"%str((msg)),True)

#----------------------------------------------------------------------   
#----------------------------------------------------------------------

def displayFixationPoint(label,position=None,outer_color=None,inner_color=None,msg=None):
    EC.PREBUILT_STIM['BACKGROUND'].draw()
    if position is not None:
        EC.PREBUILT_STIM[label]['OUTER'].setPos(position)
        EC.PREBUILT_STIM[label]['INNER'].setPos(position)
    if inner_color is not None:
        EC.PREBUILT_STIM[label]['INNER'].setFillColor(inner_color,colorSpace='rgb255')        
        EC.PREBUILT_STIM[label]['INNER'].setLineColor(inner_color,colorSpace='rgb255')        
    if outer_color is not None:
        EC.PREBUILT_STIM[label]['OUTER'].setFillColor(outer_color,colorSpace='rgb255')        
        EC.PREBUILT_STIM[label]['OUTER'].setLineColor(outer_color,colorSpace='rgb255')        
    EC.PREBUILT_STIM[label]['OUTER'].draw()
    EC.PREBUILT_STIM[label]['INNER'].draw()
    if msg is not None:
        EC.WINDOW.logOnFlip(msg,level=logging.EXP)
        sendTrackerMsg(msg,True)
    EC.WINDOW.flip()
    sendTrackerMsg("displayFixationPoint : %s : %s : %s : %s"%(label,str(position),str(inner_color),str(msg)),True)
#-----------------------------------------------------------------------

def getEvents(saveKeys=False,saveMouse=False,saveTracker=False,findKey=None):
    keyEvents=event.getKeys(timeStamped=EC.GLOBAL_CLOCK)
    keyboardEvents=list()
    keyFound=None
    
    for ke in keyEvents:
        if ke[0]=='escape':
            EC.USER_TERMINATE_EXPERIMENT=True
        keyboardEvents.append((ke[1],ke[0]))#ET.KeyboardEvent(ke[1],ke[0]))
        if saveKeys is True:
            logging.log(level=logging.DATA,msg="KEY %.3f %s"%(ke[1],ke[0]))
        if keyFound is None and findKey is not None:
            if ke[0] in findKey:
                logging.log(level=logging.EXP,msg="KEY_TRIGGER %.3f %s"%(ke[1],ke[0]))
                keyFound=(ke[1],ke[0])
    
    i=0
    buttonEvents=list()
    bList, mouseTimes=EC.MOUSE.getPressed(True)
    
    for b in bList:    
        buttonEvents.append((mouseTimes[i],b))#ET.MouseButtonEvent(mouseTimes[i],b))
        i+=1
        if saveMouse is True:
            logging.log(level=logging.DATA,msg="MOUSE %.3f %s"%(mouseTimes[i],str(b)))
            
    EC.TRACKER.poll()
    trackerEvents=EC.TRACKER.getEventHandler().getBufferedData()

    if 1:#saveTracker is True:
        for t in trackerEvents:
            logging.log(level=logging.DATA,msg="%s"%(str(t),))
            
    if keyFound is not None:
        return keyboardEvents,buttonEvents,trackerEvents,keyFound
    return keyboardEvents,buttonEvents,trackerEvents

#-----------------------------------------------------------------------

def clearEventBuffer(saveKeys=False,saveMouse=False,saveTracker=False):
    if not saveKeys and not saveMouse and not saveTracker:
        event.clearEvents() 
        EC.TRACKER.getEventHandler().clearDataBuffer()
        return
        
    getEvents(saveKeys,saveMouse,saveTracker) 
#----------------------------------------------------------------------
def asyncWait(msec_dur,callback=None,no_sleep=.05):
    stime=EC.msecTime()
    logging.log(level=logging.EXP,msg='AWAIT_START %.3f'%(stime,))
    dur1=msec_dur*(1.0-no_sleep)
    dur2=msec_dur-dur1
    while (EC.msecTime()-stime)<dur1:
        if callback:
            callback()
        time.sleep(0.001)    

    while (EC.msecTime()-stime)<dur2:
        pass
    etime= EC.msecTime()
    adur=etime-stime
    logging.log(level=logging.EXP,msg='AWAIT_END %.3f %d %.3f'%(etime,msec_dur,adur))

#-----------------------------------------------------------------------

def monitorForKeyEvent(keys,msecduration=None, saveKeys=True,saveMouse=False,saveTracker=False):
    foundKey=None
    startTime=EC.msecTime()
    
    def timeout(sTime,duration):
        if duration is None:
            return False
        return (EC.msecTime()-sTime)<=duration
        
    while not timeout(startTime,msecduration):
        results =getEvents(saveKeys,saveMouse,saveTracker,keys) 
        
        if len(results) == 3:
            keyEvents, mouseEvents, trackerEvent=results
        if len(results)==4:
            keyEvents, mouseEvents, trackerEvent,foundKey=results

        if  foundKey:       
            return foundKey
        else:
            time.sleep(0.001)
    return (EC.msecTime(),'NO_RESPONSE')
#------------------------------------------------------------------------
def userCancelledExperiment():
    if EC.USER_TERMINATE_EXPERIMENT == True:
        logging.log(level=logging.EXP,msg="EXPERIMENT TERMINATED BY USER")
        return  True
    return False

#------------------------------------------------------------------------
def copyFileToResultsDir(filePathToCopy):
    file_path,file_name=os.path.split(filePathToCopy)
    script_path,script_name=os.path.split(__file__)
     
    #copy file to results dir
    shutil.copy2(filePathToCopy,os.path.join(EC.RESULTS_DIR,file_name))
    print 'copying file from '+filePathToCopy+' to '+os.path.join(EC.RESULTS_DIR,file_name)

#----------------------------------------------------------------------

def sendTrackerMsg(msg, prependTrackerTime=False):
    if prependTrackerTime is True:
        EC.TRACKER.sendMessage("%d\t%s"%(EC.TRACKER.trackerTime(),msg))
    else:
        EC.TRACKER.sendMessage(msg)
    
