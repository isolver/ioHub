# -*- coding: utf-8 -*-
"""
Parser for directory specification in experiment file.close

Example yaml from an experiment_config.yaml:

directories:
    - experiment:
        root:
        type: [r,]
        file_types:
            - .yaml
    - results:
        root: D:/results/iohub_experiments/<code>
        type: [w,]
        file_types:
            - .hdf5                
        directories:
            - session:
                root: <session_defaults.code>
                type: [w,]
                file_types: 
                    - .xls
                    - .edf    
    - resources:
        root: resources
        directories:
            - condition_files:
                root: condition_files
                type: [r,]
                file_types: 
                    - .xls                
            - images:
                root: images
                type: [r,]
                file_types: 
                    - .png
                    - .jpeg
            - audio:
                root: audio
                type: [r,]
                file_types: 
                    - .wav
                    - .mp4

                    
@author: Sol
"""

try:
    from yaml import load
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print "*** Using Python based YAML Parsing"
    from yaml import Loader, Dumper

import os
import weakref
from collections import OrderedDict

class VirtualFolder(object):
    file_type_mappings=dict()
    def __init__(self,name,root_dir,parent_VP=None,file_types=[],vdtype=['r','w']):
        self._name=name        
        self._parent=parent_VP
        if root_dir is None:
            root_dir=''

        if self._parent:
            self._filesystem_path=os.path.join(parent_VP.getSystemPath(),root_dir)
        else:
            self._filesystem_path=os.path.abspath(root_dir)
        
        if file_types is None:
            file_types=[]
        self._file_types=file_types
        self._type=vdtype
        
        self._children=OrderedDict()
        
        for ftype in self._file_types:
            paths_for_file_type=VirtualFolder.file_type_mappings.get(ftype,weakref.WeakValueDictionary())
            paths_for_file_type[self._filesystem_path]=self
            VirtualFolder.file_type_mappings[ftype]=paths_for_file_type

    def __getattr__(self,name):
        child_VP=self._children.get(name,None)
        if child_VP:
            return child_VP
        raise AttributeError(name)
        
    def getName(self):
        return self._name
        
    def getSystemPath(self):
        return self._filesystem_path

    def getParentVP(self):
        return self._parent
        
    def getFileTypeFilter(self):
        return self._file_types
        
    def getType(self):
        return self._type
        
    def getChildren(self):
        return self._children
        
    def addVirtualSubFolder(self, virtual_folder):
        self._children[virtual_folder.getName()]=virtual_folder
    
    def _toString(self,tab_count=0):
        str_rep= ('\t'*tab_count)+'Virtual Folder:\n'
        str_rep+=('\t'*(tab_count+1))+'Name: {0}\n'.format(self.getName())
        str_rep+=('\t'*(tab_count+1))+'System Path: {0}\n'.format(self.getSystemPath())
        str_rep+=('\t'*(tab_count+1))+'File Type Filter: {0}\n'.format(self.getFileTypeFilter())
        str_rep+=('\t'*(tab_count+1))+'Type: {0}\n\n'.format(self.getType())
        for vc in self.getChildren().itervalues():
            str_rep+=vc._toString(tab_count+1)
        
        return str_rep

        
    def __str__(self):
        return self._toString()
        
def parseExperimentDirectoryStructure(experimentConfig):
    exp_dirs=experimentConfig.get('directories',None)
    if exp_dirs is None:
        return None
    
    root=VirtualFolder('virtual_folders',None)
    
    for edir in exp_dirs:
        parseExperimentDirectory(edir,root)
        
    return root
        

def parseExperimentDirectory(edir_config,parent_virtual_folder):
    for dir_label, dir_config in edir_config.iteritems(): 
        dir_root=dir_config.get('root','')
        dir_type=dir_config.get('type',['r','w'])
        file_types=dir_config.get('file_types',None)

        sub_vd=VirtualFolder(dir_label,dir_root,parent_VP=parent_virtual_folder,file_types=file_types,vdtype=dir_type)
        
        if parent_virtual_folder:
            parent_virtual_folder.addVirtualSubFolder(sub_vd)
                
        sub_dirs=dir_config.get('directories',None)
        if sub_dirs:
            for edir in sub_dirs:
                parseExperimentDirectory(edir,sub_vd)
            
if __name__ == '__main__':
    config_path = os.path.abspath('./experiment_Config.yaml')
    print 'Processing File: ', config_path
    exp_config=load(file(config_path,u'r'), Loader=Loader)
    virtual_path_structure=parseExperimentDirectoryStructure(exp_config)
    print ''
    print virtual_path_structure