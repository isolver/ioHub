# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 10:34:29 2013

@author: Sol
"""

### IMPORTANT: This setup file is not yet working completely. DO NOT USE YET.

from setuptools import setup
import iohub
import sys

print "setup.py is not yet working completely. DO NOT USE YET."
print "For now, copy the 'iohub' dictectory within the ioHub source folder to your Python site-packages' folder, or other folder that is in your Python Path."
print "Thank you for your patience."
sys.exit(1)

def readme():
    with open('README.rst') as f:
        return f.read()

def requiredDendancies():
    deps = [ 'markdown', 'psychopy >= 1.76', 
            'greenlet >= 0.4.0', 'gevent >= 1.0.0', 'msgpack-python >= 0.3.0',
            'numexpr >= 1.4.2', 'tables >= 2.3.1', 'pyYAML >= 3.0.8']
    if sys.platform == 'win32':
        deps.append('psutil >= 0.6.1')
        deps.append('pyHook >= 1.5.1')
    elif sys.platform == 'linux2':
        deps.insert(0,'cython >= 0.1.7')
        deps.append('psutil >= 0.6.1')
        deps.append('python-xlib >= 0.1.5')
    elif sys.platform == 'linux2':
        deps.insert(0,'cython >= 0.1.7')
        deps.append('pyobjc >= 2.5.0')        
    return deps

setup(name='iohub',
      version=iohub.__version__,
      description='A cross-platform, operating system wide, device event reporting and storage framework.',
      long_description=readme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: Microsoft :: Windows :: Windows XP',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator'
      ],
      url=iohub.__url__,
      author=iohub.__author__,
      author_email=iohub.__author_email__,
      packages=['iohub'],
      install_requires=requiredDendancies(),
      zip_safe=False)