# -*- coding: utf-8 -*-
# randomNode.py
#   Produces random locations to be used with the Maya instancer node.

import sys, math
import random
import LSystem

import maya
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx

import StemGlobal as SG

import pymel.all as pm
from pymel.core import *
from functools import partial


#------------------------------------------------------------------------------#
# StemNode Class - Subclassed Maya Mpx.Node that implements the Self-organizing
# L-system presented in Self-organizing tree models for image synthesis by
# Pałubicki, W., et al.
#------------------------------------------------------------------------------#

# The Stem Node Name
kPluginStemNodeTypeName = "kStemInstanceNode"

# The Stem Node Id
kStemInstanceNodeId = OpenMaya.MTypeId(0xFA234)

# Node definition
class StemInstanceNode(OpenMayaMPx.MPxNode):
  # Declare class variables:
  # TODO - declare the input and output class variables
  #         i.e. inNumPoints = OpenMaya.MObject()

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

  # Other values
  mBranches = OpenMaya.MObject()
  mFlowers = OpenMaya.MObject()



  # constructor
  def __init__(self):
    OpenMayaMPx.MPxNode.__init__(self)

  # compute
  def compute(self,plug,data):
    if plug == StemInstanceNode.outputMesh:

      # Create branch segments array from LSystemBranches use id, position, aimDirection, scale
      # Note: Can change input geometry of instancer

      # Create Flowers array from LSystemGeometry use id, position, aim direction, scale
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

      # Grammar File String
      grammarData =  data.inputValue(StemInstanceNode.mDefGrammarFile)
      grammarFile = grammarData.asString()

      # Get output objects
      # outputHandle = data.outputValue(StemInstanceNode.outputPoints)
      # dataCreator = OpenMaya.MFnMeshData()
      # newOutputData = dataCreator.create()
      #self.createPoints(iters, angle, step, grammarFile, newOutputData)

      # The New mesh!
      self.createPoints(iters, angle, step, grammarFile, data)

      # Set new output data
      #outputHandle.set(newOutputData)

      # Clear up the data
      data.setClean(plug)

  ''' Create the Points for this node '''
  def createPoints(self, iters, angle, step, grammarFile, data):

    #------------------------------------------------#
    ############ POINTS DATA FOR ATTR_ARRAY ##########
    #------------------------------------------------#
    # Set up the array for adding random points
    pointsData = data.outputValue(StemInstanceNode.outPoints) #the MDataHandle
    pointsAAD = OpenMaya.MFnArrayAttrsData() #the MFnArrayAttrsData
    pointsObject = pointsAAD.create() #the MObject

    # Create the vectors for “position” and “id”. Names and types must match # table above.
    positionArray = pointsAAD.vectorArray('position')
    idArray = pointsAAD.doubleArray('id')

    # Create the vectors for “position” and “id”. Names and types must match # table above.
    scaleArray = pointsAAD.vectorArray('scale')
    aimDirArray = pointsAAD.vectorArray('aimDirection')

    #------------------------------------#
    ############# LSYSTEM INIT ###########
    #------------------------------------#

    lsys = LSystem.LSystem()
    lsys.setDefaultAngle(angle)
    lsys.setDefaultStep(step)

    lsys.load(grammarFile)
    print "Grammar File: " + grammarFile
    print "Grammar: " + lsys.getGrammarString()

    branches = LSystem.VectorPyBranch()
    flowers = LSystem.VectorPyBranch()

    # Run Grammar String
    lsys.processPy(iters, branches, flowers)


    # Set up the array for adding random points
    pointsData = data.outputValue(StemInstanceNode.mBranches) #the MDataHandle
    pointsAAD = OpenMaya.MFnArrayAttrsData() #the MFnArrayAttrsData
    pointsObject = pointsAAD.create() #the MObject

    # Create the vectors for “position” and “id”. Names and types must match # table above.
    positionArray = pointsAAD.vectorArray('position')
    idArray = pointsAAD.doubleArray('id')

    # Create the vectors for “position” and “id”. Names and types must match # table above.
    scaleArray = pointsAAD.vectorArray('scale')
    aimDirArray = pointsAAD.vectorArray('aimDirection')


    # BRANCH ME OUT
    for i in range(0, branches.size()):
      index = i + 2 * i
      # Make Branch! wooo
      b = branches.at(i)

      # Get points
      start = OpenMaya.MVector(b.at(0), b.at(1), b.at(2))
      end = OpenMaya.MVector(b.at(3), b.at(4), b.at(5))
      sFactor = (1 - branches.size() / (i + 1))
      scale = OpenMaya.MVector(1.1 * sFactor, 1.2 * sFactor, 1.1 * sFactor)
      aim = OpenMaya.MVector(random.random(), random.random(), random.random())


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

      # Create the vectors for “position” and “id”. Names and types must match # table above.
      positionArray = fAAD.vectorArray('position')
      idArray = fAAD.doubleArray('id')

      # Create the vectors for “position” and “id”. Names and types must match # table above.
      scaleArray = fAAD.vectorArray('scale')
      aimDirArray = fAAD.vectorArray('aimDirection')

      # FLOWER POWER
      for i in range(0, flowers.size()):
        index = i + 2 * i * branches.size()
        f = flowers.at(i)
        start = OpenMaya.MVector(f.at(0), f.at(1), f.at(2))
        sFactor = (1 - flowers.size() / (i + 1))
        scale = OpenMaya.MVector(1.1 * sFactor, 1.1 * sFactor, 1.1 * sFactor)
        aim = OpenMaya.MVector(random.random(), random.random(), random.random())

        # Append
        positionArray.append(start)
        idArray.append(index)
        scaleArray(scale)
        aimDirArray.append(aim)

        # Now set the flower data :)
        fData.setMObject(fObject)

        print 'create mesh!'

