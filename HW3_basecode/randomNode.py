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

import pymel.all as pm
from pymel.core import * 
from functools import partial


# Useful functions for declaring attributes as inputs or outputs.
def MAKE_INPUT(attr):
    attr.setKeyable(1)
    attr.setStorable(1)
    attr.setReadable(1)
    attr.setWritable(1)
def MAKE_OUTPUT(attr):
    attr.setKeyable(0)
    attr.setStorable(0)
    attr.setReadable(1)
    attr.setWritable(0)

#----------------------------------------------------------------------------------#
#################################### LSYSTEM CMD NODE ##############################
#----------------------------------------------------------------------------------#

# Define the name of the node
kPluginLSystemInstanceNodeTypeName = "lSystemInstanceNode"

# Give the node a unique ID. Make sure this ID is different from all of your
# other nodes!
LSystemInstanceNodeId = OpenMaya.MTypeId(0xFA222)

# Node definition
class LSystemInstanceNode(OpenMayaMPx.MPxNode):
    # Declare class variables:
    # TODO:: declare the input and output class variables
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
        if plug == LSystemInstanceNode.outputMesh:

            # Create branch segments array from LSystemBranches use id, position, aimDirection, scale 
            # Note: Can change input geometry of instancer

            # Create Flowers array from LSystemGeometry use id, position, aim direction, scale
            # Note: Can change input geometry of instancer
            

            # Time 
            timeData = data.inputValue(LSystemInstanceNode.time)
            t = timeData.asInt()

            # Num Iterations
            iterData = data.inputValue(LSystemInstanceNode.mIterations)
            iters = iterData.asInt()

            # Step Size 
            stepSizeData = data.inputValue(LSystemInstanceNode.mDefStepSize)
            step = stepSizeData.asFloat()

            # Angle
            angleData = data.inputValue(LSystemInstanceNode.mDefAngle)
            angle = angleData.asFloat()

            # Grammar File String
            grammarData =  data.inputValue(LSystemInstanceNode.mDefGrammarFile)
            grammarFile = grammarData.asString()

            # Get output objects
            # outputHandle = data.outputValue(LSystemInstanceNode.outputPoints)
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
        pointsData = data.outputValue(LSystemInstanceNode.outPoints) #the MDataHandle 
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
        pointsData = data.outputValue(LSystemInstanceNode.mBranches) #the MDataHandle 
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
        fData = data.outputValue(LSystemInstanceNode.mBranches) #the MDataHandle 
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

# lSystem creator
def LSystemNodeCreator():
    return OpenMayaMPx.asMPxPtr(LSystemInstanceNode())

