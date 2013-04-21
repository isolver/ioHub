#######################
ScreenState Classes
#######################

ScreenState classes attempt to encapsulate within a single class the ability to
display a screen with predetermined graphics elements based on the ScreenState type. 
Furthermore, ScreenState classes support monitoring for events that match a specified set
of criteria while the screen state is being displayed, as well as exiting the 
ScreenState after a set timeout period. This allows very short experiment screens
to be created where the experiment design is similar to displaying a set of 'slides' 
to the participant and waiting for a specific reaction or a timeout for each slide before
the experiment will continue to the next ScreenState in the experiment.

ScreenState Class
##################

.. autoclass:: iohub.util.experiment.ScreenState
    :members:

ClearScreen State
##################

.. autoclass:: iohub.util.experiment.ClearScreen
    :members:

InstructionScreen State
#########################

.. autoclass:: iohub.util.experiment.InstructionScreen
    :members:

ImageScreen State
##################

.. autoclass:: iohub.util.experiment.ImageScreen
    :members:

DeviceEventTrigger for use with ScreenState classes
####################################################


.. autoclass:: iohub.util.experiment.DeviceEventTrigger
    :members:
