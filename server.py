"""
ioHub Python Module

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
"""

import gevent
from gevent.server import DatagramServer
from gevent import Greenlet
import os,sys,gc
import time, bisect
import pythoncom
from collections import deque
import ioHub
from ioHub.devices import Computer,computer
currentMsec= Computer.currentMsec
currentUsec= Computer.currentUsec
             
class udpServer(DatagramServer):
    def __init__(self,ioHubServer,address,coder='msgpack'):
        self.iohub=ioHubServer
        self.feed=None
        self._inHighPriorityMode=False
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
        print " **** TO DO: Implement multipacket sending when size of response is > packet size **** " 
        
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
            return self.handleGetEvents(replyTo)
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
                except:
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
        currentEvents=[]
        eventBuffer=self.iohub.eventBuffer

        while len(eventBuffer)>0:
             e=eventBuffer.popleft()
             bisect.insort(currentEvents, e)       
        events=[e.I_tuple for e in currentEvents]
        
        if len(events)>0:
            self.sendResponse(('GET_EVENTS_RESULT',events),replyTo)
        else:
            self.sendResponse(('GET_EVENTS_RESULT', None),replyTo)
 
    def handleExperimentDeviceRequest(self,request,replyTo):
        request_type= request.pop(0)
        if request_type == 'EVENT_TX':
            exp_events=request.pop(0)
            for eventAsTuple in exp_events:
                self.iohub.experimentRuntimeDevice.eventCallback(eventAsTuple)
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
            
    def sendResponse(self,data,address):
        packet_data=self.pack(data)+'\r\n'
        self.socket.sendto(packet_data,address)         
           
    def clearEventBuffer(self):
        l= len(self.iohub.eventBuffer)
        self.iohub.eventBuffer.clear()
        return l
        
    def currentMsec(self):
        return currentMsec()

    def currentUsec(self):
        return currentUsec()
        
    def enableHighPriority(self,disable_gc=True):
        import psutil, os
        if self._inHighPriorityMode is False:
            if disable_gc:
                gc.disable()
            p = psutil.Process(os.getpid())
            p.nice=psutil.HIGH_PRIORITY_CLASS
            self._inHighPriorityMode=True

    def disableHighPriority(self):
        import psutil, os
        if self._inHighPriorityMode is True:
            gc.enable()
            p = psutil.Process(os.getpid())
            p.nice=psutil.NORMAL_PRIORITY_CLASS
            self._inHighPriorityMode=False
    
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
    def __init__(self,config=None):
        self._running=True
        
        self.config=config
        ioServer.eventBuffer=deque(maxlen=config['global_event_buffer'])
        self.emrt_file=None
        self.devices=[]
        self.deviceDict={}
        self.deviceMonitors=[]
        
        # start UDP service
        self.udpService=udpServer(self,':%d'%config['udpPort'])

        # dataStore setup
        if 'ioDataStore' in config and config['ioDataStore']['enable'] is True:
            self.createDataStoreFile(config['ioDataStore']['filename']+'.rt',config['ioDataStore']['filepath'],'w',config['ioDataStore']['storage_type'])
        
        # device configuration
        if len(config['monitor_devices']) > 0:
            import ioHub.devices as devices
            
        #built device list and config from yaml config settings
        for key,deviceConfig in config['monitor_devices'].iteritems():
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
                deviceInstance._addEventListener(self)

            # add event listeners for saving events
            if (self.emrt_file is not None) and ('saveEvents' in deviceConfig) and (deviceConfig['saveEvents'] is True):
                self.log("Event saving is being enabled for: %s"%deviceConfig['device_class'])
                deviceInstance._addEventListener(self.emrt_file)
            self.log("==============================")
        deviceDict=self.deviceDict
        iohub=self
        if (('Mouse' in deviceDict) or ('Keyboard' in deviceDict)) and computer.system == 'Windows':
            class pyHookDevice(object):
                def __init__(self):
                    import pyHook
                    self._hookManager=pyHook.HookManager()
                    
                    if 'Mouse' in deviceDict:
                        self._hookManager.MouseAll = deviceDict['Mouse'].eventCallback
                    if 'Keyboard' in deviceDict:
                        self._hookManager.KeyAll = deviceDict['Keyboard'].eventCallback
                    if 'Mouse' in deviceDict:
                        self._hookManager.HookMouse()    
                    if 'Keyboard' in deviceDict:
                        self._hookManager.HookKeyboard()
                        
                    iohub.log("WindowsHook PumpEvents Periodic Timer Created.")
        
                def _poll(self):
                    quit=pythoncom.PumpWaitingMessages()
                    if quit == 1:
                        raise KeyboardInterrupt()               

            hookMonitor=DeviceMonitor(pyHookDevice(),0.00375)
            
            self.deviceMonitors.append(hookMonitor)

    def processDeviceEvents(self,sleep_interval):
        while self._running:
            for device in self.devices:
                events=device._getEventBuffer()
                while len(events)>0:
                    evt=events.popleft()                    
                    e=device.getIOHubEventObject(evt,device.instance_code)
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
            self.emrt_file.log(currentUsec(),text,level)
        else:
            print ">> %d\t\t%d\t%s"%(currentUsec(),level,text)

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
        
        gevent.run()
        
        #print "ioServer Process Completed!"
   
    def _handleEvent(self,event):
        self.eventBuffer.append(event)
        
        
    def __del__(self):
        self.emrt_file.close()
   
################### End of Class Def. #########################

# ------------------ Main / Quickstart testing -------------------------



def run(configFile=None):
    from yaml import load, dump
    try:
        from yaml import CLoader as Loader, CDumper as Dumper
    except ImportError:
        self.log("*** Using Python based YAML Parsing")
        from yaml import Loader, Dumper

    ioHubConfig=load(file(configFile,'r'), Loader=Loader)
    
    s = ioServer(ioHubConfig)
    s.start()    
    
if __name__ == '__main__':
    prog=sys.argv[0]
    
    if len(sys.argv)==2:
        configFileName=sys.argv[1]
    else:
        configFileName=None
        
    run(configFile=configFileName)