def LSystemNodeInitializer():
    #------------------------------------#
    ############ NUM RAND PTS ##########
    #------------------------------------#
    # Num Random Points
    #MAKE_INPUT(nAttr)
    # Numeric Attributes
    nAttr = OpenMaya.MFnNumericAttribute()
    LSystemInstanceNode.mDefAngle = nAttr.create("angle", "a", OpenMaya.MFnNumericData.kFloat, 22.5)
    MAKE_INPUT(nAttr)
    
    # Step size
    nAttr = OpenMaya.MFnNumericAttribute()
    LSystemInstanceNode.mDefStepSize = nAttr.create("stepSize", "s", OpenMaya.MFnNumericData.kFloat, 1.0)
    MAKE_INPUT(nAttr)

    # Iterations
    nAttr = OpenMaya.MFnNumericAttribute()
    LSystemInstanceNode.mIterations = nAttr.create("iterations", "iter", OpenMaya.MFnNumericData.kLong, 1)
    MAKE_INPUT(nAttr)

    # Time
    uAttr = OpenMaya.MFnUnitAttribute()
    LSystemInstanceNode.time = uAttr.create("time", "tm", OpenMaya.MFnUnitAttribute.kTime, 0)
    MAKE_INPUT(uAttr)

    # Grammar File
    tAttr = OpenMaya.MFnTypedAttribute()
    LSystemInstanceNode.mDefGrammarFile = tAttr.create("grammar", "g", OpenMaya.MFnData.kString)
    MAKE_INPUT(tAttr)

    # Branch Segments
    tAttr = OpenMaya.MFnTypedAttribute()
    LSystemInstanceNode.mBranches =  tAttr.create("branches", "b", OpenMaya.MFnArrayAttrsData.kDynArrayAttrs)
    MAKE_OUTPUT(tAttr)
    # MAKE_INPUT(tAttr)

    # Flowers
    tAttr = OpenMaya.MFnTypedAttribute()
    LSystemInstanceNode.mFlowers =  tAttr.create("flowers", "f", OpenMaya.MFnArrayAttrsData.kDynArrayAttrs)
    MAKE_OUTPUT(tAttr)
    #MAKE_INPUT(tAttr)

    # Output mesh
    tAttr = OpenMaya.MFnTypedAttribute()
    LSystemInstanceNode.outputMesh = tAttr.create("outputMesh", "out", OpenMaya.MFnData.kMesh)
    MAKE_OUTPUT(tAttr)

        # Random points (*OUT* vs in)
    # tAttr = OpenMaya.MFnTypedAttribute()
    # LSystemInstanceNode.outPoints = tAttr.create("outPoints", "output", OpenMaya.MFnArrayAttrsData.kDynArrayAttrs)
    # MAKE_OUTPUT(tAttr)


    # add Attributues
    LSystemInstanceNode.addAttribute(LSystemInstanceNode.mDefAngle) 
    LSystemInstanceNode.addAttribute(LSystemInstanceNode.mDefStepSize)
    LSystemInstanceNode.addAttribute(LSystemInstanceNode.mDefGrammarFile)
    LSystemInstanceNode.addAttribute(LSystemInstanceNode.mIterations)
    LSystemInstanceNode.addAttribute(LSystemInstanceNode.time)
    LSystemInstanceNode.addAttribute(LSystemInstanceNode.outputMesh)
    LSystemInstanceNode.addAttribute(LSystemInstanceNode.mFlowers)
    LSystemInstanceNode.addAttribute(LSystemInstanceNode.mBranches)
    # LSystemInstanceNode.addAttribute(LSystemInstanceNode.outPoints)


    # Attribute Affects
    # LSystemInstanceNode.attributeAffects(LSystemInstanceNode.time, LSystemInstanceNode.outputMesh)
    # LSystemInstanceNode.attributeAffects(LSystemInstanceNode.mIterations, LSystemInstanceNode.outputMesh)
    # LSystemInstanceNode.attributeAffects(LSystemInstanceNode.mDefAngle, LSystemInstanceNode.outputMesh)
    # LSystemInstanceNode.attributeAffects(LSystemInstanceNode.mDefStepSize, LSystemInstanceNode.outputMesh)
    # LSystemInstanceNode.attributeAffects(LSystemInstanceNode.mDefGrammarFile, LSystemInstanceNode.outputMesh)
    LSystemInstanceNode.attributeAffects(LSystemInstanceNode.time, LSystemInstanceNode.mFlowers)
    LSystemInstanceNode.attributeAffects(LSystemInstanceNode.mIterations, LSystemInstanceNode.mFlowers)
    LSystemInstanceNode.attributeAffects(LSystemInstanceNode.mDefAngle, LSystemInstanceNode.mFlowers)
    LSystemInstanceNode.attributeAffects(LSystemInstanceNode.mDefStepSize, LSystemInstanceNode.mFlowers)
    LSystemInstanceNode.attributeAffects(LSystemInstanceNode.mDefGrammarFile, LSystemInstanceNode.mFlowers)
   

    LSystemInstanceNode.attributeAffects(LSystemInstanceNode.time, LSystemInstanceNode.mBranches)
    LSystemInstanceNode.attributeAffects(LSystemInstanceNode.mIterations, LSystemInstanceNode.mBranches)
    LSystemInstanceNode.attributeAffects(LSystemInstanceNode.mDefAngle, LSystemInstanceNode.mBranches)
    LSystemInstanceNode.attributeAffects(LSystemInstanceNode.mDefStepSize, LSystemInstanceNode.mBranches)
    LSystemInstanceNode.attributeAffects(LSystemInstanceNode.mDefGrammarFile, LSystemInstanceNode.mBranches)
    # Todo check if this is valid?
    # LSystemInstanceNode.attributeAffects(LSystemInstanceNode.mFlowers, LSystemInstanceNode.outputMesh)
    # LSystemInstanceNode.attributeAffects(LSystemInstanceNode.mBranches, LSystemInstanceNode.outputMesh)
    # LSystemInstanceNode.attributeAffects(LSystemInstanceNode.mFlowers, LSystemInstanceNode.outputPoints)
    # LSystemInstanceNode.attributeAffects(LSystemInstanceNode.mBranches, LSystemInstanceNode.outputPoints)

