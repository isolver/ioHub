import platform,os,sys
from ioHub import module_directory

def getOS():
    return platform.system()

def getPythonVerStr():
    cur_version = sys.version_info
    return 'python%d.%d'%(cur_version[0],cur_version[1])

external_lib_path=module_directory(getOS)

_python_ver_str=getPythonVerStr()
  
_os_name=getOS()
if _os_name == 'Windows':
    _os_name='win32'
elif _os_name == 'Linux':
    _os_name='linux'
else: #assume osx?
    _os_name='osx'

external_lib_path=os.path.join(external_lib_path,_python_ver_str,_os_name)
if external_lib_path:
    if external_lib_path not in sys.path:
        sys.path.append(external_lib_path)