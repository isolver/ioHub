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
import os,sys,gc
import time
from operator import itemgetter, attrgetter
from collections import deque
import ioHub
from ioHub.devices import Computer,computer
currentMsec= Computer.currentMsec
currentUsec= Computer.currentUsec

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
            import msgpack
            self.coder=msgpack
            self.packer=msgpack.Packer()
            self.unpacker=msgpack.Unpacker(use_list=True)
            self.pack=self.packer.pack
            self.feed=self.unpacker.feed
            self.unpack=self.unpacker.unpack

        
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
        currentEvents=list(self.iohub.eventBuffer)
        self.iohub.eventBuffer.clear()

        if len(currentEvents)>0:
            sorted(currentEvents, key=itemgetter(7))
            self.sendResponse(('GET_EVENTS_RESULT',currentEvents),replyTo)
        else:
            self.sendResponse(('GET_EVENTS_RESULT', None),replyTo)
 
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
            dev=self.iohub.deviceDict[dclass]
            method=getattr(dev,dmethod)
            result=[]
            try:
                if args and kwargs:
                    result=method(*args, **kwargs)
                if args:
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
                dev_list.append((d.user_label,d.instance_code,d.device_class))
            self.sendResponse(('GET_DEV_LIST_RESULT',len(dev_list),dev_list),replyTo)
        elif request_type == 'GET_DEV_INTERFACE':
            dclass=request.pop(0)
            dev=self.iohub.deviceDict[dclass]
            data=dev._getRPCInterface()
            self.sendResponse(('GET_DEV_INTERFACE',data),replyTo)
        else:
            edata=('IOHUB_ERROR','EXP_DEVICE',request_type,"The request type provided for EXP_DEVICE is not recognized.")
            self.sendResponse(edata,replyTo)
            
    def sendResponse(self,data,address,printResponseInfo=False):
        packet_data=self.pack(data)+'\r\n'
        self.socket.sendto(packet_data,address)         
    
    def setExperimentInfo(self,experimentInfoList):
        if self.iohub.emrt_file:
            return self.iohub.emrt_file.createOrUpdateExperimentEntry(experimentInfoList)           
        return None
        
    def createExperimentSessionEntry(self,sessionInfoDict):
        if self.iohub.emrt_file:
            return self.iohub.emrt_file.createExperimentSessionEntry(sessionInfoDict)
        return None
        
    def clearEventBuffer(self):
        l= len(self.iohub.eventBuffer)
        self.iohub.eventBuffer.clear()
        return l

    def currentSec(self):
        return Computer.currentSec()

    def currentMsec(self):
        return currentMsec()

    def currentUsec(self):
        return currentUsec()
        
    def enableHighPriority(self,disable_gc=True):
        ioHub.computer.enableHighPriority(disable_gc)

    def disableHighPriority(self):
        ioHub.computer.disableHighPriority()

    def getProcessAffinity(self):
        return ioHub.computer.getCurrentProcessAffinity()

    def setProcessAffinity(self, processorList):
        return ioHub.computer.setCurrentProcessAffinity(processorList)

    def shutDown(self):
        import time
        self._running=False
        self.iohub._running=False
        time.sleep(1.0)
        while len(self.iohub.deviceMonitors) > 0:
            m=self.iohub.deviceMonitors.pop(0)
            m.running=False
        self.clearEventBuffer()
        self.iohub.closeDataStoreFile()
        self.disableHighPriority()
        time.sleep(1.0)
            
        while len(self.iohub.devices) > 0:
            self.iohub.devices.pop(0)
        
        #for key in self.iohub.deviceDict:
        #    self.iohub.deviceDict['key']=None
        
        time.sleep(1)
        
        self.stop()
        #self.close()    
        
    def getProcessInfoString(self):
        return computer.getProcessInfoString()

class DeviceMonitor(Greenlet):
    def __init__(self, device,sleep_interval):
        Greenlet.__init__(self)
        self.device = device
        self.sleep_interval=sleep_interval
        self.running=False
        
    def _run(self):
        self.running = True
        
        while self.running is True:
            self.device._poll()
            gevent.sleep(self.sleep_interval)
        
        self.device=None
        
