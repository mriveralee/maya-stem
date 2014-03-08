# -*- coding: utf-8 -*-
import sys, math
import random
#import LSystem

import maya
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx

import pymel.all as pm
from pymel.core import *
from functools import partial

import StemGlobal as SG

#------------------------------------------------------------------------------#
# StemSpaceNode Class - Subclassed Maya Mpx.Node that implements the Space Node
# for the Self-organizing L-system presented in Self-organizing tree models for
# image synthesis by Pałubicki, W., et al.
#------------------------------------------------------------------------------#

# The Stem Node Name
STEM_SPACE_NODE_TYPE_NAME = "kStemSpaceNode"

# The Stem Node Id
STEM_SPACE_NODE_ID = OpenMaya.MTypeId(0xFA236)

class StemSpaceNode(OpenMayaMPx.MPxNode):
  # Declare class variables:
  # TODO - declare the input and output class variables
  #         i.e. inNumPoints = OpenMaya.MObject()
  # constructor
  def __init__(self):
    OpenMayaMPx.MPxNode.__init__(self)

  # compute
  def compute(self,plug,data):
    print 'Space Node Compute!'


# StemNode creator
def StemSpaceNodeCreator():
  return OpenMayaMPx.asMPxPtr(StemSpaceNode())

def StemSpaceNodeInitializer():
  #------------------------------------#
  ############ NUM RAND PTS ##########
  #------------------------------------#
  # Num Random Points
  #SG.MAKE_INPUT(nAttr)
  # Numeric Attributes
  print 'Space Node Init'
  # nAttr = OpenMaya.MFnNumericAttribute()
  # StemLightNode.mDefAngle = nAttr.create("angle", "a", OpenMaya.MFnNumericData.kFloat, 22.5)
  # SG.MAKE_INPUT(nAttr)
