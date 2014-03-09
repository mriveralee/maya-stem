# -*- coding: utf-8 -*-
import sys, math

import maya
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx

import pymel.all as pm
from pymel.core import *
from functools import partial

import StemGlobal as SG
import StemInstanceNode as SI
import StemLightNode as SL
import StemSpaceNode as SS

#------------------------------------------------------------------------------#
# StemUI Class - represents the UI in the Maya STEM Plugin
#------------------------------------------------------------------------------#

##############################################################
###  Custom Drop Down Menu   ########################
##############################################################
# TODO MOVE UI into separate class
STEM_DROP_DOWN_MENU_NAME = "kStemSystemDropDownMenu"

class StemUIMenu(object):

  name = STEM_DROP_DOWN_MENU_NAME

  def printbutton(self):
    print 'Button clicked'

  def makeStemInstanceNode(self):
    cmds.createNode(SI.STEM_INSTANCE_NODE_TYPE_NAME)

  def makeStemSpaceResourceNode(self):
    cmds.createNode(SS.STEM_SPACE_NODE_TYPE_NAME)

  def makeStemLightResourceNode(self):
    cmds.createNode(SL.STEM_LIGHT_NODE_TYPE_NAME)

  def makeUsingMelExample(self):
    cmd = ('sphere; instancer; createNode StemInstanceNode; '
      'connectAttr nurbsSphere1.matrix instancer1.inputHierarchy[0]; '
      'connectAttr StemInstanceNode.mBranches instancer1.inputPoints; '
      'connectAttr StemInstanceNode.mFlowers instancer1.inputPoints; ')
    maya.mel.eval(cmd)

  def openGitHubPage(self):
    cmds.launch(webPage=SG.STEM_GITHUB_SITE)

  def openHelpPage(self):
    cmds.launch(webPage=SG.STEM_HELP_SITE)

  '''
  '' Initialize the DropDown Menu
  '''
  def __init__(self):
    print 'Init the menu!'
    gMainWindow = maya.mel.eval('$temp1=$gMainWindow')
    # Delete the old window by name if it exists
    if (self.exists()):
      cmds.deleteUI(self.name)

    dropDownMenu = cmds.menu(
      STEM_DROP_DOWN_MENU_NAME,
      label='STEM',
      parent=gMainWindow,
      tearOff=True)

    # Create Stem Instance Node
    cmds.menuItem(
      label='Create Stem Instance Node',
      parent=dropDownMenu,
      command=pm.Callback(self.makeStemInstanceNode))

    # Create Space Resource Node
    cmds.menuItem(
      label='Create Space Resouce Node',
      parent=dropDownMenu,
      command=pm.Callback(self.makeStemSpaceResourceNode))

    # Create Light Resource Node
    cmds.menuItem(
      label='Create Light Resource Node',
      parent=dropDownMenu,
      command=pm.Callback(self.makeStemLightResourceNode))
    #cmds.menuItem(divider=True)
    # Show help menu
    cmds.menuItem(
      label='Help',
      parent=dropDownMenu,
      command=pm.Callback(self.openHelpPage))

    # Show the Source Code
    cmds.menuItem(
      label='Source Code',
      parent=dropDownMenu,
      command=pm.Callback(self.openGitHubPage))

  '''
  '' Returns true if this menu exists in Maya's top option menu
  '''
  def exists(self):
    return cmds.menu(self.name, query=True, exists=True)
