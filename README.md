# ioHub Framework, including the pyEyeTrackerInterface

## Project Status

Please see the [project wiki](https://www.github.com/isolver/ioHub/wiki/) for current status details, installation instructions,
and current documentation etc. for the ioHub and pyEyeTrackerInterface.

## Overview

The ioHub is a Python framework that runs as a seperate system process in parallel to the most excellent [Psychopy](http://www.psychopy.org)
during experiment runtime / data collection. The ioHub effectively acts as a proxy between the experiment logic and the
input and output devices used by the experiment, centralizing a large portion of the I/O bound tasks an application may
have into a common asynchronous, non-blocking, architecture that runs in a seperate independent process.

The pyEyeTrackerInterface is a common eye tracker interface written in python that has been designed to be as hardware
independent as possible. This does not mean that the interface specification can and will not change as more eye trackers
implement the interface and more feedback is received from both eye tracker researchers and manufacturers.

The pyEyeTrackerInterface acts as the *eyetracker* device implementation in the ioHub. Other currently supported devices
include keyboard, mouse, parallel port, and joysticks.

The ioHub and pyEyeTrackerInterface are being developed for use by the [COGAIN Technical Committee on Eye Data Quality](http://www.cogain.org/info/eye-data-quality)
and as an open resource for the eye tracking and psychology research community in general. I would like to acknowledge all the hard work that the volenteers
of the committee membership have been contributing toward the effort overall.

Thank you,

Sol

## Getting Help

email: sds-git _AT_ isolver-software.coT (change _AT_ to an @ and the T to an m)

## License

ioHub and ioDataStore are Copyright (C) 2012 Sol Simpson, except for files where otherwise noted.

ioHub and ioDataStore are distributed under the terms of the GNU General Public License (GPL version 3 or any later version).
See the LICENSE file for details.

Please see the Credits page of the wiki for more details on who has contributed to the implementation of the ioHub
and the pyEyeTrackerInterface.