# StemNode creator
def StemNodeCreator():
  return OpenMayaMPx.asMPxPtr(StemInstanceNode())

def StemNodeInitializer():
  #------------------------------------#
  ############ NUM RAND PTS ##########
  #------------------------------------#
  # Num Random Points
  #SG.MAKE_INPUT(nAttr)
  # Numeric Attributes
  nAttr = OpenMaya.MFnNumericAttribute()
  StemInstanceNode.mDefAngle = nAttr.create("angle", "a", OpenMaya.MFnNumericData.kFloat, 22.5)
  SG.MAKE_INPUT(nAttr)

  # Step size
  nAttr = OpenMaya.MFnNumericAttribute()
  StemInstanceNode.mDefStepSize = nAttr.create("stepSize", "s", OpenMaya.MFnNumericData.kFloat, 1.0)
  SG.MAKE_INPUT(nAttr)

  # Iterations
  nAttr = OpenMaya.MFnNumericAttribute()
  StemInstanceNode.mIterations = nAttr.create("iterations", "iter", OpenMaya.MFnNumericData.kLong, 1)
  SG.MAKE_INPUT(nAttr)

  # Time
  uAttr = OpenMaya.MFnUnitAttribute()
  StemInstanceNode.time = uAttr.create("time", "tm", OpenMaya.MFnUnitAttribute.kTime, 0)
  SG.MAKE_INPUT(uAttr)

  # Grammar File
  tAttr = OpenMaya.MFnTypedAttribute()
  StemInstanceNode.mDefGrammarFile = tAttr.create("grammar", "g", OpenMaya.MFnData.kString)
  SG.MAKE_INPUT(tAttr)

  # Branch Segments
  tAttr = OpenMaya.MFnTypedAttribute()
  StemInstanceNode.mBranches =  tAttr.create("branches", "b", OpenMaya.MFnArrayAttrsData.kDynArrayAttrs)
  SG.MAKE_OUTPUT(tAttr)
  # SG.MAKE_INPUT(tAttr)

  # Flowers
  tAttr = OpenMaya.MFnTypedAttribute()
  StemInstanceNode.mFlowers =  tAttr.create("flowers", "f", OpenMaya.MFnArrayAttrsData.kDynArrayAttrs)
  SG.MAKE_OUTPUT(tAttr)
  #SG.MAKE_INPUT(tAttr)

  # Output mesh
  tAttr = OpenMaya.MFnTypedAttribute()
  StemInstanceNode.outputMesh = tAttr.create("outputMesh", "out", OpenMaya.MFnData.kMesh)
  SG.MAKE_OUTPUT(tAttr)

  # add Attributues
  StemInstanceNode.addAttribute(StemInstanceNode.mDefAngle)
  StemInstanceNode.addAttribute(StemInstanceNode.mDefStepSize)
  StemInstanceNode.addAttribute(StemInstanceNode.mDefGrammarFile)
  StemInstanceNode.addAttribute(StemInstanceNode.mIterations)
  StemInstanceNode.addAttribute(StemInstanceNode.time)
  StemInstanceNode.addAttribute(StemInstanceNode.outputMesh)
  StemInstanceNode.addAttribute(StemInstanceNode.mFlowers)
  StemInstanceNode.addAttribute(StemInstanceNode.mBranches)


  # Attribute Affects
  StemInstanceNode.attributeAffects(StemInstanceNode.time, StemInstanceNode.mFlowers)
  StemInstanceNode.attributeAffects(StemInstanceNode.mIterations, StemInstanceNode.mFlowers)
  StemInstanceNode.attributeAffects(StemInstanceNode.mDefAngle, StemInstanceNode.mFlowers)
  StemInstanceNode.attributeAffects(StemInstanceNode.mDefStepSize, StemInstanceNode.mFlowers)
  StemInstanceNode.attributeAffects(StemInstanceNode.mDefGrammarFile, StemInstanceNode.mFlowers)


  StemInstanceNode.attributeAffects(StemInstanceNode.time, StemInstanceNode.mBranches)
  StemInstanceNode.attributeAffects(StemInstanceNode.mIterations, StemInstanceNode.mBranches)
  StemInstanceNode.attributeAffects(StemInstanceNode.mDefAngle, StemInstanceNode.mBranches)
  StemInstanceNode.attributeAffects(StemInstanceNode.mDefStepSize, StemInstanceNode.mBranches)
  StemInstanceNode.attributeAffects(StemInstanceNode.mDefGrammarFile, StemInstanceNode.mBranches)