class ioServer(object):
    eventBuffer=None 
    _logMessageBuffer=None
    def __init__(self,configFilePath,config):
        self._running=True
        self.config=config
        self.configFilePath=configFilePath
        ioServer.eventBuffer=deque(maxlen=config['global_event_buffer'])
        ioServer._logMessageBuffer=deque(maxlen=128)
        self.emrt_file=None
        self.devices=[]
        self.deviceDict={}
        self.deviceMonitors=[]
        # start UDP service
        self.udpService=udpServer(self,':%d'%config['udpPort'])

        # dataStore setup
        if 'ioDataStore' in config and config['ioDataStore']['enable'] is True:
            configFileDir,cfn=os.path.split(self.configFilePath)
            resultsFilePath=os.path.join(configFileDir,config['ioDataStore']['filepath'])
            self.createDataStoreFile(config['ioDataStore']['filename']+'.hdf5',resultsFilePath,'a',config['ioDataStore']['storage_type'])
        
        # device configuration
        if len(config['monitor_devices']) > 0:
            import ioHub.devices as devices

        #built device list and config from yaml config settings
        for iodevice in config['monitor_devices']:
            for _key,deviceConfig in iodevice.iteritems():
                try:
                    # build devices to monitor
                    self.log("Creating Device: %s"%deviceConfig['device_class'])
                    dclass=deviceConfig['device_class']
                    parentModule=devices
                    modulePathTokens=dclass.split('.')
                    for mt in modulePathTokens:
                        DeviceClass=getattr(parentModule,mt)
                        parentModule=DeviceClass
                    deviceInstance=DeviceClass(dconfig=deviceConfig)
                    self.devices.append(deviceInstance)
                    self.deviceDict[deviceConfig['device_class']]=deviceInstance

                    if 'device_timer' in deviceConfig:
                        interval = deviceConfig['device_timer']['interval']
                        self.log("%s has requested a timer with period %.5f"%(deviceConfig['device_class'], interval))
                        dPoller=DeviceMonitor(deviceInstance,interval)
                        self.deviceMonitors.append(dPoller)

                    # add event listeners for streaming events
                    if 'streamEvents' in deviceConfig and deviceConfig['streamEvents'] is True:
                        self.log("Online event access is being enabled for: %s"%deviceConfig['device_class'])
                        # add listener for global event queue
                        deviceInstance._addEventListener(self)
                        # add listener for device event queue
                        deviceInstance._addEventListener(deviceInstance)

                    # add event listeners for saving events
                    if (self.emrt_file is not None) and ('saveEvents' in deviceConfig) and (deviceConfig['saveEvents'] is True):
                        self.log("Event saving is being enabled for: %s"%deviceConfig['device_class'])
                        deviceInstance._addEventListener(self.emrt_file)
                    self.log("==============================")
                except Exception as e:
                    ioHub.print2err("Exception creating device %s: %s. Is device connected?"%(deviceConfig['device_class'],str(e)))
                    #ioHub.printExceptionDetailsToStdErr()
                    self.log("Exception creating device %s: %s"%(deviceConfig['device_class'],str(e)))
        deviceDict=self.deviceDict
        iohub=self
        if ('Mouse' in deviceDict or 'Keyboard' in deviceDict) and computer.system == 'Windows':
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

    def processDeviceEvents(self,sleep_interval):
        while self._running:
            for device in self.devices:
                events=device._getNativeEventBuffer()
                while len(events)>0:
                    evt=events.popleft()                    
                    e=device._getIOHubEventObject(evt,device.instance_code)
                    for l in device._getEventListeners():
                        l._handleEvent(e) 
            gevent.sleep(sleep_interval)

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
            self.emrt_file.log(currentUsec(),text,level)
        else:
            logMsg=(currentUsec(),text,level)
            self._logMessageBuffer.append(logMsg)

    def createDataStoreFile(self,fileName,folderPath,fmode,ftype):        
        from ioHub import ioDataStore
        try:
            if ftype == 'pytables':
                from ioDataStore import EMRTpyTablesFile
                self.closeDataStoreFile()
                
                self.emrt_file=EMRTpyTablesFile(fileName,folderPath,fmode)
                
                hfile=self.emrt_file
                
                return True
            else:
                return False #('RPC_ERROR','createDataStoreFile','Only DataStore File Type "pytables" is currently Supported, not %s'%str(ftype)) 
        except Exception, err:
            raise err


    # -------------------- I/O loop ---------------------------------

    def start(self):       
        self.log('Receiving datagrams on :9000')
        self.udpService.start()

        for m in self.deviceMonitors:
            m.start()
        
        gevent.spawn(self.processDeviceEvents,0.0009)
        
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



def run(configFilePath=None):
    from yaml import load, dump
    try:
        from yaml import CLoader as Loader, CDumper as Dumper
    except ImportError:
        from yaml import Loader, Dumper

    ioHubConfig=load(file(configFilePath,'r'), Loader=Loader)
    
    s = ioServer(configFilePath, ioHubConfig)

    ioHub.devices.Computer.isIoHubProcess=True

    s.start()    
    
if __name__ == '__main__':
    prog=sys.argv[0]
    
    if len(sys.argv)==2:
        configFileName=sys.argv[1]
    else:
        configFileName=None
        
    run(configFilePath=configFileName)