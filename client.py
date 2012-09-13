"""
ioHub
.. file: ioHub/client.py

Copyright (C) 2012 Sol Simpson
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

from __builtin__ import object, dict, iter, classmethod, unicode, str, type, len
from exceptions import Exception

from gevent import socket
import os,sys
import time
import psutil
import ioHub
from ioHub.devices import Computer
from ioHub.devices.experiment import MessageEvent #,CommandEvent
import subprocess
from collections import deque
import struct
import numpy as N

currentMsec= Computer.currentMsec

class ioHubClientException(Exception):
    pass

class SocketConnection(object):
    def __init__(self,local_host=None,local_port=None,remote_host=None,remote_port=None,rcvBufferLength=1492, broadcast=False, blocking=0, timeout=0,coder=None):
        self._local_port= local_port
        self._local_host = local_host
        self._remote_host= remote_host
        self._remote_port = remote_port
        self._rcvBufferLength=rcvBufferLength
        self.lastAddress=None
        self.sock=None
        self.initSocket()
        self.coder=None
        self.feed=None
        self.configCoder(coder)

    def initSocket(self,broadcast=False,blocking=0, timeout=0):
        #print 'Default SocketConnection being used'
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if broadcast is True:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('@i', 1))

        if blocking is not 0:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.settimeout(timeout)
        self.sock.setblocking(blocking)

    #noinspection PyArgumentList
    def configCoder(self,coder):
        #print "** In configCoder...", coder
        if coder:
            if coder == 'ujson':
                import ujson
                self.coder=ujson
                self.pack=ujson.encode
                self.unpack=ujson.decode
                #print 'ujson:', self.pack
            elif coder =='msgpack':
                import msgpack
                self.coder=msgpack
                self.packer=msgpack.Packer()
                self.unpacker=msgpack.Unpacker(use_list=True)
                self.pack=self.packer.pack
                self.feed=self.unpacker.feed
                self.unpack=self.unpacker.unpack
                #print 'msgpack:', self.pack
            else:
                raise Exception ("Unknown coder type: %s. Must be either 'ujson' or 'msgpack'"%(str(coder),))

    def sendTo(self,data,address=None):
        #print 'DATA [%s] %s %s'%(data,self._remote_host, str(self._remote_port))
        if address is None:
            address=self._remote_host, self._remote_port
        d=self.pack(data)
        byte_count=len(d)+2
        #print 'Sending byte count of ',len(d)+2,type(d)
        self.sock.sendto(d+'\r\n',address)
        return byte_count

    #noinspection PyArgumentList
    def receive(self):
        try:
            data, address = self.sock.recvfrom(self._rcvBufferLength)
            self.lastAddress=address
            if self.feed: # using msgpack
                self.feed(data[:-2])
                return self.unpack(),address

            return self.unpack(data[:-2]),address
        except Exception as e:
            ioHubClientException(("IO_HUB_ERROR", "ioHubClient socket.receive ERROR",str(e)))
            return ("IO_HUB_ERROR", "ioHubClient socket.receive ERROR",str(e)),None

    def close(self):
        self.sock.close()


class UDPClientConnection(SocketConnection):
    def __init__(self,remote_host='127.0.0.1',remote_port=9000,rcvBufferLength=64*1024,broadcast=False,blocking=1, timeout=1, coder=None):
        SocketConnection.__init__(self,remote_host=remote_host,remote_port=remote_port,rcvBufferLength=rcvBufferLength,broadcast=broadcast,blocking=blocking, timeout=timeout,coder=coder)
    def initSocket(self,**kwargs):
        #print 'UDPClientConnection being used'
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 64*1024)

#
# The ioHubClientDevice is the ioHub client side representation of an ioHub device.
# It has a dynamically created list of methods that can be called
# (matching the list of methods for the device in the ioHub.devices module),
# however here, each results in an RPC call to the ioHub for the device, which returns
# the result.
#
class DeviceRPC(object):
    def __init__(self,sendToHub,device_class,method_name):
        self.device_class=device_class
        self.method_name=method_name
        self.sendToHub=sendToHub

    def __call__(self, *args,**kwargs):
        r = self.sendToHub(('EXP_DEVICE','DEV_RPC',self.device_class,self.method_name,args,kwargs))
        r=r[1:]
        if len(r)==1:
            return r[0]
        else:
            return r

class ioHubClientDevice(object):
    def __init__(self,hubClient,name,code,dclass):
        self.hubClient=hubClient
        self.user_label=name
        self.instance_code=code
        self.device_class=dclass

        r=self.hubClient.sendToHub(('EXP_DEVICE','GET_DEV_INTERFACE',dclass))
        self._methods=r[1]

    def __getattr__(self,name):
        if name in self._methods:
            return DeviceRPC(self.hubClient.sendToHub,self.device_class,name)

    def getRemoteMethodNames(self):
        return self._methods


#
# ioHubDevices is a class that contains an attribute (dynamically created)
# for each device that is created in the ioHub. These devices are each of type
# ioHubClientDevice. The attribute name for the device is the user_label / name
# given to the device by the user, so it must be a valid python attribute name.
# The ioHubClientDevice itself  has a list of methods that can be called
# (matching the list of methods for the device in the ioHub.devices module),
# however here, each results in an RPC call to the ioHub for the device, which returns
# the result.
#
class ioHubDevices(object):
    def __init__(self,hubClient):
        self.hubClient=hubClient

class ioHubClient(object):
    _replyDictionary=dict()

    def __init__(self,config,configAbsPath):
        self.ioHubConfig=config
        self.ioHubConfigAbsPath=configAbsPath
        # udp port setup
        self.udp_client = UDPClientConnection(coder=self.ioHubConfig['ipcCoder'])

        self.devices=ioHubDevices(self)
        self.deviceByLabel=dict()
        self.experimentID=None
        self.experimentSessionID=None

    def startServer(self):
            # start up ioHub using subprocess module so we can have it run for duration of experiment only
            run_script=os.path.join(ioHub.IO_HUB_DIRECTORY,'server.py')
            subprocessArgList=[sys.executable, run_script,self.ioHubConfigAbsPath]
            self._server_process = subprocess.Popen(subprocessArgList,stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            self.server_pid = self._server_process.pid
            self._psutil_server_process=psutil.Process(self.server_pid)

            #print "started ioHub Server subprocess %d"%self.server_pid

            hubonline=False

            server_output='hi there'
            while server_output:
                #stime=currentMsec()
                isDataAvail=self.serverStdOutHasData()
                if isDataAvail is True:
                    server_output=self.readServerStdOutLine().next()
                    #etime=currentMsec()
                    #print 'get ioHub line dur:',etime-stime,server_output
                    if server_output.rstrip() == 'IOHUB_READY':
                        hubonline=True
                        break
                else:
                    import time
                    time.sleep(0.0001)

            if hubonline is False:
                print "ioHub could not be contacted, exiting...."
                try:
                    self._server_process.terminate()
                except Exception as e:
                    raise ioHubClientException(e)
                finally:
                    sys.exit(1)


    def _get_maxsize(self, maxsize):
        if maxsize is None:
            maxsize = 1024
        elif maxsize < 1:
            maxsize = 1
        return maxsize

    def serverStdOutHasData(self, maxsize=256):
        #import pywintypes
        import msvcrt
        from win32pipe import PeekNamedPipe

        maxsize = self._get_maxsize(maxsize)
        conn=self._server_process.stdout

        if conn is None:
            return False
        try:
            x = msvcrt.get_osfhandle(conn.fileno())
            (read, nAvail, nMessage) = PeekNamedPipe(x, 0)
            if maxsize < nAvail:
                nAvail = maxsize
            if nAvail > 0:
                return True
        except Exception as e:
            raise ioHubClientException(e)

    def readServerStdOutLine(self):
        for line in iter(self._server_process.stdout.readline, ''):
            yield line

    def _calculateClientServerTimeOffset(self, sampleSize=100):
        results=N.zeros((sampleSize,2),dtype='f4')
        for i in xrange(sampleSize):     # make multiple calles to local and ioHub times to calculate 'offset' and 'delay' in calling the ioHub server time
            tc=Computer.currentMsec()    # get the local time 1
            ts=self.currentMsec()        # get the ioHub server time (this results in a RPC call and response from the server)
            tc2=Computer.currentMsec()   # get local time 2, to calculate e2e delay for the ioHub server time call
            results[i][0]=ts-tc          # calculate time difference between returned iohub server time, and 1 read local time (offset)
            results[i][1]=tc2-tc         # calculate delay / duration it took to make the call to the ioHub server and get reply
            time.sleep(0.001)            # sleep for a little before going next loop
        #print N.min(results,axis=0) ,N.max(results,axis=0) , N.average(results,axis=0), N.std(results,axis=0)
        return results

    def getDevices(self):
        return self.devices

    def createDeviceList(self,deviceList):
        for user_label,instance_code,device_class in deviceList:
            d=ioHubClientDevice(self,user_label,instance_code,device_class)
            self.devices.__dict__[user_label]=d
            self.deviceByLabel[user_label]=d

    # UDP communication with ioHost
    def sendToHub(self,argsList):
        '''
        General purpose UDP packet sending routine. For the most part,
        ioHub expect data to be sent json encoded using the ujson library
        ( it is fast ). You should send argsList, a tuple of the form:

        (resquest_type, [optional_callable_name for RPC], (optional_inner_list_or arguements, {optional:inner, dict:of, kwarg:arguements})

        The client currently blocks until your request is fulfilled and retuned to you.
        Any aysnc. version could be added if desired. Instead of using callbacks, I prefer the idea
        of the client sendiong a quest and getting a request ticket #. Client can then ask status of
        ticket based on mumber. When result is ready, it is sent back as the reply to the
        status request.

        RPC examples:

        # If the method if part of the ioHub class, just provide the method name and any args:

        # get current ioHub Time (msec.usec)
        -> RPC List: ('RPC','currentMsec')
        -> Method call: result=sendToHub(('RPC','currentMsec'))
        -> Result if OK: ('RPC_RESULT','currentMsec',1033.473)
        -> Result if error occurred: (*_ERROR,*args), where *_ERROR is a possible ioHub RCP error type,
        and *args is the data frovided with the error.

        # clear out any events built up in the Hub event Buffer-

        -
        -> Result if OK: ('RPC_RESULT','getProcessInfoString',".....see below .....")
        -> Result if error occurred: (*_ERROR,*args), where *_ERROR is a possible ioHub RCP error type,
        -> Example string output:
                    HUB STATS:
                    --------------------------------------
                    Process ( 8952 ):
                    psutil.Process(pid=8952, name='python.exe')Thread Count: 3
                    Thread Info:
                        thread(id=8776, user_time=16.0057026, system_time=4.8984314)
                        thread(id=9816, user_time=0.0, system_time=0.0)
                        thread(id=9452, user_time=0.0, system_time=0.0)

        Non-RCP Calls
        ++++++++++++++

        There are some calls to the Hub that are treated specially, to try and fast track their response.
        They are:

        getEvents
        +++++++++

        Get the current list of bufferred events from the ioHub. Currently there is no filtering
        etc. possible. Events are returned in chronological order 'WITHIN' each call to getEvents.
        -> Method : events=client.getEvents()
        -> Sends: ('GET_EVENTS',) message type
        -> Response: ('GET_EVENTS_RESULT',[{event1_as_dict},{event2_as_dict},....}])
                     or if no events are available: ('GET_EVENTS_RESULT', None)
        -> Error Return: Not defined.

        sendEvents
        +++++++++

        Send a list of Experiment Events to the ioHub.

        -> Method : events=client.sendEvents([{event1_as_tuple},{event2_as_tuple},....}])
        -> Sends: List of experiment events, as dictionaries. You can convert an event object to a list
                  representation by calling the_event._asList(), which returns the_event as a python list.
        -> Response: ('SEND_EVENTS_RESULT',number_of_events_received)
        -> Error Return: Not defined.
        '''
        # send request to host, return is # bytes sent.
        bytes_sent=self.udp_client.sendTo(argsList)

        # what for response from host, return is result ( decoded already ), and Hub address (ip4,port).
        result,address=self.udp_client.receive()

        ioHubClient._addResponseToHistory(result,bytes_sent,address)

        errorReply=self.isErrorReply(result)

        if errorReply:
            raise errorReply

        return result

    @classmethod
    def _addResponseToHistory(cls,result,bytes_sent,address):
        """

        """
        address=str(address)
        if address in cls._replyDictionary:
            cls._replyDictionary[address].append((result,bytes_sent))
        else:
            cls._replyDictionary[address]=deque(maxlen=128)
            cls._replyDictionary[address].append((result,bytes_sent))



    def sendExperimentInfo(self,experimentInfoDict):
        fieldOrder=(('experiment_id',0), ('code','') , ('title','') , ('description','')  , ('version','') , ('total_sessions_to_run',0))
        values=[]
        for key,defaultValue in fieldOrder:
            if key in experimentInfoDict:
                values.append(experimentInfoDict[key])
            else:
                values.append(defaultValue)

        r=self.sendToHub(('RPC','setExperimentInfo',(values,)))
        self.experimentID=r[2]
        return r[2]

    def sendSessionInfo(self,sessionInfoDict):
        if self.experimentID is None:
            raise ioHubClientException("Experiment ID must be set by calling sendExperimentInfo before calling sendSessionInfo.")
        if 'code' not in sessionInfoDict:
            raise ioHubClientException("code must be provided in sessionInfoDict ( StringCol(8) ).")
        if 'name' not in sessionInfoDict:
            sessionInfoDict['name']=''
        if 'comments' not in sessionInfoDict:
            sessionInfoDict['comments']=''
        if 'user_variables' not in sessionInfoDict:
            sessionInfoDict['user_variables']={}

        import ujson
        sessionInfoDict['user_variables']=ujson.encode(sessionInfoDict['user_variables'])

        r=self.sendToHub(('RPC','createExperimentSessionEntry',(sessionInfoDict,)))

        self.experimentSessionID=r[2]
        return r[2]

    def getEvents(self):
        r = self.sendToHub(('GET_EVENTS',))
        return r[1]

    def sendEvents(self,events):
        eventList=[]
        for e in events:
            eventList.append(e._asList())
        r=self.sendToHub(('EXP_DEVICE','EVENT_TX',eventList))
        return r

    def sendMessageEvent(self,text,prefix='',offset=0.0,usec_time=None):
        self.sendToHub(('EXP_DEVICE','EVENT_TX',[MessageEvent.createAsList(text,prefix=prefix,msg_offset=offset,usec_time=usec_time),]))
        return True

    def sendMessages(self,msgArgList):
        msgEvents=[]
        for msg in msgArgList:
            msgEvents.append(MessageEvent.createAsList(*msg))
        self.sendToHub(('EXP_DEVICE','EVENT_TX',msgEvents))
        return True

    #def sendCommands(self,cmdArgList):
    #    cmdEvents=[]
    #    for cmde in cmdArgList:
    #        cmdEvents.append(CommandEvent.createAsList(*cmde))
    #    self.sendToHub(('EXP_DEVICE','EVENT_TX',cmdEvents))
    #    return True

    #def sendCommandEvent(self,command,text,priority=255,prefix='',offset=0.0):
    #    self.sendToHub(('EXP_DEVICE','EVENT_TX',[CommandEvent.createAsList(command,text,priority=priority,prefix=prefix,msg_offset=offset),]))
    #    return True

    # client utility methods.
    def _getDeviceList(self):
        r=self.sendToHub(('EXP_DEVICE','GET_DEV_LIST'))
        return r[2]

    def shutDownServer(self):
        self.udp_client.sendTo(('RPC','shutDown'))
        self.udp_client.close()
        if self._psutil_server_process.is_running():
            print "Warning: Having to force kill ioHub Server process."
            self._psutil_server_process.kill()
        self._server_process=None
        self._psutil_server_process=None
        return True

    def currentSec(self):
        r=self.sendToHub(('RPC','currentSec'))
        return r[2]

    def currentMsec(self):
        r=self.sendToHub(('RPC','currentMsec'))
        return r[2]

    def currentUsec(self):
        r=self.sendToHub(('RPC','currentUsec'))
        return r[2]

    def getIoHubServerProcessAffinity(self):
        r=self.sendToHub(('RPC','getProcessAffinity'))
        return r[2]

    def setIoHubServerProcessAffinity(self, processorList):
        r=self.sendToHub(('RPC','setProcessAffinity',processorList))
        return r[2]

    def isErrorReply(self,data):
        """

        """
        if ioHub.isIterable(data) and len(data)>0:
            if ioHub.isIterable(data[0]):
                return False
            else:
                if (type(data[0]) in (str,unicode)) and data[0].find('ERROR')>=0:
                    return ioHubClientException(data)
                return False
        else:
            raise ioHubClientException('Response from ioHub should always be iterable and have a length > 0')
