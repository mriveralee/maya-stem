# -*- coding: utf-8 -*-
import sys, math
import random
import maya
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx

import pymel.all as pm
from pymel.core import *
from functools import partial

# Import the necessary STEM Plugin Nodes
import StemGlobal as SG
import StemInstanceNode as SI
import StemSpaceNode as SS
import StemLightNode as SL
import StemUI as SU

#------------------------------------------------------------------------------#
# StemPlugin Class - Loads/Initializes the STEM Plugin classes
#------------------------------------------------------------------------------#

##############################################################
###  INIT FUNCTIONS FOR PLUG-IN  #############################
##############################################################
# The UI Drop Down Menu
STEM_SYSTEM_MENU = SU.StemUIMenu()

# initialize the script plug-in
def initializePlugin(mobject):
  print "Trying to init"
  mplugin = OpenMayaMPx.MFnPlugin(mobject,
    SG.STEM_AUTHORS,
    SG.STEM_VERSION,
    "Any")

  try:
    # Register StemNode
    mplugin.registerNode(SI.STEM_INSTANCE_NODE_TYPE_NAME,
      SI.STEM_INSTANCE_NODE_ID,
      SI.StemInstanceNodeCreator,
      SI.StemInstanceNodeInitializer,
      OpenMayaMPx.MPxNode.kLocatorNode)

    # Register StemSpaceNode
    mplugin.registerNode(SS.STEM_SPACE_NODE_TYPE_NAME,
      SS.STEM_SPACE_NODE_ID,
      SS.StemSpaceNodeCreator,
      SS.StemSpaceNodeInitializer,
      OpenMayaMPx.MPxNode.kLocatorNode)

    # Register StemLightNode
    mplugin.registerNode(SL.STEM_LIGHT_NODE_TYPE_NAME,
      SL.STEM_LIGHT_NODE_ID,
      SL.StemLightNodeCreator,
      SL.StemLightNodeInitializer,
      OpenMayaMPx.MPxNode.kLocatorNode)
      
  except:
    sys.stderr.write(
      "Failed to register node: %s\n" % SI.STEM_INSTANCE_NODE_TYPE_NAME)
    # uninitialize the script plug-in

def uninitializePlugin(mobject):
  mplugin = OpenMayaMPx.MFnPlugin(mobject)
  try:

    # Unregister StemNode
    mplugin.deregisterNode(SI.STEM_INSTANCE_NODE_ID)

    # Unregister StemSpaceNode
    mplugin.deregisterNode(SS.STEM_SPACE_NODE_ID)

    # Unregister StemLightNode
    mplugin.deregisterNode(SL.STEM_LIGHT_NODE_ID)

    # Delete old UI
    if STEM_SYSTEM_MENU != None:
      #print 'removing menu'
      cmds.deleteUI(STEM_SYSTEM_MENU.name)
  except:
    sys.stderr.write(
      "Failed to unregister node: %s\n" % SI.STEM_INSTANCE_NODE_TYPE_NAME)
