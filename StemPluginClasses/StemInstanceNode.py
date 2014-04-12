# -*- coding: utf-8 -*-
import sys, math, ctypes
import random
import LSystem
from collections import deque

import maya
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaRender as OpenMayaRender
import maya.OpenMayaUI as OpenMayaUI

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

# Bud List Keys
KEY_BUD = 'bud'
KEY_RESOURCE_NODE_LIST = 'resNodes'

# BH Model Coefficients
BH_LAMBDA = 0.5 # controls bias of resource allocation. values in [0,1]
BH_ALPHA = 1 #2# coefficient of proportionality for v_base, value from paper ex.

# Default Grammar File
DEFAULT_GRAMMAR_FILE = './StemPluginClasses/trees/simple4.txt'

# Default LSystem Step Size
DEFAULT_STEP_SIZE = 1.0

# Default Angle
DEFAULT_ANGLE = 42.5


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

  mOptimalGrowthPairs = []

  # LSystem Variables
  mLSystem = LSystem.LSystem()
  mPrevGrammarFile = None
  mPrevGrammarContent = None
  # constructor
  def __init__(self):
    OpenMayaMPx.MPxLocatorNode.__init__(self)

  '''
  '' Draw/Onscreen render method for displaying this node
  '''
  def draw(self, view, path, style, status):
    # circle
    glFT = SG.GLFT
    view.beginGL()
    glFT.glBegin(OpenMayaRender.MGL_POLYGON)
    #glFT.glColor4f(0.8, 0.5, 0.0, 0.8)
    for i in range(0,360):
      if (i % 2 != 0):
        continue
      rad = (i * 2 * math.pi)/360;
      glFT.glNormal3f(0.0, 1.0, 0.0)
      if (i == 360):
        glFT.glTexCoord3f(
          self.mDisplayRadius * math.cos(0),
          0.0,
          self.mDisplayRadius * math.sin(0))
        glFT.glVertex3f(
          self.mDisplayRadius * math.cos(0),
          0.0,
          self.mDisplayRadius * math.sin(0))
      else:
        glFT.glTexCoord3f(
          self.mDisplayRadius * math.cos(rad),
          0.0,
          self.mDisplayRadius * math.sin(rad))
        glFT.glVertex3f(
          self.mDisplayRadius * math.cos(rad),
          0.0,
          self.mDisplayRadius * math.sin(rad))
    glFT.glEnd()

    # Draw resource distribution values at "bud" (ahem) locations
    glFT.glPushAttrib(OpenMayaRender.MGL_CURRENT_BIT)
    glFT.glColor4f(0.0, 1.0, 0.0, 0.0)
    #view.drawText("bob <3", OpenMaya.MPoint(0.0,0.0,0.0))
    for b in self.mInternodes:
      val = int(b.mVResourceAmount * 100) / 100.0
      view.drawText(str(val), b.mEnd, OpenMayaUI.M3dView.kCenter)
    glFT.glPopAttrib()

    # Draw light distribution values at base locations
    glFT.glPushAttrib(OpenMayaRender.MGL_CURRENT_BIT)
    glFT.glColor4f(1.0, 0.84, 0.0, 0.0)
    for b in self.mInternodes:
      val = int(b.mQLightAmount * 100) / 100.0
      point = b.mStart + ((b.mEnd - b.mStart) / 2.0)
      view.drawText(str(val), point, OpenMayaUI.M3dView.kCenter)
    glFT.glPopAttrib()
    view.endGL()
		# view.beginGL()
		# SG.GLFT.glBegin(OpenMayaRender.MGL_LINES)
		# SG.GLFT.glVertex3f(0.0, -0.5, 0.0)
		# SG.GLFT.glVertex3f(0.0, 0.5, 0.0)
		# SG.GLFT.glEnd()
    #
		# view.endGL()

  '''
  '' Computes input/output updates for the node
  '''
  def compute(self,plug,data):
    if plug == StemInstanceNode.outputMesh:
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
  '' Finds the optimal growth direction angles and their bud growth pairs for
  '' each bud in the tree
  '''
  def getBudOptimalGrowthDirs(self):

    # TODO - remove when finished debugging curves
    self.eraseCurves()

    # Get list of resource noces
    resNodes = cmds.ls(type=SL.STEM_LIGHT_NODE_TYPE_NAME)

    # Get list of buds in the scence
    buds = self.createBudList(self.getRootInternode())

    # If Buds is empty, we want to use the StemInstanceLocation as the only bud
    # position (it acts as a root)
    if len(buds) == 0:
      # TODO: Figure out how to get this stemInstanceNode's maya name from
      # within this class
      # budPosition = SG.getLocatorWorldPosition(None)
      rootBudPos = OpenMaya.MPoint(0, 0, 0)
      buds = [SC.StemCylinder(rootBudPos, rootBudPos)]

    # Make optimal bud-node adjacency list
    allBudsAdjList = self.createBudResNodeAdjacencyList(buds, resNodes)

    # Now compute optimal growth dirs and bud pair directions
    optimalGrowthPairs = []

    # Now compute the optimal growth dir
    for budNodePair in allBudsAdjList:
      # Separate the pair (bud, nodes)
      # print 'Bud Node Pair!', budNodePair
      bud = budNodePair.get(KEY_BUD)
      budNodes = budNodePair.get(KEY_RESOURCE_NODE_LIST)

      # Calculate the weighted average growth direction
      budPosition = bud.mEnd
      sumNodePositions = [0, 0, 0]
      numNodes = len(budNodes)

      # Sum the node positions and weight them
      for n in budNodes:
        # TODO add weighting funciton that include the radius of light/space etc
        nodePos = SG.getLocatorWorldPosition(n)
        sumNodePositions = SG.sumArrayVectors(sumNodePositions, nodePos)

      # Now average the node positions and substract the bud position to compute
      # the optimal growth direction
      budOptGrowthDir = [ (sumNodePositions[0] / numNodes) - budPosition[0],
        (sumNodePositions[1] / numNodes) - budPosition[1],
        (sumNodePositions[2] / numNodes) - budPosition[2]]

      # Compute OptimalGrowthPoint
      optPt = SG.sumArrayVectors(budPosition, budOptGrowthDir)

      # Dot prod and length of the vectors for optGrowthAngle
      optPtLength = SG.getVectorLength(optPt)
      bPosLength = SG.getVectorLength(budPosition)
      dotProd = SG.getVectorDotProduct(optPt, budPosition)
      crossProd = SG.crossVectors(budPosition, optPt)
      # For getting Optimal growth angles
      optGrowthAngle = 0
      if optPtLength != 0 and bPosLength != 0:
        optGrowthAngle = math.acos(dotProd / (bPosLength * optPtLength))
        # Convert to degrees
        optGrowthAngle = optGrowthAngle * 180 / math.pi

      # TODO - decide if we want to use growth Angle OR growth vector...
      growthPair = (budPosition, crossProd, optGrowthAngle)
      #growthAnglePair = (budPosition, optGrowthAngle)

      self.drawCurve(budPosition, optPt)
      # Now append to the list of pairs
      optimalGrowthPairs.append(growthPair)
      #optimalGrowthPairs.append(growthAnglePair)



    # print 'Optimal Growth Pairs'
    # print optimalGrowthPairs
    # print '****************************'

    # Return the Optimal Growth Pairs
    return optimalGrowthPairs

  '''
  '' Draws a curve between two points
  '''
  def drawCurve(self, p1, p2):
    # TODO - Remove when ever we figure out how that turtle shit works with
    # with rotations, nah mean?
    curve = cmds.curve( p=[(p1[0], p1[1], p1[2]), (p2[0], p2[1], p2[2])])
    curveColor = random.randint(2,10)
    cmds.setAttr(str(curve) + ".overrideColor", )
  '''
  '' Erases all curves in the Maya Scene
  '''
  def eraseCurves(self):
    # TODO - erase all curves in scene
    allCurves = cmds.ls(type="nurbsCurve")
    for c in allCurves:
      print("deleted:", c)
      cmds.delete(str(c))



  '''
  '' Creates a list of buds based on this instanceNode's internode list
  '' Returns an empty array if no buds are present
  '''
  def createBudList(self, node):
    # Creates a list of buds based on the internodes list-
    # A bud is defined as the end point of an internode that has no children
    childBuds = []
    for n in self.mInternodes:
      if n.mInternodeChildren is None or len(n.mInternodeChildren) == 0:
        childBuds.append(n)
    return childBuds
    # if node is None:
    #   return []
    # elif node.mInternodeChildren is None or len(node.mInternodeChildren) == 0:
    #   return [node]
    # else:
    #   childBuds = []
    #   for child in node.mInternodeChildren:
    #     childBuds = childBuds + self.createBudList(child)
    #   return childBuds

  '''
  '' Creates a bud to resource node adjacency list where each bud is associated
  '' with a list of resource nodes that it is the closest bud to
  '''
  def createBudResNodeAdjacencyList(self, buds, resNodes):
    # Determine the nodes that are closest to particular buds
    # Create an adjacency list (dictionary) that stores the adj list
    allBudsAdjacencyList = {}
    for n in resNodes:
      # Get position of resNode
      nPos = SG.getLocatorWorldPosition(n)

      # Init optimal bud and set the minDist to be max
      optimalBud = None
      minDist = 100000000

      # Search through the list of buds and find the closest bud
      for b in buds:
        # Get distance between bud and resNode
        currentDist = SG.getDistance(b.mEnd, nPos)

        # Update optimal bud if necessary
        if currentDist < minDist:
          optimalBud = b
          minDist = currentDist

      # Now append the resNode to the bud's adjacency list
      budKey = str(optimalBud)

      # Check if list already exists, if it does just append
      if allBudsAdjacencyList.has_key(budKey):
        # Get the budResNode pair of the bud
        budPair = allBudsAdjacencyList.get(budKey)

        # Get list of resNodes for the budPair
        budResNodes = budPair.get(KEY_RESOURCE_NODE_LIST)

        # Append to the list
        budResNodes.append(n)

        # Update the list
        allBudsAdjacencyList[budKey][KEY_RESOURCE_NODE_LIST] = budResNodes

      else:
        # If it doesn't exist, create the bud node pair
        budPair = {KEY_BUD: optimalBud, KEY_RESOURCE_NODE_LIST: [n]}

        # And add it to the adjacency list
        allBudsAdjacencyList[budKey] = budPair

    # Return a list of the adjacency lists
    return allBudsAdjacencyList.values()

  '''
  '' Returns the root internode of the Stem tree
  '''
  def getRootInternode(self):
    if len(self.mInternodes) == 0:
      return None
    return self.mInternodes[0]

  '''
  '' Converts optimal growth pairs into vectors for the LSystem
  '''
  def convertOptGrowthPairsForLSystem(self, optimalGrowthPairs):
    # The buds and dirs
    buds = LSystem.VectorPyBranch()
    dirs = LSystem.VectorPyBranch()
    angles = LSystem.VecFloat()


    # Convert all the maya points to std::vector<float> and push into vector
    for pair in optimalGrowthPairs:
      b = pair[0]
      pos = LSystem.VecFloat()
      pos.push_back(b[0])
      pos.push_back(b[1])
      pos.push_back(b[2])
      buds.push_back(pos)

      # Convert list of directions to std::vector<float> and push into the vector
      d = pair[1]
      dirVec = LSystem.VecFloat()
      dirVec.push_back(d[0])
      dirVec.push_back(d[1])
      dirVec.push_back(d[2])
      dirs.push_back(dirVec)

      # Convert list of angles
      a = pair[2]
      angles.push_back(a)

    return [buds, dirs, angles]


  '''
  '' Creates a Cylinder Mesh based on the LSystem
  '''
  def createMesh(self, iters, angle, step, grammarFile, data, newOutputData):
    # # Get optimal growth pairs and send to LSystem
    # mOptimalGrowthPairs = self.getBudOptimalGrowthDirs()
    # # Convert optimal growth pairs into vectors
    # [buds, dirs] = self.convertOptGrowthPairsForLSystem(optimalGrowthPairs)
    #
    # # Sets the optimal growth directions for the LSystem
    # self.mLSystem.setOptimalBudDirs(buds, dirs)

    # Test the output of the buds and angles in the LSystem
    # self.verifyLSystemBudAngles(buds, dirs)

    # Get Grammar File Contents & load to lsys
    if grammarFile != self.mPrevGrammarFile:
      self.mPrevGrammarContent = self.readGrammarFile(grammarFile)
      self.mPrevGrammarFile = grammarFile

    grammarContent = self.mPrevGrammarContent

    if len(grammarContent) == 0:
      print "Invalid Grammar File!"
      return None

    # Init the LSystem from the parameters
    self.mLSystem.setDefaultAngle(float(angle))
    self.mLSystem.setDefaultStep(float(step))
    self.mLSystem.loadProgramFromString(grammarContent)

    # Print contents
    print "Grammar File: " + grammarFile
    print "Grammar File Contents: " + self.mLSystem.getGrammarString()

    # The branches and flowers objects
    branches = LSystem.VectorPyBranch()
    flowers = LSystem.VectorPyBranch()

    # Run Grammar String
    self.mLSystem.processPy(iters, branches, flowers)

    # Set up cylinder mesh
    cPoints = OpenMaya.MPointArray()
    cFaceCounts = OpenMaya.MIntArray()
    cFaceConnects = OpenMaya.MIntArray()

    self.mInternodes = []
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

    # TODO: possibly remove this later, using for testing
    self.performBHModelResourceDistribution()

    # TODO - Handle flowers (uncomment when needed)
    # for i in range(0, flowers.size()):
    #   f = flowers[i]
    #   centerLoc = OpenMaya.MVector(f[0], f[1], f[2])
    #   print 'create flower!'

    # print("point Length: ", cPoints.length())
    # print("faceCount Length: ", cFaceCounts.length())
    # print("faceConnect Length: ", cFaceConnects.length())

    ''' Compute Optimal Growth pairs '''
    # Get optimal growth pairs and send to LSystem
    mOptimalGrowthPairs = self.getBudOptimalGrowthDirs()
    # Convert optimal growth pairs into vectors
    [buds, dirs, angles] = self.convertOptGrowthPairsForLSystem(mOptimalGrowthPairs)

    # Sets the optimal growth directions for the LSystem
    self.mLSystem.setOptimalBudDirs(buds, dirs, angles)


    # Verify a mesh was made
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

  '''
  ''  Performs a BFS traversal from the root and pushes each node
  ''  onto a stack along the way, returning a list in BFS order.
  ''  Can be used to get reverse order traversal.
  '''
  def getBfsTraversal(self, root):
    if root is None:
      return []

    queue = deque([root])
    stack = []

    while (len(queue) > 0):
      b = queue.popleft()
      # TODO: remove later. this bit is for testing on simple case
      if len(b.mInternodeChildren) == 0:
        b.mQLightAmount = 1
      queue.extend(b.mInternodeChildren)
      stack.append(b)

    return stack

  '''
  ''  Distributes amount of resource (v) from a single internode to its children
  ''  using given equations. Currently assumes first child is m and second is l
  '''
  def distributeSingleResource(self, internode):
    if (internode is None):
      return
    if (len(internode.mInternodeChildren) == 0):
      return
    if (len(internode.mInternodeChildren) == 1):
      child = internode.mInternodeChildren[0]
      child.mVResourceAmount = internode.mVResourceAmount
      return

    pV = internode.mVResourceAmount

    # TODO: still need to determine which is along main axis and which isn't
    pQm = internode.mInternodeChildren[0].mQLightAmount
    pQl = internode.mInternodeChildren[1].mQLightAmount

    # Compute amount of resource distributed to axis branch and lateral branch
    pVm = pV * (BH_LAMBDA * pQm) / (BH_LAMBDA*pQm + (1-BH_LAMBDA)*pQl + 0.001)
    pVl = pV * ((1-BH_LAMBDA)*pQl) / (BH_LAMBDA*pQm + (1-BH_LAMBDA)*pQl + 0.001)

    # Distribute
    internode.mInternodeChildren[0].mVResourceAmount = pVm
    internode.mInternodeChildren[1].mVResourceAmount = pVl

  '''
  ''  Propogates light amounts (Q) from outermost internodes to towards the base.
  ''  (TODO: May have to edit to grab the light information from buds themselves)
  '''
  def performBasipetalPass(self):
    branchStack = self.getBfsTraversal(self.getRootInternode())
    # newList = list(branchStack)
    # for each internode, propogate light information from leaf nodes towards base
    while (len(branchStack) > 0):
      b = branchStack.pop()
      if (b.mInternodeParent != None):
        b.mInternodeParent.mQLightAmount += b.mQLightAmount

    # TODO: remove later. prints light values after propogation in BFS order
    # for b in newList:
    #   print b.mQLightAmount

  '''
  ''  Distributes resource acropetally between continuing main axes
  ''  and lateral branches throughout entire tree.
  '''
  def performAcropetalPass(self):
    # v_base = alpha * Q_base
    root = self.getRootInternode()
    vBase = BH_ALPHA * root.mQLightAmount
    root.mVResourceAmount = vBase
    bfsTraversal = self.getBfsTraversal(root)
    # newList = list(bfsTraversal)

    # Distribute resource acropetally (from base upwards)
    for b in bfsTraversal:
      self.distributeSingleResource(b)

    # TODO: remove later. prints resource values in BFS order
    # for b in newList:
    #   print b.mVResourceAmount

  '''
  ''  Performs BH Model passes to distribute resources throught the tree.
  '''
  def performBHModelResourceDistribution(self):
    self.performBasipetalPass()
    self.performAcropetalPass()


  '''
  '' Verifies the output passed to the LSystem
  '' Where <buds> and <angles> are sent to the LSystem and
  '' and <b1> and <d1> are read back from the LSystem
  '''
  def verifyLSystemBudAngles(self, buds, angles):
    b1 = LSystem.VectorPyBranch()
    d1 = LSystem.VecFloat()
    self.mLSystem.getOptimalBudDirs(b1, d1)
    for i in range(0, b1.size()):
      b = b1[i]
      # Get points
      print ('BudDir', d1[i], b[0], b[1], b[2])
      print ('Dirs', d1[i] == dirs[i], 'Positions', buds[i][0] == b[0], buds[i][1] == b[1], buds[i][2] == b[2])
    print 'Finished verifying buds and dirs'
    return

# StemNode creator
def StemInstanceNodeCreator():
  return OpenMayaMPx.asMPxPtr(StemInstanceNode())

def StemInstanceNodeInitializer():
  # Numeric Attributes
  nAttr = OpenMaya.MFnNumericAttribute()
  StemInstanceNode.mDefAngle = nAttr.create(
    KEY_ANGLE[0],
    KEY_ANGLE[1],
    OpenMaya.MFnNumericData.kFloat, DEFAULT_ANGLE)
  SG.MAKE_INPUT(nAttr)

  # Step size
  nAttr = OpenMaya.MFnNumericAttribute()
  StemInstanceNode.mDefStepSize = nAttr.create(
    KEY_STEP_SIZE[0],
    KEY_STEP_SIZE[1],
    OpenMaya.MFnNumericData.kFloat, DEFAULT_STEP_SIZE)
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
