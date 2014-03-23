# -*- coding: utf-8 -*-
import sys, math
import random

import maya
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaRender as OpenMayaRender

#------------------------------------------------------------------------------#
# Global Functions & Variables for Maya-Stem
#------------------------------------------------------------------------------#

# Stem Authorship  & Links
STEM_AUTHORS = 'Michael Rivera (mriveralee) & Judy Trinh (judytrinh)'
STEM_VERSION = '0.1'
STEM_GITHUB_SITE = 'https://github.com/mriveralee/maya-stem/'
STEM_HELP_SITE = 'http://github.com/mriveralee/maya-stem/issues'

# Maya's OpenGL Renderer & Function table api
GL_RENDERER = OpenMayaRender.MHardwareRenderer.theRenderer()
GLFT = GL_RENDERER.glFunctionTable()

'''
'' Functions for declaring attributes as inputs
'''
def MAKE_INPUT(attr):
  attr.setKeyable(1)
  attr.setStorable(1)
  attr.setReadable(1)
  attr.setWritable(1)

'''
'' Function for declaring attribute as output
'''
def MAKE_OUTPUT(attr):
  attr.setKeyable(0)
  attr.setStorable(0)
  attr.setReadable(1)
  attr.setWritable(0)

'''
'' Function for getting all nodes of a type
'''
def getNodesByType(nodeType):
  return cmds.ls(type=nodeType)

'''
'' Sum two array-based vectors
'''
def sumArrayVectors(v1, v2):
  v3 = [ v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2] ]
  return v3


'''
'' Computes the parent
'''
def getLocatorWorldPosition(locatorNode):
  if locatorNode is None:
    # TODO: Add an error message at some point / exception
    return [0, 0, 0]

  # Get parents of node (if any)
  parents = cmds.listRelatives(locatorNode, p=True, type='transform')

  # Only continue if there is a parent
  if len(parents) == 0:
    return [0, 0, 0]

  # Get world space transform matrix of parent
  mat = cmds.xform(parents[0], query=True, ws=True, m=True)
  # Get Local position of locator node
  localPos = cmds.getAttr(locatorNode + '.localPosition')[0]

  # Transform position by matrix - assuming pos[3] == 1
  worldPos = [0.0, 0.0, 0.0]

  # Compute world position
  worldPos[0] = mat[0] * localPos[0] + mat[4] * localPos[1] + mat[8] * localPos[2] + mat[12];

  worldPos[1] = mat[1] * localPos[0] + mat[5] * localPos[1] + mat[9] * localPos[2] + mat[13];

  worldPos[2] = mat[2] * localPos[0] + mat[6] * localPos[1] + mat[10] * localPos[2] + mat[14];

  # Return the computed world position
  return worldPos
