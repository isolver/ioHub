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

from psychopy.iohub.util import OrderedDict,print2err, printExceptionDetailsToStdErr, ioHubError, createErrorResult,convertCamelToSnake
from psychopy.iohub.constants import DeviceConstants,EventConstants
from psychopy.iohub.devices import Computer, DeviceEvent, import_device        
from psychopy.iohub.devices.deviceConfigValidation import validateDeviceConfiguration
from psychopy.iohub.net import MAX_PACKET_SIZE
from psychopy.iohub import IO_HUB_DIRECTORY
from yaml import load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
        
currentSec= Computer.currentSec

import json
import msgpack
    
#noinspection PyBroadException,PyBroadException
class udpServer(DatagramServer):
    def __init__(self,ioHubServer,address,coder='msgpack'):
        self.iohub=ioHubServer
        self.feed=None
        self._running=True
        if coder == 'msgpack':
            self.iohub.log("ioHub Server configuring msgpack...")
            self.coder=msgpack
            self.packer=msgpack.Packer()
            self.pack=self.packer.pack
            self.unpacker=msgpack.Unpacker(use_list=True)
            self.unpack=self.unpacker.unpack      
            self.feed=self.unpacker.feed
        DatagramServer.__init__(self,address)
         
    def handle(self, request, replyTo):
        if self._running is False:
            return False
        
        self.feed(request[:-2])
        request = self.unpack()   
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
                self.sendResponse(createErrorResult('RPC_ATTRIBUTE_ERROR',
                                        msg="The method name referenced could not be found by the RPC server.",
                                        method_name=callable_name),
                                    replyTo)
                return False
                
            if result and callable(result):
                funcPtr=result
                try:
                    if args is None and kwargs is None:
                        result = funcPtr()
                    elif args and kwargs:
                        result = funcPtr(*args,**kwargs)
                    elif args and not kwargs:
                        result = funcPtr(*args)
                    elif not args and kwargs:
                        result = funcPtr(**kwargs)
                    edata=('RPC_RESULT',callable_name,result)
                    self.sendResponse(edata,replyTo)
                    return True
                except Exception,e:
                    self.sendResponse(createErrorResult('RPC_RUNTIME_ERROR',
                                      msg="An error occurred on the ioHub Server while evaulating an RPC request",
                                      method_name=callable_name,
                                      args=args,
                                      kwargs=kwargs,
                                      exception=str(e))
                                ,replyTo)
                    return False
            else:
                self.sendResponse(createErrorResult('RPC_NOT_CALLABLE_ERROR',
                                    msg="The method name give is not callable (it is not a method).",
                                    method_name=callable_name,
                                    resolved_result=str(result))
                                ,replyTo)
                return False
        elif request_type == 'STOP_IOHUB_SERVER':
            try:
                self.shutDown()
            except:
                printExceptionDetailsToStdErr
        else:
            self.sendResponse(createErrorResult('RPC_TYPE_NOT_SUPPORTED_ERROR',
                                    msg="The request type provided is not recognized by the ioHub Server.",
                                    request_type=request_type),
                                replyTo)
            return False
            
    def handleGetEvents(self,replyTo):
        try:
            currentEvents=list(self.iohub.eventBuffer)
            self.iohub.eventBuffer.clear()

            if len(currentEvents)>0:
                sorted(currentEvents, key=itemgetter(DeviceEvent.EVENT_HUB_TIME_INDEX))
                self.sendResponse(('GET_EVENTS_RESULT',currentEvents),replyTo)
            else:
                self.sendResponse(('GET_EVENTS_RESULT', None),replyTo)
            return True
        except Exception,e:
            self.sendResponse(createErrorResult('IOHUB_GET_EVENTS_ERROR',
                                    msg="An error occurred while events were being retrived from the ioHub Server",
                                    exception=str(e)),
                                replyTo)
            return False

    def handleExperimentDeviceRequest(self,request,replyTo):
        request_type= request.pop(0)
        if request_type == 'EVENT_TX':
            exp_events=request.pop(0)
            for eventAsTuple in exp_events:
                ioServer.deviceDict['Experiment']._nativeEventCallback(eventAsTuple)
            self.sendResponse(('EVENT_TX_RESULT',len(exp_events)),replyTo)
            return True
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
            if dclass.find('.') > 0:
                for dname, dev in ioServer.deviceDict.iteritems():
                    if dname.endswith(dclass):
                        dev=ioServer.deviceDict.get(dname,None)
                        break
            else:
                dev=ioServer.deviceDict.get(dclass,None)
            
            if dev is None:
                self.sendResponse(createErrorResult('IOHUB_DEVICE_ERROR',
                                        msg="An instance of the ioHub Device class provided is not enabled on the ioHub Server",
                                        device_class=dclass),
                                    replyTo)                
                return False
            
            try:
                method=getattr(dev,dmethod)
            except:
                self.sendResponse(createErrorResult('IOHUB_DEVICE_METHOD_ERROR',
                                        msg="Device class {0} does not have a method called {1}".format(dclass,dmethod)),
                                    replyTo)                
                return False
                
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
                return True
            except Exception, e:
                self.sendResponse(createErrorResult('RPC_DEVICE_RUNTIME_ERROR',
                                      msg="An error occurred on the ioHub Server while evaulating an Device RPC request",
                                      device=dclass,
                                      dmethod=dmethod,
                                      args=args,
                                      kwargs=kwargs,
                                      exception=str(e))
                                ,replyTo)
                return False
        elif request_type == 'GET_DEVICE_LIST':
            try:            
                dev_list=[]
                for d in self.iohub.devices:
                    dev_list.append((d.name,d.__class__.__name__))
                self.sendResponse(('GET_DEV_LIST_RESULT',len(dev_list),dev_list),replyTo)
                return True
            except Exception, e:
                printExceptionDetailsToStdErr()
                self.sendResponse(createErrorResult('RPC_DEVICE_RUNTIME_ERROR',
                                      msg="An error occurred on the ioHub Server while getting the Device list for the Experiment Process",
                                      devices=str(self.iohub.devices),
                                      dev_list=str(dev_list),
                                      exception=str(e))
                                ,replyTo)
                return False                

        elif request_type == 'GET_DEV_INTERFACE':
            dclass=request.pop(0)
            data=None
            if dclass in ['EyeTracker','DAQ']:
                for dname, hdevice in ioServer.deviceDict.iteritems():
                    if dname.endswith(dclass):
                        data=hdevice._getRPCInterface()
                        break
            else:
                dev=ioServer.deviceDict.get(dclass,None)
                if dev:                
                    data=dev._getRPCInterface()
                    
            if data:
                self.sendResponse(('GET_DEV_INTERFACE',data),replyTo)
                return True
            else:
                self.sendResponse(createErrorResult('GET_DEV_INTERFACE_ERROR',
                                        msg="An error occurred on the ioHub Server while retrieving device interface information.",
                                        device=dclass),
                                  replyTo)
                return False
        elif request_type == 'ADD_DEVICE':
            dclass_name=request.pop(0)
            dconfig_dict=request.pop(1)
            
            # add device to ioSever here
            data=self.iohub.createNewMonitoredDevice(dclass_name,dconfig_dict)
            # end adding device to server
                    
            if data:
                self.sendResponse(('ADD_DEVICE',data),replyTo)
                return True
            else:
                self.sendResponse(createErrorResult('ADD_DEVICE_ERROR',
                                        msg="An error occurred on the ioHub Server while adding a device to be monitored.",
                                        device=dclass_name,
                                        config=dconfig_dict),
                                  replyTo)
            return False
        else:
            self.sendResponse(createErrorResult('DEVICE_RPC_TYPE_NOT_SUPPORTED_ERROR',
                                    msg="The device RPC request type provided is not recognized by the ioHub Server.",
                                    request_type=request_type),
                              replyTo)
            return False
            
    def sendResponse(self,data,address):
        packet_data=None
        try:
            max_size=MAX_PACKET_SIZE/2-20
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
            print2err('Error trying to send data to experiment process:')
            print2err('data length:',len(data))
            print2err("=============================")            
            printExceptionDetailsToStdErr()
            print2err("=============================")            

            first_data_element="NO_DATA_AVAILABLE"            
            if data:
                print2err('Data was [{0}]'.format(data))     
                try:    
                    first_data_element=data[0]
                except:
                    pass
                    
            packet_data_length=0
            if packet_data:
                packet_data_length=len(packet_data)
                print2err('packet Data length: ',len(packet_data))

            data=createErrorResult('IOHUB_SERVER_RESPONSE_ERROR',       
                                   msg="The ioHub Server Failed to send the intended response.",
                                   first_data_element=str(first_data_element),
                                   packet_data_length=packet_data_length,
                                   max_packet_size=max_size)
            packet_data=self.pack(data)+'\r\n'
            packet_data_length=len(packet_data)            
            self.socket.sendto(packet_data,address)
            
    def setExperimentInfo(self,experimentInfoList):
        self.iohub.experimentInfoList=experimentInfoList
        if self.iohub.emrt_file:
            exp_id= self.iohub.emrt_file.createOrUpdateExperimentEntry(experimentInfoList) 
            self.iohub._experiment_id=exp_id
            self.iohub.log("Current Experiment ID: %d"%(self.iohub._experiment_id))
            return exp_id
        return False
        
    def checkIfSessionCodeExists(self,sessionCode):
        try:
            if self.iohub.emrt_file:
                return self.iohub.emrt_file.checkIfSessionCodeExists(sessionCode)
            return False
        except:
            printExceptionDetailsToStdErr()
            
    def createExperimentSessionEntry(self,sessionInfoDict):
        self.iohub.sessionInfoDict=sessionInfoDict
        if self.iohub.emrt_file:
            sess_id= self.iohub.emrt_file.createExperimentSessionEntry(sessionInfoDict)
            self.iohub._session_id=sess_id
            self.iohub.log("Current Session ID: %d"%(self.iohub._session_id))
            return sess_id
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
        return self.iohub.clearEventBuffer()

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
        try:
            self.disableHighPriority()
            self.iohub.shutdown()
            self._running=False
            self.stop()
        except:
            print2err("Error in ioSever.shutdown():")
            printExceptionDetailsToStdErr()
            sys.exit(1)

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
    _logMessageBuffer=deque(maxlen=128)
    def __init__(self, rootScriptPathDir, config=None):
        self._session_id=None
        self._experiment_id=None

        self.log("Server Time Offset: {0}".format(Computer.globalClock.getLastResetTime()))

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
        self._hookDevice=None
        ioServer.eventBuffer=deque(maxlen=config.get('global_event_buffer',2048))

        self._running=True
        
        # start UDP service
        self.udpService=udpServer(self,':%d'%config.get('udpPort',9000))

        from .. import iohub
        # read temp paths file
        iohub.data_paths=None
        try:
            expJsonPath=os.path.join(rootScriptPathDir,'exp.paths')
            f=open(expJsonPath,'r')
            iohub.data_paths=json.loads(f.read())
            f.flush()
            f.close()
            os.remove(expJsonPath)
        except:
            pass


        try:
            # initial dataStore setup
            if 'data_store' in config:
                experiment_datastore_config=config.get('data_store')
                default_datastore_config_path=os.path.join(IO_HUB_DIRECTORY,'datastore','default_datastore.yaml')
                #print2err('default_datastore_config_path: ',default_datastore_config_path)
                _dslabel,default_datastore_config=load(file(default_datastore_config_path,'r'), Loader=Loader).popitem()

                for default_key,default_value in default_datastore_config.iteritems():
                    if default_key not in experiment_datastore_config:
                        experiment_datastore_config[default_key]=default_value
                                
                if experiment_datastore_config.get('enable', True):
                    #print2err("Creating ioDataStore....")

                    if iohub.data_paths is None:
                        resultsFilePath=rootScriptPathDir
                    else:
                        resultsFilePath=iohub.data_paths[u'IOHUB_DATA']
                    self.createDataStoreFile(experiment_datastore_config.get('filename','events')+'.hdf5',resultsFilePath,'a',experiment_datastore_config)

                    #print2err("Created ioDataStore.")
        except:
            print2err("Error during ioDataStore creation....")
            printExceptionDetailsToStdErr()


        #built device list and config from initial yaml config settings
        try:
            for iodevice in config.get('monitor_devices',()):
                for device_class_name,deviceConfig in iodevice.iteritems():
                    #print2err("======================================================")
                    #print2err("Started load process for: {0}".format(device_class_name))
                    self.createNewMonitoredDevice(device_class_name,deviceConfig)
        except:
            print2err("Error during device creation ....")
            printExceptionDetailsToStdErr()
            raise ioHubError("Error during device creation ....")


        # initial time offset
        #print2err("-- ioServer Init Complete -- ")
        

    def processDeviceConfigDictionary(self,device_module_path, device_class_name, device_config_dict,default_device_config_dict):
        for default_config_param,default_config_value in default_device_config_dict.iteritems():
            if default_config_param not in device_config_dict:            
                if isinstance(default_config_value,(dict,OrderedDict)):
                    #print2err("dict setting value in default config not in device config:\n\nparam: {0}\n\nvalue: {1}\n============= ".format(default_config_param,default_config_value ))
                    device_param_value=dict()
                    self.processDeviceConfigDictionary(None,None,
                                                       device_param_value,default_config_value)
                    device_config_dict[default_config_param]=device_param_value
                else:
                    device_config_dict[default_config_param]=default_config_value
                    
        # Start device config verification.
        if device_module_path and  device_class_name:
            #print2err('** Verifying device configuartion: {0}\t{1}'.format(device_module_path,device_class_name))
    
            device_config_errors=validateDeviceConfiguration(device_module_path,device_class_name,device_config_dict)
    
            for error_type, error_list in device_config_errors.iteritems():
                if len(error_list)>0:
                    device_errors=self._all_device_config_errors.get(device_module_path,{})
                    device_errors[error_type]=error_list                
                    self._all_device_config_errors[device_module_path]=device_errors

    def createNewMonitoredDevice(self,device_class_name,deviceConfig):
        #print2err("#### createNewMonitoredDevice: ",device_class_name)
        self._all_device_config_errors=dict()

        try:
            device_instance=None
            device_config=None
            device_event_ids=None
            event_classes=None
            
            device_instance_and_config=self.addDeviceToMonitor(device_class_name,deviceConfig)
            if device_instance_and_config:
                device_instance,device_config,device_event_ids,event_classes=device_instance_and_config 
                DeviceConstants.addClassMapping(device_instance.__class__)
                EventConstants.addClassMappings(device_instance.__class__,device_event_ids,event_classes)
            else:
                print2err('## Device was not started by the ioHub Server: ',device_class_name)
                raise ioHubError("Device config validation failed")
                
        except:
            print2err("Error during device creation ....")
            printExceptionDetailsToStdErr()
            raise ioHubError("Error during device creation ....")


        # Update DataStore Structure if required.
        try:            
            if self.emrt_file is not None:
                self.emrt_file.updateDataStoreStructure(device_instance,event_classes)
        except:
            print2err("Error while updating datastore for device addition:",device_instance,device_event_ids)
            printExceptionDetailsToStdErr()


        self.log("Adding ioServer and DataStore event listeners......")

        # add event listeners for saving events
        if self.emrt_file is not None:
            if device_config['save_events']:
                device_instance._addEventListener(self.emrt_file,device_event_ids)
                self.log("DataStore listener for device added: device: %s eventIDs: %s"%(device_instance.__class__.__name__,device_event_ids))
                #print2err("DataStore listener for device added: device: %s eventIDs: %s"%(device_instance.__class__.__name__,device_event_ids))
            else:
                #print2err("DataStore saving disabled for device: %s"%(device_instance.__class__.__name__,))
                self.log("DataStore saving disabled for device: %s"%(device_instance.__class__.__name__,))
        else:
            #print2err("DataStore Not Evabled. No events will be saved.")
            self.log("DataStore Not Enabled. No events will be saved.")
    

        # Add Device Monitor for Keyboard or Mouse device type 
        deviceDict=ioServer.deviceDict
        iohub=self
        if device_class_name in ('Mouse','Keyboard'):
            if Computer.system == 'win32':  
                if self._hookDevice is None:
                    iohub.log("Creating pyHook Monitors....")
                    #print2err("Creating pyHook Monitor....")
    
                    class pyHookDevice(object):
                        def __init__(self):
                            import pyHook
                            self._hookManager=pyHook.HookManager()
                            
                            self._mouseHooked=False
                            self._keyboardHooked=False
                            
                            if device_class_name == 'Mouse':
                                #print2err("Hooking Mouse.....")
                                self._hookManager.MouseAll = deviceDict['Mouse']._nativeEventCallback
                                self._hookManager.HookMouse()
                                self._mouseHooked=True
                            elif device_class_name == 'Keyboard':
                                #print2err("Hooking Keyboard.....")
                                self._hookManager.KeyAll = deviceDict['Keyboard']._nativeEventCallback
                                self._hookManager.HookKeyboard()
                                self._keyboardHooked=True
    
                            #iohub.log("WindowsHook PumpEvents Periodic Timer Created.")
                
                        def _poll(self):
                            import pythoncom
                            # PumpWaitingMessages returns 1 if a WM_QUIT message was received, else 0
                            if pythoncom.PumpWaitingMessages() == 1:
                                raise KeyboardInterrupt()               
        
                    #print2err("Creating pyHook Monitor......")
                    self._hookDevice=pyHookDevice()
                    hookMonitor=DeviceMonitor(self._hookDevice,0.00375)
                    self.deviceMonitors.append(hookMonitor)
                
                    #print2err("Created pyHook Monitor.")
                else:
                    #print2err("UPDATING pyHook Monitor....")
                    if device_class_name == 'Mouse' and self._hookDevice._mouseHooked is False:
                        #print2err("Hooking Mouse.....")
                        self._hookDevice._hookManager.MouseAll = deviceDict['Mouse']._nativeEventCallback
                        self._hookDevice._hookManager.HookMouse()
                        self._hookDevice._mouseHooked=True
                    elif device_class_name == 'Keyboard' and self._hookDevice._keyboardHooked is False:
                        #print2err("Hooking Keyboard.....")
                        self._hookDevice._hookManager.KeyAll = deviceDict['Keyboard']._nativeEventCallback
                        self._hookDevice._hookManager.HookKeyboard()
                        self._hookDevice._keyboardHooked=True
                
                    #print2err("Finished Updating pyHook Monitor.")
                
            elif Computer.system == 'linux2':
                # TODO: consider switching to xlib-ctypes implementation of xlib
                # https://github.com/garrybodsworth/pyxlib-ctypes
                from .devices import pyXHook
                if self._hookManager is None:
                    #iohub.log("Creating pyXHook Monitors....")
                    self._hookManager = pyXHook.HookManager()
                    self._hookManager._mouseHooked=False
                    self._hookManager._keyboardHooked=False

                    if device_class_name == 'Keyboard':
                        #print2err("Hooking Keyboard.....")
                        self._hookManager.HookKeyboard()
                        self._hookManager.KeyDown = deviceDict['Keyboard']._nativeEventCallback
                        self._hookManager.KeyUp = deviceDict['Keyboard']._nativeEventCallback
                        self._hookManager._keyboardHooked=True
                    elif device_class_name == 'Mouse':                
                        #print2err("Hooking Mouse.....")
                        self._hookManager.HookMouse()
                        self._hookManager.MouseAllButtonsDown = deviceDict['Mouse']._nativeEventCallback
                        self._hookManager.MouseAllButtonsUp = deviceDict['Mouse']._nativeEventCallback
                        self._hookManager.MouseAllMotion = deviceDict['Mouse']._nativeEventCallback
                        self._hookManager._mouseHooked=True
    
                    #print2err("Starting pyXHook.HookManager.....")
                    self._hookManager.start()
                    #iohub.log("pyXHook Thread Created.")
                    #print2err("pyXHook.HookManager thread created.")
                else:
                    #iohub.log("Updating pyXHook Monitor....")
                    if device_class_name == 'Keyboard' and self._hookManager._keyboardHooked is False:
                        #print2err("Hooking Keyboard.....")
                        self._hookManager.HookKeyboard()
                        self._hookManager.KeyDown = deviceDict['Keyboard']._nativeEventCallback
                        self._hookManager.KeyUp = deviceDict['Keyboard']._nativeEventCallback
                        self._hookManager._keyboardHooked=True
                    if device_class_name == 'Mouse' and self._hookManager._mouseHooked is False:                
                        #print2err("Hooking Mouse.....")
                        self._hookManager.HookMouse()
                        self._hookManager.MouseAllButtonsDown = deviceDict['Mouse']._nativeEventCallback
                        self._hookManager.MouseAllButtonsUp = deviceDict['Mouse']._nativeEventCallback
                        self._hookManager.MouseAllMotion = deviceDict['Mouse']._nativeEventCallback
                        self._hookManager._mouseHooked=True
                    #iohub.log("Finished Updating pyXHook Monitor....")
                    

            else: # OSX
                if self._hookDevice is None:
                    self._hookDevice=[]
                    
                if  device_class_name == 'Mouse' and 'Mouse' not in self._hookDevice:
                    #print2err("Hooking OSX Mouse.....")
                    mouseHookMonitor=DeviceMonitor(deviceDict['Mouse'],0.004)
                    self.deviceMonitors.append(mouseHookMonitor)
                    deviceDict['Mouse']._CGEventTapEnable(deviceDict['Mouse']._tap, True)
                    self._hookDevice.append('Mouse')
                    #print2err("Done Hooking OSX Mouse.....")
                if device_class_name == 'Keyboard'  and 'Keyboard' not in self._hookDevice:
                    #print2err("Hooking OSX Keyboard.....")
                    kbHookMonitor=DeviceMonitor(deviceDict['Keyboard'],0.004)
                    self.deviceMonitors.append(kbHookMonitor)
                    deviceDict['Keyboard']._CGEventTapEnable(deviceDict['Keyboard']._tap, True)
                    self._hookDevice.append('Keyboard')
                    #print2err("DONE Hooking OSX Keyboard.....")


            return [device_class_name, device_config['name'], device_instance._getRPCInterface()]

                    
    def addDeviceToMonitor(self,device_class_name,device_config):
        device_class_name=str(device_class_name)
        
        self.log("Handling Device: %s"%(device_class_name,))
        #print2err("addDeviceToMonitor:\n\tdevice_class: {0}\n\texperiment_device_config:{1}\n".format(device_class_name,device_config))

        DeviceClass=None
        class_name_start=device_class_name.rfind('.')
        iohub_sub_mod='psychopy.iohub.'
        iohub_submod_path_length=len(iohub_sub_mod)
        device_module_path=iohub_sub_mod+'devices.'
        if class_name_start>0:
            device_module_path="{0}{1}".format(device_module_path,device_class_name[:class_name_start].lower())   
            device_class_name=device_class_name[class_name_start+1:]
        else:
            device_module_path="{0}{1}".format(device_module_path,device_class_name.lower())

        #print2err("Processing device, device_class_name: {0}, device_module_path: {1}".format(device_class_name, device_module_path))
         
        dconfigPath=os.path.join(IO_HUB_DIRECTORY,device_module_path[iohub_submod_path_length:].replace('.',os.path.sep),"default_%s.yaml"%(device_class_name.lower()))

