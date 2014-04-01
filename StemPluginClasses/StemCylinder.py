# -*- coding: utf-8 -*-
import sys, math
import random
import maya
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx

 # Global Mesh Variables
G_POINTS = OpenMaya.MPointArray()
G_NORMALS =  OpenMaya.MVectorArray()
G_FACE_COUNTS =  OpenMaya.MIntArray()
G_FACE_CONNECTS =  OpenMaya.MIntArray()

def initCylinderMesh(r):
  print 'initCylinderMesh x1'
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
  # Stem Variablees
  mStart = OpenMaya.MPoint()
  mEnd = OpenMaya.MPoint()
  mRadius = 0.25

  def __init__(self, start, end, radius=0.25):
    mStart = start
    mEnd = end
    mRadius = radius
    print 'Making cylinder'
    if (G_POINTS.length() == 0):
      initCylinderMesh(radius)


  '''
  '' Appends the cylinder to the mesh
  '''
  def appendToMesh(self, points, faceCounts, faceConnects):
    cpoints = OpenMaya.MPointArray()
    cnormals = OpenMaya.MVectorArray()
    self.transform(cpoints, cnormals)

    startIndex = points.length()
    # append points
    for i in range(0, points.length()):
      points.append(cpoints[i])

    for i in range(0, G_FACE_COUNTS.length()):
      faceCounts.append(G_FACE_COUNTS[i])

    for i in range(0, G_FACE_CONNECTS.length()):
      faceConnects.append(G_FACE_CONNECTS[i] + startIndex)

    print 'Finished Appending to Mesh!'


  '''
  '' Gets the mesh of the cylinders
  '''
  def getMesh(self, points, faceCounts, faceConnects):
    cnormals = OpenMaya.MVectorArray()
    self.transform(points, cnormals)
    faceCounts = G_FACE_COUNTS
    faceConnects = G_FACE_CONNECTS
    return (points, faceCounts, faceConnects)


  '''
  '' Transforms apoints to match
  '''
  def transform(self, points, normals):
    print 'Transforming points'
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
    print 'constructing matrix'
    mat[0][0] = forward[0]
    print 'assigned 0,0'
    mat[0][1] = left[0]
    mat[0][2] = up[0]
    mat[0][3] = 0
    mat[1][0] = forward[1]
    mat[1][1] = left[1]
    mat[1][2] = up[1]
    mat[1][3] = 0
    mat[2][0] = forward[2]
    mat[2][1] = left[2]
    mat[2][2] = up[2]
    mat[2][3] = 0
    mat[3][0] = 0
    mat[3][1] = 0
    mat[3][2] = 0
    mat[3][3] = 1
    matTrans = mat.transpose()
    print 'finished matrix'
    for i in range(0, G_POINTS.length()):
      p = G_POINTS[i]
      p.x = p.x * s # scale
      p = p * matTrans + self.mStart #transform
      points.append(p)

      # Normal Vector
      n = G_NORMALS[i] * matTrans
      normals.append(n)
