####################
ioHub Configuration
####################

The ioHub Event Framework has been designed to be highly configurable, ensuring 
that is can be tailoried to the needs of a specific use case or experiment paradigm.

This section outlines how ioHub configuration works, what mechanisms are in 
place allowing a user to update configuration settings, and how configuration settings
are validated. There are two ways configuration settings can be specified, 
using configuration files for using configuration dictionaries within the experiment script.

ioHub tries to seperate experiment logic ( the python code that defines how your experimental
paradigm is implemented, how stimuli are read and presented, etc. ) from experiment configuration
( defining the experiment and experiment session metadata, experiment session variable input, 
and the configuration of the device hardware being used by the experiment ). 

By doing so, the experiment scripts will often become much reusable when switching between
device hardware for a given device type. The definition and collection of experiment
and experiment session information becomes more structured, easier to and understand visually,
and also can help to ensure different memebers of a lab are following the same or similar 
process when providing and collecting data about participants and the experiment devices used.
This can help in experiment reproducablity and result validaion if ever needed.

The current implementation state of ioHub is a work in process towards fully 
meeting the above goals and objectives; much more can be done to both improve 
and refine the existing functionailty provide as well as working towards a 
more functional implementation.

This section outlines:

* Areas of configuration within the ioHub Framework.
* Default configuration values and experiment defined confiuration values
* Using configuration files vs. python dictionaries.
* Experiment defined confiuration validation.
* Where to find confiuration setting options, and vailid values for each, within the documentation.


Areas of Configuration
#######################

The ioHub Event Framework supports the configuration of several 
different areas of the functionality. How the ioHub Framework is used defines which of
these areas can be taken advantage of by the experiment.

Configuration Options with ioHubExperimentRuntime Class
========================================================

* Experiment metadata.
* Experiment Session metadata definition, including custom session level variables.
* Device selection and configuration.
* Experiment Resource (condition variable files, images, audio files, vidio files, etc.) location specifiecation.
* Experiment Output File(s) (custom files, ioHub DataStore files, Native Device Data Files, ect) locations.
* Some Experiment and ioHub Process OS configuration     

Other than the ioHub device spcification, and any configuration settings needed for the devices being used, all other
items in the list are optional. By providing all the above information (at a level of detail you can choose),
your experiment logic script will be able to take advantage of the full fucntionality set
provided by the ioHub Framework.


When using the ioHubExperimentRuntime Class, aff configuration details provided are done so using
two configuration files that reside in the same directory as the experiment python script. 
These are descibed in detail later on this page.

Configuration Options with the launchHubProcess Function
=========================================================

* Experiment Code.
* Session Code.
* PsychoPy Monitor Configuration File Name.
* Defice configuration.

When using the launchHubProcess function to interface to the ioHub framework any configuration
information that is provided is done using kwargs to the fucntion, or a 
python dictionary for each device that needs configuration settings updated.

A default set of devices are enabled when the launchHubProcess function is used:

* Display
* Experiment
* Keyboard
* Mouse

Therefore the launchHubProcess can be very useful for quick initial setup of access to the 
ioHub Framework is is completely useable in many cases. However the trade-offs 
(you deside if they are possitive or negative) are:

* Access to all the extended functionality witin the ioHub Framework is significantly reduced 
* When devices are used that *require* a moderate degree of configuration, directly using python dictionaries to do so starts to become combersome and error prone. 
* This approach to using the ioHub Framework effectively voids any of the possible beneifits outlined at the start of this section regarding the speration of experiment logic and configuration.

Default and Custom Provided Configuration Settings
#######################################################

Regardless of which of the two approaches just described are used, all the possible
configuration options are set when the ioHUb Process starts. What can differ is which
are sets using default values and which are set using confiruation options
defined by the experiment designer. the following process is used when setting
configutation options:

#. Default settings are read from default configuration files which exist in the ioHub package directory structure.
#. Any custom settings or values specified by the PsychoPy Process are read. 
#. These two configuration sets are merged, where any settings not provided by the PsychoPy Process are given the default value specified by  the default configuration file in question.

    #. If the configuration group is for an ioHub Device, the combined confiuartion set for the device is validated against a spcification of what thhat device accepts for configuration options, whether it is manditory or not, and what the valid value set or range is for each option.
    #. If the configuration validator finds problems, an error is generated when the experiment starts and the device is not loaded.
    #. If the configuration of the device passes, the device is created and the full set of configuration otpns and values used can be read as a Python dictionary using the device.getConfiguration() method.

#. The configuation settings are used when initializing the ioHub Process and creating the ioHub runtime objects used within the PsychoPy script.


Default Configuration Settings
==================================

All default confiuration settings are specified in configuration files, as mentioned above. 

The default settings for the ioHub Process and DataStore are located in the
'default_config.yaml' file located in the root iohub module directory.

The default settings for each ioHub device are located in a file called 
default_<device_name>.yaml found in the device submodule
directory within the iohub package; where <device_name> is the unqualified class 
name of the defive in all lowercase form.  

