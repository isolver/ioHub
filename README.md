# ioHub

ioHub is not a complete experiment design and runtime API. It's main focus is on device event monitoring, 
real-time reporting, and persistant storage of input device events on a system wide basis. When ioHub is used
for experiment device monitoring during a psychopolgy or neuroscience type study, ioHub is designed to be used
with the most excellent [PsychoPy](http://www.psychopy.org). 

>> Note: In the near future **ioHub will be merging with PsychoPy ( psychopy.iohub )**, so it can be used
>> out of the box with a PsychoPy installation, even if the desire is to use the ioHub event reporting
>> features in a 'headless' mode that does not create any windows or graphics. 
>> 
>> This will effect (in a positive way) how ioHub can be installed, where documentation is found, 
>> and how to get support for the ioHub Event Framework. 
>>
>> Stay tuned for updated on this exciting development !

## Download

**Note that the provided setup.py file is currently broken, and will be fixed ASAP. For now simply download the source distribution and copy the internal 'iohub' folder (all lower case folder name) to your python path; for example your site-packages folder. Sorry for the inconvience.**

ioHub source is hosted on GitHub [here](https://www.github.com/isolver/ioHub/).

Download the source, uncompress the file downloaded, open a terminal or console in the 
uncompressed directory location, and run::

    >> python setup.py install
    
A package installers will also be made available soon.


## Documentation

The documentation, which is **still being completed** (firm completion date of May 3rd), is now available 
[online](http://www.isolver-solutions.com/iohubdocs/0.7/index.html). 

If you would like to help by correcting grammatical errors, spelling, 
filling in incomplete doc strings, etc, (which would be greatly apprieciated)
please make a fork of the ioHub project to your github account, make changes
to the master branch docs, and submit a pull request back to isolver/ioHub to have the updates merged.

The ioHub source contains a documentation folder that has been written using Sphinx.
If the ioHub source is downloaded, open a console or terminal window in the
iohub/doc/ directory and build the documentation using::

    >> make html

[Sphinx](http://sphinx-doc.org/#) must be installed.

## Installation

Please refer to the Installation section of the [documentation](http://www.isolver-solutions.com/iohubdocs/0.7/index.html).

## Support

A [user forum / mailing list](https://groups.google.com/forum/?hl=en&fromgroups#!forum/iohub-users) 
and [developer forum / mailing list](https://groups.google.com/forum/?hl=en&fromgroups#!forum/iohub-dev)
are available on Google Groups for support questions and development discussion topics respectively.

## License

ioHub and the Python Common Eye Tracker Interface are Copyright (C) 2012-2013 iSolver Software Solutions, except for files or modules where otherwise noted.

ioHub is distributed under the terms of the GNU General Public License (GPL version 3 or any later version). See the LICENSE file for details. 

Python module dependancies and other 3rd party libraries are copyright their respective copyright holders. Any trademarked names used are owned by their trademark owners and use of any such names is not an endorsement of ioHub by the trademark owner.
