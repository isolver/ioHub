from __future__ import division
import psychopy
import psychopy.visual
from psychoTracker_functions import *
import os
import pyeyetracker

def main():
    #USE_TRACKER='SR_RESEARCH'
    USE_TRACKER='SMI'
    
    ## ----General experiment initialization and setup functions.
    ## All functions are in psychoTracker_functions.py
    ## EC acts as a global struction holding many useful functions and settings for the experiment,
    
    intializeTimerAndLogging()    
    inializeExperimentData()

    
    expStartTime=EC.GC_FUNC()


    inializeGraphicsAndStim()
    testSystemCapabilitiesAndStatus()
    
    EC.TRACKER =pyeyetracker.SUPPORTED_EYE_TRACKER_INTERFACES[USE_TRACKER][0](EC)
    print 'Tracker loaded:', pyeyetracker.SUPPORTED_EYE_TRACKER_INTERFACES[USE_TRACKER][1]
    ## -- Do general tracker setup that occurs at the start of an experiment.
    ## NOTE: currenly does nothing.
    EC.TRACKER.experimentStartDefaultLogic(fileName=EC.EXP_XINFO['subject_id'])
    
    ## -- logging.log writes the text in the first parameter out the the log file that supports logging
    ## level equal to the level param or higher. Each time the experiment  runs it creates a lastrun.log file.
    logging.log('EXP START: ',level=logging.EXP)
    
    clearScreen(msg="EXP_START_CLEAR_SCREEN")
    
    
    ## -- For each block in the list of block values, run one iterations if ll internal vaerialbes nas well.
    for BL in EC.BLOCK_LABEL_LIST:
        
        trials = createTrialHandlerForBlock(EC.BLOCKS[BL])
        EC.EXP_HANDLER.addLoop(trials)
        
        ## -- clearEventBuffer: Clears out old events from the event buffers that we do not want to included.  
        clearEventBuffer()

    ## -- displayTextScreenWaitForKeypress lets you display a line of text on the center
        ## of the screen, shows the text, logs the display time in the .log file, and waits until
        ## one of the buttons in the button list provided is pressed. 
        ## Nice a quick for instuction screens.
        
        displayTextScreenWaitForKeypress('Ready to start Block %s of %d. Press Enter (Return) to Start.'%(BL,EC.N_BLOCKS),('return','s'))
        logging.log(level=logging.EXP,msg='START BLOCK %s of %d'%(BL,EC.N_BLOCKS))
        clearScreen(msg="READY_BLOCK_CLEAR_SCREEN")
        
        EC.TRACKER.blockStartDefaultLogic()
        
        if EC.USER_TERMINATE_EXPERIMENT == True:
            logging.log(level=logging.EXP,msg="EXPERIMENT TERMINATED BY USER")
            break

        last_fp2_pos=(0.0,0.0)
        
        EC.TRACKER.enableRecording(True)
        
        for trial_num,eachTrial in enumerate(trials):#automatically stops when done
            clearEventBuffer(saveKeys=True)
            tn=trials.thisIndex
            
            logging.log(level=logging.EXP,msg='START TRIAL %d of BLOCK %s'%(tn,BL))
            
            if userCancelledExperiment():
                break
                
            EC.TRACKER.trialStartDefaultLogic()
            
            fp1_pos=(0,0)
            try:
                x=float(eachTrial['FP1_X'])
                y=float(eachTrial['FP1_Y'])
                fp1_pos=(x,y)
            except:
                fp1_pos=last_fp2_pos
                
            x=float(eachTrial['FP2_X'])
            y=float(eachTrial['FP2_Y'])  
            fp2_pos=(x,y)
            #print "B: ", fp2_pos
            last_fp2_pos=fp2_pos 
                
            if trial_num==0:
                displayFixationPoint(label="FP1",position=fp2_pos,inner_color=eachTrial["FP1_INNER_COLOR"],outer_color=eachTrial["FP1_OUTER_COLOR"],msg="FP1")
                clearEventBuffer(saveKeys=True)
                startKeys=['return',]
                startKeys.extend(eachTrial["POSSIBLE_RESPONSES"])
                monitorForKeyEvent(startKeys)
            else:
                displayFixationPoint(label="FP1",position=fp1_pos,inner_color=eachTrial["FP1_INNER_COLOR"],outer_color=eachTrial["FP1_OUTER_COLOR"],msg="FP1")
                
            
            displayFixationPoint(label="FP2",position=fp2_pos, inner_color=eachTrial["FP2_INNER_COLOR"],outer_color=eachTrial["FP2_OUTER_COLOR"],msg="FP2_INITIAL_DISPLAY")
            clearEventBuffer(saveKeys=True)
            asyncWait(eachTrial['FP2_ISI_1'])           
 
            displayFixationPoint(label="FP2",inner_color=eachTrial["FP2_INNER_COLOR2"],msg="FP2_COLOR_CHANGE_START")  
            clearEventBuffer(saveKeys=True)

            asyncWait(eachTrial['FP2_CHANGE_INTERVAL'])
            
  
            displayFixationPoint(label="FP2",inner_color=eachTrial["FP2_INNER_COLOR"] ,msg="FP2_COLOR_CHANGE_END")  
            ccStart=EC.GC_FUNC()
            mt=eachTrial["MAX_RESPONSE_WAIT"]
            mresponse=monitorForKeyEvent(keys=eachTrial["POSSIBLE_RESPONSES"] ,msecduration=mt) #collect response 'b'b for blue, 'r' for 'red'
            
            waitLeft=mt-(EC.GC_FUNC()-ccStart)
            if waitLeft>0:
                asyncWait(waitLeft)
            
            EC.TRACKER.trialEndDefaultLogic()
            
            logging.log(level=logging.EXP,msg='END TRIAL %d of BLOCK %s'%(tn,BL))
            
            if userCancelledExperiment():
                break
        
            trials.addData("choice_response", mresponse)
            sendTrackerMsg("RESPONSE : %s : %s"%(str(mresponse),str(eachTrial["FP2_INNER_COLOR"])))

        # end of each block, save data to a sheet in excel file
        
        fname="%s"%(EC.EXP_XINFO['subject_id'],)
        dataFileName=os.path.join(EC.RESULTS_DIR,fname)
        head,condition_file=os.path.split(EC.CONDITIONS_FILE)
        
        trials.saveAsExcel(dataFileName,sheetName=condition_file,stimOut=EC.IV_HEADER,dataOut=('n',r'all_raw'),appendFile=True)
        
        EC.TRACKER.blockEndDefaultLogic()
        
        logging.log(level=logging.EXP,msg='END BLOCK %s of %d'%(BL,EC.N_BLOCKS))
        EC.TRACKER.enableRecording(False)
    
    ## --- Experiment complete, copy data files, clean-up, etc
    
    expTime=(EC.GC_FUNC()-expStartTime)/1000/60
    xDoneMsg='EXPERIMENT_COMPLETED dur=%.3f minutes'%(expTime)
    print xDoneMsg
    clearScreen(msg=xDoneMsg)
    
    EC.TRACKER.experimentEndDefaultLogic()
    
    if userCancelledExperiment():
        pass

    
    copyFileToResultsDir(EC.CONDITIONS_FILE)
   
    endExperiment()

   #copy log File to result dir
    EC.MAIN_LOG.stream.flush()
    EC.MAIN_LOG=None
    
    pname,fname=os.path.split(__file__)
    logFilePath=os.path.join(pname,'logLastRun.log')
    copyFileToResultsDir(logFilePath)

    try:
        core.quit()
    except:
        pass
if __name__ == "__main__":    
    main()
