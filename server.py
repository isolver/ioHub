"""
ioHub
.. file: ioHub/server.py

Copyright (C) 2012-2013 iSolver Software Solutions
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
from ioHub import client,EventConstants
from ioHub.devices import Computer, DeviceEvent
try:
    from devices import filters
except:
    pass

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
                ioServer.deviceDict['ExperimentDevice']._nativeEventCallback(eventAsTuple)
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
            if dclass in ['EyeTracker','DAQ']:
                for dname, dev in ioServer.deviceDict.iteritems():
                    if dname.endswith(dclass):
                        dev=ioServer.deviceDict[dname]
                        break
            else:
                dev=ioServer.deviceDict[dclass]
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
            if dclass in ['EyeTracker','DAQ']:
                for dname, hdevice in ioServer.deviceDict.iteritems():
                    if dname.endswith(dclass):
                        data=hdevice._getRPCInterface()
                        break
            else:
                dev=ioServer.deviceDict[dclass]
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
            if data:
                ioHub.print2err('Data was [{0}]'.format(data))     
            if packet_data:
                ioHub.print2err('packet Data length: ',len(packet_data))
            ioHub.printExceptionDetailsToStdErr()

    def setExperimentInfo(self,experimentInfoList):
        self.iohub.experimentInfoList=experimentInfoList
        if self.iohub.emrt_file:
            return self.iohub.emrt_file.createOrUpdateExperimentEntry(experimentInfoList)           
        return False
        
    def checkIfSessionCodeExists(self,sessionCode):
        try:
            if self.iohub.emrt_file:
                return self.iohub.emrt_file.checkIfSessionCodeExists(sessionCode)
            return False
        except:
            ioHub.printExceptionDetailsToStdErr()
            
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

        if Computer.system=='Linux':
            if self.iohub._hookManager:
                self.iohub._hookManager.cancel()

        while len(self.iohub.deviceMonitors) > 0:
            m=self.iohub.deviceMonitors.pop(0)
            m.running=False
        self.clearEventBuffer()
        try:
            self.iohub.closeDataStoreFile()
        except:
            pass
        self.disableHighPriority()
        while len(self.iohub.devices) > 0:
            d=self.iohub.devices.pop(0)
            try:
                if d is not None:
                    d._close()
            except:
                    pass
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

        
class ioServer(object):
    eventBuffer=None
    deviceDict={}
    _logMessageBuffer=None
    def __init__(self, initial_time_offset, rootScriptPathDir, config=None):
        import ioHub
        Computer.isIoHubProcess=True
        Computer.globalClock=ioHub.ioClock(None,initial_time_offset)
        self._hookManager=None
        self.emrt_file=None
        self.config=config
        self.devices=[]
        self.deviceMonitors=[]
        self.sessionInfoDict=None
        self.experimentInfoList=None
        self.filterLookupByInput={}
        self.filterLookupByOutput={}
        self.filterLookupByName={}        
        ioServer.eventBuffer=deque(maxlen=config.get('global_event_buffer',2048))
        ioServer._logMessageBuffer=deque(maxlen=128)

        self._running=True
        
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

        try:
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
        except:
            ioHub.print2err("Error during ioDataStore creation....")
            ioHub.printExceptionDetailsToStdErr()

        try:
            #built device list and config from yaml config settings
            for iodevice in config.get('monitor_devices',()):
                for device_class,deviceConfig in iodevice.iteritems():
                    self.addDeviceToMonitor(device_class,deviceConfig)
        except:
            ioHub.print2err("Error during device creation ....")
            ioHub.printExceptionDetailsToStdErr()

        try:
            #built filter graph and config from yaml config settings
            for iofilters in config.get('filters',()):
                for filter_class,filterConfig in iofilters.iteritems():
                    self.addFilterToMonitor(filter_class,filterConfig)
        except:
            ioHub.print2err("Error during filter creation ....")
            ioHub.printExceptionDetailsToStdErr()

        self.log("Creating pyHook Monitors....")
        deviceDict=ioServer.deviceDict
        iohub=self
        if ('Mouse' in deviceDict or 'Keyboard' in deviceDict):
            if Computer.system == 'Windows':           
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
            elif Computer.system == 'Linux':
                # TODO: consider switching to xlib-ctypes implementation of xlib
                # https://github.com/garrybodsworth/pyxlib-ctypes
                import ioHub.devices.pyXHook
                
                self._hookManager = ioHub.devices.pyXHook.HookManager()
                self._hookManager.HookKeyboard()
                self._hookManager.HookMouse()
                self._hookManager.KeyDown = deviceDict['Keyboard']._nativeEventCallback
                self._hookManager.KeyUp = deviceDict['Keyboard']._nativeEventCallback
                self._hookManager.MouseAllButtonsDown = deviceDict['Mouse']._nativeEventCallback
                self._hookManager.MouseAllButtonsUp = deviceDict['Mouse']._nativeEventCallback
                self._hookManager.MouseAllMotion = deviceDict['Mouse']._nativeEventCallback
                self._hookManager.start()
                iohub.log("pyXHook Thread Created.")
                
        self.log("Time Offset: {0}".format(initial_time_offset))

    def addDeviceToMonitor(self,device_class,deviceConfig):
        self.log("Handling Device: %s"%(device_class,))
        if len(deviceConfig)==0:
            self.log("Loading Device Defaults file: %s"%(device_class,))
            dconfigPath=os.path.join(ioHub.IO_HUB_DIRECTORY,'devices',device_class,"default_%s.yaml"%(device_class))
            dclass,deviceConfig=load(file(dconfigPath,'r'), Loader=Loader).popitem()

        if deviceConfig.get('enable',True):
            deviceConfig.setdefault('name', device_class.lower())
            deviceConfig.setdefault('saveEvents', True)
            deviceConfig.setdefault('streamEvents', True)
            deviceConfig.setdefault('auto_report_events', True)
            deviceConfig.setdefault('event_buffer_length', 256)

            self.log("Searching Device Path: %s"%(device_class,))
            self.log("Creating Device: %s"%(device_class,))
            self.log("Creating Device: %s"%(device_class,))
            parentModule=ioHub.devices
            modulePathTokens=device_class.split('.')
            for mt in modulePathTokens:
                DeviceClass=getattr(parentModule,mt)
                if inspect.isfunction(DeviceClass):
                    DeviceClass()
                parentModule=DeviceClass
            self.log("Creating Device Instance: %s"%(device_class,))
            devconfig=deviceConfig
            devconfig['_ioServer']=self
            if DeviceClass.__name__.endswith('EyeTracker'):
                ioHub.devices.EyeTrackerEvent.PARENT_DEVICE=device_class
            if DeviceClass.__name__.endswith('DAQ'):
                ioHub.devices.DAQEvent.PARENT_DEVICE=device_class

            deviceInstance=DeviceClass(dconfig=devconfig)

            self.log(" Device Instance Created: %s"%(device_class,))

            self.devices.append(deviceInstance)
            ioServer.deviceDict[device_class]=deviceInstance

            if 'device_timer' in deviceConfig:
                interval = deviceConfig['device_timer']['interval']
                self.log("%s has requested a timer with period %.5f"%(device_class, interval))
                dPoller=DeviceMonitor(deviceInstance,interval)
                self.deviceMonitors.append(dPoller)

            # add event listeners for streaming events
            if deviceConfig.get('streamEvents',False) is True:
                self.log("Adding standard event stream listeners: %s"%(device_class,))

                eventIDs=[]
                for kn in deviceConfig.get('monitor_events',[]):
                    EventKlass=getattr(ioHub.devices,kn)
                    eventIDs.append(EventKlass.EVENT_TYPE_ID)

                self.log("Online event access is being enabled for: %s"%device_class)
                # add listener for global event queue
                deviceInstance._addEventListener(self,eventIDs)
                self.log("Standard event stream listener added for ioServer for event ids %s"%(str(eventIDs),))
                # add listener for device event queue
                deviceInstance._addEventListener(deviceInstance,eventIDs)
                self.log("Standard event stream listener added for class %s for event ids %s"%(device_class,str(eventIDs)))
                # add event listeners for saving events
            if (self.emrt_file is not None) and (deviceConfig.get('saveEvents',False) is True):
                self.log("Adding standard DataStore listener: %s"%(device_class,))
                self.log("Event saving is being enabled for: %s"%device_class)
                deviceInstance._addEventListener(self.emrt_file)
                self.log("Done with Device creation: %s"%(device_class,))

    def addFilterToMonitor(self,filter_class,filterConfig):
        self.log("Handling Filter: %s"%(filter_class,))
        if len(filterConfig)==0:
            self.log("Loading Filter Defaults file: %s"%(filter_class,))
            fconfigPath=os.path.join(ioHub.IO_HUB_DIRECTORY,'devices',filter_class,"default_%s.yaml"%(filter_class))
            fclass,deviceConfig=load(file(fconfigPath,'r'), Loader=Loader).popitem()

        if filterConfig.get('enable',True):
            self.log("Searching Filter Path: %s"%(filter_class,))
            self.log("Creating Filter: %s"%(filter_class,))
            self.log("Creating Filter: %s"%(filter_class,))
            parentModule=ioHub.devices
            modulePathTokens=filter_class.split('.')
            for mt in modulePathTokens:
                FilterClass=getattr(parentModule,mt)
                if inspect.isfunction(FilterClass):
                    FilterClass()
                parentModule=FilterClass
            self.log("Creating Filter Instance: %s"%(filter_class,))
            filterConfig['_ioServer']=self
            filterInstance=FilterClass(dconfig=filterConfig)
            self.log(" Filter Instance Created: %s"%(filter_class,))

            self.devices.append(filterInstance)
            ioServer.deviceDict[filter_class]=filterInstance

            # add event listeners for streaming events
            if filterConfig.get('streamEvents',True) is True:
                self.log("Adding standard event stream listeners for filter: %s"%(filter_class,))
                self.log("Online event access is being enabled for filter: %s"%filter_class)
                # add listener for global event queue
                filterInstance._addEventListener(self)
                self.log("ioHub Server event stream listener added for filter: %s"%(filter_class,))
                # add event listeners for saving events
            if (self.emrt_file is not None) and (filterConfig.get('saveEvents',False) is True):
                self.log("Adding standard DataStore listener for filter: %s"%(filter_class,))
                self.log("Event saving is being enabled for filter: %s"%filter_class)
                filterInstance._addEventListener(self.emrt_file)
                self.log("Done with Filter creation: %s"%(filter_class,))



            temp=filterConfig.get('input_events',[])
            tempdict={}
            for l in temp:
                for k,v in l.iteritems():
                    tempdict[k]=v

            for input_event_class_name, input_event_class_config in tempdict.iteritems():
                EventKlass=getattr(ioHub.devices,input_event_class_name)
                ioServer.deviceDict[str(EventKlass.PARENT_DEVICE)]._addEventListener(filterInstance,[EventKlass.EVENT_TYPE_ID,])
                self.log("Adding FilterDevice %s as listener to Device %s event type %s"%(filter_class,EventKlass.PARENT_DEVICE,str(EventKlass.EVENT_TYPE_ID)))



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

    def closeDataStoreFile(self):
        if self.emrt_file:
            pytablesfile=self.emrt_file
            self.emrt_file=None
            pytablesfile.flush()
            pytablesfile.close()

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

    def processDeviceEvents(self,sleep_interval):
        while self._running:
            self._processDeviceEventIteration()
            gevent.sleep(sleep_interval)

    def _processDeviceEventIteration(self):
        for device in self.devices:
            try:
                events=device._getNativeEventBuffer()
                #if events and len(events)>0:
                #    ioHub.print2err("_processDeviceEventIteration.....", device._eventListeners)
                while len(events)>0:
                    evt=events.popleft()
                    e=device._getIOHubEventObject(evt)
                    if e is not None:
                        #ioHub.print2err("ioHub event: ", e[DeviceEvent.EVENT_FILTER_ID_INDEX])
                        for l in device._getEventListeners(e[DeviceEvent.EVENT_TYPE_ID_INDEX]):
                            #ioHub.print2err("ioServer Handling event to: ",device)
                            l._handleEvent(e)
            except:
                ioHub.printExceptionDetailsToStdErr()
                ioHub.print2err("Error in processDeviceEvents: ", device, " : ", len(events), " : ", e)
                ioHub.print2err("Event type ID: ",e[DeviceEvent.EVENT_TYPE_ID_INDEX], " : " , EventConstants.getName(e[DeviceEvent.EVENT_TYPE_ID_INDEX]))
                ioHub.print2err("--------------------------------------")
                ioHub.print2err(EventConstants._classes)

                ioHub.print2err("--------------------------------------")

                eclass=EventConstants.getClass(e[DeviceEvent.EVENT_TYPE_ID_INDEX])
                ioHub.print2err("eclass: ",eclass)
                ioHub.print2err("Event array length: ", len(e), " should be : ", len(eclass.NUMPY_DTYPE)," : ",eclass.NUMPY_DTYPE)

    def _handleEvent(self,event):
        #ioHub.print2err("ioServer Handle event: ",event)
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