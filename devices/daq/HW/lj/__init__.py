import ioHub

try:
    import LabJackPython
    from LabJackPython import LJ_dtU3, LJ_dtU6, LJ_dtUE9 , LJ_ctUSB, LJ_ctETHERNET, LJ_ctLJSOCKET
except:
    ioHub.print2err("Warning: Could not import LabJackPython DAQ.")

global _LJ_DAQS
_LJ_DAQS=[]

try:
    LJ_ConnectionDevices={LJ_ctUSB:[LJ_dtU3,LJ_dtU6,LJ_dtUE9,12], LJ_ctETHERNET:[LJ_dtUE9,]}#  , LJ_ctLJSOCKET:[]}
    for ljcType, ljDevices in LJ_ConnectionDevices.iteritems():
        for ljdType in ljDevices:
            ljDeviceList=LabJackPython.listAll(ljdType,ljcType)

            for ljd in ljDeviceList:
                ioHub.print2err("** Found LabJack Device:",ljd)
                _LJ_DAQS.append(ljd)
except:
    ioHub.print2err("Warning: Error looking for LabJack Devices")
    ioHub.printExceptionDetailsToStdErr()

if len(_LJ_DAQS) > 0:
    ioHub.print2err("\n")
    ioHub.print2err("Found %d LabJacks."%(len(_LJ_DAQS,)))
