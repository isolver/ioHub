import platform,os,sys
from ioHub import module_directory

def getOS():
    return platform.system()

OS_NAME=getOS()

external_lib_path=None

if OS_NAME == 'Windows':

    external_lib_path=os.path.join(module_directory(getOS),'win32')
elif OS_NAME == 'Linux':
    external_lib_path=os.path.join(module_directory(getOS),'linux')
else: #assume osx?
    external_lib_path=os.path.join(module_directory(getOS),'osx')

if external_lib_path:
    if external_lib_path not in sys.path:
        sys.path.append(external_lib_path)