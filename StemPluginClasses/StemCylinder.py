# -*- coding: utf-8 -*-
import sys, math
import random
import maya
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx

import StemGlobal as SG

 # Global Mesh Variables
G_POINTS = OpenMaya.MPointArray()
G_NORMALS =  OpenMaya.MVectorArray()
G_FACE_COUNTS =  OpenMaya.MIntArray()
G_FACE_CONNECTS =  OpenMaya.MIntArray()

def initCylinderMesh(r):
  numslices = 10
  angle = math.pi * 2 / numslices

  # Add points and normals
  G_POINTS.clear()
  G_NORMALS.clear()
  G_FACE_COUNTS.clear()
  G_FACE_CONNECTS.clear()

  for i in range(0, numslices):
    G_POINTS.append(OpenMaya.MPoint(0, r*math.cos(angle*i), r*math.sin(angle*i)))
    G_NORMALS.append(OpenMaya.MVector(0, r*math.cos(angle*i), r*math.sin(angle*i)))

  for i in range(0, numslices):
    G_POINTS.append(OpenMaya.MPoint(1, r*math.cos(angle*i), r*math.sin(angle*i)))
    G_NORMALS.append(OpenMaya.MVector(0, r*math.cos(angle*i), r*math.sin(angle*i)))

  # endcap 1
  G_POINTS.append(OpenMaya.MPoint(0,0,0))
  G_NORMALS.append(OpenMaya.MVector(-1,0,0))

  # endcap 2
  G_POINTS.append(OpenMaya.MPoint(1,0,0))
  G_NORMALS.append(OpenMaya.MVector(1,0,0))

  # Set indices for endcap 1
  for i in range(0, numslices):
    G_FACE_COUNTS.append(3) # append triangle
    G_FACE_CONNECTS.append(2*numslices)
    G_FACE_CONNECTS.append((i+1)%numslices)
    G_FACE_CONNECTS.append(i)

  # Set indices for endcap 2
  for i in range(numslices, 2*numslices):
    G_FACE_COUNTS.append(3) # append triangle
    G_FACE_CONNECTS.append(2*numslices+1)
    G_FACE_CONNECTS.append(i)
    nextNum = i+1
    if (nextNum >= 2*numslices):
      nextNum = numslices
    G_FACE_CONNECTS.append(nextNum)

  # Set indices for middle
  for i in range(0, numslices):
    G_FACE_COUNTS.append(4)
    G_FACE_CONNECTS.append(i)
    G_FACE_CONNECTS.append((i+1)%numslices)
    G_FACE_CONNECTS.append((i+1)% numslices + numslices)
    G_FACE_CONNECTS.append(i + numslices)

'''
'' Stem Cylinder Class for creating a cylinder based mesh for LSystems
'''
class StemCylinder():

  def __init__(self, start, end, radius=0.25):
    self.mStart = start
    self.mEnd = end
    self.mRadius = radius
    self.mInternodeParent = None
    self.mInternodeChildren = []
    if (G_POINTS.length() == 0):
      initCylinderMesh(radius)


  '''
  '' Appends the cylinder to the mesh
  '''
  def appendToMesh(self, points, faceCounts, faceConnects):
    (cpoints, cnormals) = self.transform(
      OpenMaya.MPointArray(),
      OpenMaya.MVectorArray())

    startIndex = points.length()
    # append points
    for i in range(0, cpoints.length()):
      points.append(cpoints[i])

    for i in range(0, G_FACE_COUNTS.length()):
      faceCounts.append(G_FACE_COUNTS[i])

    for i in range(0, G_FACE_CONNECTS.length()):
      faceConnects.append(G_FACE_CONNECTS[i] + startIndex)

    return (points, faceCounts, faceConnects)


  '''
  '' Gets the mesh of the cylinders
  '''
  def getMesh(self, points, faceCounts, faceConnects):
    cnormals = OpenMaya.MVectorArray()
    (cpoints, cnormals) = self.transform(points, cnormals)
    faceCounts = G_FACE_COUNTS
    faceConnects = G_FACE_CONNECTS
    return (cpoints, faceCounts, faceConnects)


  '''
  '' Transforms apoints to match
  '''
  def transform(self, points, normals):
    forward = self.mEnd - self.mStart
    s = forward.length()
    forward.normalize()

    left = OpenMaya.MVector(0,0,1) ^ forward
    up = OpenMaya.MVector()

    if (left.length() < 0.0001):
      up = forward ^ OpenMaya.MVector(0,1,0)
      left = up^forward
    else:
      up = forward ^ left

    # Construct matrix
    mat = OpenMaya.MMatrix()
    row0 = OpenMaya.MPoint(forward[0], left[0], up[0], 0)
    row1 = OpenMaya.MPoint(forward[1], left[1], up[1], 0)
    row2 = OpenMaya.MPoint(forward[2], left[2], up[2], 0)
    row3 = OpenMaya.MPoint(0, 0, 0, 1)

    # Set the values in the Matrix
    SG.setRow(mat, row0, 0)
    SG.setRow(mat, row1, 1)
    SG.setRow(mat, row2, 2)
    SG.setRow(mat, row3, 3)

    # Take the transpose of the matrix
    matTrans = mat.transpose()

    # Add points and normals
    for i in range(0, G_POINTS.length()):
      p = G_POINTS[i]
      # Scale
      p.x = p.x * s

      # Transform
      p = p * matTrans
      p = SG.sumMayaVectors(p, self.mStart) #transform

      # Points Vector
      points.append(p)

      # Normal Vector
      n = G_NORMALS[i] * matTrans
      normals.append(n)
    return (points, normals)