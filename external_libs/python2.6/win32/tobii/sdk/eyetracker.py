
#
# Generated on: 2011-01-25T13:53:55.389+01:00
#

from tobii.sdk.basic import BasicEyetracker
from tobii.sdk.utils.events import Events
from tobii.sdk._native import tobiisdkpy

from tobii.sdk.types import *

from tobii.sdk import converters
from tobii.sdk.converters import ParamStackReader
from tobii.sdk.xds import Converter
#from zope.interface.adapter import _convert_None_to_Interface

# Helper Types

class CalibrationStartedEventArgs:
    def __init__(self):
        pass

class CalibrationStoppedEventArgs:
    def __init__(self):
        pass

class HeadMovementBoxChangedEventArgs:
    def __init__(self):
        pass
    
class AuthorizeChallenge(object):
    def __init__(self):        
        """
        The realm id for this challenge
        """
        self.RealmId = long()
        """
        The encryption algorithm for this challenge
        """
        self.Algorithm = long()
        """
        The challenge data
        """
        self.ChallengeData = Blob()


class Configuration(object):
    def __init__(self):        
        self.Root = Node()


class ConfigurationKey(object):
    def __init__(self):        
        self.Key = Node()


class HeadMovementBox(object):
    def __init__(self):        
        self.Point1 = Point3D()
        self.Point2 = Point3D()
        self.Point3 = Point3D()
        self.Point4 = Point3D()
        self.Point5 = Point3D()
        self.Point6 = Point3D()
        self.Point7 = Point3D()
        self.Point8 = Point3D()


class XConfiguration(object):
    def __init__(self):        
        self.UpperLeft = Point3D()
        self.UpperRight = Point3D()
        self.LowerLeft = Point3D()

class UnitInfo(object):
    def __init__(self):        
        self.SerialNumber = str()
        self.Model = str()
        self.Generation = str()
        self.FirmwareVersion = str()


class PayperuseInfo(object):
    def __init__(self):        
        """
        Whether PayPerUse is enabled for this eyetracker.
        """
        self.Enabled = bool()
        """
        The realm to authorize if PayPerUse is enabled.
        """
        self.Realm = long()
        """
        Whether the client has already been authorized.
        """
        self.Authorized = bool()
        
class Extension(object):
    def __init__(self):
        self.ProtocolVersion = long()
        self.ExtensionId = long()
        self.Name = str()
        self.Realm = long()



class EyetrackerEvents(Events):
    __events__ = ("OnCalibrationStarted", "OnCalibrationStopped", "OnFramerateChanged", "OnHeadMovementBoxChanged", "OnXConfigurationChanged", "OnGazeDataReceived", "OnError")


