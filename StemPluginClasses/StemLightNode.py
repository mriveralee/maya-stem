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
# StemLightNode Class - Subclassed Maya Mpx.Node that implements the Light Node
# for the Self-organizing L-system presented in Self-organizing tree models for
# image synthesis by Pałubicki, W., et al.
#------------------------------------------------------------------------------#

# The Stem Node Name
STEM_LIGHT_NODE_TYPE_NAME = 'StemLightNode'

# The Stem Node Id
STEM_LIGHT_NODE_ID = OpenMaya.MTypeId(0xFA235)

# Attribute Keys
KEY_DEF_LIGHT_RADIUS = 'lightRadius', 'lr'

class StemLightNode(OpenMayaMPx.MPxLocatorNode):

  # Light Radius Attribute
  mDefaultLightRadius = OpenMaya.MObject()

  # Size of drawn lines
  mDisplayRadius = 0.6

  # Size of drawn circle This doesn't change
  mCircleDisplayRadius = 0.3

  # This node's colors
  mR = 0.9
  mG = 0.9
  mB = 0.0
  mA = 0.6

  # constructor
  def __init__(self):
    OpenMayaMPx.MPxLocatorNode.__init__(self)


  # Draw/Onscreen render method
  def draw(self, view, path, style, status):
    glFT = SG.GLFT

    #store the current user setup colors
    glFT.glPushAttrib(OpenMayaRender.MGL_CURRENT_BIT)

    #enable the transparency
    glFT.glEnable(OpenMayaRender.MGL_BLEND)

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
    glFT.glColor4f(self.mR, self.mG, self.mB, self.mA)
    SG.GLFT.glVertex3f(0.0, -self.mDisplayRadius, -self.mDisplayRadius)
    SG.GLFT.glVertex3f(0.0, self.mDisplayRadius, self.mDisplayRadius)
    SG.GLFT.glEnd()

    SG.GLFT.glBegin(OpenMayaRender.MGL_LINES)
    glFT.glColor4f(self.mR, self.mG, self.mB, self.mA)
    SG.GLFT.glVertex3f(0.0, -self.mDisplayRadius, self.mDisplayRadius)
    SG.GLFT.glVertex3f(0.0, self.mDisplayRadius, -self.mDisplayRadius)
    SG.GLFT.glEnd()

    glFT.glBegin(OpenMayaRender.MGL_POLYGON)
    glFT.glColor4f(self.mR, self.mG, self.mB, self.mA)
    for i in range(0,360):
        rad = (i * 2 * math.pi)/360;
        glFT.glNormal3f(0.0, 0.0, 1.0)
        if (i == 360):
          glFT.glTexCoord3f(
            self.mCircleDisplayRadius * math.cos(0),
            self.mCircleDisplayRadius * math.sin(0),
            0.0)
          glFT.glVertex3f(
            self.mCircleDisplayRadius * math.cos(0),
            self.mCircleDisplayRadius * math.sin(0),
            0.0)
        else:
          glFT.glTexCoord3f(
            self.mCircleDisplayRadius * math.cos(rad),
            self.mCircleDisplayRadius * math.sin(rad),
            0.0)
          glFT.glVertex3f(
            self.mCircleDisplayRadius * math.cos(rad),
            self.mCircleDisplayRadius * math.sin(rad),
            0.0)
    glFT.glEnd()
    glFT.glDisable(OpenMayaRender.MGL_BLEND)
    glFT.glPopAttrib()
    view.endGL()


  # compute
  def compute(self,plug,data):
    # do nothing
    return

# StemNode creator
def StemLightNodeCreator():
  return OpenMayaMPx.asMPxPtr(StemLightNode())

def StemLightNodeInitializer():
  # Numeric Attributes
  nAttr = OpenMaya.MFnNumericAttribute()
  StemLightNode.mDefLightRadius = nAttr.create(
    KEY_DEF_LIGHT_RADIUS[0],
    KEY_DEF_LIGHT_RADIUS[1],
    OpenMaya.MFnNumericData.kFloat, 0.6)
  SG.MAKE_INPUT(nAttr)

  # Add attributes
  StemLightNode.addAttribute(StemLightNode.mDefLightRadius)