For example, the default Mouse device settings are located in::

     iohub.devices.mouse.default_mouse.yaml

For the Keyboard::

     iohub.devices.mouse.default_keyboard.yaml

For the different Eye Tracker implementations::

    iohub.devices.eyetracker.hw.lc_technolgies.eyegaze.default_eyetracker.yaml
    
    iohub.devices.eyetracker.hw.smi.iviewx.default_eyetracker.yaml

    iohub.devices.eyetracker.hw.sr_research.eyelink.default_eyetracker.yaml

    iohub.devices.eyetracker.hw.tobii.default_eyetracker.yaml

etc.

.. note:: The documentation page for each device includes the ioHub default
    settings for each device based on the latest default file settings for that device. 
    This can be used to quickly review the configuartion options available, 
    get a description of each, and see what the default value is.

    It is important to understand that if the default setting for a device 
    configuration option is satisfactory for the experiment being written, there is
    no need to provide it at the experiment confiuration setting level. However doing so
    does not hurt and provides a direct statement of what setting values are being 
    used for the experiment.


Custom Configuration Settings
===================================

Any configuration setting that need to use a non-default value are specified in
one of two ways, depending on whether the launchHubProcess function is used to
create the access point to the ioHub Process, or if the ioHubExperimentRuntime class
is being used to embed the experiment logic within the ioHub Framework.

**When using the launchHubProcess function:**

When the launchHubProcess function  is used, device configuratiions can be 
specified by creating a python dictionary for the device settings being specified.
One dictionary is created for each device that is needed.

.. note:: Remember that, as a convience, the launchHubProcess function will create
    four base device insatnces without the need to specify them as launchHubProcess
    function kwargs. These defaults use the default settings for the device. If 
    a configuration dictionary is provided for a device of the same Classs, then the
    default device that would have been created is created using the provided parameter
    dictionary instead 

Please see the launchHubProcess function documentation for more details.

**When using the ioHubExperimentRuntime class:**

When using the ioHubExperimentRuntime class, all experiment, session, process, 
and device configuation settings are specified in two configuratiion files that
are created in the same directory as the PsychoPy Python script file.

ioHub Configuration Files are defines using a simple subset of the `YAML synax <http://yaml.org/>`_ ,
which is parsed using the `PyYAML <http://pyyaml.org/wiki/PyYAMLDocumentation>`_ package.

The two configuartion files are:

#. experiment_config.yaml 
    * Specifies the experiment and session metadata for the experiment.
    * Defines any custom session variables, which allow custom input fields to be provided in the Session Information Input Dialog at the start of any experiment 
    * Can include experiment resource path information and result data file save locations.
    * Specifies the PsychoPy and ioHub Process OS settings (Windows and Linux only).
#. iohub_config.yaml
    * Specifies the ioHub Process UDP port number to use.
    * Defines the maximum number of events to store in the Global Event Buffer.
    * Specifies the list of ioHub devices to use within the experiment, allong with any configuration settings needed for each device specified.
    * Defines ioHub DataStore parameter settings.

Several of the ioHub examples use the ioHubExperimentRuntime class and two configuration files,
and they provide a good way to gain better insite into how the configuration options can be used.

.. note:: The documentation page for each device includes the ioHub default
    settings for each device based on the latest default file settings for that device. 
    This can be used to quickly review the configuartion options available, 
    get a description of each, and see what the default value is.


Example Configurations 
#######################

In YAML file Format
=====================

