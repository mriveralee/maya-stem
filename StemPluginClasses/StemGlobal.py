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
STEM_VERSION = '0.2'
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
'' Get length of float vector
'''
def getVectorLength(v1):
  sx = math.pow(v1[0], 2)
  sy = math.pow(v1[1], 2)
  sz = math.pow(v1[2], 2)
  return math.sqrt(sx + sy + sz)

'''
'' Get dot product of two float vectors
'''
def getVectorDotProduct(v1, v2):
  return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

'''
'' Sum two array-based vectors
'''
def sumArrayVectors(v1, v2):
  v3 = [ v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2] ]
  return v3

'''
'' Add two MPoints OR MVectors
'''
def sumMayaVectors(v1, v2):
  if type(v1) != type(v2):
    print 'Vectors must be both MPoint or MVector'
    return None
  elif type(v1) is type(OpenMaya.MPoint()):
    v3 = OpenMaya.MPoint(v1.x + v2.x,
      v1.y + v2.y,
      v1.z + v2.z,
      v1.w + v2.w)
    return v3
  elif type(v1) is type(OpenMaya.MVector()):
    v3 = OpenMaya.MVector(
      v1.x + v2.x,
      v1.y + v2.y,
      v1.z + v2.z)
    return v3
  else:
    return None

'''
'' Gets the cross product between two 3x3 vectors:
'''
def crossVectors(a, b):
    return [a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0] ]


'''
'' Gets the Euclidean distance of two vectors, points, or 3-floats in 3D space
'''
def getDistance(v1, v2):
  p1 = v1
  p2 = v2

  # Get point values as float array if type is a point or vector
  if type(v1) is type(OpenMaya.MPoint()) or type(v1) is type(OpenMaya.MVector()):
    p1 = [v1.x, v1.y, v1.z]

  if type(v2) is type(OpenMaya.MPoint()) or type(v2) is type(OpenMaya.MVector()):
    p2 = [v2.x, v2.y, v2.z]

  # Compute squared distance components
  x = math.pow(p2[0] - p1[0], 2)
  y = math.pow(p2[1] - p1[1], 2)
  z = math.pow(p2[2] - p1[2], 2)
  # compute distance
  dist = math.sqrt(x + y + z)

  return dist


'''
'' Sets the row of a Maya MMatrix
'''
def setRow(matrix, newVector, row):
  OpenMaya.MScriptUtil.setDoubleArray(matrix[row], 0, newVector.x)
  OpenMaya.MScriptUtil.setDoubleArray(matrix[row], 1, newVector.y)
  OpenMaya.MScriptUtil.setDoubleArray(matrix[row], 2, newVector.z)

  # Handle case where vector passed has 4-Dimensions
  if type(newVector) is type(OpenMaya.MPoint()):
    OpenMaya.MScriptUtil.setDoubleArray(matrix[row], 3, newVector.w)
  return

'''
'' Sets a cell of a Maya MMatrix
'''
def setCell(matrix, value, row, column):
  OpenMaya.MScriptUtil.setDoubleArray( matrix[row], column, value )


'''
'' Computes position of a locator node in 3D space
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
  worldPos[0] = mat[0] * localPos[0] + mat[4] * localPos[1] + mat[8] * localPos[2] + mat[12]

  worldPos[1] = mat[1] * localPos[0] + mat[5] * localPos[1] + mat[9] * localPos[2] + mat[13]

  worldPos[2] = mat[2] * localPos[0] + mat[6] * localPos[1] + mat[10] * localPos[2] + mat[14]

  # Return the computed world position
  return worldPos


'''
'' Draws a curve between two points
'''
def drawCurve(p1, p2):
  curve = cmds.curve(p=[(p1[0], p1[1], p1[2]), (p2[0], p2[1], p2[2])], degree=1)
  curveColor = random.randint(2,10)
  cmds.setAttr(str(curve) + ".overrideColor", )

'''
'' Erases all curves in the Maya Scene
'''
def eraseCurves():
  allCurves = cmds.ls(type="nurbsCurve")
  for c in allCurves:
    # print("deleted:", c)
    cmds.delete(str(c))
