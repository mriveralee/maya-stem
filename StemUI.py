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

#------------------------------------------------------------------------------#
# StemUI Class - represents the UI in the Maya STEM Plugin
#------------------------------------------------------------------------------#


##############################################################
###  Custom Drop Down Menu   ########################
##############################################################
# TODO MOVE UI into separate class
DROP_DOWN_MENU_NAME = "kStemSystemDropDownMenu"

class StemUIMenu(object):

  def printbutton(self):
    print 'Button clicked'

  def makeRNNetwork(self):
      cmd = 'sphere; instancer; createNode randomNode; connectAttr nurbsSphere1.matrix instancer1.inputHierarchy[0]; '
      cmd += 'connectAttr randomNode1.outPoints instancer1.inputPoints;'
      maya.mel.eval(cmd)

  def makeRNNetworkSelected(self):
    cmd = 'sphere; instancer; createNode randomNode; connectAttr nurbsSphere1.matrix instancer1.inputHierarchy[0]; '
    cmd += 'connectAttr randomNode1.mBranches instancer1.outPoints;'
    maya.mel.eval(cmd)

  def makeLSINNetwork(self):
    cmd = 'sphere; instancer; createNode StemInstanceNode; connectAttr nurbsSphere1.matrix instancer1.inputHierarchy[0]; '
    cmd += 'connectAttr StemInstanceNode.mBranches instancer1.inputPoints; connectAttr StemInstanceNode.mFlowers instancer1.inputPoints;'
    maya.mel.eval(cmd)

  def makeLSINNetworkSelected(self):
    cmd = 'sphere; instancer; createNode randomNode; connectAttr nurbsSphere1.matrix instancer1.inputHierarchy[0]; '
    cmd += 'connectAttr StemInstanceNode.mBranches instancer1.inputPoints; connectAttr StemInstanceNode.mFlowers instancer1.inputPoints;'
    maya.mel.eval(cmd)


  '''
  '' Initialize the DropDown Menu
  '''
  def __init__(self):
    gMainWindow = maya.mel.eval('$temp1=$gMainWindow')
    self.name = DROP_DOWN_MENU_NAME
    # Delete the old window by name if it exists
    if (self.exists()):
      cmds.deleteUI(self.name)

      dropDownMenu = cmds.menu(
      DROP_DOWN_MENU_NAME,
      label='LSystemInstance',
      parent=gMainWindow,
      tearOff=True)
      cmds.menuItem(
      label='Create RN Network',
      parent=dropDownMenu,
      command=pm.Callback(self.makeRNNetwork))
      cmds.menuItem(
      label='Create RN Network from Selected',
      parent=dropDownMenu,
      command=pm.Callback(self.makeRNNetworkSelected))
      cmds.menuItem(
      label='Create LSIN Network',
      parent=dropDownMenu,
      command=pm.Callback(self.makeLSINNetwork))
      #cmds.menuItem(divider=True)
      cmds.menuItem(
      label='Create LSIN Network',
      parent=dropDownMenu,
      command=pm.Callback(self.makeLSINNetworkSelected))


  '''
  '' Returns true if this menu exists in Maya's top option menu
  '''
  def exists(self):
    return cmds.menu(self.name, query=True, exists=True)


STEM_SYSTEM_MENU = StemUIMenu()
