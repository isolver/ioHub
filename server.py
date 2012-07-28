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
import ioDataStore
from ioDataStore import EMRTpyTablesFile
             
class udpServer(DatagramServer):
    def __init__(self,ioHubServer,address,coder='msgpack'):
        self.iohub=ioHubServer
        self.feed=None
        self._inHighPriorityMode=False
        
        if coder=='ujson':
            print " ioHub Server configuring ujson..."
            import ujson
            self.coder=ujson
            self.pack=ujson.encode
            self.unpack=ujson.decode
        elif coder == 'msgpack':
            print " ioHub Server configuring msgpack..."
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
                
                if not error:
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
        elif request_type == 'CMD_TX':
            exp_cmds=request.pop(0)
            print 'Should handle experiment CMDs: ', exp_cmds
            self.sendResponse(('CMD_TX_RESULT',len(exp_cmds)),replyTo)
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
    
    def closeDataStoreFile(self):
        if self.iohub.emrt_file:
            self.iohub.emrt_file.flush()
            self.iohub.emrt_file.close()
        self.iohub.emrt_file=None

    def createDataStoreFile(self,fileName,folderPath,fmode,ftype):        
        try:
            if ftype == 'pytables':
                self.closeDataStoreFile()
                self.iohub.emrt_file=EMRTpyTablesFile(fileName,folderPath,fmode)
                return True
            else:
                return ('RPC_ERROR','createDataStoreFile','Only DataStore File Type "pytables" is currently Supported, not %s'%str(ftype)) 
        except Exception, err:
            print "Error ruuning createDataStoreFile:", err
            return ('RPC_ERROR','createDataStoreFile',str(err))
    
    def registerDevice(self,deviceInstanceInfoDict):
        deviceInfo=deviceInstanceInfoDict
        if 'category' in deviceInfo:
            dcat=deviceInfo['category']
            if dcat in ioHub.DEVICE_CATEGORY_ID_LABEL:
                # continue registering device, resulting in it being added to devices list and a
                # deviceMonitor being created.
                pass
                # ......
            else:
                ioDeviceError("registerDevice ERROR: supplied device category is not recognized: %s"%(str(dcat)))
        else:
            ioDeviceError("registerDevice ERROR: supplied deviceInstanceInfo does not have a 'category' key")
            
    def currentMsec(self):
        return currentMsec()
    
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
            self.device.poll()
            gevent.sleep(self.sleep_interval)
            
class ioServer(object):
    eventBuffer=None 
    eventDictionary=None
    flushCounter=128
    def __init__(self,configFile=None):
        if configFile==None:
            self.config=None
        else:
            self.config=configFile
    
        ioServer.eventBuffer=deque(maxlen=4096)
        self.emrt_file=None
        self.devices=[]
        self.deviceMonitors=[]
        
        self.udpService=udpServer(self,':9000')

        defaults=ioHub.devices.Keyboard.getDefaultAtrributeValueDict()
        kb=ioHub.devices.Keyboard(**defaults)
        

        defaults=ioHub.devices.Mouse.getDefaultAtrributeValueDict()
        ms=ioHub.devices.Mouse(**defaults)
        
        defaults=ioHub.devices.ParallelPort.getDefaultAtrributeValueDict()
        pp=ioHub.devices.ParallelPort(**defaults)

        defaults=ioHub.devices.ExperimentRuntimeDevice.getDefaultAtrributeValueDict()
        self.experimentRuntimeDevice=ioHub.devices.ExperimentRuntimeDevice(**defaults)
        
        self.devices.extend([kb,ms,pp,self.experimentRuntimeDevice])
        
        ppMonitor=DeviceMonitor(pp,0.0001)
        self.deviceMonitors.append(ppMonitor)
        
        if computer.system == 'Windows':
            class pyHookDevice(object):
                def __init__(self):
                    import pyHook
                    self._hookManager=pyHook.HookManager()
                    self._hookManager.MouseAll = ms.eventCallback
                    self._hookManager.KeyAll = kb.eventCallback
                    self._hookManager.HookMouse()    
                    self._hookManager.HookKeyboard()
        
                def poll(self):
                    quit=pythoncom.PumpWaitingMessages()
                    if quit == 1:
                        raise KeyboardInterrupt()               

            hookMonitor=DeviceMonitor(pyHookDevice(),0.00375)
            
            self.deviceMonitors.append(hookMonitor)

    def processDeviceEvents(self,sleep_interval):
        numEventsForFlush=ioServer.flushCounter
        nevents=0
        
        addEventToFile=None
        flush=None
        if self.emrt_file:
            addEventToFile=self.emrt_file.addEventToFile
            flush=self.emrt_file.flush
        appendEvent=self.eventBuffer.append
        while 1:
            for device in self.devices:
                events=device.getEventBuffer()
                while len(events)>0:
                    evt=events.popleft()
                    e=device.getIOHubEventObject(evt,device.instance_code)
                    if device.events_ipc is True:
                        appendEvent(e)
                    if addEventToFile and device.data_presistance is True:
                        addEventToFile(e)
                        nevents+=1
                        if nevents==numEventsForFlush:
                            flush()
                            nevents=0
            gevent.sleep(sleep_interval)    
    # -------------------- I/O loop ---------------------------------

    def start(self):       
        print 'Receiving datagrams on :9000'
        self.udpService.start()

        for m in self.deviceMonitors:
            m.start()
        
        gevent.spawn(self.processDeviceEvents,0.0009)
        
        gevent.run()
        
    def __del__(self):
        self.emrt_file.close()
   
################### End of Class Def. #########################

# ------------------ Main / Quickstart testing -------------------------



def run(configFile=None):
    s = ioServer(configFile)
    s.start()    
    
if __name__ == '__main__':
    prog=sys.argv[0]
    
    if len(sys.argv)>1:
        configFileName=sys.argv[1]
    else:
        configFileName=None
        
    run(configFile=configFileName)