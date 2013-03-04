#import EyeTech
#import LC_Technologies
try:
    import SMI
except ImportError:
    import ioHub
    ioHub.print2err(" Could not import SMI eye tracker interface.")
except:
    ioHub.printExceptionDetailsToStdErr() 

try:
    import SR_Research
except ImportError:
    import ioHub
    ioHub.print2err(" Could not import SR_Research eye tracker interface.")
except:
    ioHub.printExceptionDetailsToStdErr() 

try:
    import Tobii
except ImportError:
    import ioHub
    ioHub.print2err(" Could not import Tobii eye tracker interface.")
except:
    ioHub.printExceptionDetailsToStdErr() 
