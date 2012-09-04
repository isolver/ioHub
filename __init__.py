"""
ioHub Python Module

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""
from __future__ import division

 
class ioDeviceError(Exception):
    def __init__(self, device,msg):
        self.device = device
        self.msg=msg
    def __str__(self):
        return repr("ioDeviceError:\nMsg: %s\nDevice: %s\n"%(self.msg),repr(self.device))

DEVICE_CATERGORY_ID_LABEL={
        1:'KEYBOARD',
        2:'MOUSE',
        4:'VISUAL_STIMULUS_PRESENTER',
        8:'VIRTUAL',
        16:'DIGITAL_IO',
#        32:'DA_CONVERTER',
#        64:'AD_CONVERTER',
#        128:'BUTTON_BOX',
#        256:'TOUCH_SCREEN',
#        512:'SPEAKER',
#        1024:'AMPLIFIER',
#        2048:'MICROPHONE',
        4096:'EYE_TRACKER',
#        8192:'EEG',
#        16384:'MRI',
#        32768:'MEG',
        18446744073709551616:'OTHER'
        }

if 'KEYBOARD' not in DEVICE_CATERGORY_ID_LABEL:
    temp={}
    for key,value in DEVICE_CATERGORY_ID_LABEL.iteritems():
        temp[value]=key
    DEVICE_CATERGORY_ID_LABEL.update(temp)
    
    del temp

DEVICE_TYPE_LABEL={
        1:'KEYBOARD_DEVICE',
        2:'MOUSE_DEVICE',
        3:'DISPLAY_DEVICE',
        4:'PARALLEL_PORT_DEVICE',
        5:'EXPERIMENT_DEVICE',
#        6:'ANALOG_INPUT_DEVICE',
#        7:'ANALOG_OUTPUT_DEVICE',
        8:'BUTTON_BOX_DEVICE',
#        9:'TOUCH_SCREEN_DEVICE',
#        10:'SPEAKER_DEVICE',
#        11:'AMPLIFIER_DEVICE',
#        12:'MICROPHONE_DEVICE',
        13:'EYE_TRACKER_DEVICE',
#        14:'EEG_DEVICE',
#        15:'MRI_DEVICE',
#        16:'MEG_DEVICE',
        17:'OTHER_DEVICE'    
    }

if 'KEYBOARD_DEVICE' not in DEVICE_TYPE_LABEL:
    temp={}
    for key,value in DEVICE_TYPE_LABEL.iteritems():
        temp[value]=key
    DEVICE_TYPE_LABEL.update(temp)
    
    del temp
    
DEVICE_LABELS = DEVICE_TYPE_LABEL

DEVICE_ID_TO_CATERGORYS=dict()

EVENT_TYPES=dict(UNDEFINED_EVENT=0, EXPERIMENT_EVENT =1,  MESSAGE =2,  COMMAND =3, 
                 KEYBOARD_EVENT =50, KEYBOARD_PRESS =51, KEYBOARD_RELEASE =52,BUTTON_BOX_PRESS =60, BUTTON_BOX_RELEASE =61,
                 MOUSE_EVENT =54, MOUSE_PRESS =55, MOUSE_RELEASE =56, MOUSE_WHEEL =57, MOUSE_MOVE =58, MOUSE_DOUBLE_CLICK=59,
                 PARALLEL_PORT_INPUT =73, TTL_INPUT =70,EYE_SAMPLE=100,BINOC_EYE_SAMPLE =101, 
                 FIXATION_START =106, FIXATION_UPDATE =107, FIXATION_END =108,
                 SACCADE_START =111, SACCADE_END =112,
                 BLINK_START =116, BLINK_END =117, 
                 SMOOTH_PURSUIT_START =119, SMOOTH_PURSUIT_END =120,
                )
if 50 not in EVENT_TYPES:
    temp={}
    for key,value in EVENT_TYPES.iteritems():
        temp[value]=key
    EVENT_TYPES.update(temp)
    
    del temp                
'''
                 EVENT_TRIGGER =35,FUNCTION_START =30, FUNCTION_END =31,
                 SEQUENCE_START =10, SEQUENCE_END =11, EXPERIMENT_START =12, EXPERIMENT_END =13, BLOCK_START =14, BLOCK_END =15,
                 TRIAL_START =16, TRIAL_END =17, EXPERIMENT_LOG =20, EXPERIMENT_DV =21, EXPERIMENT_IV =22,
                 DRAW_START =23, DRAW_END =24, SWAP_START =25, SWAP_END =26, VBLANK =27, DISPLAY_START =28, DISPLAY_END =29,                 ANALOG_INPUT_SAMPLE =73, ANALOG_OUTPUT_SAMPLE =74, ANALOG_INPUT_EVENT =75, ANALOG_OUTPUT_EVENT =76,
                 INTEREST_AREA_ACTIVE =90, INTEREST_AREA_INACTIVE =91, INTEREST_AREA_POSITION_CHANGE =92, INTEREST_AREA_SHAPE_CHANGE =93, INTEREST_AREA_SHAPE_POSITION_CHANGE =94,
                 DATA_MISSING =200, DATA_MISSING_START =201, DATA_MISSING_END =202,
                 DATA_GAP =205, DATA_GAP_START =206, DATA_GAP_END =207,
                 IP_DATA_INPUT =79, IP_DATA_OUTPUT =80,
                 SERIAL_DATA_INPUT =77, SERIAL_DATA_OUTPUT =78,
                 TTL_INPUT =70, TTL_OUPUT =71,PARALLEL_PORT_OUPUT =74,
                 AUDIO_OUT_START =40, AUDIO_OUT_END =41, VOICE_KEY =42, AUDIO_IN_START =43, AUDIO_IN_END =44,
'''
import sys
 
def print2stderr(text):
    sys.stderr.write(text)
    sys.stderr.write('\n\r')
    sys.stderr.flush()

    
 
import devices
import os
global IO_HUB_DIRECTORY
IO_HUB_DIRECTORY=os.path.dirname(os.path.abspath(__file__))
