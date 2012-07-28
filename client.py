from gevent import socket
import sys
import ioHub
from ioHub.devices import Computer
currentMsec= Computer.currentMsec

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
 
    def receive(self):
        data, address = self.sock.recvfrom(self._rcvBufferLength)
        self.lastAddress=address
        if self.feed: # using msgpack
            self.feed(data[:-2])
            return self.unpack(),address          
        return self.unpack(data[:-2]),address

    def close(self):    
        self.sock.close()


class UDPClientConnection(SocketConnection):
    def __init__(self,remote_host='127.0.0.1',remote_port=9000,rcvBufferLength=1492,broadcast=False,blocking=1, timeout=1, coder=None):
        SocketConnection.__init__(self,remote_host=remote_host,remote_port=remote_port,rcvBufferLength=rcvBufferLength,broadcast=broadcast,blocking=blocking, timeout=timeout,coder=coder)
    def initSocket(self,**kwargs):
        #print 'UDPClientConnection being used'
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 64*1024) 
         
class ioHubClient(object):
    #outgoingEventBuffer=deque(maxlen=256)
    #incomingEventBuffer=deque(maxlen=1024)
    def __init__(self,config=None):
        coder='ujson'
        if config:
            coder=config['ioHub']['IPCcoder']
           
        # udp port setup
        self.udp_client = UDPClientConnection(coder=coder)
 
    # UDP communication with ioHost    
    def sendToHub(self,argsList,timeTxRx=False):
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
        
        # clear out any events built up in the Hub event Buffer
        -> RPC List: ('RPC','clearEventBuffer')
        -> Method Call:  result=sendToHub(('RPC','clearEventBuffer'))
        -> Result if OK: ('RPC_RESULT','clearEventBuffer',453)   # where 453 represents the total number of events cleared.
        -> Result if error occurred: (*_ERROR,*args), where *_ERROR is a possible ioHub RCP error type, 

        # get stats on the ioHub process, as a string.
        -> RPC List: ('RPC','getProcessInfoString')
        -> Method Call:  result=sendToHub(('RPC','getProcessInfoString'))
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
        
        -> Method : events=client.sendEvents([{event1_as_dict},{event2_as_dict},....}])
        -> Sends: List of experiment events, as dictionaries. You can convery an event object to a dictionary
                  representation by calling the_event.toDict(), which returns the_event as a dict.
        -> Response: ('SEND_EVENTS_RESULT',number_of_events_received)
        -> Error Return: Not defined.     
        '''
        startMsec=0
        endMsec=0
        if timeTxRx is True:
            startMsec=currentMsec()
        # send request to host, return is # bytes sent.
        bytes_sent=self.udp_client.sendTo(argsList)
        
        # what for response from host, return is result ( decoded already ), and Hub address (ip4,port).
        result,address=self.udp_client.receive()
        
        r = (result,bytes_sent,address)
        if not timeTxRx:
            return r
            
        endMsec=currentMsec()
        return (endMsec-startMsec),r

    def getEvents(self,timeTxRx=False):
        return self.sendToHub(('GET_EVENTS',),timeTxRx)
 
    def sendEvents(self,events,timeTxRx=False):
        stime=0
        etime=0
        if timeTxRx is True:
            stime=currentMsec()
            
        eventList=[]
        for e in events:
            eventList.append(e.asTuple())
        r = self.sendToHub(('EXP_DEVICE','EVENT_TX',eventList))
 
        if timeTxRx is True:
            etime=currentMsec()
            return etime-stime,r
        return r
        
    def sendCommands(self,commands,timeTxRx=False):
        stime=0
        etime=0
        if timeTxRx is True:
            stime=currentMsec()
            
        commandList=[]
        for e in commands:
            commandList.append(e.asTuple())
        r = self.sendToHub(('EXP_DEVICE','CMD_TX',commandList))
 
        if timeTxRx is True:
            etime=currentMsec()
            return etime-stime,r
        return r
    # client utility methods.

    def testConnection(self):
        return self.sendToHub(('RPC','getProcessInfoString'))
        
    def close(self): 
        self.udp_client.close()

    
'''      
if __name__ == '__main__':  
    SELECTED_TEST='GEVENT'
    AVAILABLE_TESTS={'GEVENT':{'ITERATIONS':1000},'SEVENTS':{'ITERATIONS':1000,'EVENT_COUNT':16},'ESTREAM':{'DURATION':10}}
    
    c = ioClient()
    results=[] 
    sum=0.0
    i=0
    r=c.clearEventBuffer()
    print 'clearBufferedEvents: ', r
    if SELECTED_TEST in AVAILABLE_TESTS:
        TEST_CONDITIONS=AVAILABLE_TESTS[SELECTED_TEST]
        
        if SELECTED_TEST == 'GEVENT':
            loops=TEST_CONDITIONS['ITERATIONS']
            bt=currentMsec()
            while i < loops:
                st= currentMsec()
                r=c.getEvents()
                #print 'return:',r
                rpcType,rpcFunction,events=r
                if events and len(events)>0:
                   results.append(events)
                   #print events
                   i+=1
                   et= currentMsec()
                   sum+=(et-st)
        elif SELECTED_TEST == 'ESTREAM':
            duration=TEST_CONDITIONS['DURATION']*60*1000
            bt=currentMsec()
            while currentMsec() < bt+duration:
                st= currentMsec()
                rpcType,rpcFunction,events=c.getEvents()
                if events and len(events)>0:
                   #results.append(events)
                   print events
                   i+=1
                   et= currentMsec()
                   sum+=(et-st)
        elif  SELECTED_TEST == 'SEVENTS':
            loops=TEST_CONDITIONS['ITERATIONS']
            ecount=TEST_CONDITIONS['EVENT_COUNT']
                   
            bt=currentMsec()
            while i < loops:
                elist=[]
                for x in xrange(ecount):
                    e=(100,currentMsec(),currentMsec()+1000.0,"This is the event message.","Obj_ref1","Obj_ref2",123,456)
                    elist.append(e)
               
                st= currentMsec()
                response=c.sendEvents(elist)
                results.append(response)
                i+=1
                et= currentMsec()
                sum+=(et-st)
            nowt=currentMsec()
            sumBytes=0
            sumEvents=0
            for r in results:
               sumBytes+=r[0]
               sumEvents+=r[1][2]
               
            print "Sent %d bytes ( %d experiment events, %.2f bytes // event avg.) in %.3f msec wall time. = %.3f bytes // sec"%(sumBytes,sumEvents,sumBytes/float(sumEvents),nowt-bt, (sumBytes/1000.0))
                    
    print SELECTED_TEST,"Average Delay: ", sum /i, i

    t1=currentMsec()
    rpc,func_name,ht=c.currentIOHubMsec()
    t2=currentMsec()
    
    print "Currrent Host / Local times",ht,(t2-t1),ht-t1,t2-ht

    print 'CLIENT STATS:'
    Computer.printProcessInfo()
    print '\n'
    print 'HUB STATS:'    
    r=c.getProcessInfoString()
    print r[2]
'''