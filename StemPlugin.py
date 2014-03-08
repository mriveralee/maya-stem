# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# The STEM Functions for Stem Maya
#----------------------------------------------------------------------------
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
import StemNode
import StemSpaceNode
import StemLightNode
import StemUI


##############################################################
###  INIT FUNCTIONS FOR PLUG-IN  #############################
##############################################################

# initialize the script plug-in
def initializePlugin(mobject):
  print "Trying to init"
  mplugin = OpenMayaMPx.MFnPlugin(mobject,
    "Mriveralee & Judytrinh",
    "0.1",
    "Any")

  try:
    # Register StemNode
    mplugin.registerNode(kPluginStemNodeTypeName, kStemInstanceNodeId,
    StemNodeCreator, StemNodeInitializer)

    # Register StemSpaceNode
    # mplugin.registerNode(kPluginStemNodeTypeName, kStemInstanceNodeId,
    #   StemNodeCreator, StemNodeInitializer)

    # Register StemLightNode
    mplugin.registerNode(kPluginStemNodeTypeName, kStemInstanceNodeId,
    StemNodeCreator, StemNodeInitializer)
  except:
    sys.stderr.write(
    "Failed to register node: %s\n" % kPluginStemNodeTypeName)
    # uninitialize the script plug-in

def uninitializePlugin(mobject):
  global STEM_SYSTEM_MENU
  mplugin = OpenMayaMPx.MFnPlugin(mobject)
  try:

    # Unregister StemNode
    mplugin.deregisterNode(StemInstanceNodeId)

    # Unregister StemLightNode
    # mplugin.deregisterNode(StemInstanceNodeId)

    # Unregister StemSpaceNode
    # mplugin.deregisterNode(StemInstanceNodeId)

    # Delete old UI
    if STEM_SYSTEM_MENU != None:
      cmds.deleteUI(STEM_SYSTEM_MENU.name)
  except:
    sys.stderr.write( "Failed to unregister node: %s\n" % kPluginNodeTypeName )
