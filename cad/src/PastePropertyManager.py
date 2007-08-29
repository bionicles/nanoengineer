# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PastePropertyManager.py

The PastePropertyManager class provides the Property Manager for the
B{Paste mode}.

@author: Ninad
@version: $Id:$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History:
ninad 2007-08-29: Created to support new 'Paste mode'. 
"""
from PyQt4.Qt import SIGNAL

from BuildAtomsPropertyManager import BuildAtomsPropertyManager
from PM.PM_Clipboard           import PM_Clipboard

class PastePropertyManager(BuildAtomsPropertyManager):
    """
    The PastePropertyManager class provides the Property Manager for the
    B{Paste mode}. It lists the 'pastable' clipboard items and also shows the 
    current selected item in its 'Preview' box. 
    
    @ivar title: The title that appears in the property manager header.
    @type title: str
    
    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str
    
    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """
    # The title that appears in the Property Manager header        
    title = "Paste Items"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to the PNG file that appears in the header
    iconPath = "ui/actions/Properties Manager/clipboard-full.png"
    
    def __init__(self, parentMode):
        """
	Constructor for the B{Build Atoms} property manager class that defines 
        its UI.
        
        @param parentMode: The parent mode where this Property Manager is used
        @type  parentMode: L{PasteMode}    
        """              
        BuildAtomsPropertyManager.__init__(self, parentMode)
	    
    def _addGroupBoxes(self):
        """
	Add various group boxes to the Paste Property manager.
        """
        self._addPreviewGroupBox()
        self._addClipboardGroupBox()
        
    def _addClipboardGroupBox(self):
        """
	Add the 'Clipboard' groupbox
        """
        if not self.previewGroupBox:
           return
        
        elementViewer = self.previewGroupBox.elementViewer
	        
        self.clipboardGroupBox = \
            PM_Clipboard(self, 
                         win = self.parentMode.w, 
                         elementViewer = elementViewer)
	       
    def show(self):
	"""
	Show this property manager. Also calls the update method of 
	L{self.clipboardGroupBox} to update the list of clipboard items.
	"""
        BuildAtomsPropertyManager.show(self)
        self.clipboardGroupBox.update()
    
    def connect_or_disconnect_signals(self, isConnect): 	
	"""
        Connect or disconnect widget signals sent to their slot methods.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
	
        if isConnect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect
	
	self.clipboardGroupBox.connect_or_disconnect_signals(isConnect)
	    
    def getPastable(self):
        """
	Retrieve the 'pastable' clipboard item. 
	@return: The pastable clipboard item
	@rtype:  L{molecule} or L{Group}
	"""
		
	self.parentMode.pastable = self.previewGroupBox.elementViewer.model
		
	return self.parentMode.pastable
    
    def update_clipboard_items(self):
	"""
	Update the items in the clipboard groupbox.
	"""
        self.clipboardGroupBox.update()    
    
    def updateMessage(self):
        """
	Update the message box in the property manager with an informative 
	message.
        """  
        
	msg = "Double click on empty space inside the 3D workspace,"\
	    " to paste the item shown in the <b> Preview </b> box. <br>" \
	    " To return to the previous mode hit, <b>Escape </b> key or press "\
	    "<b> Done </b>"

        # Post message.
        self.MessageGroupBox.insertHtmlMessage(msg, minLines = 5)
    