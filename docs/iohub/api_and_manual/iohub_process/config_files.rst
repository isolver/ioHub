####################
ioHub Configuration
####################

The ioHub Event Framework has been designed to be highly configurable, ensuring 
that is can be tailored to the needs of a specific use case or experiment paradigm.
This section outlines how ioHub configuration works, what mechanisms are in 
place allowing a user to update configuration settings, and how configuration settings
are validated. There are two ways configuration settings can be specified, 
using configuration files for using configuration dictionaries within the experiment script.

Configuration Files
=====================

Configuration files are created using Y.A.M.L syntax and are parsed using 
the PyYAML Package, from here on simply refered to as YAML.  This syntax was 
choosen for the following reasons:

* YAML is very readable.
* YAML syntax is similar to Python syntax, in that raw indentation determines relevant scope.
* Convertion from a YAML file to a Python Object struct is a simple mapping to Python dictionaries and lists and values are automatically converted to the appropriate built-in Python type.
* Nested, or hierarchical, representations can be specified.
* A YAML definition can be converted to JSON format for wire level transmission, and the converted back to YAML format. JSON is a subset of the YAML specification (not because JSON came after YAML, but because YAML was designed this way).
* XML could have also been used, however the author's experience is that for configuration files, XML is overly verbose, less readable by humans, and just overkill in general.

The ioHub supports two configuration files, the experiment_config.yaml file and the iohub_config.yaml file.

experiment_config.yaml 
-----------------------

* explain the purpose of the experiment_config
* provide the full default experiment_config.yaml definition ith default values
* list config parameters that **must** be provided in an experiments configuration.

iohub_config.yaml
------------------

* explain the purpose of the iohub_config
* give an example of a simple iohub_config
* note that details on each ioHub Device's configuration options and default values are found in the specific manual page devoted to the Device in question.  

Configuration Dictionaries
===========================

For Device level configuration, a python dictionary can be used to specify the 
ioHub Device's desired configuration settings. The dictionary must provide 
the expected structure for the Device being configured, 
and must specify valid key name and associated values.

Example Configuration Dictionary
-----------------------------------

TBC