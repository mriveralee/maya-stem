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
import StemLightNode as SL
import StemCylinder as SC

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

# Default Grammar File
DEFAULT_GRAMMAR_FILE = "./StemPluginClasses/trees/simple1.txt"


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

  # Branch and Bud Data Structures
  mInternodes = []
  mBudAnglePairs = []

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
    if plug == StemInstanceNode.outputMesh:
      print 'Optimal Growth direction', self.calculateOptimalGrowthDirection()
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
      outputHandle = data.outputValue(self.outputMesh)
      dataCreator = OpenMaya.MFnMeshData()
      newOutputData = dataCreator.create()

      # The New mesh!
      meshResult = self.createMesh(
        iters, angle, step, grammarFile,
        data, newOutputData)

      # Make sure we have a valid mesh
      if (meshResult != None):
        # Set new output data/mesh
        outputHandle.setMObject(newOutputData)

        # Clear up the data
        data.setClean(plug)

        print 'StemInstance Generated!'

  '''
  '' Calculates the optimal growth direction vector for branch growth
  '''
  def calculateOptimalGrowthDirection(self):
    # Get the list of stem nodes
    #resNodes = cmds.ls(type=SL.STEM_LIGHT_NODE_TYPE_NAME) + cmds.ls(type=SS.STEM_SPACE_NODE_TYPE_NAME)
    resNodes = cmds.ls(type=SL.STEM_LIGHT_NODE_TYPE_NAME)
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
  '''
  '' Finds the optimal growth direction angles and their bud growth pairs for
  '' each bud in the tree
  '''
  def getOptimateGrowthDirs(self):
    # Take the list of light resource nodes
    # Take the list of buds - get
    # for each light resource node
    budList = self.createBudList()
    return None

  '''
  '' Creates a list of buds based on this instanceNode's internode list
  '' Returns an empty array if no buds are present
  '''
  def createBudList(self):
    # Creates a list of buds based on the internodes list-
    # A bud is defined as the end point of an internode that has no children
    return [('bud', 'angle')]
  '''
  '' Creates a Cylinder Mesh based on the LSystem
  '''
  def createMesh(self, iters, angle, step, grammarFile, data, newOutputData):
    #------------------------------------#
    ############# LSYSTEM INIT ###########
    #------------------------------------#
    # Get Grammar File Contents & load to lsys
    grammarContent = self.readGrammarFile(grammarFile)

    if len(grammarContent) == 0:
      print "Invalid Grammar File!"
      return None

    # Create LSystem from the parameters
    lsys = LSystem.LSystem()
    lsys.setDefaultAngle(float(angle))
    lsys.setDefaultStep(float(step))
    lsys.loadProgramFromString(grammarContent)
    print "Grammar File: " + grammarFile
    print "Grammar File Contents: " + lsys.getGrammarString()

    # The branches and flowers objects
    branches = LSystem.VectorPyBranch()
    flowers = LSystem.VectorPyBranch()

    # Run Grammar String
    lsys.processPy(iters, branches, flowers)


    # Set up cylinder mesh
    cPoints = OpenMaya.MPointArray()
    cFaceCounts = OpenMaya.MIntArray()
    cFaceConnects = OpenMaya.MIntArray()

    for i in range(0, branches.size()):
      b = branches[i]
      # Get points
      start = OpenMaya.MPoint(b[0], b[1], b[2])
      end = OpenMaya.MPoint(b[3], b[4], b[5])
      radius = 0.25

      # Create a cylinder from the end points
      cyMesh = SC.StemCylinder(start, end, radius)
      self.mInternodes.append(cyMesh)

      # Append the Cylinder's mesh to our main mesh
      cyMesh.appendToMesh(cPoints, cFaceCounts, cFaceConnects)

   # Create parent/child heirarchy
    for iBranch in self.mInternodes:
      for jBranch in self.mInternodes:
        if (iBranch.mEnd == jBranch.mStart):
          iBranch.mInternodeChildren.append(jBranch)
          jBranch.mInternodeParent = iBranch


    # TODO - Handle flowers (uncomment when needed)
    # for i in range(0, flowers.size()):
    #   f = flowers[i]
    #   centerLoc = OpenMaya.MVector(f[0], f[1], f[2])
    #   print 'create flower!'

    # print("point Length: ", cPoints.length())
    # print("faceCount Length: ", cFaceCounts.length())
    # print("faceConnect Length: ", cFaceConnects.length())

    if (cPoints.length() == 0
      or cFaceCounts.length() == 0
      or cFaceConnects.length() == 0):
      print 'No LSystem generated!'
      return None


    status = OpenMaya.MStatus()
    meshFs = OpenMaya.MFnMesh()
    # Now create the new mesh!
    newMesh = meshFs.create(
      int(cPoints.length()), int(cFaceCounts.length()),
      cPoints, cFaceCounts, cFaceConnects, newOutputData)

    return meshFs

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
  defStringData = OpenMaya.MFnStringData().create(DEFAULT_GRAMMAR_FILE)
  tAttr = OpenMaya.MFnTypedAttribute()
  StemInstanceNode.mDefGrammarFile = tAttr.create(
    KEY_GRAMMAR[0],
    KEY_GRAMMAR[1],
    OpenMaya.MFnData.kString,
    defStringData)
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
