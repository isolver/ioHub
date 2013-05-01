# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 16:32:33 2013

@author: Sol
"""

# Takes a device configuration yaml dict and processes it based on the devices
# support_settings_values.yaml (which must be in the same directory as the Device class)
# to ensure all entries for the device setting are valid values.

import socket
import os


from yaml import load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from psychopy.iohub.util import module_directory


class ValidationError(Exception):
    """Base class for exceptions in this module."""
    pass

class BooleanValueError(ValidationError):
    """Exception raised for errors when a bool was expected for the settings parameter value.

    Attributes:
        device_config_setting_name -- The name of the Device configuration parameter that has the error.
        value_given  -- the value read from the experiment configuration file.
        msg -- explanation of the error
    """

    def __init__(self, device_param_name, value_given):
        self.msg="A bool value is required for the given Device configuration parameter"
        self.device_config_param_name=device_param_name
        self.value_given=value_given

    def __str__(self):
        return "\n{0}:\n\tmsg: {1}\n\tparam_name: {2}\n\tvalue: {3}\n".format(self.__class__.__name__,self.msg,self.device_config_param_name,self.value_given)
class StringValueError(ValidationError):
    """Exception raised for errors when a str was expected for the settings parameter value.

    Attributes:
        device_config_param_name -- The name of the Device configuration parameter that has the error.
        value_given  -- the value read from the experiment configuration file.
        device_config_param_constraints  -- the set of constraints that apply to the parameter.
        msg -- explanation of the error
    """

    def __init__(self, device_config_param_name, value_given, device_config_param_constraints):
        self.msg="A str value is required for the given Device configuration parameter that meets the specified constraints"
        self.device_config_param_name=device_config_param_name
        self.value_given=value_given
        self.device_config_param_constraints=device_config_param_constraints

    def __str__(self):
        return "\n{0}:\n\tmsg: {1}\n\tparam_name: {2}\n\tvalue: {3}\n".format(self.__class__.__name__,self.msg,self.device_config_param_name,self.value_given)

class FloatValueError(ValidationError):
    """Exception raised for errors when a float was expected for the settings parameter value.

    Attributes:
        device_config_param_name -- The name of the Device configuration parameter that has the error.
        value_given  -- the value read from the experiment configuration file.
        device_config_param_constraints  -- the set of constraints that apply to the parameter.
        msg -- explanation of the error
    """

    def __init__(self, device_config_param_name, value_given, device_config_param_constraints):
        self.msg="A float value is required for the given Device configuration parameter that meets the specified constraints"
        self.device_config_param_name=device_config_param_name
        self.value_given=value_given
        self.device_config_param_constraints=device_config_param_constraints

    def __str__(self):
        return "\n{0}:\n\tmsg: {1}\n\tparam_name: {2}\n\tvalue: {3}\n".format(self.__class__.__name__,self.msg,self.device_config_param_name,self.value_given)

class IntValueError(ValidationError):
    """Exception raised for errors when an int was expected for the settings parameter value.

    Attributes:
        device_config_param_name -- The name of the Device configuration parameter that has the error.
        value_given  -- the value read from the experiment configuration file.
        device_config_param_constraints  -- the set of constraints that apply to the parameter.
        msg -- explanation of the error
    """

    def __init__(self, device_config_param_name, value_given, device_config_param_constraints):
        self.msg="An int value is required for the given Device configuration parameter that meets the specified constraints"
        self.device_config_param_name=device_config_param_name
        self.value_given=value_given
        self.device_config_param_constraints=device_config_param_constraints

    def __str__(self):
        return "\n{0}:\n\tmsg: {1}\n\tparam_name: {2}\n\tvalue: {3}\n".format(self.__class__.__name__,self.msg,self.device_config_param_name,self.value_given)

class NumberValueError(ValidationError):
    """Exception raised for errors when an int OR float was expected for the settings parameter value.

    Attributes:
        device_config_param_name -- The name of the Device configuration parameter that has the error.
        value_given  -- the value read from the experiment configuration file.
        device_config_param_constraints  -- the set of constraints that apply to the parameter.
        msg -- explanation of the error
    """

    def __init__(self, device_config_param_name, value_given, device_config_param_constraints):
        self.msg="An int or float value is required for the given Device configuration parameter that meets the specified constraints"
        self.device_config_param_name=device_config_param_name
        self.value_given=value_given
        self.device_config_param_constraints=device_config_param_constraints

    def __str__(self):
        return "\n{0}:\n\tmsg: {1}\n\tparam_name: {2}\n\tvalue: {3}\n".format(self.__class__.__name__,self.msg,self.device_config_param_name,self.value_given)

class IpValueError(ValidationError):
    """Exception raised for errors when an IP address was expected for the settings parameter value.

    Attributes:
        device_config_param_name -- The name of the Device configuration parameter that has the error.
        value_given  -- the value read from the experiment configuration file.
        msg -- explanation of the error
    """

    def __init__(self, device_config_param_name, value_given):
        self.msg="An IP address value is required for the given Device configuration parameter."
        self.device_config_param_name=device_config_param_name
        self.value_given=value_given

    def __str__(self):
        return "\n{0}:\n\tmsg: {1}\n\tparam_name: {2}\n\tvalue: {3}\n".format(self.__class__.__name__,self.msg,self.device_config_param_name,self.value_given)

class ColorValueError(ValidationError):
    """Exception raised for errors when a color was expected for the settings parameter value.

    Attributes:
        device_config_param_name -- The name of the Device configuration parameter that has the error.
        value_given  -- the value read from the experiment configuration file.
        msg -- explanation of the error
    """

    def __init__(self, device_config_param_name, value_given):
        self.msg="A color value is required for the given Device configuration parameter."
        self.device_config_param_name=device_config_param_name
        self.value_given=value_given

    def __str__(self):
        return "\n{0}:\n\tmsg: {1}\n\tparam_name: {2}\n\tvalue: {3}\n".format(self.__class__.__name__,self.msg,self.device_config_param_name,self.value_given)

class DateStringValueError(ValidationError):
    """Exception raised for errors when a date string was expected for the settings parameter value.

    Attributes:
        device_config_param_name -- The name of the Device configuration parameter that has the error.
        value_given  -- the value read from the experiment configuration file.
        msg -- explanation of the error
    """

    def __init__(self, device_config_param_name, value_given):
        self.msg="A date string value is required for the given Device configuration parameter."
        self.device_config_param_name=device_config_param_name
        self.value_given=value_given
        
    def __str__(self):
        return "\n{0}:\n\tmsg: {1}\n\tparam_name: {2}\n\tvalue: {3}\n".format(self.__class__.__name__,self.msg,self.device_config_param_name,self.value_given)

class NonSupportedValueError(ValidationError):
    """Exception raised when the configuration value provided does not match one of the possible valid Device configuration parameter values.

    Attributes:
        device_config_setting_name -- The name of the Device configuration parameter that has the error.
        value_given  -- the value read from the experiment configuration file.
        valid_values  -- the valid options for the configuration setting.
        msg -- explanation of the error
    """

    def __init__(self, device_param_name, value_given, valid_values):
        self.msg="A the provided value is not supported for the given Device configuration parameter"
        self.device_config_param_name=device_param_name
        self.value_given=value_given
        self.valid_values=valid_values

    def __str__(self):
        return "\n{0}:\n\tmsg: {1}\n\tparam_name: {2}\n\tvalue: {3}\n\tconstraints: {4}".format(self.__class__.__name__,self.msg,self.device_config_param_name,self.value_given,self.valid_values)

MIN_VALID_STR_LENGTH=1
MAX_VALID_STR_LENGTH=1024

MIN_VALID_FLOAT_VALUE=0.0
MAX_VALID_FLOAT_VALUE=1000000.0

MIN_VALID_INT_VALUE=0
MAX_VALID_INT_VALUE=1000000

def isValidRgb255Color(config_param_name,color,constraints):
    if isinstance(color,(list,tuple)):
        if len(color) in [3,4]:
            for c in color:
                if isinstance(c,int):
                    if c < 0 or c > 255:
                        raise ColorValueError(config_param_name,color)
                else:
                    raise ColorValueError(config_param_name,color)
        else:
            raise ColorValueError(config_param_name,color)
            
        if len(color) == 3:
            color=list(color)
            color.append(255)
        return color
        
    raise ColorValueError(config_param_name,color)

def isValidString(config_param_name,value,constraints):
    if isinstance(value,basestring):
        constraints.setdefault('min_length',MIN_VALID_STR_LENGTH)
        constraints.setdefault('max_length',MAX_VALID_STR_LENGTH)
        constraints.setdefault('first_char_alpha',False)
        min_length=int(constraints.get('min_length'))
        max_length=int(constraints.get('max_length'))
        first_char_alpha=bool(constraints.get('first_char_alpha'))
        
            
        if len(value)>=min_length:
            if len(value)<=max_length:
                if first_char_alpha is True and value[0].isalpha() is False:
                    raise StringValueError(config_param_name,value,constraints)
                else:
                    return value

    elif int(constraints.get('min_length')) == 0 and value is None:
        return value

    raise StringValueError(config_param_name,value,constraints)

def isValidFloat(config_param_name,value,constraints):
    if isinstance(value,float):
        constraints.setdefault('min',MIN_VALID_FLOAT_VALUE)
        constraints.setdefault('max',MAX_VALID_FLOAT_VALUE)
        minv=float(constraints.get('min'))
        maxv=float(constraints.get('max'))
        
        if value>=minv:
            if value<=maxv:
                return value
                
    raise FloatValueError(config_param_name,value,constraints)

def isValidInt(config_param_name,value,constraints):
    if isinstance(value,(int,long)):
        constraints.setdefault('min',MIN_VALID_INT_VALUE)
        constraints.setdefault('max',MAX_VALID_INT_VALUE)
        minv=int(constraints.get('min'))
        maxv=int(constraints.get('max'))
        
        if value>=minv:
            if value<=maxv:
                return value
                
    raise IntValueError(config_param_name,value,constraints)

def isValidNumber(config_param_name,value,constraints):
    try:
        int_value=isValidInt(config_param_name,value,constraints)
        return int_value
    except:
        try:
            float_value=isValidFloat(config_param_name,value,constraints)
            return float_value
        except:
            raise NumberValueError(config_param_name,value,constraints)

    
def isBool(config_param_name,value,valid_value):
    try:
        value=bool(value)
        return value
    except:
        raise BooleanValueError(config_param_name,value)

def isValidIpAddress(config_param_name,value,valid_value):
    try:
        socket.inet_aton(value)
        return value
    except:
        raise IpValueError(config_param_name,value)

def isValidDateString(config_param_name,value,valid_value):
    try:
        if value == 'DD-MM-YYYY':
            return value
        day,month,year=value.split('-')
        if int(day) < 1 or int(day) > 31:
            raise DateStringValueError(config_param_name,value)
        if int(month) < 1 or int(month) > 12:
            raise DateStringValueError(config_param_name,value)
        if int(year) < 1900 or int(year) > 2013:
            raise DateStringValueError(config_param_name,value)
        return value
    except:
        raise DateStringValueError(config_param_name,value)

def isValidList(config_param_name,value,constraints):
    try:
        min_length=constraints.get('min_length',1)
        max_length=constraints.get('max_length',128)

        if min_length == 0 and value == None or value == 'None':
            return value

        valid_values=constraints.get('valid_values',[])
            
        if not isinstance(value,(list,tuple)):         
            if value not in valid_values:
                raise NonSupportedValueError(config_param_name,value,constraints)
            elif min_length in [0,1]:
                return value
                
        current_length=len(value)
        
        if current_length<min_length or current_length>max_length:
            raise NonSupportedValueError(config_param_name,value,constraints)
        
        for v in value:
            if v not in valid_values:
                raise NonSupportedValueError(config_param_name,v,valid_values)
        
        return value
            
    except:
        raise NonSupportedValueError(config_param_name,value,constraints)
       

def isValueValid(config_param_name,value,valid_values):
    if value not in valid_values:
        raise NonSupportedValueError(config_param_name,value,valid_values)
    return value
        
CONFIG_VALIDATION_KEY_WORD_MAPPINGS=dict(IOHUB_STRING=isValidString,
                                 IOHUB_BOOL=isBool,
                                 IOHUB_FLOAT=isValidFloat,
                                 IOHUB_INT=isValidInt,
                                 IOHUB_NUMBER=isValidNumber,
                                 IOHUB_LIST=isValidList,
                                 IOHUB_RGBA255_COLOR=isValidRgb255Color,
                                 IOHUB_IP_ADDRESS_V4=isValidIpAddress,
                                 IOHUB_DATE=isValidDateString)
###############################################

# load a support_settings_values.yaml

def loadYamlFile(yaml_file_path,print_file=False):
    yaml_file_contents=load(file(yaml_file_path,'r'), Loader=Loader)    
#    if print_file:
#        print 'yaml_file_contents:'
#        print 'file: ',yaml_file_path
#        print 'contents:'    
#        pprint(yaml_file_contents)    
    return yaml_file_contents
    
_current_dir=module_directory(isValidString)

def buildConfigParamValidatorMapping(device_setting_validation_dict,param_validation_func_mapping,parent_name):
    for param_name,param_config in device_setting_validation_dict.iteritems():
        current_param_path=None
        if parent_name is None:
            current_param_path=param_name
        else:
            current_param_path="%s.%s"%(parent_name,param_name)
            
        keyword_validator_function=None        
        if isinstance(param_name,basestring):
            keyword_validator_function=CONFIG_VALIDATION_KEY_WORD_MAPPINGS.get(param_name,None)

        if keyword_validator_function:
            param_validation_func_mapping[parent_name]=keyword_validator_function,param_config
#            ioHub.print2err('ADDED MAPPING')
        elif isinstance(param_config,basestring):
            keyword_validator_function=CONFIG_VALIDATION_KEY_WORD_MAPPINGS.get(param_config,None)
            if keyword_validator_function:
                param_validation_func_mapping[current_param_path]=keyword_validator_function,{}
#                ioHub.print2err('ADDED MAPPING')
            else:
                param_validation_func_mapping[current_param_path]=isValueValid,[param_config,]
#                ioHub.print2err('ADDED MAPPING')
        elif isinstance(param_config,dict):
            buildConfigParamValidatorMapping(param_config,param_validation_func_mapping,current_param_path)
        elif isinstance(param_config,(list,tuple)):
            param_validation_func_mapping[current_param_path]=isValueValid,param_config
#            ioHub.print2err('ADDED MAPPING')
        else:
            param_validation_func_mapping[current_param_path]=isValueValid,[param_config,]
#            ioHub.print2err('ADDED MAPPING')

def validateConfigDictToFuncMapping(param_validation_func_mapping,current_device_config,parent_param_path):    
    validation_results=dict(errors=[],not_found=[])    
    for config_param,config_value in current_device_config.iteritems():
        if parent_param_path is None:
            current_param_path=config_param
        else:
            current_param_path="%s.%s"%(parent_param_path,config_param)
            
        param_validation=param_validation_func_mapping.get(current_param_path,None)
        if param_validation:
            param_validation_func,constraints=param_validation
            try:
                param_value=param_validation_func(current_param_path,config_value,constraints)
                current_device_config[config_param]=param_value
#                ioHub.print2err("PARAM {0}, VALUE {1} is VALID.".format(current_param_path,param_value))
            except ValidationError:
                validation_results['errors'].append((config_param,config_value))
                #ioHub.print2err("Device Config Validation Error: param: {0}, value: {1}\nError: {2}".format(config_param,config_value,e))
                
        elif isinstance(config_value,dict):
            validateConfigDictToFuncMapping(param_validation_func_mapping,config_value,current_param_path)
        else:
            validation_results['not_found'].append((config_param,config_value))    
    return validation_results
            
def validateDeviceConfiguration(relative_module_path,device_class_name,current_device_config):
    validation_file_path=os.path.join(_current_dir,relative_module_path[len('psychopy.iohub.devices.'):].replace('.',os.path.sep),'supported_config_settings.yaml')

    device_settings_validation_dict=loadYamlFile(validation_file_path,print_file=True)
    device_settings_validation_dict=device_settings_validation_dict[device_settings_validation_dict.keys()[0]]
    
    param_validation_func_mapping=dict()
    parent_config_param_path=None
    buildConfigParamValidatorMapping(device_settings_validation_dict,param_validation_func_mapping,parent_config_param_path)
    
#    ioHub.print2err("#### buildConfigParamValidatorMapping results:\n\ncurrent_device_config: {0}\n\n validation_rules config: {1}\n\n Config Constants Mapping: {2}\n".format(current_device_config,device_settings_validation_dict,param_validation_func_mapping))
    
    validation_results=validateConfigDictToFuncMapping(param_validation_func_mapping,current_device_config,None)

#    ioHub.print2err('=================================================')    
#    ioHub.print2err('{0} VALIDATION RESULTS: '.format(device_class_name))    
#    ioHub.print2err('\tPARAMS NOT FOUND: {0} '.format(len(validation_results['not_found'])))
#    for p,v in validation_results['not_found']:
#        ioHub.print2err('\tparam: {0}\t\tvalue: {1}'.format(p,v))
#    ioHub.print2err('\tPARAMS WITH ERROR: {0} '.format(len(validation_results['errors'])))
#    for p,v in validation_results['errors']:
#        ioHub.print2err('\tparam: {0}\t\tvalue: {1}'.format(p,v))
#    ioHub.print2err('=================================================')    
    
    return validation_results 