#----------------------------------------------------------------------------------#
###################################### GLOBAL FXNS #################################
#----------------------------------------------------------------------------------#


##############################################################
###  Custom Drop Down Menu   ########################
##############################################################
# TODO MOVE UI into separate class
DROP_DOWN_MENU_NAME = "kStemSystemDropDownMenu"

class StemUIMenu(object):

  def printbutton(self):
    print 'Button clicked'

  def makeRNNetwork(self):
      cmd = 'sphere; instancer; createNode randomNode; connectAttr nurbsSphere1.matrix instancer1.inputHierarchy[0]; '
      cmd += 'connectAttr randomNode1.outPoints instancer1.inputPoints;'
      maya.mel.eval(cmd)

  def makeRNNetworkSelected(self):
    cmd = 'sphere; instancer; createNode randomNode; connectAttr nurbsSphere1.matrix instancer1.inputHierarchy[0]; '
    cmd += 'connectAttr randomNode1.mBranches instancer1.outPoints;'
    maya.mel.eval(cmd)

  def makeLSINNetwork(self):
    cmd = 'sphere; instancer; createNode StemInstanceNode; connectAttr nurbsSphere1.matrix instancer1.inputHierarchy[0]; '
    cmd += 'connectAttr StemInstanceNode.mBranches instancer1.inputPoints; connectAttr StemInstanceNode.mFlowers instancer1.inputPoints;'
    maya.mel.eval(cmd)

  def makeLSINNetworkSelected(self):
    cmd = 'sphere; instancer; createNode randomNode; connectAttr nurbsSphere1.matrix instancer1.inputHierarchy[0]; '
    cmd += 'connectAttr StemInstanceNode.mBranches instancer1.inputPoints; connectAttr StemInstanceNode.mFlowers instancer1.inputPoints;'
    maya.mel.eval(cmd)


  '''
  '' Initialize the DropDown Menu
  '''
  def __init__(self):
    gMainWindow = maya.mel.eval('$temp1=$gMainWindow')
    self.name = DROP_DOWN_MENU_NAME
    # Delete the old window by name if it exists
    if (self.exists()):
      cmds.deleteUI(self.name)

      dropDownMenu = cmds.menu(
      DROP_DOWN_MENU_NAME,
      label='LSystemInstance',
      parent=gMainWindow,
      tearOff=True)
      cmds.menuItem(
      label='Create RN Network',
      parent=dropDownMenu,
      command=pm.Callback(self.makeRNNetwork))
      cmds.menuItem(
      label='Create RN Network from Selected',
      parent=dropDownMenu,
      command=pm.Callback(self.makeRNNetworkSelected))
      cmds.menuItem(
      label='Create LSIN Network',
      parent=dropDownMenu,
      command=pm.Callback(self.makeLSINNetwork))
      #cmds.menuItem(divider=True)
      cmds.menuItem(
      label='Create LSIN Network',
      parent=dropDownMenu,
      command=pm.Callback(self.makeLSINNetworkSelected))


  '''
  '' Returns true if this menu exists in Maya's top option menu
  '''
  def exists(self):
    return cmds.menu(self.name, query=True, exists=True)


STEM_SYSTEM_MENU = StemUIMenu()

#
# ##############################################################
# ###  INIT FUNCTIONS FOR PLUG-IN  #############################
# ##############################################################
#
# # initialize the script plug-in
# def initializePlugin(mobject):
#     print "Trying to init"
#     mplugin = OpenMayaMPx.MFnPlugin(mobject, "Michael Rivera", "1.0", "Any")
#     try:
#         mplugin.registerNode(
#           kPluginStemNodeTypeName,
#           kStemInstanceNodeId,
#           StemNodeCreator,
#           StemNodeInitializer)
#     except:
#         sys.stderr.write(
#         "Failed to register node: %s\n" % kPluginStemNodeTypeName)
#
#
# # uninitialize the script plug-in
# def uninitializePlugin(mobject):
#     global STEM_SYSTEM_MENU
#     mplugin = OpenMayaMPx.MFnPlugin(mobject)
#     try:
#         mplugin.deregisterNode(StemInstanceNodeId)
#
#         # Delete old UI
#         if STEM_SYSTEM_MENU != None:
#             cmds.deleteUI(STEM_SYSTEM_MENU.name)
#     except:
#         sys.stderr.write( "Failed to unregister node: %s\n" % kPluginNodeTypeName )
