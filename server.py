"""
ioHub
.. file: ioHub/server.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

import gevent
from gevent.server import DatagramServer
from gevent import Greenlet
import os,sys
from operator import itemgetter
from collections import deque
import inspect
import ioHub
from ioHub import client
from ioHub.devices import Computer, DeviceEvent, EventConstants

from yaml import load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
        
currentSec= Computer.currentSec

import msgpack
msgpk_unpacker=msgpack.Unpacker(use_list=True)
msgpk_unpack=msgpk_unpacker.unpack

#noinspection PyBroadException,PyBroadException
class udpServer(DatagramServer):
    def __init__(self,ioHubServer,address,coder='msgpack'):
        self.iohub=ioHubServer
        self.feed=None
        self._running=True
        if coder=='ujson':
            self.iohub.log(" ioHub Server configuring ujson...")
            import ujson
            self.coder=ujson
            self.pack=ujson.encode
            self.unpack=ujson.decode
        elif coder == 'msgpack':
            self.iohub.log("ioHub Server configuring msgpack...")
            self.coder=msgpack
            self.packer=msgpack.Packer()
            self.unpacker=msgpk_unpacker
            self.pack=self.packer.pack
            self.feed=msgpk_unpacker.feed
            self.unpack=msgpk_unpack

        
        DatagramServer.__init__(self,address)
         
    def handle(self, request, replyTo):
        if self._running is False:
            return
            
        if self.feed: # using msgpack
            self.feed(request[:-2])
            request = self.unpack() 
        else: #using ujson
            request=self.unpack(request[:-2])
        
        request_type= request.pop(0)
        
        if request_type == 'GET_EVENTS':
            r= self.handleGetEvents(replyTo)
            return r
        elif request_type == 'EXP_DEVICE':
            return self.handleExperimentDeviceRequest(request,replyTo)
        elif request_type == 'RPC':
            callable_name=request.pop(0)
            args=None
            kwargs=None
            if len(request)==1:
                args=request.pop(0)
            if len(request)==1:
                kwargs=request.pop(0)    
            
            result=None
            try:
                result=getattr(self,callable_name)
            except:
                edata=('RPC_ERROR',callable_name,"The method name referenced could not be found by the RPC server.")
                self.sendResponse(edata,replyTo)

            if result and callable(result):
                funcPtr=result
                error=False
                try:
                    if args is None and kwargs is None:
                        result = funcPtr()
                    elif args and kwargs:
                        result = funcPtr(*args,**kwargs)
                    elif args and not kwargs:
                        result = funcPtr(*args)
                    elif not args and kwargs:
                        result = funcPtr(**kwargs)
                except Exception, e:
                    print "Unexpected error:", sys.exc_info()[0]
                    print sys.exc_info()
                    print '-----------------------'
                    edata=('RPC_ERROR',callable_name,args,kwargs,sys.exc_info())
                    self.sendResponse(edata,replyTo)
                    error=True
                
                if not error and (result is not None):
                        edata=('RPC_RESULT',callable_name,result)
                        self.sendResponse(edata,replyTo)
            else:
                edata=('RPC_ERROR',callable_name,str(result),"The name provided is not callable on the RPC server.")
                self.sendResponse(edata,replyTo)
        else:
            edata=('IOHUB_ERROR',request_type,"The request type provided is not recognized by the ioHub UDP server.")
            self.sendResponse(edata,replyTo)
            
    def handleGetEvents(self,replyTo):
        try:
            currentEvents=list(self.iohub.eventBuffer)
            self.iohub.eventBuffer.clear()

            if len(currentEvents)>0:
                sorted(currentEvents, key=itemgetter(DeviceEvent.EVENT_HUB_TIME_INDEX))
                self.sendResponse(('GET_EVENTS_RESULT',currentEvents),replyTo)
            else:
                self.sendResponse(('GET_EVENTS_RESULT', None),replyTo)
        except:
            ioHub.printExceptionDetailsToStdErr()

    def handleExperimentDeviceRequest(self,request,replyTo):
        request_type= request.pop(0)
        if request_type == 'EVENT_TX':
            exp_events=request.pop(0)
            for eventAsTuple in exp_events:
                self.iohub.deviceDict['ExperimentDevice']._nativeEventCallback(eventAsTuple)
            self.sendResponse(('EVENT_TX_RESULT',len(exp_events)),replyTo)
        elif request_type == 'DEV_RPC':
            dclass=request.pop(0)
            dmethod=request.pop(0)
            args=None
            kwargs=None
            if len(request)==1:
                args=request[0]
            elif len(request)==2:
                args=request[0]
                kwargs=request[1]
                if len(kwargs)==0:
                    kwargs=None

            dev=None
            if dclass in ['EyeTracker',]:
                for dname, dev in self.iohub.deviceDict.iteritems():
                    if dname.endswith(dclass):
                        dev=self.iohub.deviceDict[dname]
                        break
            else:
                dev=self.iohub.deviceDict[dclass]
            method=getattr(dev,dmethod)
            result=[]
            try:
                if args and kwargs:
                    result=method(*args, **kwargs)
                elif args:
                    result=method(*args)
                elif kwargs:
                    result=method(**kwargs)
                else:
                    result=method()
                self.sendResponse(('DEV_RPC_RESULT',result),replyTo)
            except Exception, e:
                result=('DEV_RPC',dclass,dmethod,args,"An error occurred executing method",str(e))
                self.sendResponse(('IOHUB_ERROR',result),replyTo)
        elif request_type == 'GET_DEV_LIST':
            dev_list=[]
            for d in self.iohub.devices:
                dev_list.append((d.name,d.device_class))
            self.sendResponse(('GET_DEV_LIST_RESULT',len(dev_list),dev_list),replyTo)
        elif request_type == 'GET_DEV_INTERFACE':
            dclass=request.pop(0)
            data=None
            if dclass in ['EyeTracker',]:
                for dname, hdevice in self.iohub.deviceDict.iteritems():
                    if dname.endswith(dclass):
                        data=hdevice._getRPCInterface()
                        break
            else:
                dev=self.iohub.deviceDict[dclass]
                data=dev._getRPCInterface()
            if data:
                self.sendResponse(('GET_DEV_INTERFACE',data),replyTo)
            else:
                edata=('IOHUB_ERROR','GET_DEV_INTERFACE',dclass,"The requested class is not known.")
                self.sendResponse(edata,replyTo)
        else:
            edata=('IOHUB_ERROR','EXP_DEVICE',request_type,"The request type provided for EXP_DEVICE is not recognized.")
            self.sendResponse(edata,replyTo)
            
    def sendResponse(self,data,address):
        packet_data=None
        try:
            max_size=client.MAX_PACKET_SIZE/2-20
            packet_data=self.pack(data)+'\r\n'
            packet_data_length=len(packet_data)
            if packet_data_length>= max_size:
                num_packets=len(packet_data)/max_size+1
                self.sendResponse(('IOHUB_MULTIPACKET_RESPONSE',num_packets),address)
                for p in xrange(num_packets-1):
                    self.socket.sendto(packet_data[p*max_size:(p+1)*max_size],address)
                self.socket.sendto(packet_data[(p+1)*max_size:packet_data_length],address)
            else:
                self.socket.sendto(packet_data,address)
        except:
            ioHub.print2err('Error trying to send data to experiment process:')
            ioHub.print2err('data length:',len(data))
            if packet_data:
                ioHub.print2err('packet Data length: ',len(packet_data))
            ioHub.printExceptionDetailsToStdErr()

    def setExperimentInfo(self,experimentInfoList):
        self.iohub.experimentInfoList=experimentInfoList
        if self.iohub.emrt_file:
            return self.iohub.emrt_file.createOrUpdateExperimentEntry(experimentInfoList)           
        return False
        
    def createExperimentSessionEntry(self,sessionInfoDict):
        self.iohub.sessionInfoDict=sessionInfoDict
        if self.iohub.emrt_file:
            return self.iohub.emrt_file.createExperimentSessionEntry(sessionInfoDict)
        return False

    def initializeConditionVariableTable(self, experiment_id, session_id, numpy_dtype):
        if self.iohub.emrt_file:
            output=[('session_id','u4'),('index_id','u4')]
            for a in numpy_dtype:
                if isinstance(a[1],(str,unicode)):
                    output.append(tuple(a))
                else:
                    temp=[a[0],[]]
                    for i in a[1]:
                        temp[1].append(tuple(i))
                    output.append(tuple(temp))

            return self.iohub.emrt_file._initializeConditionVariableTable(experiment_id,output)
        return False

    def addRowToConditionVariableTable(self,session_id,data):
        if self.iohub.emrt_file:
            return self.iohub.emrt_file._addRowToConditionVariableTable(session_id,data)
        return False

    def clearEventBuffer(self):
        l= len(self.iohub.eventBuffer)
        self.iohub.eventBuffer.clear()
        return l

    def currentSec(self):
        return currentSec()

    def updateGlobalTimeOffset(self,offset):
        Computer.globalClock.setOffset(offset)

    def enableHighPriority(self,disable_gc=True):
        Computer.enableHighPriority(disable_gc)

    def disableHighPriority(self):
        Computer.disableHighPriority()

    def getProcessAffinity(self):
        return Computer.getCurrentProcessAffinity()

    def setProcessAffinity(self, processorList):
        return Computer.setCurrentProcessAffinity(processorList)

    def flushIODataStoreFile(self):
        if self.iohub.emrt_file:
            self.iohub.emrt_file.emrtFile.flush()
            return True
        return False

    def shutDown(self):
        import time
        self._running=False
        self.iohub._running=False
        while len(self.iohub.deviceMonitors) > 0:
            m=self.iohub.deviceMonitors.pop(0)
            m.running=False
        self.clearEventBuffer()
        self.iohub.closeDataStoreFile()
        self.disableHighPriority()
        while len(self.iohub.devices) > 0:
            d=self.iohub.devices.pop(0)
            d._close()
        time.sleep(1)
        
        self.stop()

class DeviceMonitor(Greenlet):
    def __init__(self, device,sleep_interval):
        Greenlet.__init__(self)
        self.device = device
        self.sleep_interval=sleep_interval
        self.running=False
        
    def _run(self):
        self.running = True
        ctime=Computer.currentSec
        while self.running is True:
            stime=ctime()
            self.device._poll()
            i=self.sleep_interval-(ctime()-stime)
            if i > 0.0:
                gevent.sleep(i)
        
        self.device=None
        
class ioServer(object):
    eventBuffer=None 
    _logMessageBuffer=None
    def __init__(self, initial_time_offset, rootScriptPathDir, config=None):
        ioHub.devices.Computer.isIoHubProcess=True
        ioHub.devices.Computer.globalClock=ioHub.ioClock(None,initial_time_offset)
        self._running=True
        self.emrt_file=None
        self.config=config
        ioServer.eventBuffer=deque(maxlen=config.get('global_event_buffer',2048))
        ioServer._logMessageBuffer=deque(maxlen=128)

        self.devices=[]
        self.deviceDict={}
        self.deviceMonitors=[]
        self.sessionInfoDict=None
        self.experimentInfoList=None
        # start UDP service
        self.udpService=udpServer(self,':%d'%config.get('udpPort',9000))

        # read temp paths file
        ioHub.data_paths=None
        try:
            expJsonPath=os.path.join(rootScriptPathDir,'exp.paths')
            f=open(expJsonPath,'r')
            import ujson
            ioHub.data_paths=ujson.loads(f.read())
            f.flush()
            f.close()
            os.remove(expJsonPath)
        except:
            pass

        # dataStore setup
        if 'ioDataStore' in config:
            dataStoreConfig=config.get('ioDataStore')
                
            if len(dataStoreConfig)==0:
                dsconfigPath=os.path.join(ioHub.IO_HUB_DIRECTORY,'ioDataStore','default_ioDataStore.yaml')              
                dslabel,dataStoreConfig=load(file(dsconfigPath,'r'), Loader=Loader).popitem()                
            
            if dataStoreConfig.get('enable', True):            
                if ioHub.data_paths is None:
                    resultsFilePath=rootScriptPathDir
                else:
                    resultsFilePath=ioHub.data_paths['IOHUB_DATA']
                self.createDataStoreFile(dataStoreConfig.get('filename','events')+'.hdf5',resultsFilePath,'a',dataStoreConfig.get('storage_type','pytables'),dataStoreConfig)
        #built device list and config from yaml config settings
        for iodevice in config.get('monitor_devices',()):
            for device_class,deviceConfig in iodevice.iteritems():
                self.addDeviceToMonitor(device_class,deviceConfig)
                
        deviceDict=self.deviceDict
        iohub=self
        if ('Mouse' in deviceDict or 'Keyboard' in deviceDict) and Computer.system == 'Windows':
            class pyHookDevice(object):
                def __init__(self):
                    import pyHook
                    self._hookManager=pyHook.HookManager()
                    
                    if 'Mouse' in deviceDict:
                        self._hookManager.MouseAll = deviceDict['Mouse']._nativeEventCallback
                    if 'Keyboard' in deviceDict:
                        self._hookManager.KeyAll = deviceDict['Keyboard']._nativeEventCallback
                    if 'Mouse' in deviceDict:
                        self._hookManager.HookMouse()    
                    if 'Keyboard' in deviceDict:
                        self._hookManager.HookKeyboard()
                       
                    iohub.log("WindowsHook PumpEvents Periodic Timer Created.")
        
                def _poll(self):
                    import pythoncom
                    # PumpWaitingMessages returns 1 if a WM_QUIT message was received, else 0
                    if pythoncom.PumpWaitingMessages() == 1:
                        raise KeyboardInterrupt()               

            hookMonitor=DeviceMonitor(pyHookDevice(),0.00375)
            
            self.deviceMonitors.append(hookMonitor)
            
        self.log("Time Offset: {0}".format(initial_time_offset))

    def addDeviceToMonitor(self,device_class,deviceConfig):
        if len(deviceConfig)==0:
            dconfigPath=os.path.join(ioHub.IO_HUB_DIRECTORY,'devices',device_class,"default_%s.yaml"%(device_class))              
            dclass,deviceConfig=load(file(dconfigPath,'r'), Loader=Loader).popitem()
            
        if deviceConfig.get('enable',True):
            try:
                self.log("Creating Device: %s"%(device_class,))
                parentModule=ioHub.devices
                modulePathTokens=device_class.split('.')
                for mt in modulePathTokens:
                    DeviceClass=getattr(parentModule,mt)
                    if inspect.isfunction(DeviceClass):
                        DeviceClass()
                    parentModule=DeviceClass
                deviceInstance=DeviceClass(dconfig=deviceConfig)
                self.devices.append(deviceInstance)
                self.deviceDict[device_class]=deviceInstance

                if 'device_timer' in deviceConfig:
                    interval = deviceConfig['device_timer']['interval']
                    self.log("%s has requested a timer with period %.5f"%(device_class, interval))
                    dPoller=DeviceMonitor(deviceInstance,interval)
                    self.deviceMonitors.append(dPoller)

                # add event listeners for streaming events
                if deviceConfig.get('streamEvents',False) is True:
                    self.log("Online event access is being enabled for: %s"%device_class)
                    # add listener for global event queue
                    deviceInstance._addEventListener(self)
                    # add listener for device event queue
                    deviceInstance._addEventListener(deviceInstance)

                # add event listeners for saving events
                if (self.emrt_file is not None) and (deviceConfig.get('saveEvents',False) is True):
                    self.log("Event saving is being enabled for: %s"%device_class)
                    deviceInstance._addEventListener(self.emrt_file)
                self.log("==============================")
            except Exception as e:
                ioHub.print2err("Exception creating device %s: %s. Is device connected?"%(device_class,str(e)))
                ioHub.printExceptionDetailsToStdErr()
                self.log("Exception creating device %s: %s"%(device_class,str(e)))



    def processDeviceEvents(self,sleep_interval):
        while self._running:
            self._processDeviceEventIteration()
            gevent.sleep(sleep_interval)

    def _processDeviceEventIteration(self):
        for device in self.devices:
            try:
                 events=device._getNativeEventBuffer()
                 while len(events)>0:
                    evt=events.popleft()
                    e=device._getIOHubEventObject(evt)
                    for l in device._getEventListeners():
                        l._handleEvent(e)
            except:
                ioHub.printExceptionDetailsToStdErr()
                ioHub.print2err("Error in processDeviceEvents: ", device, " : ", len(events), " : ", e)
                eclass=EventConstants.EVENT_CLASSES[e[DeviceEvent.EVENT_TYPE_ID_INDEX]]
                ioHub.print2err("eclass: ",eclass)
                ioHub.print2err("Event array length: ", len(e), " should be : ", len(eclass.NUMPY_DTYPE)," : ",eclass.NUMPY_DTYPE)
        
    def closeDataStoreFile(self):
        if self.emrt_file:
            pytablesfile=self.emrt_file
            self.emrt_file=None
            pytablesfile.flush()
            pytablesfile.close()

    def log(self,text,level=1):
        if self.emrt_file:
            while len(self._logMessageBuffer)>0:
                time,text,level=self._logMessageBuffer.popleft()
                self.emrt_file.log(time,text,level)
            self.emrt_file.log(currentSec(),text,level)
        else:
            logMsg=(currentSec(),text,level)
            self._logMessageBuffer.append(logMsg)

    def createDataStoreFile(self,fileName,folderPath,fmode,ftype,ioHubsettings):
        try:
            if ftype == 'pytables':
                from ioDataStore import EMRTpyTablesFile
                self.closeDataStoreFile()                
                self.emrt_file=EMRTpyTablesFile(fileName,folderPath,fmode,ioHubsettings)                
                return True
            else:
                return False #('RPC_ERROR','createDataStoreFile','Only DataStore File Type "pytables" is currently Supported, not %s'%str(ftype)) 
        except Exception, err:
            ioHub.printExceptionDetailsToStdErr()
            raise err


    # -------------------- I/O loop ---------------------------------

    def start(self):       
        self.log('Receiving datagrams on :9000')
        self.udpService.start()

        for m in self.deviceMonitors:
            m.start()
        
        gevent.spawn(self.processDeviceEvents,0.001)
        
        sys.stdout.write("IOHUB_READY\n\r\n\r")
        sys.stdout.flush()
        
        gevent.run()
        
        #print "ioServer Process Completed!"
   
    def _handleEvent(self,event):
        self.eventBuffer.append(event)
        
        
    def __del__(self):
        self.emrt_file.close()
   
################### End of Class Def. #########################

# ------------------ Main / Quickstart testing -------------------------



def run(initial_time_offset,rootScriptPathDir,configFilePath):

    import tempfile
    tdir=tempfile.gettempdir()
    cdir,cfile=os.path.split(configFilePath)

    if tdir==cdir:
        tf=open(configFilePath)
        msgpk_unpacker.feed(tf.read())
        ioHubConfig=msgpk_unpack()
        tf.close()
        os.remove(configFilePath)
    else:
        ioHubConfig=load(file(configFilePath,'r'), Loader=Loader)

    s = ioServer(initial_time_offset, rootScriptPathDir, ioHubConfig)

    s.start()    
    
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
        initial_offset=ioHub.highPrecisionTimer()
        
    run(initial_time_offset=initial_offset, rootScriptPathDir=rootScriptPathDir, configFilePath=configFileName)