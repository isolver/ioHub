"""
ioHub
.. file: ioHub/util/dialogs.py

* Implements dialogs using PyQt4 / guidata *

Copyright (C) 2012-2013 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: ioHub Team

------------------------------------------------------------------------------------------------------------------------
"""

import os

def set_frame_display(frame, display_index):
    """
    Centers a wx window on the given Display index.
    """
    import wx
    num_displays=wx.Display.GetCount()
    if display_index < 0:
        display_index=0
    if display_index >= num_displays:
        display_index=num_displays-1
    display = wx.Display(display_index)
    x, y, w, h = display.GetGeometry()
    frame.SetPosition((x, y))
    frame.Center()

#
## ProgressBar
#

class ProgressBarDialog(object):
    """
    wx based progress bar interface.
    """
    def __init__(self,dialogTitle="Progress Dialog",dialogText="Percent Complete", maxValue=100.0,display_index=0):
        import wx
        self.wxapp = wx.PySimpleApp()
        self.dialog = wx.ProgressDialog(dialogTitle,dialogText,maxValue, None,wx.PD_AUTO_HIDE|wx.PD_APP_MODAL|wx.PD_ELAPSED_TIME|wx.PD_ESTIMATED_TIME|wx.PD_REMAINING_TIME)
        
        if display_index is not None:        
            set_frame_display(self.dialog,display_index)
        self.minimumValue=0.0
        self.maximumValue=maxValue
        self.currentValue=self.minimumValue

    def updateStatus(self,value):
        self.dialog.Update(value)
        self.currentValue=value

    def close(self):
        self.wxapp.Exit()
        self.dialog=None
        self.wxapp=None

    def getCurrentStatus(self):
        return self.currentValue

#
## MessageDialog
#

class MessageDialog(object):
    import wx    
    YES_NO_BUTTONS=wx.YES_NO
    OK_BUTTON=wx.OK
    CANCEL_BUTTON = wx.CANCEL
    YES_BUTTON = wx.YES
    NO_BUTTON = wx.NO
    
    INFORMATION_DIALOG=wx.ICON_INFORMATION
    WARNING_DIALOG=wx.ICON_WARNING
    IMPORTANT_DIALOG=wx.ICON_EXCLAMATION
    ERROR_DIALOG=wx.ICON_ERROR
    QUESTION_DIALOG=wx.ICON_QUESTION
    
    YES_RESULT=wx.ID_YES
    NO_RESULT=wx.ID_NO
    OK_RESULT=wx.ID_OK
    CANCEL_RESULT=wx.ID_CANCEL
     
    def __init__(self,msg,title=None,showButtons=wx.OK, 
                 dialogType=wx.ICON_INFORMATION, allowCancel=True,display_index=0):
        import wx
        import wx.lib.agw.genericmessagedialog as GMD     

        self.wxapp = wx.PySimpleApp()
        
        if showButtons not in [MessageDialog.YES_NO_BUTTONS,MessageDialog.OK_BUTTON]:
            raise AttributeError(
            "MessageDialog showButtons arg must be either MessageDialog.YES_NO_BUTTONS or MessageDialog.OK_BUTTON")
        if showButtons == MessageDialog.YES_NO_BUTTONS:
            showButtons |= wx.YES_DEFAULT
        if allowCancel:
            showButtons |= wx.CANCEL
            
        if dialogType not in [MessageDialog.INFORMATION_DIALOG,
                              MessageDialog.WARNING_DIALOG,
                              MessageDialog.IMPORTANT_DIALOG,
                              MessageDialog.ERROR_DIALOG, 
                              MessageDialog.QUESTION_DIALOG]:
            raise AttributeError(
            "MessageDialog dialogType arg must one of MessageDialog.INFORMATION_DIALOG, MessageDialog.WARNING_DIALOG, MessageDialog.IMPORTANT_DIALOG, MessageDialog.ERROR_DIALOG, MessageDialog.QUESTION_DIALOG.")
        
        if title is None:
            if dialogType == MessageDialog.INFORMATION_DIALOG:
                title="For Your Information"
            elif dialogType == MessageDialog.WARNING_DIALOG:
                title="Warning"
            elif dialogType ==  MessageDialog.IMPORTANT_DIALOG:
                title="Important Note"
            elif dialogType == MessageDialog.ERROR_DIALOG:
                title="Error"
            elif dialogType == MessageDialog.QUESTION_DIALOG:
                title="Input Required"
        
        d=wx.Display(0)
        x,y,w,h=d.GetGeometry()
        del d
        
        self.dlg = GMD.GenericMessageDialog(None, msg,
                                       title,
                                       showButtons | dialogType, wrap=int(w/4))
        #TODO Change to own image         
        import images        
        self.dlg.SetIcon(images.Mondrian.GetIcon())

        if display_index is not None:
            set_frame_display(self.dlg,display_index)        
        
    def show(self):
        result=self.dlg.ShowModal()
        self.destroy()
        return result
    
    def destroy(self):
        try:
            self.dlg.Destroy()
        except:
            pass      
        try:
            del self.dlg
        except:
            pass      
        try:
            self.wxapp.Exit()
        except:
            pass
        try:
            del self.wxapp
        except:
            pass
        
        
    def __del__(self):
        self.destroy()
        
