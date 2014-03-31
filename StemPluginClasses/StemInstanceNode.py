# -*- coding: utf-8 -*-
import sys, math, ctypes
import random
import LSystem

import maya
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaRender as OpenMayaRender

import StemGlobal as SG
import StemSpaceNode as SS
import StemLightNode as SL

#------------------------------------------------------------------------------#
# StemInstanceNode Class - Subclassed Maya Mpx.Node that implements the
# Self-organizing presented in Self-organizing tree models for image synthesis
# by Pałubicki, W., et al.
#------------------------------------------------------------------------------#

# The Stem Node Name
STEM_INSTANCE_NODE_TYPE_NAME = "StemInstanceNode"

# The Stem Node Id
STEM_INSTANCE_NODE_ID = OpenMaya.MTypeId(0xFA234)

# Input Keys
KEY_ITERATIONS = 'iterations', 'iter'
KEY_TIME = 'time', 'tm'
KEY_GRAMMAR = 'grammarFile', 'grf'
KEY_ANGLE = 'angle', 'ang'
KEY_STEP_SIZE = 'stepSize' , 'ss'

# Toggle Keys
KEY_BRANCH_SHEDDING = 'useBranchShedding', 'shed'
KEY_RESOURCE_DISTRIBUTION = 'useResources', 'resd'

# Output Keys
KEY_BRANCHES = 'branches', 'br'
KEY_FLOWERS = 'flowers', 'fl'
KEY_OUTPUT = 'outputMesh', 'out'
KEY_OUTPOINTS = 'outPoints', 'op'

