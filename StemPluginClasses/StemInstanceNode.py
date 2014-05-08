# -*- coding: utf-8 -*-
import sys, math, ctypes, copy
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
import StemBud as SB


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
KEY_ITERATIONS = 'baseIterations', 'baseIter'
KEY_TIME = 'time', 'tm'
KEY_GRAMMAR = 'grammarFile', 'grf'
KEY_ANGLE = 'angle', 'ang'
KEY_STEP_SIZE = 'stepSize', 'ss'

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

# Key for ResNodeName and Pos
KEY_RESOURCE_NODE_NAME = 'name'
KEY_RESOURCE_NODE_POSITION = 'position'

# BH Model Coefficients
BH_LAMBDA = 0.5 # controls bias of resource allocation. values in [0,1]
BH_ALPHA = 1 #2# coefficient of proportionality for v_base, value from paper ex.

# Default Grammar File
DEFAULT_GRAMMAR_FILE = './StemPluginClasses/trees/simple1.txt'

# Default LSystem Step Size
DEFAULT_STEP_SIZE = 1.0

# Default Angle
DEFAULT_ANGLE = 42.5

# Enable test drawing
ENABLE_RESOURCE_DRAWING = True

# Use Tree Curves
ENABLE_TREE_CURVES = True

# Use Cylinder Mesh
ENABLE_CYLINDER_MESH = False

# Resource Nodes List
# Get list of resource noces
SCENE_RESOURCE_NODES = {}


