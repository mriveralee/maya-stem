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
STEM_LIGHT_NODE_TYPE_NAME = "StemLightNode"

# The Stem Node Id
STEM_LIGHT_NODE_ID = OpenMaya.MTypeId(0xFA235)

class StemLightNode(OpenMayaMPx.MPxLocatorNode):
  # Declare class variables

  # Size of drawn sphere
  mDisplayRadius = 0.6
  mSphereDisplayRadius = 0.3

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

    glFT.glBegin(OpenMayaRender.MGL_POLYGON)
    for i in range(0,360):
        rad = (i * 2 * math.pi)/360;
        glFT.glNormal3f(0.0, 0.0, 1.0)
        if (i == 360):
          glFT.glTexCoord3f(
            self.mSphereDisplayRadius * math.cos(0),
            self.mSphereDisplayRadius * math.sin(0),
            0.0)
          glFT.glVertex3f(
            self.mSphereDisplayRadius * math.cos(0),
            self.mSphereDisplayRadius * math.sin(0),
            0.0)
        else:
          glFT.glTexCoord3f(
            self.mSphereDisplayRadius * math.cos(rad),
            self.mSphereDisplayRadius * math.sin(rad),
            0.0)
          glFT.glVertex3f(
            self.mSphereDisplayRadius * math.cos(rad),
            self.mSphereDisplayRadius * math.sin(rad),
            0.0)
    glFT.glEnd()

    view.endGL()


  # compute
  def compute(self,plug,data):
    print 'Light Node Compute!'


# StemNode creator
def StemLightNodeCreator():
  return OpenMayaMPx.asMPxPtr(StemLightNode())

def StemLightNodeInitializer():
  #------------------------------------#
  ############ NUM RAND PTS ##########
  #------------------------------------#
  # Num Random Points
  #SG.MAKE_INPUT(nAttr)
  # Numeric Attributes
  print 'Light Node Init'
  # nAttr = OpenMaya.MFnNumericAttribute()
  # StemLightNode.mDefAngle = nAttr.create(
  #  "angle", "a", OpenMaya.MFnNumericData.kFloat, 22.5)
  # SG.MAKE_INPUT(nAttr)