#----------------------------------------------------------------------------------#
###################################### RANDOM NODE #################################
#----------------------------------------------------------------------------------#

# Define the name of the node
kPluginNodeTypeName = "randomNode"

# Give the node a unique ID. Make sure this ID is different from all of your
# other nodes!
randomNodeId = OpenMaya.MTypeId(0xFA16)

# Node definition
class randomNode(OpenMayaMPx.MPxNode):
    # Declare class variables:
    # TODO:: declare the input and output class variables
    #         i.e. inNumPoints = OpenMaya.MObject()
    
    # The number of Random points to generate
    mNumPoints = OpenMaya.MObject()

    # Lower point bounds 
    mLowerPointXBound = OpenMaya.MObject()
    mLowerPointYBound = OpenMaya.MObject()
    mLowerPointZBound = OpenMaya.MObject()
    
    # Vect containing the lower point bound
    mLowerPointBoundVec = OpenMaya.MObject()

    # Upper point bound
    mUpperPointXBound = OpenMaya.MObject()
    mUpperPointYBound = OpenMaya.MObject()
    mUpperPointZBound = OpenMaya.MObject()
    
    # Vect containing the upper point bound
    mUpperPointBoundVec = OpenMaya.MObject()

    # The random points object
    outPoints = OpenMaya.MObject()


    # constructor
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    # compute
    def compute(self,plug,data):
        # TODO:: create the main functionality of the node. Your node should 
        #         take in three floats for max position (X,Y,Z), three floats 
        #         for min position (X,Y,Z), and the number of random points to
        #         be generated. Your node should output an MFnArrayAttrsData 
        #         object containing the random points. Consult the homework
        #         sheet for how to deal with creating the MFnArrayAttrsData. 

        if plug == randomNode.outPoints:

            # Set up the array for adding random points
            pointsData = data.outputValue(randomNode.outPoints) #the MDataHandle 
            pointsAAD = OpenMaya.MFnArrayAttrsData() #the MFnArrayAttrsData
            pointsObject = pointsAAD.create() #the MObject

            # Create the vectors for “position” and “id”. Names and types must match # table above.
            positionArray = pointsAAD.vectorArray('position')
            idArray = pointsAAD.doubleArray('id')

            # Get the num of points we need
            numPtData = data.inputValue(randomNode.mNumPoints) 
            numPts = numPtData.asInt()
            
            # Get the num points from the data
            for ptIndex in range(0, numPts):
                # Make Random Points using min and max values
                # X BOUND
                minXData = data.inputValue(randomNode.mLowerPointXBound)
                maxXData = data.inputValue(randomNode.mUpperPointXBound)
                # Y BOUNDS
                minYData = data.inputValue(randomNode.mLowerPointYBound)
                maxYData = data.inputValue(randomNode.mUpperPointYBound)
                # Z BOUNDS      
                minZData = data.inputValue(randomNode.mLowerPointZBound)
                maxZData = data.inputValue(randomNode.mUpperPointZBound)

                # Generate Rand Num b/w min and max
                x = random.uniform(minXData.asDouble(), maxXData.asDouble())
                y = random.uniform(minYData.asDouble(), maxYData.asDouble())
                z = random.uniform(minZData.asDouble(), maxZData.asDouble())
                
                # Make MVector of random values
                ptVec = OpenMaya.MVector(x, y, z)

                # Append to points & id
                positionArray.append(ptVec) 
                idArray.append(ptIndex)

            # Now set the points data :)
            pointsData.setMObject(pointsObject)

            # Clear up the data
            data.setClean(plug)
    
