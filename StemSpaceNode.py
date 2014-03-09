# -*- coding: utf-8 -*-
import sys, math
import random
#import LSystem

import maya
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaRender as OpenMayaRender

import StemGlobal as SG

#------------------------------------------------------------------------------#
# StemSpaceNode Class - Subclassed Maya Mpx.Node that implements the Space Node
# for the Self-organizing L-system presented in Self-organizing tree models for
# image synthesis by Pałubicki, W., et al.
#------------------------------------------------------------------------------#

# The Stem Node Name
STEM_SPACE_NODE_TYPE_NAME = "StemSpaceNode"

# The Stem Node Id
STEM_SPACE_NODE_ID = OpenMaya.MTypeId(0xFA236)

class StemSpaceNode(OpenMayaMPx.MPxLocatorNode):
  # Declare class variables:
  mDisplayRadius = 0.7

  # constructor
  def __init__(self):
    OpenMayaMPx.MPxLocatorNode.__init__(self)
    # Draw/Onscreen render method
  def draw(self, view, path, style, status):
    # circle
    glFT = SG.GLFT
    view.beginGL()

    SG.GLFT.glBegin(OpenMayaRender.MGL_LINES)
    SG.GLFT.glVertex3f(0.0, -self.mDisplayRadius, 0.0)
    SG.GLFT.glVertex3f(0.0, self.mDisplayRadius, 0.0)
    SG.GLFT.glEnd()

    SG.GLFT.glBegin(OpenMayaRender.MGL_LINES)
    SG.GLFT.glVertex3f(-self.mDisplayRadius, 0, 0.0)
    SG.GLFT.glVertex3f(self.mDisplayRadius, 0, 0.0)
    SG.GLFT.glEnd()

    SG.GLFT.glBegin(OpenMayaRender.MGL_LINES)
    SG.GLFT.glVertex3f(-self.mDisplayRadius, -self.mDisplayRadius, 0.0)
    SG.GLFT.glVertex3f(self.mDisplayRadius, self.mDisplayRadius, 0.0)
    SG.GLFT.glEnd()

    SG.GLFT.glBegin(OpenMayaRender.MGL_LINES)
    SG.GLFT.glVertex3f(-self.mDisplayRadius, self.mDisplayRadius, 0.0)
    SG.GLFT.glVertex3f(self.mDisplayRadius, -self.mDisplayRadius, 0.0)
    SG.GLFT.glEnd()

    SG.GLFT.glBegin(OpenMayaRender.MGL_LINES)
    SG.GLFT.glVertex3f(0.0, 0, -self.mDisplayRadius)
    SG.GLFT.glVertex3f(0.0, 0, self.mDisplayRadius)
    SG.GLFT.glEnd()

    SG.GLFT.glBegin(OpenMayaRender.MGL_LINES)
    SG.GLFT.glVertex3f(0.0, -self.mDisplayRadius, -self.mDisplayRadius)
    SG.GLFT.glVertex3f(0.0, self.mDisplayRadius, self.mDisplayRadius)
    SG.GLFT.glEnd()

    SG.GLFT.glBegin(OpenMayaRender.MGL_LINES)
    SG.GLFT.glVertex3f(0.0, -self.mDisplayRadius, self.mDisplayRadius)
    SG.GLFT.glVertex3f(0.0, self.mDisplayRadius, -self.mDisplayRadius)
    SG.GLFT.glEnd()

    view.endGL()

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