# Node definition
class StemInstanceNode(OpenMayaMPx.MPxLocatorNode):
  # Declare class variables:

  # Size of drawn sphere
  mDisplayRadius = 1.0

  # Node Time

  time = OpenMaya.MObject()
  mID = OpenMaya.MObject()

  # Output Mesh
  outputMesh = OpenMaya.MObject()

  # Outpoints
  outPoints = OpenMaya.MObject()

  # Default Values
  mDefAngle = OpenMaya.MObject()
  mDefStepSize = OpenMaya.MObject()
  mDefGrammarFile = OpenMaya.MObject()
  mIterations = OpenMaya.MObject()

  # Stem Option Values
  mHasResourceDistribution = OpenMaya.MObject()
  mHasBranchShedding = OpenMaya.MObject()


  # Other values
  mBranches = OpenMaya.MObject()
  mFlowers = OpenMaya.MObject()

  # constructor
  def __init__(self):
    OpenMayaMPx.MPxLocatorNode.__init__(self)

  # Draw/Onscreen render method
  def draw(self, view, path, style, status):
    # circle
    glFT = SG.GLFT
    view.beginGL()
    glFT.glBegin(OpenMayaRender.MGL_POLYGON)
    for i in range(0,360):
        rad = (i * 2 * math.pi)/360;
        glFT.glNormal3f(0.0, 0.0, 1.0)
        if (i == 360):
          glFT.glTexCoord3f(
            self.mDisplayRadius * math.cos(0),
            self.mDisplayRadius * math.sin(0),
            0.0)
          glFT.glVertex3f(
            self.mDisplayRadius * math.cos(0),
            self.mDisplayRadius * math.sin(0),
            0.0)
        else:
          glFT.glTexCoord3f(
            self.mDisplayRadius * math.cos(rad),
            self.mDisplayRadius * math.sin(rad),
            0.0)
          glFT.glVertex3f(
            self.mDisplayRadius * math.cos(rad),
            self.mDisplayRadius * math.sin(rad),
            0.0)
    glFT.glEnd()
    view.endGL()
		# view.beginGL()
		# SG.GLFT.glBegin(OpenMayaRender.MGL_LINES)
		# SG.GLFT.glVertex3f(0.0, -0.5, 0.0)
		# SG.GLFT.glVertex3f(0.0, 0.5, 0.0)
		# SG.GLFT.glEnd()
    #
		# view.endGL()

  # compute
  def compute(self,plug,data):
    print self.calculateOptimalGrowthDirection()
    if plug == StemInstanceNode.outputMesh:
      print 'is output mesh #2'
      # Create branch segments array from LSystemBranches use id, position,
      # aimDirection, scale
      # Note: Can change input geometry of instancer

      # Create Flowers array from LSystemGeometry use id, position,
      # aim direction, scale
      # Note: Can change input geometry of instancer

      # Time
      timeData = data.inputValue(StemInstanceNode.time)
      t = timeData.asInt()

      # Num Iterations
      iterData = data.inputValue(StemInstanceNode.mIterations)
      iters = iterData.asInt()

      # Step Size
      stepSizeData = data.inputValue(StemInstanceNode.mDefStepSize)
      step = stepSizeData.asFloat()

      # Angle
      angleData = data.inputValue(StemInstanceNode.mDefAngle)
      angle = angleData.asFloat()

      # Grammar File String and convert from the maya object
      grammarData =  data.inputValue(StemInstanceNode.mDefGrammarFile)
      grammarFile = str(grammarData.asString())
      #c_char_p(str(grammarFile))

      # Get output objects
      outputHandle = data.outputValue(StemInstanceNode.outputMesh)
      dataCreator = OpenMaya.MFnMeshData()
      newOutputData = dataCreator.create()
      #self.createPoints(iters, angle, step, grammarFile, newOutputData)

      # The New mesh!

      self.createPoints(iters, angle, step, grammarFile, data)

      # Set new output data
      outputHandle.set(data)

      # Clear up the data
      data.setClean(plug)

  '''
  ''  Reads a text file that is selected using a file dialog then returns its
  ''  contents. If no file exists, it returns the empty string
  '''
  def readGrammarFileUsingDialog(self):
    txtFileFilter = 'Text Files (*.txt)'
    fileNames = cmds.fileDialog2(fileFilter=txtFileFilter, dialogStyle=2, fileMode=1)
    return self.readGrammarFile(fileNames[0])

  '''
  ''  Reads a text file that is passed by string
  ''  contents. If no file exists, it returns the empty string
  '''
  def readGrammarFile(self, fileName):
      if (len(fileName) <= 0):
        return ""
      try:
        f = open(fileName, 'r')
        fileContents = f.read()
        f.close()
        return fileContents
      except:
        return ""

  '''
  '' Calculates the optimal growth direction vector for branch growth
  '''
  def calculateOptimalGrowthDirection(self):
    # Get the list of stem nodes
    resNodes = cmds.ls(type=SL.STEM_LIGHT_NODE_TYPE_NAME) + cmds.ls(type=SS.STEM_SPACE_NODE_TYPE_NAME)

    # The sum of the resource node locations and the number of resource nodes
    sumLocations = [0.0, 0.0, 0.0]
    numNodes = len(resNodes)

    if (numNodes == 0):
      # TODO: handle case where there is no place to go (pick random dir?)
      return [0.0, 0.0, 0.0]

    # Now go through each node and sum node locations
    for n in resNodes:
      # TODO add weighting funciton that include the radius of light/space etc
      pos = SG.getLocatorWorldPosition(n)
      sumLocations = SG.sumArrayVectors(sumLocations, pos)

    # Get position of the instance node
    # TODO: get position of the instance node
    startPos = [0.0, 0.0, 0.0]  #SG.getLocatorWorldPosition(self)

    # Now average the position to get the optimal grown direction
    optGrowthDir = [ (sumLocations[0] / numNodes) - startPos[0],
      (sumLocations[1] / numNodes) - startPos[1],
      (sumLocations[2] / numNodes) - startPos[2]]

    print optGrowthDir
    # return the value
    return optGrowthDir

  ''' Create the Points for this node '''
  def createPoints(self, iters, angle, step, grammarFile, data):

    #------------------------------------------------#
    ############ POINTS DATA FOR ATTR_ARRAY ##########
    #------------------------------------------------#
    # Set up the array for adding random points
    pointsData = data.outputValue(StemInstanceNode.outPoints) #the MDataHandle
    pointsAAD = OpenMaya.MFnArrayAttrsData() #the MFnArrayAttrsData
    pointsObject = pointsAAD.create() #the MObject

    # Create the vectors for “position” and “id”. Names and types must
    # match # table above.
    positionArray = pointsAAD.vectorArray('position')
    idArray = pointsAAD.doubleArray('id')

    # Create the vectors for “position” and “id”. Names and types must
    # match # table above.
    scaleArray = pointsAAD.vectorArray('scale')
    aimDirArray = pointsAAD.vectorArray('aimDirection')

    #------------------------------------#
    ############# LSYSTEM INIT ###########
    #------------------------------------#

    lsys = LSystem.LSystem()
    lsys.setDefaultAngle(float(angle))
    lsys.setDefaultStep(float(step))

    # Get Grammar File Contents & load to lsys
    grammarContent = self.readGrammarFile(grammarFile)
    lsys.loadProgramFromString(grammarContent)
    print "Grammar File: " + grammarFile
    print "Grammar File Contents: " + lsys.getGrammarString()


    branches = LSystem.VectorPyBranch()
    flowers = LSystem.VectorPyBranch()

    # Run Grammar String
    lsys.processPy(iters, branches, flowers)

    print 'finished lsystem process!'

    # Set up the array for adding random points
    pointsData = data.outputValue(StemInstanceNode.mBranches) #the MDataHandle
    pointsAAD = OpenMaya.MFnArrayAttrsData() #the MFnArrayAttrsData
    pointsObject = pointsAAD.create() #the MObject

    # Create the vectors for “position” and “id”. Names and types must
    # match # table above.
    positionArray = pointsAAD.vectorArray('position')
    idArray = pointsAAD.doubleArray('id')

    # Create the vectors for “position” and “id”. Names and types must
    # match # table above.
    scaleArray = pointsAAD.vectorArray('scale')
    aimDirArray = pointsAAD.vectorArray('aimDirection')


    # BRANCH ME OUT
    for i in range(0, branches.size()):
      index = i + 2 * i
      # Make Branch! wooo

      b = branches[i]
      print 'made it!'

      # Get points
      start = OpenMaya.MVector(b[0], b[1], b[2])
      end = OpenMaya.MVector(b[3], b[4], b[5])
      sFactor = (1 - branches.size() / (i + 1))
      scale = OpenMaya.MVector(1.1 * sFactor, 1.2 * sFactor, 1.1 * sFactor)

      # Append
      positionArray.append(start)
      positionArray.append(end)
      idArray.append(index)
      idArray.append(index + 1)
      scaleArray.append(scale)
      aimDirArray.append(aim)

    # Finish branch set up
    pointsData.setMObject(pointsObject)

    # Set up the array for adding random points
    fData = data.outputValue(StemInstanceNode.mBranches) #the MDataHandle
    fAAD = OpenMaya.MFnArrayAttrsData() #the MFnArrayAttrsData
    fObject = fAAD.create() #the MObject

    # Create the vectors for “position” and “id”. Names and types must
    # match # table above.
    positionArray = fAAD.vectorArray('position')
    idArray = fAAD.doubleArray('id')

    # Create the vectors for “position” and “id”. Names and types must
    # match # table above.
    scaleArray = fAAD.vectorArray('scale')
    aimDirArray = fAAD.vectorArray('aimDirection')

    # FLOWER POWER
    for i in range(0, flowers.size()):
      index = i + 2 * i * branches.size()
      f = flowers[i]
      start = OpenMaya.MVector(f[0], f[1], f[2])
      sFactor = (1 - flowers.size() / (i + 1))
      scale = OpenMaya.MVector(1.1 * sFactor, 1.1 * sFactor, 1.1 * sFactor)
      aim = OpenMaya.MVector(
        random.random(), random.random(), random.random())

      # Append
      positionArray.append(start)
      idArray.append(index)
      scaleArray(scale)
      aimDirArray.append(aim)

    # Now set the flower data :)
    fData.setMObject(fObject)

    print 'create mesh!'

