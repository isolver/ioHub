# From PsychoPy (www.PsycoPy.org) examples folder.
# slightly modified to run also as a called func and to add the ioHub version and python path,
from psychopy import visual
from sys import stdout
from pyglet.gl import *

def printSystemInfo(fileLikeObj=None):
    if fileLikeObj is None:
        fileLikeObj=stdout
    import sys, platform, psutil

    fileLikeObj.write("System info:\n")
    system, node, release, version, machine, processor = platform.uname()
    fileLikeObj.write('\tSystem:'+str(system))
    fileLikeObj.write('\n\tRelease:'+str(release))
    fileLikeObj.write('\n\tVersion:'+str(version))
    fileLikeObj.write('\n\tMachine:'+str(machine))
    fileLikeObj.write('\n\tProcessor:'+str(processor))
    if sys.platform=='darwin':
        OSXver, junk, architecture = platform.mac_ver()
        fileLikeObj.write("\n\tOS X %s running on %s" %(OSXver, architecture))

    fileLikeObj.write("\nPython info:")
    fileLikeObj.write('\n\tExe:'+sys.executable)
    fileLikeObj.write('\n\tVersion:'+str(sys.version))
    fileLikeObj.write('\n\tPath: '+str(sys.path))

    fileLikeObj.write('\n\tPython Modules:')
    try:
        import numpy;
        fileLikeObj.write( "\n\tnumpy:"+str(numpy.__version__))
    except:
        fileLikeObj.write('\n\tError with import numpy.')

    try:
        import scipy; fileLikeObj.write("\n\tscipy:"+str(scipy.__version__))
    except:
        fileLikeObj.write('\n\tError with import scipy.')

    try:
        import matplotlib; fileLikeObj.write("\n\tmatplotlib:"+str(matplotlib.__version__))
    except:
        fileLikeObj.write('\n\tError with import matplotlib.')
    try:
        import pyglet; fileLikeObj.write("\n\tpyglet:"+pyglet.version)
    except:
        fileLikeObj.write('\n\tError with import pyglet.')
    try:
        fileLikeObj.write('\n\t')
        import pyo
        pv=pyo.getVersion()
        fileLikeObj.write("\tpyo: pyo"+'.'.join(map(str,pv)))
    except:
        fileLikeObj.write('\n\tError with import pyo.')
    try:
        from psychopy import __version__
        fileLikeObj.write("\n\tPsychoPy"+str(__version__))
    except:
        fileLikeObj.write('\n\tError with import PsychoPy.')
    try:
        from ioHub import __version__ as ioHubVersion
        fileLikeObj.write("\n\tioHub"+str(ioHubVersion))
    except:
        fileLikeObj.write('\n\tError with import ioHub.')


    win = visual.Window([100,100])#some drivers want a window open first
    fileLikeObj.write('\n\tOpenGL info:')
    #get info about the graphics card and drivers
    fileLikeObj.write('\n\tvendor:'+gl_info.get_vendor())
    fileLikeObj.write('\n\trendering engine:'+gl_info.get_renderer())
    fileLikeObj.write('\n\tOpenGL version:'+gl_info.get_version())
    fileLikeObj.write('\n\t(Selected) Extensions:')
    extensionsOfInterest=['GL_ARB_multitexture', 
        'GL_EXT_framebuffer_object','GL_ARB_fragment_program',
        'GL_ARB_shader_objects','GL_ARB_vertex_shader',
        'GL_ARB_texture_non_power_of_two','GL_ARB_texture_float', 'GL_STEREO']
    for ext in extensionsOfInterest:
        fileLikeObj.write('\n\t'+str(bool(gl_info.have_extension(ext)))+str(ext))
    #also determine nVertices that can be used in vertex arrays
    maxVerts=GLint()
    glGetIntegerv(GL_MAX_ELEMENTS_VERTICES,maxVerts)
    fileLikeObj.write('\n\tmax vertices in vertex array:'+str(maxVerts.value))

    fileLikeObj.write('\n\nProcessor / Computer Info:')
    fileLikeObj.write('\n\tBOOT_TIME:'+str(psutil.BOOT_TIME))
    fileLikeObj.write('\n\tNUM_CPUS:'+str(psutil.NUM_CPUS))
    fileLikeObj.write('\n\tAvail_phymem / avail_virtmem / TOTAL_PHYMEM: '+str(psutil.avail_phymem()/1024/1024.0)+' GB / '+str(psutil.avail_virtmem()/1024/1024.0)+' GB / '+str(psutil.TOTAL_PHYMEM/1024/1024.0)+' GB')
    fileLikeObj.write('\n\tused_phymem / used_virtmem: '+str(psutil.used_phymem()/1024/1024.0)+' GB / '+str(psutil.used_virtmem()/1024/1024.0)+' GB')
    fileLikeObj.write('\n\tphymem_usage'+str(psutil.phymem_usage()))

    win.close()
    
if __name__ == '__main__':
    printSystemInfo()