class Eyetracker(BasicEyetracker):
    def __init__(self, message_passer):
        BasicEyetracker.__init__(self, message_passer)
        
        self.events = EyetrackerEvents()
        
        self._do_subscribe (1040, BasicEyetracker.ChannelHandlerFunctor(self._event_converter_CalibrationStarted, self._event_CalibrationStarted))
        self._do_subscribe (1050, BasicEyetracker.ChannelHandlerFunctor(self._event_converter_CalibrationStopped, self._event_CalibrationStopped))
        self._do_subscribe (1640, BasicEyetracker.ChannelHandlerFunctor(self._event_converter_FramerateChanged, self._event_FramerateChanged))
        self._do_subscribe (1410, BasicEyetracker.ChannelHandlerFunctor(self._event_converter_HeadMovementBoxChanged, self._event_HeadMovementBoxChanged))
        self._do_subscribe (1450, BasicEyetracker.ChannelHandlerFunctor(self._event_converter_XConfigurationChanged, self._event_XConfigurationChanged))
        self._do_subscribe (1280, BasicEyetracker.ChannelHandlerFunctor(self._event_converter_GazeDataReceived, self._event_GazeDataReceived))
        
        self._on_error_connection = self._message_passer.add_error_handler(self._on_error)
        

    def _on_error(self, error):
        self.events.OnError(error)
        
    def GetAuthorizeChallenge(self, realmId, algorithms, callback = None, *args, **kwargs):
        """
        Parameters:
            realmId: The realm to unauthorize
            algorithms: A list of encryption algorithms
        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=self._response_converter_AuthorizeChallenge,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        params.push_uint32 (realmId)
        params.push_vector_uint32 (algorithms)
        
        self._message_passer.execute_request (1900,
                                              params,
                                              response_handler)
        if response_callback is None:
            return response_handler.wait_for_result() 
                    

    def _response_converter_AuthorizeChallenge(self, payload):
        #  opcode: 1900
        reader = ParamStackReader(payload) 
        response = AuthorizeChallenge()
        response.RealmId = reader.pop()  # element: realm_ (type: uint32)
        response.Algorithm = reader.pop()  # element: algorithm (type: uint32)
        response.ChallengeData = reader.pop()  # element: challenge_data (type: blob)
        
        return response


    def ValidateChallengeResponse(self, realmId, algorithm, responseData, callback = None, *args, **kwargs):
        """
        Parameters:
            realmId: The realm to unauthorize
            algorithm: A encryption algorithm used for this challenge
            responseData: The challenge response data
        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=None,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        params.push_uint32 (realmId)
        params.push_uint32 (algorithm)
        params.push_blob (responseData)
        
        self._message_passer.execute_request (1910,
                                              params,
                                              response_handler)
        
        if response_callback is None:
            return response_handler.wait_for_result()


    def EnumerateFramerates(self, callback = None, *args, **kwargs):
        """
        Returns an enumeration of all framerates supported by this eyetracker.

        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=self._response_converter_AvailableFramerates,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        
        self._message_passer.execute_request (1630,
                                              params,
                                              response_handler)
        
        if response_callback is None:
            return response_handler.wait_for_result()
                    

    def _response_converter_AvailableFramerates(self, payload):
        #  opcode: 1630
        reader = ParamStackReader(payload) 
        return reader.pop()  # element: framerates (type: vector_fixed15x16)
        
        
    def SetFramerate(self, framerate, callback = None, *args, **kwargs):
        """
        Sets the eyetracker framerate.

        Parameters:
            framerate: The desired framerate. Must be one of the values returned by the enumerate framerate method
        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)
                # conversation: framerate_set
        #    archetype: request-response
        #       opcode: 1620
        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=None,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        params.push_float32_as_fixed_15x16 (framerate)
        
        self._message_passer.execute_request (1620,
                                              params,
                                              response_handler)
        
        if response_callback is None:
            return response_handler.wait_for_result()
                    

    def GetFramerate(self, callback = None, *args, **kwargs):
        """
        gets the current eyetracker framerate

        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)
                # conversation: framerate_get
        #    archetype: request-response
        #       opcode: 1610
        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=self._response_converter_FramerateInfo,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        
        self._message_passer.execute_request (1610,
                                              params,
                                              response_handler)
        
        if response_callback is None:
            return response_handler.wait_for_result()
                    

    def _response_converter_FramerateInfo(self, payload):
        #  opcode: 1610
        reader = ParamStackReader(payload) 
        return reader.pop()  # element: framerate (type: fixed15x16)    
        
        
    def _event_converter_FramerateChanged(self, payload):
        #    event: FramerateChanged
        #  channel: 1640
        reader = ParamStackReader(payload)
        data = reader.pop()  # element: framerate (type: fixed15x16)
        
        return data
                    
    def _event_FramerateChanged(self, error, event_args):
        self.events.OnFramerateChanged(error, event_args)        
        

    def GetLowblinkMode(self, callback = None, *args, **kwargs):

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)
                # conversation: lowblink_get_enabled
        #    archetype: request-response
        #       opcode: 1920
        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=self._response_converter_LowblinkMode,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        
        self._message_passer.execute_request (1920,
                                              params,
                                              response_handler)
        
        if response_callback is None:
            return response_handler.wait_for_result()
                    

    def _response_converter_LowblinkMode(self, payload):
        #  opcode: 1920
        reader = ParamStackReader(payload) 
        return reader.pop() > 0 # element: enabled (type: uint32)
    

    def SetLowblinkMode(self, enabled, callback = None, *args, **kwargs):
        """
        Parameters:
            enabled: not documented
        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)
                # conversation: lowblink_set_enabled
        #    archetype: request-response
        #       opcode: 1930
        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=None,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        params.push_uint32 (enabled)
        
        self._message_passer.execute_request (1930,
                                              params,
                                              response_handler)
        
        if response_callback is None:
            return response_handler.wait_for_result()
   
   
        
    def DumpImages(self, count, frequency, callback = None, *args, **kwargs):
        """
        Parameters:
            count: not documented
            frequency: not documented
        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)
                # conversation: dump_images
        #    archetype: request-response
        #       opcode: 1500
        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=None,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        params.push_uint32 (count)
        params.push_uint32 (frequency)
        
        self._message_passer.execute_request (1500,
                                              params,
                                              response_handler)
        
        if response_callback is None:
            return response_handler.wait_for_result()
                    

    def GetDiagnosticReport(self, include_images, callback = None, *args, **kwargs):
        """
        Returns a diagnostic report.

        Parameters:
            include_images: not documented
        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)
                # conversation: get_diagnostic_report
        #    archetype: request-response
        #       opcode: 1510
        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=self._response_converter_DiagnosticReport,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        params.push_uint32 (include_images)
        
        self._message_passer.execute_request (1510,
                                              params,
                                              response_handler)
        
        if response_callback is None:
            return response_handler.wait_for_result()
                    

    def _response_converter_DiagnosticReport(self, payload):
        #  opcode: 1510
        reader = ParamStackReader(payload) 
        return reader.pop()  # element: report (type: blob)
    
    
    
    def SetUnitName(self, name, callback = None, *args, **kwargs):
        """
        Sets the eyetracker name.

        Parameters:
            name: The desired name. Can only contain alphanumeric characters, punctuations or spaces
        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)
                # conversation: name_set
        #    archetype: request-response
        #       opcode: 1710
        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=None,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        params.push_string (name)
        
        self._message_passer.execute_request (1710,
                                              params,
                                              response_handler)
        
        if response_callback is None:
            return response_handler.wait_for_result()
                            

    def GetUnitName(self, callback = None, *args, **kwargs):
        """
        gets the eyetracker name

        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=self._response_converter_NameInfo,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        
        self._message_passer.execute_request (1700,
                                              params,
                                              response_handler)

        if response_callback is None:
            return response_handler.wait_for_result()                    

    def _response_converter_NameInfo(self, payload):
        #  opcode: 1700
        reader = ParamStackReader(payload) 
        return reader.pop()  # element: name (type: string)
          
                 
    def GetUnitInfo(self, callback = None, *args, **kwargs):
        """
        Returns information about the eyetracker

        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=self._response_converter_UnitInfo,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        
        self._message_passer.execute_request (1420,
                                              params,
                                              response_handler)

        if response_callback is None:
            return response_handler.wait_for_result()                    
                    

    def _response_converter_UnitInfo(self, payload):
        #  opcode: 1420
        reader = ParamStackReader(payload) 
        response = UnitInfo()
        response.SerialNumber = reader.pop()  # element: serial (type: string)
        response.Model = reader.pop()  # element: model (type: string)
        response.Generation = reader.pop()  # element: generation (type: string)
        response.FirmwareVersion = reader.pop()  # element: version (type: string)
        
        return response


    def GetPayperuseInfo(self, callback = None, *args, **kwargs):
        """
        Returns PayPerUse info about the eyetracker

        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=self._response_converter_PayPerUseInfo,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        
        self._message_passer.execute_request (1600,
                                              params,
                                              response_handler)

        if response_callback is None:
            return response_handler.wait_for_result()                    
                    

    def _response_converter_PayPerUseInfo(self, payload):
        #  opcode: 1600
        reader = ParamStackReader(payload) 
        response = PayperuseInfo()
        response.Enabled = reader.pop() > 0 # element: enabled (type: uint32)
        response.Realm = reader.pop()  # element: realm (type: uint32)
        response.Authorized = reader.pop() > 0 # element: authorized (type: uint32)
        
        return response        

    def StartCalibration(self, callback = None, *args, **kwargs):
        """
        Puts the eyetracker into the calibration state

        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=None,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        
        self._message_passer.execute_request (1010,
                                              params,
                                              response_handler)
        
        if response_callback is None:
            return response_handler.wait_for_result() 
        
                    
    def StopCalibration(self, callback = None, *args, **kwargs):
        """
        Makes the eyetracker leave the calibration state

        """
        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)
 
        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=None,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        
        self._message_passer.execute_request (1020,
                                              params,
                                              response_handler)

        if response_callback is None:
            return response_handler.wait_for_result() 


    def ClearCalibration(self, callback = None, *args, **kwargs):
        """
        Deletes all samples from the calibration under construction buffer.
         This method should be called before starting a new calibration

        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=None,
                                                                  response_callback=response_callback)       
        params = tobiisdkpy.ParamStack()
        
        self._message_passer.execute_request (1060,
                                              params,
                                              response_handler)

        if response_callback is None:
            return response_handler.wait_for_result() 



    def _event_converter_CalibrationStarted(self, payload):
        #    event: CalibrationStarted
        #  channel: 1040
        data = CalibrationStartedEventArgs()        
        return data
                    

    def _event_CalibrationStarted(self, error, event_args):
        self.events.OnCalibrationStarted(error, event_args)
                    

    def _event_converter_CalibrationStopped(self, payload):
        #    event: CalibrationStopped
        #  channel: 1050
        data = CalibrationStoppedEventArgs()        
        return data
                    

    def _event_CalibrationStopped(self, error, event_args):
        self.events.OnCalibrationStopped(error, event_args)


    def AddCalibrationPoint(self, point, callback = None, *args, **kwargs):
        """
        Collects calibration data for a specific calibration point.

        Parameters:
            point: Position of the calibration target point on the screen. The point must be in normalized coordinates, i e the point (0.0,0.0) corresponds to the upper left corner on the screen and the point (1.0,1.0) corresponds to the lower right corner of the screen
        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)
                # conversation: begin_add_point_2
        #    archetype: request-response
        #       opcode: 1030
        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=None,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        params.push_float64_as_fixed_22x41 (point.x)
        params.push_float64_as_fixed_22x41 (point.y)
        params.push_uint32 (3)
        
        self._message_passer.execute_request (1030,
                                              params,
                                              response_handler)
        
        if response_callback is None:
            return response_handler.wait_for_result()                     

                    

    def RemoveCalibrationPoint(self, point, callback = None, *args, **kwargs):
        """
        Removes all data associated with a specific calibration point from
         the in-construction calibration buffer. Does not affect the currently
         set calibration. The caller can decide if data should be removed from
         both eyes or from one specific eye.

        Parameters:
            point: The calibration point to clear.
        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=None,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        params.push_float64_as_fixed_22x41 (point.x)
        params.push_float64_as_fixed_22x41 (point.y)
        params.push_uint32 (3)
        
        self._message_passer.execute_request (1080,
                                              params,
                                              response_handler)
        
        if response_callback is None:
            return response_handler.wait_for_result()
                    

    def ComputeCalibration(self, callback = None, *args, **kwargs):
        """
        Computes new calibration parameters based on the data in the
         in-construction buffer. The data and calibration parameters is copied to the
         calibration in use buffer if the call succeeds.

        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=None,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        
        self._message_passer.execute_request (1070,
                                              params,
                                              response_handler)
        if response_callback is None:
            return response_handler.wait_for_result()
        
    
    def GetCalibration(self, callback = None, *args, **kwargs):
        """
        Gets the current calibration in use from the tracker

        """
        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=self._response_converter_Calibration,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        
        self._message_passer.execute_request (1100,
                                              params,
                                              response_handler)
        if response_callback is None:
            return response_handler.wait_for_result()                    

    def _response_converter_Calibration(self, payload):
        #  opcode: 1100 
        return converters.ToCalibration(payload)


    def SetCalibration(self, calibration, callback = None, *args, **kwargs):
        """
        Sets the current calibration

        Parameters:
            calibration: not documented
        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=None,
                                                                  response_callback=response_callback)        
        params = tobiisdkpy.ParamStack()
        params.push_blob (calibration.rawData)
        
        self._message_passer.execute_request (1110,
                                              params,
                                              response_handler)
        if response_callback is None:
            return response_handler.wait_for_result()                    

                    
    def StartTracking(self, callback = None, *args, **kwargs):

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=None,
                                                                  response_callback=response_callback)
        
        data_columns = [GazeDataConstants.TimeStamp,

                        GazeDataConstants.LeftEyePosition3D,
                        GazeDataConstants.LeftEyePosition3DRelative,
                        GazeDataConstants.LeftGazePoint3D,
                        GazeDataConstants.LeftGazePoint2D,
                        GazeDataConstants.LeftPupil,
                        GazeDataConstants.LeftValidity,

                        GazeDataConstants.RightEyePosition3D,
                        GazeDataConstants.RightEyePosition3DRelative,
                        GazeDataConstants.RightGazePoint3D,
                        GazeDataConstants.RightGazePoint2D,
                        GazeDataConstants.RightPupil,
                        GazeDataConstants.RightValidity,]
        
        
        params = tobiisdkpy.ParamStack()
        params.push_uint32 (1280) # 1280 is the gaze data stream
        params.push_vector_uint32 (data_columns)
        
        self._message_passer.execute_request (1220,
                                              params,
                                              response_handler)
        if response_callback is None:
            return response_handler.wait_for_result()            

    def StopTracking(self, callback = None, *args, **kwargs):

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=None,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        params.push_uint32 (1280) # 1280 is the gaze data stream 
        
        self._message_passer.execute_request (1230,
                                              params,
                                              response_handler)
        if response_callback is None:
            return response_handler.wait_for_result()            
        
    def _event_converter_GazeDataReceived(self, payload):
        #  channel: 1280
        data = GazeDataItem()
        reader = ParamStackReader(payload)
        data_row = reader.pop()  # element: gaze (type: tree)
        
        data.Timestamp = self.get_gaze_data_column(data_row, GazeDataConstants.TimeStamp)
        
        data.LeftEyePosition3D = Point3D._node_converter(self.get_gaze_data_column(data_row, GazeDataConstants.LeftEyePosition3D))
        data.LeftEyePosition3DRelative = Point3D._node_converter(self.get_gaze_data_column(data_row, GazeDataConstants.LeftEyePosition3DRelative))
        data.LeftGazePoint3D = Point3D._node_converter(self.get_gaze_data_column(data_row, GazeDataConstants.LeftGazePoint3D))
        data.LeftGazePoint2D = Point2D._node_converter(self.get_gaze_data_column(data_row, GazeDataConstants.LeftGazePoint2D))
        data.LeftPupil = self.get_gaze_data_column(data_row, GazeDataConstants.LeftPupil)
        data.LeftValidity = self.get_gaze_data_column(data_row, GazeDataConstants.LeftValidity)
        
        data.RightEyePosition3D = Point3D._node_converter(self.get_gaze_data_column(data_row, GazeDataConstants.RightEyePosition3D))
        data.RightEyePosition3DRelative = Point3D._node_converter(self.get_gaze_data_column(data_row, GazeDataConstants.RightEyePosition3DRelative))
        data.RightGazePoint3D = Point3D._node_converter(self.get_gaze_data_column(data_row, GazeDataConstants.RightGazePoint3D))
        data.RightGazePoint2D = Point2D._node_converter(self.get_gaze_data_column(data_row, GazeDataConstants.RightGazePoint2D))
        data.RightPupil = self.get_gaze_data_column(data_row, GazeDataConstants.RightPupil)
        data.RightValidity = self.get_gaze_data_column(data_row, GazeDataConstants.RightValidity)
        
        return data
                    

    def _event_GazeDataReceived(self, error, event_args):
        self.events.OnGazeDataReceived(error, event_args)

    def get_gaze_data_column(self, row, column_id):
        if row.type != 3000: # XDS Row
            raise ValueError("Can only extract XDS Columns from XDS nodes")
        for node in row:
            if node.type == 3001: # XDS column
                if node[0] == column_id:
                    return node[1]
        raise ValueError("Cannot find %s" % column_id)

        
    def GetHeadMovementBox(self, callback = None, *args, **kwargs):
        """
        Returns the current head movement box.

        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=self._response_converter_HeadMovementBox,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        
        self._message_passer.execute_request (1400,
                                              params,
                                              response_handler)
        
        if response_callback is None:
            return response_handler.wait_for_result()     
                    

    def _response_converter_HeadMovementBox(self, payload):
        #  opcode: 1400
        reader = ParamStackReader(payload) 
        response = HeadMovementBox()
        response.Point1 = Point3D._node_converter(reader.pop())  # element: p1 (type: tree)
        response.Point2 = Point3D._node_converter(reader.pop())  # element: p2 (type: tree)
        response.Point3 = Point3D._node_converter(reader.pop())  # element: p3 (type: tree)
        response.Point4 = Point3D._node_converter(reader.pop())  # element: p4 (type: tree)
        response.Point5 = Point3D._node_converter(reader.pop())  # element: p5 (type: tree)
        response.Point6 = Point3D._node_converter(reader.pop())  # element: p6 (type: tree)
        response.Point7 = Point3D._node_converter(reader.pop())  # element: p7 (type: tree)
        response.Point8 = Point3D._node_converter(reader.pop())  # element: p8 (type: tree)
        
        return response

       
    def _event_converter_HeadMovementBoxChanged(self, payload):
        #    event: HeadMovementBoxChanged
        #  channel: 1410
        data = HeadMovementBoxChangedEventArgs()        
        return data
                    

    def _event_HeadMovementBoxChanged(self, error, event_args):
        self.events.OnHeadMovementBoxChanged(error, event_args)
                            


    def EnableExtension(self, extensionId, callback = None, *args, **kwargs):

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=None,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        params.push_uint32 (extensionId)
        
        self._message_passer.execute_request (1800,
                                              params,
                                              response_handler)

        if response_callback is None:
            return response_handler.wait_for_result()     


                    
    def GetAvailableExtensions(self, callback = None, *args, **kwargs):

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=self._response_converter_AvailableExtensions,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        
        self._message_passer.execute_request (1810,
                                              params,
                                              response_handler)

        if response_callback is None:
            return response_handler.wait_for_result()     
                    

    def _response_converter_AvailableExtensions(self, payload):
        #  opcode: 1810
        reader = ParamStackReader(payload) 
        node = reader.pop()  # element: available_extensions (type: tree)
        
        return self._convert_node_to_extension_list(node)
    

    def GetEnabledExtensions(self, callback = None, *args, **kwargs):

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=self._response_converter_EnabledExtensions,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        
        self._message_passer.execute_request (1820,
                                              params,
                                              response_handler)
                    
        if response_callback is None:
            return response_handler.wait_for_result()     


    def _response_converter_EnabledExtensions(self, payload):
        #  opcode: 1820
        reader = ParamStackReader(payload) 
        node = reader.pop()  # element: enabled_extensions (type: tree)
        
        return self._convert_node_to_extension_list(node)
    
    

    def _convert_node_to_extension_list(self, node):
        if not isinstance(node, Node):
            raise TypeError("node must be of type Node")
        
        if not node[0] is not 9000: #9000 is Extension type ID
            raise ValueError("node parameter has unexpected format")
        
        extension_list = []
        for i in range(len(node)):
            if i > 0: # ignore type item
                if len(node[i]) is not 4:
                    raise ValueError("expected Extension node with four members")
                ext = Extension()
                ext.ProtocolVersion = node[i][0]
                ext.ExtensionId = node[i][1]
                ext.Name = node[i][2]
                ext.Realm = node[i][3]
                extension_list.append(ext)
                
        return extension_list
                            
    def GetXConfiguration(self, callback = None, *args, **kwargs):

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=self._response_converter_XConfiguration,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        
        self._message_passer.execute_request (1430,
                                              params,
                                              response_handler)
        if response_callback is None:
            return response_handler.wait_for_result()     


                
    def _response_converter_XConfiguration(self, payload):
        #  opcode: 1430
        reader = ParamStackReader(payload) 
        response = XConfiguration()
        response.UpperLeft = Point3D._node_converter(reader.pop())  # element: upper_left (type: tree)
        response.UpperRight = Point3D._node_converter(reader.pop())  # element: upper_right (type: tree)
        response.LowerLeft = Point3D._node_converter(reader.pop())  # element: lower_left (type: tree)
        
        return response


    def SetXConfiguration(self, UpperLeft, UpperRight, LowerLeft, callback = None, *args, **kwargs):

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=None,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        Converter.to_tree(params, UpperLeft)
        Converter.to_tree(params, UpperRight)
        Converter.to_tree(params, LowerLeft)
        
        # write empty tool data
        params.push_node_prolog(1 << 16 | 256)
        params.push_uint32(12345)
            
        self._message_passer.execute_request (1440,
                                              params,
                                              response_handler)
        if response_callback is None:
            return response_handler.wait_for_result()     

                    

    def _event_converter_XConfigurationChanged(self, payload):
        #    event: XconfigChanged
        #  channel: 1450
        data = XConfiguration()
        
        reader = ParamStackReader(payload)
        data.UpperLeft = Point3D._node_converter(reader.pop())  # element: upper_left (type: tree)
        data.UpperRight = Point3D._node_converter(reader.pop())  # element: upper_right (type: tree)
        data.LowerLeft = Point3D._node_converter(reader.pop())  # element: lower_left (type: tree)
        # ignore tool data element: guidlist (type: vector_string)
        return data
                    

    def _event_XConfigurationChanged(self, error, event_args):
        self.events.OnXConfigurationChanged(error, event_args)
        
        
    def SetIlluminationMode(self, illuminationMode, callback = None, *args, **kwargs):
        """
        Sets the illumination mode.

        Parameters:
            illuminationMode: The name of the desired illumination mode
        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)
        
        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=None,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        params.push_string (illuminationMode)
        
        self._message_passer.execute_request (2020,
                                              params,
                                              response_handler)
        
        if response_callback is None:
            return response_handler.wait_for_result()
                            

    def GetIlluminationMode(self, callback = None, *args, **kwargs):
        """
        gets the name of the current illumination mode

        """

        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)

        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=self._response_converter_GetIlluminationMode,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        
        self._message_passer.execute_request (2010,
                                              params,
                                              response_handler)

        if response_callback is None:
            return response_handler.wait_for_result()                    

    def _response_converter_GetIlluminationMode(self, payload):
        reader = ParamStackReader(payload) 
        return reader.pop()  # element: illumination mode (type: string)
    
    def EnumerateIlluminationModes(self, callback = None, *args, **kwargs):
        """
        Returns all illumination modes supported by this eye tracker
    
        """
        response_callback = None
        if callback is not None:
            if not callable(callback):        
                raise ValueError("response_callback must be callable")
            response_callback = lambda error, response: callback(error, response, *args, **kwargs)
    
        response_handler = BasicEyetracker.ResponseHandlerFunctor(data_converter=self._response_converter_EnumerateIlluminationModes,
                                                                  response_callback=response_callback)
        
        params = tobiisdkpy.ParamStack()
        
        self._message_passer.execute_request (2030,
                                              params,
                                              response_handler)
        
        if response_callback is None:
            return response_handler.wait_for_result()
                        

    def _response_converter_EnumerateIlluminationModes(self, payload):
        reader = ParamStackReader(payload) 
        return reader.pop()  # element: illumination modes (type: vector_string)

                    










