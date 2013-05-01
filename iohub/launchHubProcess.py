# -*- coding: utf-8 -*-
"""
Created on Wed May 01 06:30:07 2013

@author: Sol
"""
import gevent
import json
import os,sys

from yaml import load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
        

import psychopy.iohub  as iohub   
from psychopy.iohub.server import ioServer, Computer
from psychopy.iohub.util import printExceptionDetailsToStdErr, print2err, MonotonicClock

def run(rootScriptPathDir,configFilePath):
    import tempfile
    tdir=tempfile.gettempdir()
    cdir,cfile=os.path.split(configFilePath)

    if tdir==cdir:
        tf=open(configFilePath)
        ioHubConfig=json.loads(tf.read())
        tf.close()
        os.remove(configFilePath)
    else:
        ioHubConfig=load(file(configFilePath,'r'), Loader=Loader)


    try:
        s = ioServer(rootScriptPathDir, ioHubConfig)
    except Exception,e:
        printExceptionDetailsToStdErr()
        sys.stdout.flush()
        
        try:
            s.shutdown()
        except:
            pass
        
        return -1
    
    try:
        s.log('Receiving datagrams on :9000')
        s.udpService.start()

        for m in s.deviceMonitors:
            m.start()

        gevent.spawn(s.processDeviceEvents,0.001)

        sys.stdout.write("IOHUB_READY\n\r\n\r")
        sys.stdout.flush()
        
        gevent.run()

        s.log("Server END Time Offset: {0}".format(Computer.globalClock.getLastResetTime()),'DEBUG')

    except Exception as e:
        print2err("Error occurred during ioServer.start(): ",str(e))
        printExceptionDetailsToStdErr()
        print2err("------------------------------")

        sys.stdout.write("IOHUB_FAILED\n\r\n\r")
        sys.stdout.flush()
        
        try:
            s.shutdown()
        except:
            pass
    
    return -1
    
if __name__ == '__main__':
    prog=sys.argv[0]
    if len(sys.argv)>=2:
        initial_offset=float(sys.argv[1])
    if len(sys.argv)>=3:
        rootScriptPathDir=sys.argv[2]
    if len(sys.argv)>=4:        
        configFileName=sys.argv[3]        
        #ioHub.print2err("ioServer initial_offset: ",initial_offset)
    if len(sys.argv)<2:
        configFileName=None
        rootScriptPathDir=None
        initial_offset=iohub.getTime()

    Computer.isIoHubProcess=True
    Computer.globalClock=MonotonicClock(initial_offset)        

    run(rootScriptPathDir=rootScriptPathDir, configFilePath=configFileName)
