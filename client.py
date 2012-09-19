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


class ioHubDevices(object):
    """
    ioHubDevices is a class that contains an attribute (dynamically created) for each device that is created in the ioHub.
    These devices are each of type ioHubClientDevice. The attribute name for the device is the user name given to
    the device by the user in the ioHub config file label: field, so it must be a valid python attribute name.

    Each ioHubClientDevice itself has a list of methods that can be called (matching the list of public methods for the
    device in the ioHub.devices module), however here, each results in an IPC call to the ioHub Server for the device,
    which returns the result to the experiment process.

    A user never uses this class directly, it is used internallby by the ioHubVlient class to dynamically build out
    the experiment process side representation of the ioHub Server device set.
    """
    def __init__(self,hubClient):
        self.hubClient=hubClient

class ioHubClient(object):
    """
    ioHubClient is the main experiment process side class that is responsible to communicating with the ioHub Server process.
    The and instance of the ioHubClient is created and associated with the self.hub attribute of the SimpleIOHubRuntime
    utility class.

    ioHubClient is responsible for for creating the ioHub Server Process, sending message requests to the ioHub server and
    reading the server process reply, as well as telling the ioHub server when to close down and disconnect. The ioHubClient also
    has an experiment side representation of the devices that have been registered with the ioHub for monitoring, which
    can be accessed via the ioHubClient's devices attribute.

    If using the SimpleIOHubRuntime utility class to create your experiment, an instance of this class is created
    for you automatically and is accessable via self.hub.
    """
    _replyDictionary=dict()
    def __init__(self,config,configAbsPath):

        # A dictionary containing the ioHub configuration file settings
        self.ioHubConfig=config

        # the path to the ioHub configuration file itself.
        self.ioHubConfigAbsPath=configAbsPath

        # udp port setup
        self.udp_client = UDPClientConnection(coder=self.ioHubConfig['ipcCoder'])

        # the dynamically generated object that contains an attribute for each device registed for monitoring
        # with the ioHub server so that devices can be accessed experiment process side by device name.
        self.devices=ioHubDevices(self)

        # a dictionary that holds the same devices represented in .devices, but stored in a dictionary using the device
        # name as the dictionary key
        self.deviceByLabel=dict()

        # attribute to hold the current experiment ID that has been created by the ioHub ioDataStore if saving data to the
        # ioHub hdf5 file type.
        self.experimentID=None

        # attribute to hold the current experiment session ID that has been created by the ioHub ioDataStore if saving data to the
        # ioHub hdf5 file type.
        self.experimentSessionID=None

    def startServer(self):
        """
        Starts the ioHub Server Process, storing it's process id, and creating the experiment side device representation
        for IPC access to public device methods.
        """

        # TODO: Save ioHub Server ID to a local file so when a client starts the pid can be read and if it is still
        #       running, it can be killed before starting another instance of the ioHub server.

        # start up ioHub using subprocess module so we can have it run for duration of experiment only
        run_script=os.path.join(ioHub.IO_HUB_DIRECTORY,'server.py')
        subprocessArgList=[sys.executable, run_script,self.ioHubConfigAbsPath]

        # start subprocess, get pid, and get psutil process object for affinity and process priority setting
        self._server_process = subprocess.Popen(subprocessArgList,stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.server_pid = self._server_process.pid
        self._psutil_server_process=psutil.Process(self.server_pid)

        # wait for server to send back 'IOHUB_READY' text over stdout, indicating it is running
        # and ready to receive network packets
        hubonline=False
        server_output='hi there'
        while server_output:
            isDataAvail=self._serverStdOutHasData()
            if isDataAvail is True:
                server_output=self._readServerStdOutLine().next()
                #etime=currentMsec()
                #print 'get ioHub line dur:',etime-stime,server_output
                if server_output.rstrip() == 'IOHUB_READY':
                    hubonline=True
                    break
            else:
                import time
                time.sleep(0.0001)

        # If ioHub server did not repond correctly, terminate process and exit the program.
        if hubonline is False:
            print "ioHub could not be contacted, exiting...."
            try:
                self._server_process.terminate()
            except Exception as e:
                raise ioHubClientException(e)
            finally:
                sys.exit(1)

    def _get_maxsize(self, maxsize):
        """
        Used by startServer pipe reader code.
        """
        if maxsize is None:
            maxsize = 1024
        elif maxsize < 1:
            maxsize = 1
        return maxsize

    def _serverStdOutHasData(self, maxsize=256):
        """
        Used by startServer pipe reader code. Allows for async check for data on pipe in windows.
        """
        #  >> WIN32_ONLY
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
        # << WIN32_ONLY
        except Exception as e:
            raise ioHubClientException(e)

    def _readServerStdOutLine(self):
        """
        Used by startServer pipe reader code. Reads a line from the ioHub server stdout. This is blocking.
        """
        for line in iter(self._server_process.stdout.readline, ''):
            yield line

    def _calculateClientServerTimeOffset(self, sampleSize=100):
        """
        Calculates 'sampleSize' experimentTime and ioHub Server time process offsets by calling currentMsec localally
        and via IPC to the ioHub server process repeatedly, as ewell as calculating the round trip time it took to get the server process time in each case.
        Puts the 'sampleSize' salculates in a 2D numpy array, index [i][0] = server_time - local_time offset, index [i][1]
        = local_time after call to server_time - local_time before call to server_time.

        In Windows, since direct QPC implementation is used, offset should == delay to within 100 usec or so.
        """
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

    def _createDeviceList(self):
        """
        Populate the devices attribute object with the registered devices of the ioHub. Each ioHub device becomes an attribute
        of the devices instance, with the attribute name == the name give the device in the ioHub configuration file.
        Each device in allows access to the pupic method interface of the device via transparent IPC calls to the ioHub server process
        from the expriment process.
        """
        # get the list of devices registered with the ioHub
        deviceList=self._getDeviceList()

        # create an experiment process side device object to allow access to the public interface of the
        # ioHub device via transparent IPC.
        for user_label,instance_code,device_class in deviceList:
            d=ioHubClientDevice(self,user_label,instance_code,device_class)
            self.devices.__dict__[user_label]=d
            self.deviceByLabel[user_label]=d

    # UDP communication with ioHost
    def sendToHub(self,argsList):
        """
        General purpose message sending routine,  used to send a message from the experiment process to the ioHub server
        process, and then wait for the reply from the server process before returning.

        For the most part, ioHub accesps data send either encoded using the msgpack library or json encoded using the
        ujson library ( it is fast ). Which is used is specified in the ioHub configuration file. By default msgpack is selected,
        as it seems to be as fast as ujson, but it compresses the data by up to 40 - 50% for transmission.

        All messages sent to the ioHub have the following simple format:

        (resquest_type, [optional_callable_name_fo_IPC], ( [optional_list_of_args], {optional_dict_of_kw_args} ) )

        The currently supported request types are:

        #. RPC
        #. GET_EVENTS
        #. EXP_DEVICE

        Every request to the ioHub server is sent a response, even if it is just to indicate the request was receive and
        if it was processed successfully or not. All responses from the ioHub server are in the form:

        (response_type, *response_values)

        The current ioHub resposne types are:

        #. RPC_RESULT
        #. GET_EVENTS_RESULT
        #. DEV_RPC_RESULT
        #. GET_DEV_LIST_RESULT
        #. GET_DEV_INTERFACE
        #. IOHUB_ERROR
        #. RPC_ERROR

        The client currently blocks until the request is fulfilled and and a response is received from the ioHub server.

        TODO: An aysnc. version could be added if desired. Instead of using callbacks, I prefer the idea of the client sending
        a request and getting a request ticket # back from the ioHub server. The Client can then ask the ioHub Server
        for the status of the ticket based on number. When the ticket number result is ready, it is sent back as the reply
        to the status request.
        """
        # send request to host, return is # bytes sent.
        bytes_sent=self.udp_client.sendTo(argsList)

        # wait for response from ioHub server, return is result ( decoded already ), and Hub address (ip4,port).
        result,address=self.udp_client.receive()

        # store result received in an address based dictionary (incase we ever support multiple ioHub Servers)
        ioHubClient._addResponseToHistory(result,bytes_sent,address)

        # check if the reply is an error or not. If it is, raise the error.
        errorReply=self.isErrorReply(result)
        if errorReply:
            raise errorReply

        #Otherwise return the result
        return result

    @classmethod
    def _addResponseToHistory(cls,result,bytes_sent,address):
        """
        Adds a response from the ioHub to an ip:port based dictionary. Not used right now, but may be useful if we ever support
        a client connecting to > 1 ioHub.
        """
        address=str(address)
        if address in cls._replyDictionary:
            cls._replyDictionary[address].append((result,bytes_sent))
        else:
            cls._replyDictionary[address]=deque(maxlen=128)
            cls._replyDictionary[address].append((result,bytes_sent))



    def sendExperimentInfo(self,experimentInfoDict):
        """
        Sends the experiment info from the experiment config file to the ioHub Server, which passes it to the ioDataStore,
        determines if the experiment already exists in the experiment file based on 'experiment_code', and returns a new
        or existing experiment ID based on that criteria.
        """
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
        """
        Sends the experiment session info from the experiment config file and the values entered into the session dialog
        to the ioHub Server, which passes it to the ioDataStore, determines if the experiment already exists in the
        experiment file based on 'experiment_code', and returns a new or existing experiment ID based on that criteria.
        """
        if self.experimentID is None:
            raise ioHubClientException("Experiment ID must be set by calling sendExperimentInfo before calling sendSessionInfo.")
        if 'code' not in sessionInfoDict:
            raise ioHubClientException("Code must be provided in sessionInfoDict ( StringCol(8) ).")
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
        """
        Requests the current list of device events from the device wide event buffer in the ioHub server. The events are
        returned and the global ioHub server event buffer is cleared.
        """
        r = self.sendToHub(('GET_EVENTS',))
        return r[1]

    def sendEvents(self,events):
        """
        Send 1 - N Experiment Events (currently Messages) to the ioHub for storage.
        """
        eventList=[]
        for e in events:
            eventList.append(e._asList())
        r=self.sendToHub(('EXP_DEVICE','EVENT_TX',eventList))
        return r

    def sendMessageEvent(self,text,prefix='',offset=0.0,usec_time=None):
        """
        Create and send a MessageEvent to the ioHub Server for storage with the rest of the event data.

        Args:
          text (str): The text message for the message event. Can be up to 128 chracters in length.
          prefix (str): A 1 - 3 character prefix for the message that can be used to sort or group messages by 'types'
          offset (float): The offset to apply to the time stamp of the message event. If you send the event before or after
          the time the event actually occurred, and you know what the offset value is, you can provide it here and it will
          be applied to the ioHub time stampe for the event.
          usec_time: Since (at least on Windows currently) if you use the ioHub timers, the timebase of the experiment process
          is identical to that of the ioHub server process, then you can specific the ioHub time for experiment events
          right in the experiment process itself.
        """
        self.sendToHub(('EXP_DEVICE','EVENT_TX',[MessageEvent.createAsList(text,prefix=prefix,msg_offset=offset,usec_time=usec_time),]))
        return True

    def sendMessages(self,msgArgList):
        """
        Same as the sendMessage method, but accepts a list of lists of message arguments, so you can have N messages
        created and sent at once.
        """
        msgEvents=[]
        for msg in msgArgList:
            msgEvents.append(MessageEvent.createAsList(*msg))
        self.sendToHub(('EXP_DEVICE','EVENT_TX',msgEvents))
        return True

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