# initializer
def nodeInitializer():
    # TODO:: initialize the input and output attributes. Be sure to use the 
    #         MAKE_INPUT and MAKE_OUTPUT functions.
    #------------------------------------#
    ############ NUM RAND PTS ##########
    #------------------------------------#
    # Num Random Points
    nAttr = OpenMaya.MFnNumericAttribute()
    randomNode.mNumPoints = nAttr.create("numRandomPoints", "numRandPts", OpenMaya.MFnNumericData.kInt)
    MAKE_INPUT(nAttr)
    #------------------------------------#
    ############ LOWER PT BOUND ##########
    #------------------------------------#
    # Lower Point Bound X
    nAttr = OpenMaya.MFnNumericAttribute()
    randomNode.mLowerPointXBound = nAttr.create("mLowerPtBoundX", "mLowBoundPtX", OpenMaya.MFnNumericData.kDouble)
    MAKE_INPUT(nAttr)

    # Lower Point Bound Y
    nAttr = OpenMaya.MFnNumericAttribute()
    randomNode.mLowerPointYBound = nAttr.create("mLowerPtBoundY", "mLowBoundPtY", OpenMaya.MFnNumericData.kDouble)
    MAKE_INPUT(nAttr)   

    # Lower Point Bound Z
    nAttr = OpenMaya.MFnNumericAttribute()
    randomNode.mLowerPointZBound = nAttr.create("mLowerPtBoundZ", "mLowBoundPtZ", OpenMaya.MFnNumericData.kDouble)
    MAKE_INPUT(nAttr)

    # Lower Point Bound Vector
    nAttr = OpenMaya.MFnNumericAttribute()    
    randomNode.mLowerPointBoundVec = nAttr.create("mLowerPointBoundVec", 
        "mLowPtBoundVec",  
        randomNode.mLowerPointXBound,  
        randomNode.mLowerPointYBound,
        randomNode.mLowerPointZBound)
    MAKE_INPUT(nAttr)

    #------------------------------------#
    ############ UPPER PT BOUND ##########
    #------------------------------------#
    # Upper Point Bound X
    nAttr = OpenMaya.MFnNumericAttribute()
    randomNode.mUpperPointXBound = nAttr.create("mUpperPtBoundX", "mUpBoundPtX", OpenMaya.MFnNumericData.kDouble)
    MAKE_INPUT(nAttr)

    # Lower Point Bound Y
    nAttr = OpenMaya.MFnNumericAttribute()
    randomNode.mUpperPointYBound = nAttr.create("mUpperPtBoundY", "mUpBoundPtY", OpenMaya.MFnNumericData.kDouble)
    MAKE_INPUT(nAttr)   

    # Lower Point Bound Z
    nAttr = OpenMaya.MFnNumericAttribute()
    randomNode.mUpperPointZBound = nAttr.create("mUpperPtBoundZ", "mUpBoundPtZ", OpenMaya.MFnNumericData.kDouble)
    MAKE_INPUT(nAttr)

    # Lower Point Bound Vector
    nAttr = OpenMaya.MFnNumericAttribute()
    randomNode.mUpperPointBoundVec = nAttr.create("mUpperPointBoundVec", 
        "mUpPtBoundVec",  
        randomNode.mUpperPointXBound,  
        randomNode.mUpperPointYBound,
        randomNode.mUpperPointZBound)
    MAKE_INPUT(nAttr)

    #------------------------------------#
    ########### RAND POINTS ARR ##########
    #------------------------------------#
    # Random points (*OUT* vs in)
    tAttr = OpenMaya.MFnTypedAttribute()
    randomNode.outPoints = tAttr.create("outPoints", "output", OpenMaya.MFnArrayAttrsData.kDynArrayAttrs)
    MAKE_OUTPUT(tAttr)
    #------------------------------------#

    # TODO:: add the attributes to the node and set up the
    # 
    # attributeAffects (addAttribute, and attributeAffects)
    
    #------------------------------------#
    ############ ADD ATTRIBUTES ##########
    #------------------------------------#
    # Num points
    randomNode.addAttribute(randomNode.mNumPoints)

    # Lower bound
    randomNode.addAttribute(randomNode.mLowerPointBoundVec)

    # Upper bound
    randomNode.addAttribute(randomNode.mUpperPointBoundVec)

    # Random Points
    randomNode.addAttribute(randomNode.outPoints)

    #------------------------------------#
    ######### ATTRIBUTES AFFECTS #########
    #------------------------------------#
    # Now add affects
    randomNode.attributeAffects(randomNode.mNumPoints, randomNode.outPoints)
    randomNode.attributeAffects(randomNode.mLowerPointBoundVec, randomNode.outPoints)
    randomNode.attributeAffects(randomNode.mUpperPointBoundVec, randomNode.outPoints)
    print "Initialization!\n"