An example of a experiment_config.yaml file::

    # This text is being written in a YAML comment block. Looks familar right?
    #
    # Here are a few pointers to keep in mind about the confiuration file format
    # that will help ensure they are created with proper YAML syntax:
    # 
    # - Think of the whole file as representing a python dictionary. Infact when the
    #   the file is read by PyYAML, it results in the data from the file being returned as a Python dictionary.
    # - If you have ever created a Python dictionary using the form
    #
    #   mydict={ 
    #           'key1': 'value1',
    #           'key2': 2
    #           }
    #
    # Then it should be quite easy to see that the YAML format for a file is very
    # similar, other than these differences:
    #   + The file does not begin with a '{' or end with a '}'.
    #   + key: value pairs are seperation by lines, not by ','s.
    #    
    # - The indendation level of the line in the file indicates the scope of the key:value pair, 
    #     ( scope meaning the dictionary or list level that the key: value pair is associated with) 
    #    Again, should be a familar idea. ;)
    #
    # - A key can have a dictionary as it;s value, by specifying the key name and
    #   then providing the key's dictionary value starting on the nexxt line, indented by a soft tab.
    # - Keys should only contain a-z,A-Z,and underscores. (This is an ioHub spec. more than a YAML one)
    # - Keys never need to have quotes around them, and never should.
    # - String values also do not need quotes around them.
    # - Other system data types used in values can usually just be types as if you were entering the value
    #   in a python script. For example:
    #
    #       dict_of_mixed_type_values:     # So a dict value is created by having each key: value pair for the key indented one soft tab.
    #          str_type_param: This is the value for my str_type_param.
    #          int_type_param: 10          # Converted into a Python int with value 10
    #          float_type_param: 10.11     # Converted into a Python float with value 10.11
    #          bool_type_param: True       # Converted into a Python bool == True
    #          none_type_param:            # Converted into value of None
    #          another_str_type: '10'      # By placing quotes around a type that would notmally not be a string, it is made one.
    #          list_type_param: [1,2,3,Four,Five,Six]  # A Python list is created  [1,2,3,'Four','Five','Six']
    #          list2_type_param:
    #              - 1                      # This is another way to define a list value
    #              - 2                      # each element is on a seperate line
    #              - 3                      # indented by one from the key that the list is associated with.
    #              - Four                   # will also equal [1,2,3,'Four','Five','Six'] in python
    #              - Five
    #              - Six


    # This is an example experiment_config.yaml. Values that are also the default
    # value for the setting are indicated as such. 
    
    # tile: A short but non criptic name of the experiment. 
    #       Similar to what you might title a paper about the experiment.   
    #
    title: sequentialFixationTask

    # code: A vert short, usually criptic, code for the experiment.
    #       An experiment code is 'required' when using the ioHub DataStore.
    #       While not technically inforced, it is a good practive to use a unique
    #       code for each experiment you create.
    #
    code: seqFixA

    # version: The version of the experiment being run, in string format.
    #       Each version on an experiment should have it's own experiment folder
    #       that has the experiment source and configuaration.    
    version: '0.1'

    # description: Can be used to give longer, more informative text about what the experiment is for.
    #       Can also be used to indicate anything important to remember about running the experiment.
    #
    description: Implementation of the fixation sequence testing paradigm as a way to try out the ioHub.

    # display_experiment_dialog: If True, a read-only dialog will be displayed 
    #       each time the experiment starts stating the above four parameter values.
    #       This can be useful so the person running the experiment can check that
    #        they started the right one!
    #
    display_experiment_dialog: False    # Default
    
    # session_defaults: This parameter is defined as a sub dictionary containing
    # the experiment session metadata and user defined custom parameters.
    #   
    session_defaults:
        
        # name: Allows the entry of a short namefor the session. This can be the same across
        #       multiple sessions within the experiment.
        #
        name: Session Name

        # code: A short code for the experiment session. Each run of the experiment must have 
        #       a unique session code. It the code enteried already exists in the experiments DataStore
        #       An error is returned and a different code can be entered.
        #
        code: E1S01

        # comments: Can be used to give any information the experiment operator
        #       Thinks may be important to note about the session about to be run.
        #
        comments: None

        user_variables:
            participant_age: Unknown
            participant_gender: [ Select, Male, Female ]
            glasses: False
            contacts: False
            eye_color: Unknown
    session_variable_order: [ name, code, comments, participant_age, participant_gender, glasses, contacts, eye_color ]
    
    # display_session_dialog: If True, an input dialog is shown
    #       each time the experiment starts allowing the operator to enter data for
    #       The session_default parameters and any user_variables defined.
    #
    display_session_dialog: True        # Default

    # process_affinity: Specifies the processing units / cpu's that the PsychoPy
    #       Process should be allowed to run on. Not supported on OSX.
    #       An empty list indicates that the process should be able
    #       to run on any processing unit of the computer.
    #
    process_affinity: []                # Default
    
    # remaining_processes_affinity: Lists the processing units / cpu's that
    #       all other processes running on the computer (other than the ioHub Process)
    #       should be allowed to run on.
    #       An empty list indicates that the process should be able
    #       to run on any processing unit of the computer.
    #       Not supported on OSX.
    #
    remaining_processes_affinity: []    # Default

    # event_buffer_length: The maximum number of events that can be in the
    #       PsychoPy Process ioHub event cache. This is used when iohub.wait()
    #       is called and new events are received from the ioHub process.        
    #
    event_buffer_length: 1024           # Default

    # Settings for the ioHub Process itself.
    #
    ioHub:
        # Do you want the ioHub process to run ?  True == Yes
        # False == why are you creating an ioHub confiuration file then? ;)
        #                  
        enable: True                    # Default

        # process_affinity: Specifies the processing units / cpu's that the
        #       ioHub Process should be allowed to run on. 
        #       An empty list indicates that the process should be able
        #       to run on any processing unit of the computer.
        #       Not supported on OSX.
        #
        process_affinity: []            # Default

        # config: The name of the ioHub config file, specifying device 
        #       settings, etc
        #
        config: ioHub_config.yaml       # Default

    ####### End of experiment_config.yaml example ########

An example of an iohub_configuration.yaml file::


    # To Be Completed

In Python Dictionary Format
---------------------------

The following example python code illustrates how the launchHubProcess function could
be used to have the ioHub server create the default device types, as well as Direct Input
Gamepad device for use during the experiment::

    # To Be Completed

.. note:: As previously mentioned, the example set provide for the ioHub is an excellent resource
    for further examples of confuration in ioHub.
