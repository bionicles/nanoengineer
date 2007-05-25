# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PropertyManagerMixin.py
@author: Ninad
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:
ninad20061215: created this mixin class to provide helper methods in various 
Property managers 
ninad20070206: added many new methods to help prop manager ui generation.

mark 2007-05-17: added the new property manager base class PropMgrBaseClass.

"""

__author__ = "Ninad"

from PyQt4.Qt import *
from PyQt4 import Qt, QtCore, QtGui
from Utility import geticon
from PyQt4.QtGui import *
from Sponsors import SponsorableMixin
from qt4transition import lineage
from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False, Choice
from Utility import geticon, getpixmap
from PropMgr_Constants import *
import os

class PropMgrBaseClass_OBSOLETE: # Mark 2005-05-25
    '''Property Manager base class'''

    def __init__(self):
        
        # NOTE: This establishes the width and height of the
        # Property Manager "container". 
        # Height of 600 needs to be tested on a 1024 x 768 monitor.
        # The height should auto-adjust to fit contents, but
        # doesn't as of now. Needs to be fixed. Mark 2007-05-14.
        # PropMgr width (230 pixels) should be set via global constant. 
        # The width is currently set in MWsemantics.py (PartWindow).
        # The width of propmgr is 230 - (4 x 2) = 222 pixels on Windows.
        # Need to test width on MacOS.
        # Mark 2007-05-15.
        
        self.resize(QtCore.QSize(
            QtCore.QRect(0,0,222,550).size()).expandedTo(
                self.minimumSizeHint()))
        
        # Main pallete for PropMgr.
        propmgr_palette = self.getPropertyManagerPalette()
        self.setPalette(propmgr_palette)
        
        # Main vertical layout for PropMgr.
        self.pmMainVboxLO = QtGui.QVBoxLayout(self)
        self.pmMainVboxLO.setMargin(pmMainVboxLayoutMargin)
        self.pmMainVboxLO.setSpacing(pmMainVboxLayoutSpacing)

        # PropMgr's Header.
        self.addHeader()
        self.addSponsorButton()
        self.addTopRowBtns() # Create top buttons row
        self.addMessageGroupBox()
                
        # Keep this around. I might want to use it now that I understand it.
        # Mark 2007-05-17.
        #QtCore.QMetaObject.connectSlotsByName(self)
        
        
    def addHeader(self):
        """Creates the Property Manager header, which contains
        a pixmap and white text label.
        """
        
        # Heading frame (dark gray), which contains 
        # a pixmap and (white) heading text.
        self.header_frame = QtGui.QFrame(self)
        self.header_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.header_frame.setFrameShadow(QtGui.QFrame.Plain)
        
        header_frame_palette = self.getPropMgrTitleFramePalette()
        self.header_frame.setPalette(header_frame_palette)
        self.header_frame.setAutoFillBackground(True)

        # HBox layout for heading frame, containing the pixmap
        # and label (title).
        HeaderFrameHLayout = QtGui.QHBoxLayout(self.header_frame)
        HeaderFrameHLayout.setMargin(pmHeaderFrameMargin) # 2 pixels around edges.
        HeaderFrameHLayout.setSpacing(pmHeaderFrameSpacing) # 5 pixel between pixmap and label.

        # PropMgr icon. Set image by calling setPropMgrIcon() at any time.
        self.header_pixmap = QtGui.QLabel(self.header_frame)
        self.header_pixmap.setObjectName("header_pixmap")
        self.header_pixmap.setSizePolicy(
            QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(QSizePolicy.Fixed),
                              QtGui.QSizePolicy.Policy(QSizePolicy.Fixed)))
            
        self.header_pixmap.setScaledContents(True)
        
        HeaderFrameHLayout.addWidget(self.header_pixmap)
        
        # Call from PropMgr subclass.
        #self.setPropMgrIcon('ui/actions/Tools/Build Structures/DNA.png')
        
        # PropMgr title label (DNA)
        self.header_label = QtGui.QLabel(self.header_frame)
        self.header_label.setObjectName("header_label")
        header_label_palette = self.getPropMgrTitleLabelPalette()
        self.header_label.setPalette(header_label_palette)

        # PropMgr heading font (for label).
        font = QtGui.QFont(self.header_label.font())
        font.setFamily("Sans Serif")
        font.setPointSize(12)
        font.setWeight(75)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(True)
        self.header_label.setFont(font)
        
        HeaderFrameHLayout.addWidget(self.header_label)
        
        self.pmMainVboxLO.addWidget(self.header_frame)
        
    def setPropMgrTitle(self, title):
        """Set the Propery Manager header title to string <title>.
        """
        self.header_label.setText(title)
        
    def setPropMgrIcon(self, png_path):
        """Set the Propery Manager icon in the header.
        <png_path> is the relative path to the PNG file.
        """
        self.header_pixmap.setPixmap(getpixmap(png_path))
        
    
    def addSponsorButton(self):
        """Creates the Property Manager sponsor button, which contains
        a QPushButton inside of a QGridLayout inside of a QFrame.
        """
        
        # Sponsor button (inside a frame)
        self.sponsor_frame = QtGui.QFrame(self)
        self.sponsor_frame.setObjectName("sponsor_frame")
        self.sponsor_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.sponsor_frame.setFrameShadow(QtGui.QFrame.Plain)

        SponsorFrameGrid = QtGui.QGridLayout(self.sponsor_frame)
        SponsorFrameGrid.setMargin(pmSponsorFrameMargin)
        SponsorFrameGrid.setSpacing(pmSponsorFrameSpacing) # Has no effect.

        self.sponsor_btn = QtGui.QPushButton(self.sponsor_frame)
        self.sponsor_btn.setObjectName("sponsor_btn")
        self.sponsor_btn.setAutoDefault(False)
        self.sponsor_btn.setFlat(True)
        self.connect(self.sponsor_btn,SIGNAL("clicked()"),
                     self.open_sponsor_homepage)
        
        SponsorFrameGrid.addWidget(self.sponsor_btn,0,0,1,1)
        
        self.pmMainVboxLO.addWidget(self.sponsor_frame)
        
        return

    def addTopRowBtns(self, showFlags=None):
        """Creates the OK, Cancel, Preview, and What's This 
        buttons row at the top of the Pmgr.
        """
        
        #@ To do: add "Restore Defaults" button.
        #@ To do: add arg to select buttons to display (i.e. many times we
        #         only want to see "Cancel").
        #
        # The Top Buttons Row includes the following widgets:
        #
        # - self.pmTopRowBtns (Hbox Layout containing everything:)
        #   - left spacer (10x10)
        #   - frame
        #     - hbox layout "frameHboxLO" (margin=2, spacing=2)
        #     - Done (OK) button
        #     - Abort (Cancel) button
        #     - Preview button
        #     - What's This button
        #   - right spacer (10x10)
        
        
        # Main "button group" widget (but it is not a QButtonGroup).
        self.pmTopRowBtns = QtGui.QHBoxLayout()
        
        # Left and right spacers
        leftSpacer = QtGui.QSpacerItem(10, 10, 
                                       QtGui.QSizePolicy.Expanding, 
                                       QSizePolicy.Minimum)
        rightSpacer = QtGui.QSpacerItem(10, 10, 
                                        QtGui.QSizePolicy.Expanding,
                                        QSizePolicy.Minimum)
        
        # Frame containing all the buttons.
        self.TopRowBtnsFrame = QtGui.QFrame()
        self.TopRowBtnsFrame.setObjectName("TopRowBtnsFrame")
                
        self.TopRowBtnsFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.TopRowBtnsFrame.setFrameShadow(QtGui.QFrame.Raised)
        
        # Create Hbox layout for main frame.
        TopRowBtnsHLayout = QtGui.QHBoxLayout(self.TopRowBtnsFrame)
        TopRowBtnsHLayout.setMargin(pmTopRowBtnsMargin)
        TopRowBtnsHLayout.setSpacing(pmTopRowBtnsSpacing)
        TopRowBtnsHLayout.setObjectName("frameHboxLO")
        
        # OK (Done) button.
        self.done_btn = QtGui.QPushButton(self.TopRowBtnsFrame)
        self.done_btn.setObjectName("done_btn")
        self.done_btn.setIcon(
            geticon("ui/actions/Properties Manager/Done.png"))
        self.connect(self.done_btn,SIGNAL("clicked()"),
                     self.ok_btn_clicked)
        self.done_btn.setToolTip("Done")
        
        TopRowBtnsHLayout.addWidget(self.done_btn)
        
        # Cancel (Abort) button.
        self.abort_btn = QtGui.QPushButton(self.TopRowBtnsFrame)
        self.abort_btn.setObjectName("abort_btn")
        self.abort_btn.setIcon(
            geticon("ui/actions/Properties Manager/Abort.png"))
        self.connect(self.abort_btn,SIGNAL("clicked()"),
                     self.abort_btn_clicked)
        self.abort_btn.setToolTip("Cancel")
        
        TopRowBtnsHLayout.addWidget(self.abort_btn)
        
        # Restore button.
        self.restore_defaults_btn = QtGui.QPushButton(self.TopRowBtnsFrame)
        self.restore_defaults_btn.setObjectName("restore_defaults_btn")
        self.restore_defaults_btn.setIcon(
            geticon("ui/actions/Properties Manager/Restore.png"))
        self.connect(self.restore_defaults_btn,SIGNAL("clicked()"),
                     self.restore_defaults_btn_clicked)
        self.restore_defaults_btn.setToolTip("Restore Defaults")
        TopRowBtnsHLayout.addWidget(self.restore_defaults_btn)
        
        # Preview (glasses) button.
        self.preview_btn = QtGui.QPushButton(self.TopRowBtnsFrame)
        self.preview_btn.setObjectName("preview_btn")
        self.preview_btn.setIcon(
            geticon("ui/actions/Properties Manager/Preview.png"))
        self.connect(self.preview_btn,SIGNAL("clicked()"),
                     self.preview_btn_clicked)
        self.preview_btn.setToolTip("Preview")
        
        TopRowBtnsHLayout.addWidget(self.preview_btn)        
        
        # What's This (?) button.
        self.whatsthis_btn = QtGui.QPushButton(self.TopRowBtnsFrame)
        self.whatsthis_btn.setObjectName("whatsthis_btn")
        self.whatsthis_btn.setIcon(
            geticon("ui/actions/Properties Manager/WhatsThis.png"))
        self.connect(self.whatsthis_btn,SIGNAL("clicked()"),
                     self.enter_WhatsThisMode)
        self.whatsthis_btn.setToolTip("What\'s This Help")
        
        TopRowBtnsHLayout.addWidget(self.whatsthis_btn)
        
        # Create Button Row
        self.pmTopRowBtns.addItem(leftSpacer)
        self.pmTopRowBtns.addWidget(self.TopRowBtnsFrame)
        self.pmTopRowBtns.addItem(rightSpacer)
        
        self.pmMainVboxLO.addLayout(self.pmTopRowBtns)
        
        return

    def hideTopRowButtons(self, hideFlags=None):
        """Hide one or more top row buttons using <hideFlags>.
        Hide button flags not set will cause the button to be shown,
        if currently hidden.
        
        The hide button flags are:
            pmShowAllButtons = 0
            pmHideDoneButton = 1
            pmHideCancelButton = 2
            pmHideRestoreDefaultsButton = 4
            pmHidePreviewButton = 8
            pmHideWhatsThisButton = 16
            pmHideAllButtons = 31
            
        These flags are defined in PropMgr_Constants.py.
        """
        
        if hideFlags & pmHideDoneButton: self.done_btn.hide()
        else: self.done_btn.show()
            
        if hideFlags & pmHideCancelButton: self.abort_btn.hide()
        else: self.abort_btn.show()
            
        if hideFlags & pmHideRestoreDefaultsButton: 
            self.restore_defaults_btn.hide()
        else: self.restore_defaults_btn.show()
            
        if hideFlags & pmHidePreviewButton: self.preview_btn.hide()
        else: self.preview_btn.show()
            
        if hideFlags & pmHideWhatsThisButton: self.whatsthis_btn.hide()
        else: self.whatsthis_btn.show()
            
        
    def addMessageGroupBox(self):
        """Creates layout and widgets for the "Message" groupbox.
        """
        self.pmMsgGroupBox = QtGui.QGroupBox(self)
        self.pmMsgGroupBox.setObjectName("pmMsgGroupBox")
        
        self.pmMsgGroupBox.setAutoFillBackground(True) 
        palette =  self.getGroupBoxPalette()
        self.pmMsgGroupBox.setPalette(palette)
        
        styleSheet = self.getGroupBoxStyleSheet()        
        self.pmMsgGroupBox.setStyleSheet(styleSheet)

        MsgGrpBoxVLayout = QtGui.QVBoxLayout(self.pmMsgGroupBox)
        MsgGrpBoxVLayout.setMargin(pmMsgGrpBoxMargin)
        MsgGrpBoxVLayout.setSpacing(pmMsgGrpBoxSpacing) # Has no effect.
        MsgGrpBoxVLayout.setObjectName("pmMsgVboxLO")
        
        # "Message" title button for pmMsgGroupBox
        
        self.pmMsgGroupBoxBtn = self.getGroupBoxTitleButton(
            "Message", self.pmMsgGroupBox)
        self.connect(self.pmMsgGroupBoxBtn,SIGNAL("clicked()"),
                     self.toggle_pmMsgGroupBox)
        
        MsgGrpBoxVLayout.addWidget(self.pmMsgGroupBoxBtn)
        
        # "Message" TextEdit

        self.pmMsgTextEdit = QtGui.QTextEdit(self.pmMsgGroupBox)
        self.pmMsgTextEdit.setObjectName("pmMsgTextEdit")
        self.pmMsgTextEdit.setMinimumSize(200,46)
        self.pmMsgTextEdit.setMaximumSize(300,60)
        self.pmMsgTextEdit.setSizePolicy(QSizePolicy.MinimumExpanding,
                                         QSizePolicy.Minimum )
        self.pmMsgTextEdit.setReadOnly(True)
        
        
        msg_palette =  self.getMsgGroupBoxPalette()
        self.pmMsgTextEdit.setPalette(msg_palette)
        
        MsgGrpBoxVLayout.addWidget(self.pmMsgTextEdit)
        
        self.pmMainVboxLO.addWidget(self.pmMsgGroupBox) # Add Msg groupbox
        
    def insertHtmlMsg(self, htmlMsg):
        """Insert HTML message into the Prop Mgr's message groupbox.
        """
        self.pmMsgTextEdit.insertHtml(htmlMsg)
        
    def addGroupBoxSpacer(self):
        """Add vertical groupbox spacer. 
        """
        pmGroupBoxSpacer = QtGui.QSpacerItem(10,pmGroupBoxSpacing,
                                           QtGui.QSizePolicy.Fixed,
                                           QtGui.QSizePolicy.Fixed)
        
        self.pmMainVboxLO.addItem(pmGroupBoxSpacer) # Add spacer
    
    def addBottomSpacer(self):
        """Add spacer at the very bottom of the PropMgr. 
        It is needed to assist proper collasping/expanding of groupboxes.
        """
        pmBottomSpacer = QtGui.QSpacerItem(10,self.height(),
                                           QtGui.QSizePolicy.Minimum,
                                           QtGui.QSizePolicy.Expanding)
        
        self.pmMainVboxLO.addItem(pmBottomSpacer) # Add spacer to bottom
        
        
    def toggle_pmMsgGroupBox(self): # Message groupbox
        self.toggle_groupbox(self.pmMsgGroupBoxBtn, 
                             self.pmMsgTextEdit)
        

class PropertyManagerMixin(SponsorableMixin):
    '''Mixin class that provides methods common to various property managers''' 
        
    def openPropertyManager(self, tab):
        #tab = property manager widget
        self.pw = self.w.activePartWindow()         
        self.pw.updatePropertyManagerTab(tab)
        try:
            tab.setSponsor()
        except:
            print "tab has no attribute 'setSponsor()'  ignoring."
        self.pw.featureManager.setCurrentIndex(self.pw.featureManager.indexOf(tab))
     
    def closePropertyManager(self):
        if not self.pw:
            self.pw = self.w.activePartWindow() 
        self.pw.featureManager.setCurrentIndex(0)
        self.pw.featureManager.removeTab(self.pw.featureManager.indexOf(self.pw.propertyManagerScrollArea))            
        if self.pw.propertyManagerTab:
            self.pw.propertyManagerTab = None
            
    def toggle_groupbox(self, button, *things):
        """This is intended to be part of the slot method for clicking on an open/close icon
        of a dialog GroupBox. The arguments should be the button (whose icon will be altered here)
        and the child widgets in the groupbox whose visibility should be toggled.
        """
        if things:
            if things[0].isVisible():
                styleSheet = self.getGroupBoxButtonStyleSheet(bool_expand = False)
                button.setStyleSheet(styleSheet)      
                palette = self.getGroupBoxButtonPalette()
                button.setPalette(palette)
                button.setIcon(geticon("ui/actions/Properties Manager/GHOST_ICON"))
                for thing in things:
                    thing.hide()
            else:
                styleSheet = self.getGroupBoxButtonStyleSheet(bool_expand = True)
                button.setStyleSheet(styleSheet)             
                palette = self.getGroupBoxButtonPalette()
                button.setPalette(palette)
                button.setIcon(geticon("ui/actions/Properties Manager/GHOST_ICON"))
                for thing in things:
                    thing.show()
                    
        else:
            print "Groupbox has no widgets. Clicking on groupbox button has no effect"
    
    def getPropertyManagerPalette(self):
        """ Return a palette for the property manager.
        """
        # in future we might want to set different palette colors for prop managers. 
        return self.getPalette(None,
                               QtGui.QPalette.ColorRole(10),
                               pmColor)
    
    def getPropMgrTitleFramePalette(self):
        """ Return a palette for Property Manager title frame. 
        """
        #bgrole(10) is 'Windows'
        return self.getPalette(None,
                               QtGui.QPalette.ColorRole(10),
                               pmTitleFrameColor)
    
    def getPropMgrTitleLabelPalette(self):
        """ Return a palette for Property Manager title label. 
        """
        return self.getPalette(None,
                               QtGui.QPalette.WindowText,
                               pmTitleLabelColor)
    
    def getMsgGroupBoxPalette(self):
        """ Return a palette for Property Manager message groupboxes.
        """
        return self.getPalette(None,
                               QtGui.QPalette.Base,
                               pmMessageTextEditColor)
                               
    def getGroupBoxPalette(self):
        """ Return a palette for Property Manager groupboxes. 
        This distinguishes the groupboxes in a property manager.
        The color is slightly darker than the property manager background.
        """
        #bgrole(10) is 'Windows'
        return self.getPalette(None,
                               QtGui.QPalette.ColorRole(10),
                               pmGrpBoxColor)
    
    def getGroupBoxButtonPalette(self):
        """ Return a palette for the groupbox Title button. 
        """
        return self.getPalette(None,
                               QtGui.QPalette.Button, 
                               pmGrpBoxButtonColor)
    
    def getGroupBoxCheckBoxPalette(self):
        """ Returns the background color for the checkbox of any groupbox 
        in a Property Manager. The color is slightly darker than the 
        background palette of the groupbox.
        """
        palette = self.getPalette(None,
                               QtGui.QPalette.WindowText, 
                               pmCheckBoxTextColor)
        
        return self.getPalette(palette,
                               QtGui.QPalette.Button, 
                               pmCheckBoxButtonColor)
    
    def getPalette(self, palette, obj, color):
        """ Given a palette, Qt object and a color, return a new palette.
        If palette is None, create and return a new palette.
        """
        
        if palette:
            pass # Make sure palette is QPalette.
        else:
            palette = QtGui.QPalette()
            
        palette.setColor(QtGui.QPalette.Active, obj, color)
        palette.setColor(QtGui.QPalette.Inactive, obj, color)
        palette.setColor(QtGui.QPalette.Disabled, obj, color)
        return palette
    
    def getGroupBoxStyleSheet(self):
        """Return the style sheet for a groupbox. Example border style, border 
        width etc. The background color for a  groupbox is set separately"""
        
        styleSheet = "QGroupBox {border-style:solid;\
        border-width: 1px;\
        border-color: " + pmGrpBoxBorderColor + ";\
        border-radius: 0px;\
        min-width: 10em; }"
        
        ## For Groupboxs' Pushbutton : 
        
        ##Other options not used : font:bold 10px;  
        
        return styleSheet
    
    def getGroupBoxTitleButton(self, name, parent =None, bool_expand = True): #Ninad 070206
        """ Return the groupbox title pushbutton. The pushbutton is customized 
        such that  it appears as a title bar to the user. If the user clicks on 
        this 'titlebar' it sends appropriate signals to open or close the
        groupboxes   'name = string -- title of the groupbox 
        'bool_expand' = boolean .. NE1 uses a different background 
        image in the button's  Style Sheet depending on the bool. 
        (i.e. if bool_expand = True it uses a opened group image  '^')
        See also: getGroupBoxTitleCheckBox , getGroupBoxButtonStyleSheet  methods
        """
        
        button  = QtGui.QPushButton(name, parent)
        button.setFlat(False)
        button.setAutoFillBackground(True)
        
        palette = self.getGroupBoxButtonPalette()
        button.setPalette(palette)
        
        styleSheet = self.getGroupBoxButtonStyleSheet(bool_expand)
                
        button.setStyleSheet(styleSheet)        
        #ninad 070221 set a non existant 'Ghost Icon' for this button
        #By setting such an icon, the button text left aligns! 
        #(which what we want :-) )
        #So this might be a bug in Qt4.2.  If we don't use the following kludge, 
        #there is no way to left align the push button text but to subclass it. 
        #(could mean a lot of work for such a minor thing)  So OK for now 
        
        button.setIcon(geticon("ui/actions/Properties Manager/GHOST_ICON"))
        
        return button    
    
    def getGroupBoxButtonStyleSheet(self, bool_expand =True):
        """ Returns the syle sheet for a groupbox title button (or checkbox)
        of a property manager. Returns a string. 
        bool_expand' = boolean .. NE1 uses a different background image in the 
        button's  Style Sheet depending on the bool. 
        (i.e. if bool_expand = True it uses a opened group image  '^')
        """
        
        # Need to move border color and text color to top (make global constants).
        if bool_expand:        
            styleSheet = "QPushButton {border-style:outset;\
            border-width: 2px;\
            border-color: " + pmGrpBoxButtonBorderColor + ";\
            border-radius:2px;\
            font:bold 12px 'Arial'; \
            color: " + pmGrpBoxButtonTextColor + ";\
            min-width:10em;\
            background-image: url(" + pmGrpBoxExpandedImage + ");\
            background-position: right;\
            background-repeat: no-repeat;\
            }"       
        else:
            
            styleSheet = "QPushButton {border-style:outset;\
            border-width: 2px;\
            border-color: " + pmGrpBoxButtonBorderColor + ";\
            border-radius:2px;\
            font: bold 12px 'Arial'; \
            color: " + pmGrpBoxButtonTextColor + ";\
            min-width:10em;\
            background-image: url(" + pmGrpBoxCollapsedImage + ");\
            background-position: right;\
            background-repeat: no-repeat;\
            }"
            
        return styleSheet
    
    def getGroupBoxTitleCheckBox(self, name, parent =None, bool_expand = True):#Ninad 070207
        """ Return the groupbox title checkbox . The checkbox is customized such that 
        it appears as a title bar to the user. If the user clicks on this 'titlebar' it sends 
        appropriate signals to open or close the groupboxes (and also to check or uncheck the box.)
        'name = string -- title of the groupbox 
        'bool_expand' = boolean .. NE1 uses a different background image in the button's 
        Style Sheet depending on the bool. (i.e. if bool_expand = True it uses a opened group image  '^')      
        See also: getGroupBoxTitleButton method.         
        """
        
        checkbox = QtGui.QCheckBox(name, parent)
        checkbox.setAutoFillBackground(True)
        
        palette = self.getGroupBoxCheckBoxPalette()
        checkbox.setPalette(palette)
        
        styleSheet = self.getGroupBoxCheckBoxStyleSheet(bool_expand)
        checkbox.setStyleSheet(styleSheet)             
        checkbox.setText(name)
        
        return checkbox
    
       
    def getGroupBoxCheckBoxStyleSheet(self, bool_expand =True):
        """ Returns the syle sheet for a groupbox checkbox of a property manager
        Returns a string. 
        bool_expand' = boolean .. NE1 uses a different background image in the button's 
        Style Sheet depending on the bool. (i.e. if bool_expand = True it uses a opened group image  '^')
        """
 
        if bool_expand:        
            styleSheet = "QCheckBox {\
            color: " + pmGrpBoxButtonTextColor + ";\
            font: bold 12px 'Arial';\
            }"
        else:
            styleSheet = "QCheckBox {\
            color: " + pmGrpBoxButtonTextColor + ";\
            font: bold 12px 'Arial';\
            }"    
        # Excluded attributes (has issues)-- 
        ##background-image: url(ui/actions/Properties Manager/Opened_GroupBox.png);\
        ##background-position: right;\
        ##background-repeat: no-repeat;\
        
        return styleSheet
    
    def hideGroupBox(self, groupBoxButton, groupBoxWidget):
        # Hide a groupbox (this is not the same a 'toggle' groupbox)        
                 
        groupBoxWidget.hide()               
        
        styleSheet = self.getGroupBoxButtonStyleSheet(bool_expand = False)            
        groupBoxButton.setStyleSheet(styleSheet)      
        palette = self.getGroupBoxButtonPalette()
        groupBoxButton.setPalette(palette)
        groupBoxButton.setIcon(geticon("ui/actions/Properties Manager/GHOST_ICON"))
            
    def showGroupBox(self, groupBoxButton, groupBoxWidget):
        # Show a groupbox (this is not the same as 'toggle' groupbox)        
        
        if not groupBoxWidget.isVisible():               
            groupBoxWidget.show()               
            
            styleSheet = self.getGroupBoxButtonStyleSheet(bool_expand = True)            
            groupBoxButton.setStyleSheet(styleSheet)      
            palette = self.getGroupBoxButtonPalette()
            groupBoxButton.setPalette(palette)
            groupBoxButton.setIcon(geticon("ui/actions/Properties Manager/GHOST_ICON"))