# StemNode creator
def StemInstanceNodeCreator():
  return OpenMayaMPx.asMPxPtr(StemInstanceNode())

def StemInstanceNodeInitializer():
  # Numeric Attributes
  nAttr = OpenMaya.MFnNumericAttribute()
  StemInstanceNode.mDefAngle = nAttr.create(
    KEY_ANGLE[0],
    KEY_ANGLE[1],
    OpenMaya.MFnNumericData.kFloat, 22.5)
  SG.MAKE_INPUT(nAttr)

  # Step size
  nAttr = OpenMaya.MFnNumericAttribute()
  StemInstanceNode.mDefStepSize = nAttr.create(
    KEY_STEP_SIZE[0],
    KEY_STEP_SIZE[1],
    OpenMaya.MFnNumericData.kFloat, 1.0)
  SG.MAKE_INPUT(nAttr)

  # Iterations
  nAttr = OpenMaya.MFnNumericAttribute()
  StemInstanceNode.mIterations = nAttr.create(
    KEY_ITERATIONS[0],
    KEY_ITERATIONS[1],
    OpenMaya.MFnNumericData.kLong, 1)
  SG.MAKE_INPUT(nAttr)

  # Has Resource Distribution Checkbox (toggles to regular L-system)
  nAttr = OpenMaya.MFnNumericAttribute()
  StemInstanceNode.mHasResourceDistribution = nAttr.create(
    KEY_RESOURCE_DISTRIBUTION[0],
    KEY_RESOURCE_DISTRIBUTION[1],
    OpenMaya.MFnNumericData.kBoolean, 1)
  SG.MAKE_INPUT(nAttr)

  # Has Branch Shedding Checkbox
  nAttr = OpenMaya.MFnNumericAttribute()
  StemInstanceNode.mHasBranchShedding = nAttr.create(
    KEY_BRANCH_SHEDDING[0],
    KEY_BRANCH_SHEDDING[1],
    OpenMaya.MFnNumericData.kBoolean, 1)
  SG.MAKE_INPUT(nAttr)



  # Time
  uAttr = OpenMaya.MFnUnitAttribute()
  StemInstanceNode.time = uAttr.create(
    KEY_TIME[0],
    KEY_TIME[1],
    OpenMaya.MFnUnitAttribute.kTime, 0)
  SG.MAKE_INPUT(uAttr)

  # Grammar File
  tAttr = OpenMaya.MFnTypedAttribute()
  StemInstanceNode.mDefGrammarFile = tAttr.create(
    KEY_GRAMMAR[0],
    KEY_GRAMMAR[1],
    OpenMaya.MFnData.kString)
  SG.MAKE_INPUT(tAttr)

  # Branch Segments
  tAttr = OpenMaya.MFnTypedAttribute()
  StemInstanceNode.mBranches =  tAttr.create(
    KEY_BRANCHES[0],
    KEY_BRANCHES[1],
    OpenMaya.MFnArrayAttrsData.kDynArrayAttrs)
  SG.MAKE_OUTPUT(tAttr)

  # Flowers
  tAttr = OpenMaya.MFnTypedAttribute()
  StemInstanceNode.mFlowers =  tAttr.create(
    KEY_FLOWERS[0],
    KEY_FLOWERS[1],
    OpenMaya.MFnArrayAttrsData.kDynArrayAttrs)
  SG.MAKE_OUTPUT(tAttr)

  # Output mesh
  tAttr = OpenMaya.MFnTypedAttribute()
  StemInstanceNode.outputMesh = tAttr.create(
    KEY_OUTPUT[0],
    KEY_OUTPUT[1],
    OpenMaya.MFnData.kMesh)
  SG.MAKE_OUTPUT(tAttr)


  # Outpoints
  StemInstanceNode.outPoints = tAttr.create(
    KEY_OUTPOINTS[0],
    KEY_OUTPOINTS[1],
    OpenMaya.MFnArrayAttrsData.kDynArrayAttrs)
  SG.MAKE_OUTPUT(tAttr)



  # add Attributues

  StemInstanceNode.addAttribute(StemInstanceNode.mDefAngle)
  StemInstanceNode.addAttribute(StemInstanceNode.mDefStepSize)
  StemInstanceNode.addAttribute(StemInstanceNode.mDefGrammarFile)
  StemInstanceNode.addAttribute(StemInstanceNode.mHasResourceDistribution)
  StemInstanceNode.addAttribute(StemInstanceNode.mIterations)
  StemInstanceNode.addAttribute(StemInstanceNode.mHasBranchShedding)



  StemInstanceNode.addAttribute(StemInstanceNode.time)
  StemInstanceNode.addAttribute(StemInstanceNode.outputMesh)
  StemInstanceNode.addAttribute(StemInstanceNode.mFlowers)
  StemInstanceNode.addAttribute(StemInstanceNode.mBranches)

  StemInstanceNode.addAttribute(StemInstanceNode.outPoints)
  # LSystemInstanceNode.addAttribute(LSystemInstanceNode.outPoints)


  # Attribute Effects to Flowers
  StemInstanceNode.attributeAffects(
    StemInstanceNode.time,
    StemInstanceNode.mFlowers)

  StemInstanceNode.attributeAffects(
    StemInstanceNode.mIterations,
    StemInstanceNode.mFlowers)

  StemInstanceNode.attributeAffects(
    StemInstanceNode.mDefAngle,
    StemInstanceNode.mFlowers)

  StemInstanceNode.attributeAffects(
    StemInstanceNode.mDefStepSize,
    StemInstanceNode.mFlowers)

  StemInstanceNode.attributeAffects(
    StemInstanceNode.mDefGrammarFile,
    StemInstanceNode.mFlowers)

  StemInstanceNode.attributeAffects(
    StemInstanceNode.mHasResourceDistribution,
    StemInstanceNode.mFlowers)

  StemInstanceNode.attributeAffects(
    StemInstanceNode.mHasBranchShedding,
    StemInstanceNode.mFlowers)

  #Attributes Effects to Branches
  StemInstanceNode.attributeAffects(
    StemInstanceNode.time,
    StemInstanceNode.mBranches)

  StemInstanceNode.attributeAffects(
    StemInstanceNode.mIterations,
    StemInstanceNode.mBranches)

  StemInstanceNode.attributeAffects(
    StemInstanceNode.mDefAngle,
    StemInstanceNode.mBranches)

  StemInstanceNode.attributeAffects(
    StemInstanceNode.mDefStepSize,
    StemInstanceNode.mBranches)

  StemInstanceNode.attributeAffects(
    StemInstanceNode.mDefGrammarFile,
    StemInstanceNode.mBranches)

  StemInstanceNode.attributeAffects(
    StemInstanceNode.mHasResourceDistribution,
    StemInstanceNode.mBranches)

  StemInstanceNode.attributeAffects(
    StemInstanceNode.mHasBranchShedding,
    StemInstanceNode.mBranches)


  #Attributes Effects to Branches
  StemInstanceNode.attributeAffects(
    StemInstanceNode.time,
    StemInstanceNode.outputMesh)

  StemInstanceNode.attributeAffects(
    StemInstanceNode.mIterations,
    StemInstanceNode.outputMesh)

  StemInstanceNode.attributeAffects(
    StemInstanceNode.mDefAngle,
    StemInstanceNode.outputMesh)

  StemInstanceNode.attributeAffects(
    StemInstanceNode.mDefStepSize,
    StemInstanceNode.outputMesh)

  StemInstanceNode.attributeAffects(
    StemInstanceNode.mDefGrammarFile,
    StemInstanceNode.outputMesh)

  StemInstanceNode.attributeAffects(
    StemInstanceNode.mHasResourceDistribution,
    StemInstanceNode.outputMesh)

  StemInstanceNode.attributeAffects(
    StemInstanceNode.mHasBranchShedding,
    StemInstanceNode.outputMesh)