# StemInstanceNode definition
class StemInstanceNode(OpenMayaMPx.MPxLocatorNode):

  # Size of drawn sphere
  mDisplayRadius = 1.0

  # Node Time
  mTime = OpenMaya.MObject()
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
  mPrevAngle = None
  mPrevIterations = None

  # Optimal Point Curves Drawn
  mOptCurves = []

  # Tree Curves
  mTreeCurves = []

  # Tree Curve Extrusions (form the mesh)
  mTreeExtrusions = []

  # The Tree Mesh
  mTreeMesh = None

  # Reference to the the maya dependency node
  mStemNode = None

  # The Dictionary story the geometry for each iterations 0 is Lsystem Base
  mTreeGrowthInternodes = {}

  # The base branches and flowers for the LSystem
  mBaseBranches = None
  mBaseFlowers = None


  '''
  '' StemInstance Node Constructor
  '''
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
      rad = (i * 2 * math.pi)/360
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

    if ENABLE_RESOURCE_DRAWING:
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

  '''
  '' Computes input/output updates for the node
  '''
  def compute(self, plug, data):
    if plug == StemInstanceNode.outputMesh:
      # Update the reference to this maya's nodes name
      self.updateStemNodeName(plug)

      # Time
      timeData = data.inputValue(StemInstanceNode.mTime)
      timeStep = timeData.asInt()

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
      grammarData = data.inputValue(StemInstanceNode.mDefGrammarFile)
      grammarFile = str(grammarData.asString())

      # Has Resources
      hasResData = data.inputValue(StemInstanceNode.mHasResourceDistribution)
      hasResources = hasResData.asBool()

      # Init LSystem only when grammar/angle/iters change
      shouldInitLSystem = grammarFile != self.mPrevGrammarFile
      shouldInitLSystem = shouldInitLSystem or angle != self.mPrevAngle
      shouldInitLSystem = shouldInitLSystem or iters != self.mPrevIterations

      # Make LSystem Base Tree for growing
      if shouldInitLSystem:
        self.initLSystemBaseTree(iters, angle, step, grammarFile)

      # Check if scene Resource Nodes are dirty!
      resNodes = cmds.ls(type=SL.STEM_LIGHT_NODE_TYPE_NAME)

      if self.areSceneResourceNodesDirty(resNodes):
        # Update the SceneResourceNodes
        self.clearSceneResourceNodes()
        self.setSceneResourceNodes(resNodes)

        # Clear Tree growth that was based on the cleared resource nodes
        self.clearTreeGrowthInternodes()

        print 'Scene Resource Nodes are dirty!'

      # TODO Growth the branches and flowers for this growth iteration
      growthIters = int(cmds.getAttr(str(self.getStemNode()) +'.time'))
      # print ('Growth Iters', growthIters)
      angleJitter = 0.0
      # TODO make angle jitter a parameter for modifying
      self.growTree(growthIters, angle, angleJitter, hasResources, data)

      # Clear up the data
      data.setClean(plug)
      print 'StemInstance Generated!'

  '''
  '' Clears the mTreeGrowthInternodes Cache
  '''
  def clearTreeGrowthInternodes(self):
    self.mTreeGrowthInternodes.clear()

  '''
  '' Clears the SCENE_RESOURCE_NODES
  '''
  def clearSceneResourceNodes(self):
    SCENE_RESOURCE_NODES.clear()

  '''
  '' Set the SCENE_RESOURCE_NODES
  '''
  def setSceneResourceNodes(self, resNodes):
    for n in resNodes:
      nodeKey = str(n)
      nodePos = SG.getLocatorWorldPosition(n)
      # Set up dictionary for holding the RESOURCE NODE Object
      SCENE_RESOURCE_NODES[nodeKey] = {}
      SCENE_RESOURCE_NODES[nodeKey][KEY_RESOURCE_NODE_NAME] = nodeKey
      SCENE_RESOURCE_NODES[nodeKey][KEY_RESOURCE_NODE_POSITION] = nodePos

  '''
  '' Gets the SceneResourcesNodes in the scene
  '''
  def getSceneResourceNodes(self):
    return SCENE_RESOURCE_NODES.values()


  '''
  '' Determines of the SCENE_RESOURCE_NODES are dirty
  '''
  def areSceneResourceNodesDirty(self, resNodes):
    # Make sure scene hasn't changed lighting
    if len(resNodes) != len(SCENE_RESOURCE_NODES.keys()):
      return True

    # Check node positions and names
    for n in resNodes:
      nKey = str(n)
      sceneNode = SCENE_RESOURCE_NODES.get(nKey)
      if sceneNode is None:
        return True

      # Check positions
      nPos = SG.getLocatorWorldPosition(n)
      if sceneNode[KEY_RESOURCE_NODE_POSITION] != nPos:
        return True

    return False

  '''
  '' Creates a Cylinder Mesh based on the LSystem
  '''
  def growTree(self, growthIters, baseGrowthAngle, growthAngleJitter, hasResources, data):
    growthKey = str(growthIters)

    if not hasResources or growthIters is 1:
      ''' Case: No resource growth is used '''
      # grab base branches & flowers
      branches = self.mBaseBranches
      flowers = self.mBaseFlowers

      # Create Internodes for them
      internodes = self.createInternodes(branches, flowers)
      self.mTreeGrowthInternodes[growthKey] = self.copyInternodes(internodes)

    elif self.mTreeGrowthInternodes.get(growthKey) is not None:
      ''' Case: Have Internodes for growthIteration -- update the internodes'''
      self.mInternodes = self.mTreeGrowthInternodes.get(growthKey)

    else:
      ''' Case: No Internodes for a growthIteration -- compute the growth '''
      # Perform growth usings the current growth iters number
      branches = self.mBaseBranches
      flowers = self.mBaseFlowers

      startGrowthNum = 0
      endGrowthNum = growthIters

      # Create Pre Bud Growth Internodes
      preBudGrowthInternodes = self.createInternodes(branches, flowers)

      # Save compiutation if we can :)
      for i in range(0, growthIters):
        gKey = str(i)
        growth = self.mTreeGrowthInternodes.get(gKey)
        if growth is not None:
          startGrowthNum = i
          preBudGrowthInternodes = growth


      for i in range(startGrowthNum, growthIters):
        # Update the optimals pre growth internodes
        optimalGrowthPairs = self.updateOptimalGrowthPairs(preBudGrowthInternodes)

        # ^calculates growth dir, light point, ties light to bud, this is when Q
        # values will get assigned
        # Set the current internodes
        self.configureBudInternodeHeirarchy(preBudGrowthInternodes)

        # Set the current internodes
        # self.mInternodes = preBudGrowthInternodes

        # Now perform resource distribution
        self.performBHModelResourceDistribution(preBudGrowthInternodes)

        # Grow all branches of the tree using v-value (buds toward the light)
        lengthMultipler = 0.25
        radius = 0.25
        minGrowthAngle = math.floor(baseGrowthAngle - growthAngleJitter)
        maxGrowthAngle = math.floor(baseGrowthAngle + growthAngleJitter)

        nextStart = None
        nextEnd = None
        growthDir = None
        newShoots = []




        for b in preBudGrowthInternodes:
            ''' Case 1: b is a bud w/ a light '''
            # TODO add something here woomp
            bPos = [b.mEnd.x, b.mEnd.y, b.mEnd.z]
            lightPos = None
            isLightBud = False
            # growthPair = (budPosition, optPt, optGrowthAngle, lightQValue)
            for gPair in optimalGrowthPairs:
              gPairPos = [gPair[0].x, gPair[0].y, gPair[0].z]
              if (bPos == gPairPos):
                lightPos = OpenMaya.MPoint(gPair[1][0], gPair[1][1], gPair[1][2])
                isLightBud = True
                break

            '''Case 2: b is a bud w/o a light'''
            if b.hasTerminalBud():
              ''' Terminal Buds move along main axis '''
              terminalBud = b.getTerminalBud()
              numShoots = int(math.floor(terminalBud.mVResourceAmount))

              # Start Creating additional shoots
              currentStart = b.mStart
              currentEnd = b.mEnd

              # print ('Appending ', numShoots, ' Terminnal shoots!')
              print 'NumShoots', numShoots
              for j in range(0, numShoots):
                internodeLength = lengthMultipler * terminalBud.mVResourceAmount / numShoots

                if isLightBud:
                  growthDir = SG.normalize(lightPos - currentEnd) * internodeLength
                else:
                  growthDir = SG.normalize(currentEnd - currentStart) * internodeLength
                # Get start and end of next branch
                nextStart = currentEnd
                nextEnd = OpenMaya.MPoint(nextStart.x + growthDir.x,  nextStart.y + growthDir.y, nextStart.z + growthDir.z)

                ''' Now append the terminal shoot '''
                shoot = SC.StemCylinder(nextStart, nextEnd, radius)
                newShoots.append(shoot)

                # Now set the start to be the newEnd
                currentStart = currentEnd
                currentEnd = nextEnd
                # print 'appended terminal bud'

              # Clear the Terminal Bud
              #b.setTerminalBud(None)

            if b.hasLateralBud():
              ''' Lateral Buds move in baseGrownAngle direction '''
              lateralBud = b.getLateralBud()
              numShoots = int(math.floor(lateralBud.mVResourceAmount))

              # Start Creating additional shoots
              currentStart = b.mStart
              currentEnd = b.mEnd

              for j in range(0, numShoots):
                # L = v / n
                internodeLength = lengthMultipler * lateralBud.mVResourceAmount / numShoots
                if isLightBud:
                  growthDir = SG.normalize(lightPos - currentEnd) * internodeLength
                else:
                  # Compute a growth direction with some randomness the growth angle
                  theta = random.randint(minGrowthAngle, maxGrowthAngle) * SG.DEG_2_RAD
                  phi = random.randint(minGrowthAngle, maxGrowthAngle) * SG.DEG_2_RAD
                  psi =  random.randint(minGrowthAngle, maxGrowthAngle) * SG.DEG_2_RAD
                  growthDir = SG.normalize(OpenMaya.MPoint(theta, phi, psi)) * internodeLength

                # Get start and end of next branch
                nextStart = currentEnd
                nextEnd = OpenMaya.MPoint(nextStart.x + growthDir.x,  nextStart.y + growthDir.y, nextStart.z + growthDir.z)

                ''' Now append the lateral shoot '''
                shoot = SC.StemCylinder(nextStart, nextEnd, radius)
                newShoots.append(shoot)

                # Now set the start to be the newEnd
                currentStart = currentEnd
                currentEnd = nextEnd

                # print 'appended lateral bud'

              # Clear the Lateral Bud
              #b.setLateralBud(None)


        # Combine new shoots
        grownTree = preBudGrowthInternodes + newShoots

        # Parent all the shoots
        grownTree = self.createParentChildInternodeHeirarchy(grownTree)

        # Store the iternodes for this iteration
        if i+1 is growthIters:
          self.mTreeGrowthInternodes[growthKey] = self.copyInternodes(grownTree)

        # Set up internodes for the next growth iteration
        preBudGrowthInternodes = grownTree
      #### End growth lopp interation

    # Set up internodes for drawing
    self.mInternodes = self.mTreeGrowthInternodes[growthKey]

    ''' Now update the growth mesh using the current internodes '''
    # If we use tree curves, update the tree mesh
    if ENABLE_TREE_CURVES:
      # print 'Creating Tree curves'
      self.updateTreeMesh(self.mInternodes)

    # IF we enable the cylinder mesh, draw it
    if ENABLE_CYLINDER_MESH:
      self.createCylinderMesh(self.mInternodes, data)


  '''
  '' DEEP Copies a list of internodes
  '''
  def copyInternodes(self, internodes):
    internodesCopy = []
    for b in internodes:
      internode = b.makeCopy()
      internodesCopy.append(internode)

    internodesCopy = self.createParentChildInternodeHeirarchy(internodesCopy)
    return internodesCopy



  '''
  '' Initializes the LSystem and creates the base branches and flowers for the
  '' Stem Instance Node
  '''
  def initLSystemBaseTree(self, iters, angle, step, grammarFile):
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
    #self.mLSystem.setHasResources(hasResources)

    # Print contents
    print "Grammar File: " + grammarFile
    print "Grammar File Contents: " + self.mLSystem.getGrammarString()

    # The branches and flowers objects
    self.mBaseBranches = LSystem.VectorPyBranch()
    self.mBaseFlowers = LSystem.VectorPyBranch()

    # Run Grammar String to make branches and flowers
    self.mLSystem.processPy(iters, self.mBaseBranches, self.mBaseFlowers)

    self.mPrevIterations = iters
    self.mPrevAngle = angle


    # Clear the tree growth meshes
    self.clearTreeGrowthInternodes()

    return [self.mBaseBranches, self.mBaseFlowers]

  '''
  '' Create the cylinder mesh for this StemInstanceNode
  '''
  def createCylinderMesh(self, internodes, data):
    # Get output objects
    outputHandle = data.outputValue(self.outputMesh)
    dataCreator = OpenMaya.MFnMeshData()
    newOutputData = dataCreator.create()

    # Clear old cylinder mesh
    SC.clearMesh()

    # Set up global mesh
    cPoints = OpenMaya.MPointArray()
    cFaceCounts = OpenMaya.MIntArray()
    cFaceConnects = OpenMaya.MIntArray()

    # Make tree from Internode Cylinder Meshes
    for cyl in internodes:
      # Append the Cylinder's mesh to our main mesh
      cyl.appendToMesh(cPoints, cFaceCounts, cFaceConnects)

    # TODO - Handle flowers (uncomment when needed)
    # for i in range(0, flowers.size()):
    #   f = flowers[i]
    #   centerLoc = OpenMaya.MVector(f[0], f[1], f[2])
    #   print 'create flower!'


    # Verify a mesh was made
    if cPoints.length() == 0 or cFaceCounts.length() == 0 or cFaceConnects.length() == 0:
      print 'No LSystem generated!'
      return None

    # Finalize the Mesh Creation
    meshFs = OpenMaya.MFnMesh()
    meshResult = meshFs.create(int(cPoints.length()), int(cFaceCounts.length()),
      cPoints, cFaceCounts, cFaceConnects, newOutputData)

    # Make sure we have a valid mesh
    if meshResult is None:
      return None

    # Update the output mesh
    outputHandle.setMObject(newOutputData)


  '''
  '' Creates an Internodes List of CylinderMeshes from branches
  '''
  def createInternodes(self, branches, flowers):
    internodes = []
    for i in range(0, branches.size()):
      b = branches[i]
      # Get points
      start = OpenMaya.MPoint(b[0], b[1], b[2])
      end = OpenMaya.MPoint(b[3], b[4], b[5])
      radius = 0.25

      # Create a cylinder from the end points
      cyMesh = SC.StemCylinder(start, end, radius)
      internodes.append(cyMesh)

    # Create parent/child heirarchy
    internodes = self.createParentChildInternodeHeirarchy(internodes)

    # Return the internodes
    return internodes


  '''
  '' Create Internode Parent Child Heirarchy
  '''
  def createParentChildInternodeHeirarchy(self, internodes, shouldReset=True):
    if shouldReset:
      internodes = self.resetParentChildInternodeHeirarchy(internodes)
    for iBranch in internodes:
      for jBranch in internodes:
        if iBranch.mEnd == jBranch.mStart:
          iBranch.mInternodeChildren.append(jBranch)
          jBranch.mInternodeParent = iBranch
    return internodes

  '''
  '' Reset ParentChildInternodeHeirarchy
  '''
  def resetParentChildInternodeHeirarchy(self, internodes):
    for branch in internodes:
      # Clear parents
      branch.mInternodeParent = None
      # Clear Children
      branch.mInternodeChildren[:] = []
    return internodes

  '''
  '' Compute Optimal Growth Pairs
  '''
  def updateOptimalGrowthPairs(self, internodes):
    # Get optimal growth pairs and send to LSystem
    self.mOptimalGrowthPairs = self.computeBudOptimalGrowthDirs(internodes)
    return self.mOptimalGrowthPairs

  '''
  '' Finds the optimal growth direction angles and their bud growth pairs for
  '' each bud in the tree
  '''
  def computeBudOptimalGrowthDirs(self, internodes):
    # Erase old curves
    self.eraseCurves(self.mOptCurves)
    self.mOptCurves = []

    # Get list of buds in the scence
    buds = self.createBudList(internodes)

    # If Buds is empty, we want to use the StemInstanceLocation as the only bud
    # position (it acts as a root)
    if len(buds) == 0:
      # TODO: Figure out how to get this stemInstanceNode's maya name from
      # within this class
      # budPosition = SG.getLocatorWorldPosition(None)
      rootBudPos = OpenMaya.MPoint(0, 0, 0)
      buds = [SC.StemCylinder(rootBudPos, rootBudPos)]

    # Get list of resource noces
    resNodes = self.getSceneResourceNodes()

    # Make optimal bud-node adjacency list
    allBudsAdjList = self.createBudResNodeAdjacencyList(buds, resNodes)

    # Now compute optimal growth dirs and bud pair directions
    optimalGrowthPairs = []

    # Grab the StemNodeInstance
    stemNode = self.getStemNode()

    # Now compute the optimal growth dir
    for budNodePair in allBudsAdjList:
      # Separate the pair (bud, nodes)
      # print 'Bud Node Pair!', budNodePair
      bud = budNodePair.get(KEY_BUD)
      lightNodes = budNodePair.get(KEY_RESOURCE_NODE_LIST)

      if len(lightNodes) == 0:
        continue

      # Calculate the weighted average growth direction
      budPosition = bud.mEnd
      budCurveWorldPosition = bud.mEnd
      if stemNode != None:
        # Get world position of mEnd (relative to StemInstanceTransform)
        worldPos = SG.getLocatorWorldPosition(stemNode)
        budCurveWorldPosition = SG.sumArrayVectors(budPosition, worldPos)

      sumNodePositions = [0, 0, 0]
      numNodes = len(lightNodes)
      totalLightPower = 0
      # Sum the node positions and weight them
      for node in lightNodes:
        # TODO add weighting funciton that include the radius of light/space etc
        n = node[KEY_RESOURCE_NODE_NAME]
        nodePos = node[KEY_RESOURCE_NODE_POSITION]
        sumNodePositions = SG.sumArrayVectors(sumNodePositions, nodePos)
        totalLightPower += cmds.getAttr(str(n) + '.' + SL.KEY_DEF_LIGHT_RADIUS[0])

      # Q Light value to be stored at a node
      lightQValue = 0 if len(lightNodes) == 0.0 else 1.0
      # print 'BUD:', bud
      # print 'LightValue:', lightQValue

      # Set the light for the bud node
      bud.mQLightAmount = lightQValue
      # TODO: Use avg light power for lightQValue
      avgLightPower = totalLightPower / numNodes

      # print ('avgLightPower for bud:', avgLightPower)
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
      growthPair = (budPosition, optPt, optGrowthAngle, lightQValue)

      #growthAnglePair = (budPosition, optGrowthAngle)

      # Draw curve to show direction vector
      c = self.drawCurve(budCurveWorldPosition, optPt)

      # Append curve to tx node
      self.mOptCurves.append(c)

      # Link node to stem transform
      self.linkNode(c)

      # Now append to the list of pairs
      optimalGrowthPairs.append(growthPair)
      #optimalGrowthPairs.append(growthAnglePair)
    # print 'RETURNING OPTIMAL GROWTH PAIRS'
    # Return the Optimal Growth Pairs
    return optimalGrowthPairs

  '''
  '' Creates a list of buds based on this instanceNode's internode list
  '' Returns an empty array if no buds are present
  '''
  def createBudList(self, internodes):
    # Creates a list of buds based on the internodes list-
    # A bud is defined as the end point of an internode that has no children
    if internodes is None or len(internodes) is 0:
      return []
    childBuds = []
    for n in internodes:
      if n.mInternodeChildren is None or len(n.mInternodeChildren) == 0:
        childBuds.append(n)
    return childBuds

  '''
  '' Creates a bud to resource node adjacency list where each bud is associated
  '' with a list of resource nodes that it is the closest bud to
  '''
  def createBudResNodeAdjacencyList(self, buds, resNodes):
    # Determine the nodes that are closest to particular buds
    # Create an adjacency list (dictionary) that stores the adj list
    allBudsAdjacencyList = {}
    for n in resNodes:

      # Get name and position of resNode
      nPos = n[KEY_RESOURCE_NODE_POSITION]

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
  '' Configures branches to hand lateral and terminal buds
  '''
  def configureBudInternodeHeirarchy(self, internodes):
    # Create and configure buds and internode heirarchy
    for b in internodes:
      if (len(b.mInternodeChildren) == 0):
        # b.mQLightAmount = 1
        parent = b
        b.mBudTerminal = SB.StemBud(SB.BudType.TERMINAL, parent)
        b.mBudTerminal.mQLightAmount = b.mQLightAmount
        b.mBudLateral = SB.StemBud(SB.BudType.LATERAL, parent)
        b.mBudLateral.mQLightAmount = b.mQLightAmount
      elif (len(b.mInternodeChildren) == 1):
        parent = b
        child = b.mInternodeChildren[0]
        b.mBudLateral = SB.StemBud(SB.BudType.LATERAL, parent, child)
        b.mBudLateral.mQLightAmount = b.mQLightAmount
      else:
        # Added this to reset the internodes buds when necessary
        #b.mBudLateral = None
        #b.mBudTerminal = None
        print "has more than 1 child" + str(len(b.mInternodeChildren))

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
  '' Verifies the output passed to the LSystem
  '' Where <buds> and <angles> are sent to the LSystem and
  '' and <b1> and <d1> are read back from the LSystem
  '''
  def verifyLSystemBudAngles(self, buds, dirs, angles):
    lBuds = LSystem.VectorPyBranch()
    lDirs = LSystem.VectorPyBranch()
    lAngles = LSystem.VecFloat()
    # Get buds, dirs and angles from the LSystem
    self.mLSystem.getOptimalBudDirs(lBuds, lDirs, lAngles)

    # Verify that the ones sent are equal to the ones retrieved
    for i in range(0, lBuds.size()):
      # Retrieved from the LSystem
      lb = lBuds[i]
      la = lAngles[i]
      ld = lDirs[i]

      # Sent to LSystem
      b = buds[i]
      a = angles[i]
      d = dirs[i]

      # Get points
      correctDir =  ld[0] == d[0] and ld[1] == d[1] and ld[2] == d[2]
      correctAngle = la == a
      correctBud = lb[0] == b[0] and lb[1] == b[1] and lb[2] == b[2]

      correctTransfer = correctDir and correctAngle and correctBud
      if not correctTransfer:
        print 'Incorrect Transfer (LSystem,Sent)', 'Bud', lb, b, "Dir", ld, d, "Angle", la, a
    print 'Finished verifying buds and dirs'
    return

  '''
  '' Updates the StemInstanceNode name based on the input attribute of the maya
  '' node
  '''
  def updateStemNodeName(self, plug):
      attributeName = plug.name()
      attrStr = str(attributeName)
      nodeName = attrStr.split('.')[0]
      self.mStemNode = nodeName

  '''
  '' Returns the maya dependency node associated with this stem instance node
  '''
  def getStemNode(self):
    return self.mStemNode

  '''
  '' Returns the root internode of the Stem tree
  '''
  def getRootInternode(self, internodes):
    if len(internodes) == 0:
      return None
    for n in internodes:
      if n.mInternodeParent is None:
        return n
    return None

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

    while len(queue) > 0:
      b = queue.popleft()
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

    pV = internode.mVResourceAmount

    if (len(internode.mInternodeChildren) == 0):
      # if 0 children, there is 1 terminal and 1 lateral bud to split the resource
      mTarget = internode.mBudTerminal
      lTarget = internode.mBudLateral
      pQm = mTarget.mQLightAmount
      pQl = lTarget.mQLightAmount
      # Compute amount of resource distributed to axis branch and lateral branch
      denom = (BH_LAMBDA*pQm + (1-BH_LAMBDA)*pQl)
      if denom == 0:
        pVm = 0
        pVl = 0
      else:
        pVm = pV * (BH_LAMBDA * pQm) / denom
        pVl = pV * ((1-BH_LAMBDA)*pQl) / denom
      # Distribute
      mTarget.mVResourceAmount = pVm
      lTarget.mVResourceAmount = pVl

    elif (len(internode.mInternodeChildren) == 1):
      # if 1 child, there is 1 internode and 1 lateral bud to split the resource
      mTarget = internode.mInternodeChildren[0]
      lTarget = internode.mBudLateral
      pQm = mTarget.mQLightAmount
      pQl = lTarget.mQLightAmount
      # Compute amount of resource distributed to axis branch and lateral branch
      denom = (BH_LAMBDA*pQm + (1-BH_LAMBDA)*pQl)
      if denom == 0:
        pVm = 0
        pVl = 0
      else:
        pVm = pV * (BH_LAMBDA * pQm) / denom
        pVl = pV * ((1-BH_LAMBDA)*pQl) / denom
      # Distribute
      mTarget.mVResourceAmount = pVm
      lTarget.mVResourceAmount = pVl

    else:
      # TODO: still need to determine which is along main axis and which isn't
      mTarget = internode.mInternodeChildren[0]
      lTarget = internode.mInternodeChildren[1]
      pQm = mTarget.mQLightAmount
      pQl = lTarget.mQLightAmount
      # Compute amount of resource distributed to axis branch and lateral branch
      denom = (BH_LAMBDA*pQm + (1-BH_LAMBDA)*pQl)
      if denom == 0:
        pVm = 0
        pVl = 0
      else:
        pVm = pV * (BH_LAMBDA * pQm) / denom
        pVl = pV * ((1-BH_LAMBDA)*pQl) / denom
      # Distribute
      mTarget.mVResourceAmount = pVm
      lTarget.mVResourceAmount = pVl

  '''
  ''  Propogates light amounts (Q) from outermost internodes to towards the base.
  ''  (TODO: May have to edit to grab the light information from buds themselves)
  '''
  def performBasipetalPass(self, internodes):
    root = self.getRootInternode(internodes) #self.getRootInternode()
    branchStack = self.getBfsTraversal(root)

    # TODO: remove later. this bit is for testing on simple case
    # currently configuring appropriate bud types and locations using the
    # given geometry from the LSystem

    # newList = list(branchStack)
    # for each internode, propogate light information from leaf nodes towards base
    while (len(branchStack) > 0):
      b = branchStack.pop()
      # if the internode has buds with Q values, store cum Q values in internode
      if (b.mBudTerminal is not None):
        b.mQLightAmount += b.mBudTerminal.mQLightAmount
      if (b.mBudLateral is not None):
        b.mQLightAmount += b.mBudLateral.mQLightAmount
      # if internode parent stores Q value, also store that in internode
      if (b.mInternodeParent is not None):
        b.mInternodeParent.mQLightAmount += b.mQLightAmount

    # TODO: remove later. prints light values after propogation in BFS order
    # for b in newList:
    #   print b.mQLightAmount

  '''
  ''  Distributes resource acropetally between continuing main axes
  ''  and lateral branches throughout entire tree.
  '''
  def performAcropetalPass(self, internodes):
    # v_base = alpha * Q_base
    #root = self.getRootInternode()
    root = self.getRootInternode(internodes)
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
  def performBHModelResourceDistribution(self, internodes):
    self.performBasipetalPass(internodes)
    self.performAcropetalPass(internodes)

  '''
  ''  Reads a text file that is selected using a file dialog then returns its
  ''  contents. If no file exists, it returns the empty string
  '''
  def readGrammarFileUsingDialog(self):
    txtFileFilter = 'Text Files (*.txt)'
    fileNames = cmds.fileDialog2(fileFilter=dialogStyle, txtFileFilter=2, fileMode=1)
    return self.readGrammarFile(fileNames[0])

  '''
  ''  Reads a text file that is passed by string
  ''  contents. If no file exists, it returns the empty string
  '''
  def readGrammarFile(self, fileName):
    if len(fileName) <= 0:
      return ""
    try:
      f = open(fileName, 'r')
      fileContents = f.read()
      f.close()
      return fileContents
    except:
      return ""

  '''
  '' Draws a curve between two points
  '''
  def drawCurve(self, p1, p2):
    curve = cmds.curve(p=[(p1[0], p1[1], p1[2]), (p2[0], p2[1], p2[2])], degree=1)
    curveColor = random.randint(5,31)
    c = str(curve)
    # Change curve color
    cmds.setAttr(c + ".overrideEnabled", True)
    cmds.setAttr(c + ".overrideColor", curveColor)

    return c

  '''
  '' Erases all curves in the Maya Scene
  '''
  def eraseCurves(self, allCurves):
    for i in range(0, len(allCurves)):
      s = allCurves[i].strip()
      if len(s) > 0:
        cmds.delete(s)
    # Clear the Curves
    del allCurves[:]

  '''
  '' Update Tree Curves
  '''
  def updateTreeMesh(self, internodes):
    # Erase tree curves
    self.eraseCurves(self.mTreeCurves)
    self.mTreeCurves = []

    # Erase the extruded tree Mesh
    self.deleteTreeExtrusionMesh()

    # Create new curve list
    treeCurveList = self.createTreeCurveList(internodes)

    # Draw curves
    self.mTreeCurves = self.drawTreeCurves(treeCurveList)

    # Extrude mesh
    self.mTreeExtrusions = self.extrudeTreeCurves(self.mTreeCurves)

    # Unite Tree Extrusions into a Mesh
    self.mTreeMesh = self.createTreeMesh(self.mTreeExtrusions)

    # Link mesh to this Stem Node
    self.linkNode(self.mTreeMesh)

  '''
  '' Erases the extruded tree mesh
  '''
  def deleteTreeExtrusionMesh(self):
    # for ext in self.mTreeExtrusions:
    #   cmds.delete(str(ext[0]))
    # del self.mTreeExtrusions[:]

    # Delete the actual mesh
    if self.mTreeMesh:
      cmds.delete(str(self.mTreeMesh))

  '''
  '' Creates a list of tree curves
  '''
  def createTreeCurveList(self, internodes):
    # Grab the StemNodeInstance
    worldPos = SG.getLocatorWorldPosition(self.getStemNode())
    buds = self.createBudList(internodes)
    curves = []
    for b in buds:
      curve = []
      # Add end point of curve
      cEnd = b.getEndPointTuple()
      cEnd = (cEnd[0] + worldPos[0], cEnd[1]  + worldPos[1], cEnd[2] + worldPos[2])
      curve.append(cEnd)

      # Now use Reverse DFS
      parent = b
      while parent is not None:
        cStart = parent.getStartPointTuple()
        cStart = (cStart[0] + worldPos[0], cStart[1]  + worldPos[1], cStart[2] + worldPos[2])
        curve.insert(0, cStart)
        parent = parent.mInternodeParent

      # Add curve to curves list
      curves.append(curve)
    return curves

  '''
  '' Draws a tree curve
  '''
  def drawTreeCurves(self, curvePtsSet):
    treeCurves = []
    for ptSet in curvePtsSet:
      deg = len(ptSet) - 1
      curve = cmds.curve(p=ptSet, degree=deg)
      curveColor = 14
      c = str(curve)
      cmds.setAttr(c + ".overrideEnabled", True)
      cmds.setAttr(c + ".overrideColor", curveColor)
      treeCurves.append(c)
    return treeCurves

  '''
  '' Extrudes Curves for the branch segments
  '''
  def extrudeTreeCurves(self, treeCurves):
    # Generate Parameters for circle
    cId = str(random.randint(0, sys.maxint))
    cName = 'StemCircle' + cId

    # Generate random radius for the circle
    cRadius = (random.randint(0, 20) / 100.0) + 0.1

    # Create circle for extrusion
    circleExt = cmds.circle( nr=(0, 1, 0), c=(0, 0, 0), r=cRadius, n=cName)

    treeExtrusions = []
    treeScale = 0.4
    for treeCurve in treeCurves:
      # Generate Random Scale
      treeScale = (random.randint(0, 35) / 100) + 0.4

      # Create Tree Name
      tName = 'StemCircleExt' + cId

      # Extrude the tree
      tExt = cmds.extrude(cName, str(treeCurve), n=tName,
        scale=0.4, ch=True, rn=False, po=1, et=2,
        ucp=1, fpt=True, upn=1, rotation=0)
      # Append extrusion
      treeExtrusions.append(tExt)

    # Erase the extrusion circle [Circle, NurbCircle]
    cmds.delete(str(circleExt[0]))
    #cmds.delete(str(circleExt[1]))

    return treeExtrusions

  '''
  '' Create Tree Mesh
  '''
  def createTreeMesh(self, treeExtrusions):
    if treeExtrusions is None or len(treeExtrusions) == 0:
      return None
    treeExts = [ext[0] for ext in treeExtrusions]

    # Create a string of all the treeExtrusion names: 'curve1 curve2 curve3 ...'
    # Each name is separated by spaces
    treeExtStr = ''
    for t in treeExts:
      treeExtStr += str(t) + ' '
    #treeExtStr = str(treeExts).strip('[]').replace(',', ' ').replace('\'','')
    treeCombined = maya.mel.eval('polyUnite ' + treeExtStr)
    treeMesh = treeCombined[0]
    return treeMesh

  '''
  '' Links a tree Mesh to this node
  '''
  def linkNode(self, node):
    # Get the parent transform node
    txNode = SG.getParentTransformNode(self.getStemNode())
    if node is None or txNode is None:
      print 'Failed to link tree mesh'
      return
    # Link mesh
    cmds.parent(str(node), txNode)

######################## End StemInstanceNode Class ############################
'''
'' StemInstanceNode Creator for Maya Plug-in
'''
def StemInstanceNodeCreator():
  return OpenMayaMPx.asMPxPtr(StemInstanceNode())

'''
'' StemInstanceNode Initializer for Maya Plug-in
'''
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
  StemInstanceNode.mTime = uAttr.create(
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

  StemInstanceNode.addAttribute(StemInstanceNode.mTime)
  StemInstanceNode.addAttribute(StemInstanceNode.outputMesh)
  StemInstanceNode.addAttribute(StemInstanceNode.mFlowers)
  StemInstanceNode.addAttribute(StemInstanceNode.mBranches)
  StemInstanceNode.addAttribute(StemInstanceNode.outPoints)

  # Attribute Effects to Flowers
  StemInstanceNode.attributeAffects(
    StemInstanceNode.mTime,
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
    StemInstanceNode.mTime,
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
    StemInstanceNode.mTime,
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
