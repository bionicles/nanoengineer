# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Piotr
@version:   $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

import foundation.changes as changes
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from command_support.EditCommand import EditCommand
from utilities.constants import red
from protein.commands.EditRotamers.EditRotamers_PropertyManager import EditRotamers_PropertyManager
from utilities.GlobalPreferences import MODEL_AND_SIMULATE_PROTEINS
from utilities.GlobalPreferences import USE_COMMAND_STACK
# == GraphicsMode part

_superclass_for_GM = SelectChunks_GraphicsMode

class EditRotamers_GraphicsMode(SelectChunks_GraphicsMode ):
    """
    Graphics mode for Edit Rotamers command. 
    """
    pass
    
# == Command part


class EditRotamers_Command(EditCommand): 
    """
    
    """
    #Temporary attr 'command_porting_status. See baseCommand for details.
    command_porting_status = "PARTIAL: As of 2008-09-18 it has a bug in opening the protein sequence editor, may be due to PM.update_residue_combobox()??"
    
    # class constants
    GraphicsMode_class = EditRotamers_GraphicsMode
    
    PM_class = EditRotamers_PropertyManager
           
    commandName = 'EDIT_ROTAMERS'
    featurename = "Edit Rotamers"
    from utilities.constants import CL_SUBCOMMAND
    command_level = CL_SUBCOMMAND
    command_parent = 'BUILD_PROTEIN'
    
    if MODEL_AND_SIMULATE_PROTEINS:
        command_parent = 'MODEL_PROTEIN'
        
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True 
    command_has_its_own_PM = True
    
    flyoutToolbar = None
    
    def _getFlyoutToolBarActionAndParentCommand(self):
        """
        See superclass for documentation.
        @see: self.command_update_flyout()
        """
        flyoutActionToCheck = 'editRotamersAction'
        if MODEL_AND_SIMULATE_PROTEINS:
            parentCommandName = 'MODEL_AND_SIMULATE_PROTEIN'    
        else:
            parentCommandName = None
            
        return flyoutActionToCheck, parentCommandName
    
    if not USE_COMMAND_STACK:
        def init_gui(self):
            """
            Initialize GUI for this mode 
            """
            
            if MODEL_AND_SIMULATE_PROTEINS:
                self._init_gui_flyout_action( 'editRotamersAction', 'MODEL_AND_SIMULATE_PROTEIN' )  
            else:
                self._init_gui_flyout_action( 'editRotamersAction')
            if self.propMgr is None:
                self.propMgr = EditRotamers_PropertyManager(self)
                #@bug BUG: following is a workaround for bug 2494.
                #This bug is mitigated as propMgr object no longer gets recreated
                #for modes -- niand 2007-08-29
                changes.keep_forever(self.propMgr)  
                
            self.propMgr.show()
                
            
        def restore_gui(self):
            """
            Restore the GUI 
            """
            EditCommand.restore_gui(self)
            if self.flyoutToolbar:
                self.flyoutToolbar.editRotamersAction.setChecked(False)    
        
    def keep_empty_group(self, group):
        """
        Returns True if the empty group should not be automatically deleted. 
        otherwise returns False. The default implementation always returns 
        False. Subclasses should override this method if it needs to keep the
        empty group for some reasons. Note that this method will only get called
        when a group has a class constant autdelete_when_empty set to True. 
        (and as of 2008-03-06, it is proposed that dna_updater calls this method
        when needed. 
        @see: Command.keep_empty_group() which is overridden here. 
        """
        
        bool_keep = EditCommand.keep_empty_group(self, group)
        
        return bool_keep