#
## FileChooserDialog
#        

class FileDialog(object):
    import wx
    PYTHON_SCRIPT_FILES="Python source (*.py)|*.py" 
    EXCEL_FILES="Spreadsheets (*.xls)|*.xls"
    IODATA_FILES="ioDataStore Files (*.hdf5)|*.hdf5"
    CONFIG_FILES="Configuration Files (*.yaml)|*.yaml"
    TEXT_FILES="Text Files (*.txt)|*.txt"
    ALL_FILES="All Files (*.*)|*.*"
    OK_RESULT=wx.ID_OK
    CANCEL_RESULT=wx.ID_CANCEL    
    def __init__(self,message="Select a File", defaultDir=os.getcwd(), 
                 defaultFile="", openFile=True, allowMultipleSelections= False, 
                 allowChangingDirectories = True, fileTypes="All files (*.*)|*.*",
                 display_index=0):
                     
        import wx
        self.wxapp = wx.PySimpleApp()

        dstyle=0
        
        if openFile is True:
            dstyle=dstyle | wx.OPEN
        if allowMultipleSelections is True:
            dstyle=dstyle | wx.MULTIPLE
        if allowChangingDirectories is True:
            dstyle=dstyle | wx.CHANGE_DIR
        
        fileTypesCombined=""
        if isinstance(fileTypes,(list,tuple)):    
            for ft in fileTypes:
                fileTypesCombined+=ft
                fileTypesCombined+='|'
            fileTypesCombined=fileTypesCombined[:-1]
            
        self.dlg = wx.FileDialog(
            None, message=message,
            defaultDir=defaultDir, 
            defaultFile=defaultFile,
            wildcard=fileTypesCombined,
            style=dstyle
            )

        if display_index is not None:
            set_frame_display(self.dlg,display_index)        

    def show(self):
        result=self.dlg.ShowModal()
        selections=self.dlg.GetPaths()
        self.dlg.Destroy()
        self.wxapp.Exit()
        return result, selections
    
    def destroy(self):
        try:
            self.dlg.Destroy()
        except:
            pass
        try:
            del self.dlg
        except:
            pass
        try:
            self.wxapp.Exit()
        except:
            pass
        try:
            del self.wxapp
        except:
            pass
        
        
    def __del__(self):
        self.destroy()
        
if __name__ == '__main__':
    md = MessageDialog('My message!')
    result=md.show()
    md.destroy()
    print 'MessageDialog is OK_RESULT', md.OK_RESULT==result
    
    md = FileDialog('My message!')
    result=md.show()
    md.destroy()
    print 'FileDialog result is: ', result