# creator
def nodeCreator():
    print "In Creator!\n"
    return OpenMayaMPx.asMPxPtr(randomNode())

#----------------------------------------------------------------------------------#
###################################### GLOBAL FXNS #################################
#----------------------------------------------------------------------------------#


##############################################################
###  Custom Drop Down Menu for PAALM  ########################
##############################################################

DROP_DOWN_MENU_NAME = "LSYSMENU"

class LSystemUIMenu(object):

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
        cmd = 'sphere; instancer; createNode lSystemInstanceNode; connectAttr nurbsSphere1.matrix instancer1.inputHierarchy[0]; '
        cmd += 'connectAttr lSystemInstanceNode.mBranches instancer1.inputPoints; connectAttr lSystemInstanceNode.mFlowers instancer1.inputPoints;'
        maya.mel.eval(cmd)


    def makeLSINNetworkSelected(self):
        cmd = 'sphere; instancer; createNode randomNode; connectAttr nurbsSphere1.matrix instancer1.inputHierarchy[0]; '
        cmd += 'connectAttr lSystemInstanceNode.mBranches instancer1.inputPoints; connectAttr lSystemInstanceNode.mFlowers instancer1.inputPoints;'
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


LSYSTEM_MENU = LSystemUIMenu()




##############################################################
###  INIT FUNCTIONS FOR PLUG-IN  #############################
##############################################################

# initialize the script plug-in
def initializePlugin(mobject):
    print "Trying to init"
    global LSYSTEM_MENU
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Michael Rivera", "1.0", "Any")
    try:
        mplugin.registerNode( kPluginNodeTypeName, randomNodeId, nodeCreator, nodeInitializer)
        mplugin.registerNode( kPluginLSystemInstanceNodeTypeName, LSystemInstanceNodeId, LSystemNodeCreator, LSystemNodeInitializer)
        # Show UI Menu
        #LSYSTEM_MENU = LSystemUIMenu()
    except:
        sys.stderr.write( "Failed to register node: %s\n" % kPluginNodeTypeName )


# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode( randomNodeId )
        mplugin.deregisterNode( LSystemInstanceNodeId )

        # Delete old UI
        if LSYSTEM_MENU != None:
            cmds.deleteUI(LSYSTEM_MENU.name)
    except:
        sys.stderr.write( "Failed to unregister node: %s\n" % kPluginNodeTypeName )