#        print2err("dconfigPath: {0}, device_module_path: {1}\n".format(dconfigPath,device_module_path))
#        print2err("Loading Device Defaults file:\n\tdevice_class: {0}\n\tdeviceConfigFile:{1}\n".format(device_class_name,dconfigPath))
        self.log("Loading Device Defaults file: %s"%(device_class_name,))

        _dclass,default_device_config=load(file(dconfigPath,'r'), Loader=Loader).popitem()

        #print2err("Device Defaults:\n\tdevice_class: {0}\n\tdefault_device_config:{1}\n".format(device_class_name,default_device_config))
        
        self.processDeviceConfigDictionary(device_module_path, device_class_name, device_config,default_device_config)

        if device_module_path in self._all_device_config_errors:
            # Complete device config verification.
            print2err("**** ERROR: DEVICE CONFIG ERRORS FOUND ! NOT LOADING DEVICE: ",device_module_path)
            device_config_errors=self._all_device_config_errors[device_module_path]
            for error_type,errors in device_config_errors.iteritems():
                print2err("%s count %d:"%(error_type,len(errors)))
                for error in errors:
                    print2err("\t{0}".format(error))
                print2err("\n")
            return None
        
        DeviceClass,device_class_name,event_classes=import_device(device_module_path,device_class_name)
        #print2err("Updated Experiment Device Config:\n\tdevice_class: {0}\n\tdevice_config:{1}\n".format(device_class_name,default_device_config))
            
        if device_config.get('enable',True):
            self.log("Searching Device Path: %s"%(device_class_name,))
            self.log("Creating Device: %s"%(device_class_name,))
            #print2err("Creating Device: %s"%(device_class_name,))
            
            if DeviceClass._iohub_server is None:
                DeviceClass._iohub_server=self
            
            if device_class_name != 'Display' and DeviceClass._display_device is None:
                DeviceClass._display_device=ioServer.deviceDict['Display']  
                
            deviceInstance=DeviceClass(dconfig=device_config)

            self.log("Device Instance Created: %s"%(device_class_name,))
            #print2err("Device Instance Created: %s"%(device_class_name,))

            self.devices.append(deviceInstance)
            ioServer.deviceDict[device_class_name]=deviceInstance

            if 'device_timer' in device_config:
                interval = device_config['device_timer']['interval']
                self.log("%s has requested a timer with period %.5f"%(device_class_name, interval))
                dPoller=DeviceMonitor(deviceInstance,interval)
                self.deviceMonitors.append(dPoller)

            eventIDs=[]
            monitor_events_list=device_config.get('monitor_event_types',[])
            if isinstance(monitor_events_list,(list,tuple)):
                for event_class_name in monitor_events_list:
                    eventIDs.append(getattr(EventConstants,convertCamelToSnake(event_class_name[:-5],False)))
            
            self.log("{0} Instance Event IDs To Monitor: {1}".format(device_class_name,eventIDs))
            #ioHub.print2err("{0} Instance Event IDs To Monitor: {1}".format(device_class_name,eventIDs))

            # add event listeners for streaming events
            if device_config.get('stream_events') is True:
                self.log("Online event access is being enabled for: %s"%device_class_name)
                # add listener for global event queue
                deviceInstance._addEventListener(self,eventIDs)
                #ioHub.print2err("ioServer event stream listener added: device=%s eventIDs=%s"%(device_class_name,eventIDs))
                self.log("Standard event stream listener added for ioServer for event ids %s"%(str(eventIDs),))
                # add listener for device event queue
                deviceInstance._addEventListener(deviceInstance,eventIDs)
                #  ioHub.print2err("%s event stream listener added: eventIDs=%s"%(device_class_name,eventIDs))
                self.log("Standard event stream listener added for class %s for event ids %s"%(device_class_name,str(eventIDs)))

            return deviceInstance,device_config,eventIDs,event_classes


    def log(self,text,level=None):
        try:
            log_time=currentSec()
            exp=self.deviceDict.get('Experiment',None)
            if exp and self._session_id and self._experiment_id:
                while len(self._logMessageBuffer):
                    lm=self._logMessageBuffer.popleft()
                    #print2err('>>>!!! Logging BACKLOGGED LogEvent: ',lm,", ",(exp, self._session_id, self._experiment_id))
                    exp.log(*lm)
                #print2err('>>>!!! Logging LogEvent: ',(text,level,log_time),", ",(exp, self._session_id, self._experiment_id))
                exp.log(text,level,log_time)
            else:
                #print2err('>>>!!! Adding LogEvent to _logMessageBuffer: ',(text,level,log_time),", ",(exp, self._session_id, self._experiment_id))
                self._logMessageBuffer.append((text,level,log_time))
        except:
            printExceptionDetailsToStdErr()
            
    def createDataStoreFile(self,fileName,folderPath,fmode,ioHubsettings):
        from datastore import ioHubpyTablesFile
        self.closeDataStoreFile()                
        self.emrt_file=ioHubpyTablesFile(fileName,folderPath,fmode,ioHubsettings)                

    def closeDataStoreFile(self):
        if self.emrt_file:
            pytablesfile=self.emrt_file
            self.emrt_file=None
            pytablesfile.flush()
            pytablesfile.close()
            
    def processDeviceEvents(self,sleep_interval):
        while self._running:
            self._processDeviceEventIteration()
            gevent.sleep(sleep_interval)

    def _processDeviceEventIteration(self):
        for device in self.devices:
            try:
                events=device._getNativeEventBuffer()
                #if events and len(events)>0:
                #    ioHub.print2err("_processDeviceEventIteration.....", device._event_listeners)
                while len(events)>0:
                    evt=events.popleft()
                    e=device._getIOHubEventObject(evt)
                    if e is not None:
                        for l in device._getEventListeners(e[DeviceEvent.EVENT_TYPE_ID_INDEX]):
                            l._handleEvent(e)
            except:
                printExceptionDetailsToStdErr()
                print2err("Error in processDeviceEvents: ", device, " : ", len(events), " : ", e)
                print2err("Event type ID: ",e[DeviceEvent.EVENT_TYPE_ID_INDEX], " : " , EventConstants.getName(e[DeviceEvent.EVENT_TYPE_ID_INDEX]))
                print2err("--------------------------------------")

    def _handleEvent(self,event):
        #ioHub.print2err("ioServer Handle event: ",event)
        self.eventBuffer.append(event)

    def clearEventBuffer(self):
        l= len(self.eventBuffer)
        self.eventBuffer.clear()
        return l

    def shutdown(self):
        try:
            self._running=False
    
            if Computer.system=='linux2':
                if self._hookManager:
                    self._hookManager.cancel()
    
            while len(self.deviceMonitors) > 0:
                m=self.deviceMonitors.pop(0)
                m.running=False
            if self.eventBuffer:
                self.clearEventBuffer()
            try:
                self.closeDataStoreFile()
            except:
                pass
            while len(self.devices) > 0:
                d=self.devices.pop(0)
                try:
                    if d is not None:
                        d._close()
                except:
                        pass
            gevent.sleep()
        except:
            print2err("Error in ioSever.shutdown():")
            printExceptionDetailsToStdErr()
            
    def __del__(self):
        self.shutdown()

