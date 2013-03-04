import traceback

import ioHub
import ioHub.external_libs
from ioHub.devices import Computer
import pylabjack
from pylabjack import u6 # Import the u6 class
import numpy as N
import os
import cStringIO


default_timer = ioHub.highPrecisionTimer

def runTest():
    dataFile = open(os.path.join(ioHub.IO_HUB_DIRECTORY,"examples","labjacktest.dat"), mode = 'w')

    Computer.enableHighPriority(False)

    # MAX_REQUESTS is the number of packets to be read.
    MAX_REQUESTS = 100
    #NUM_CHANNELS is the number of channels to read from
    NUM_CHANNELS=4

    #SCAN_RATE = Hz to scan all channels at. So NUM_CHANNELS * SCAN_RATE == SAMPLING_FREQ
    SCAN_RATES=[500,1000,1500,2000,4000,8000,10000,12000,14000]
    SCAN_RATE_GAIN=1.01
    SETTLING_FACTORS=[0,1]

    RESOLUTION_INDEX=[1,]

    d = u6.U6()
    #
    ## For applying the proper calibration to readings.
    d.getCalibrationData()
    #
    print "configuring U6 stream"
    #

    dataFile.write("scan_rate\tsettling_factor\tres_index\tread_time\tAIN_1V_E\tAIN_5V_I\tAIN_9V_E\tAIN_GND_I\n")

    for scan_rate in SCAN_RATES:
        for settling_factor in SETTLING_FACTORS:
            for res_index in RESOLUTION_INDEX:
                try:
                    d.streamConfig( NumChannels = NUM_CHANNELS, ChannelNumbers = range(NUM_CHANNELS),
                        ChannelOptions = [ 0, 0, 0 , 0 ], SettlingFactor = settling_factor,
                        ResolutionIndex = res_index, ScanFrequency = scan_rate*SCAN_RATE_GAIN )

                    output = cStringIO.StringIO()

                    print "started stream with scan_rate %d, settling_factor %d, res_index %d for %d packets."%(scan_rate,
                                                                                    settling_factor,res_index,MAX_REQUESTS)
                    missed = 0
                    dataCount = 0
                    packetCount = 0
                    stop=0

                    d.streamStart()
                    start = default_timer()
                    print "Start Time: ", start

                    for r in d.streamData():
                        read_time=default_timer()
                        if r is not None:
                            # Our stop condition
                            if dataCount >= MAX_REQUESTS:
                                d.streamStop()
                                print "stream stopped."
                                break

                            if r['errors'] != 0:
                                print "Error: %s ; " % r['errors'], default_timer()

                            if r['numPackets'] != d.packetsPerRequest:
                                print "----- UNDERFLOW : %s : " % r['numPackets'], ()

                            if r['missed'] != 0:
                                missed += r['missed']
                                print "+++ Missed ", r['missed']

                            try:
                                for ia in xrange(len(r['AIN0'])):
                                    output.write("%d\t%d\t%d\t%.6f\t%.9f\t%.9f\t%.9f\t%.9f\n"%(scan_rate,settling_factor,res_index,read_time,r['AIN0'][ia],r['AIN1'][ia],r['AIN2'][ia],r['AIN3'][ia]))
                            except:
                                print 'ERROR SAVING DATA:', len(r['AIN1'])
                                print "".join(i for i in traceback.format_exc())

                            #print "Average of" , len(r['AIN0']), "AIN0," , len(r['AIN1']) , "AIN1 reading(s):", len(r['AIN2']) , "AIN2 reading(s):",  len(r['AIN3']) , "AIN3 reading(s):",
                            #print sum(r['AIN0'])/len(r['AIN0']) , "," , sum(r['AIN1'])/len(r['AIN1']), "," , sum(r['AIN2'])/len(r['AIN2']), "," , sum(r['AIN3'])/len(r['AIN3'])

                            dataCount += 1
                            packetCount += r['numPackets']
                        else:
                            # Got no data back from our read.
                            # This only happens if your stream isn't faster than the
                            # the USB read timeout, ~1 sec.
                            print "No data", default_timer()
                except:
                    print "".join(i for i in traceback.format_exc())
                finally:
                    stop = default_timer()
                    runTime = (stop-start)

                    dataFile.write(output.getvalue())
                    output.close()

                    sampleTotal = packetCount * d.streamSamplesPerPacket
                    scanTotal = sampleTotal / NUM_CHANNELS #sampleTotal / NumChannels

                    print "%s requests with %s packets per request with %s samples per packet = %s samples total." % ( dataCount, (float(packetCount) / dataCount), d.streamSamplesPerPacket, sampleTotal )
                    print "%s samples were lost due to errors." % missed
                    sampleTotal -= missed
                    print "Adjusted number of samples = %s" % sampleTotal

                    print "Scan Rate : %s scans / %s seconds = %s Hz" % ( scanTotal, runTime, float(scanTotal)/runTime )
                    print "Sample Rate : %s samples / %s seconds = %s Hz" % ( sampleTotal, runTime, float(sampleTotal)/runTime )

                    print "The condition took %s seconds." % runTime
                    print '----------------------------------------------------'
    d.close()
    dataFile.close()


def readTestFile(filePath=None):
    if filePath is None:
        filePath=os.path.join(ioHub.IO_HUB_DIRECTORY,"examples","labjacktest.dat")
    return N.genfromtxt(filePath,delimiter='\t',names=True)

if __name__ == '__main__':
    import sys
    if sys.argv>1:
        pmode= sys.argv[1]
        if pmode == 'w':
            runTest()
        if pmode == 'r':
            d=readTestFile()
            print 'Loaded data: ',d.shape