import sys, math
import random
import LSystem
import LSystemUI
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx


def create command 
        gMainWindow = maya.mel.eval('$temp1=$gMainWindow')
        self.name = PAALM_DROP_DOWN_MENU_NAME
        # Delete the old window by name if it exists
        if (self.exists()):
            cmds.deleteUI(self.name)

        dropDownMenu = cmds.menu(
            PAALM_DROP_DOWN_MENU_NAME, 
            label=PAALM_DROP_DOWN_MENU_LABEL, 
            parent=gMainWindow, 
            tearOff=True)
        cmds.menuItem(
            label='Show Editor', 
            parent=dropDownMenu,
            command=pm.Callback(self.show_editor_window))
        cmds.menuItem(
            label='About',
            parent=dropDownMenu,
            command=pm.Callback(self.show_about_page))
        #cmds.menuItem(divider=True)
        cmds.menuItem(
            label='Quit',
            parent=dropDownMenu,
            command=pm.Callback(self.quit))