# -*- coding: utf-8 -*-
import sys, math
import random
import maya
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx

import StemGlobal as SG

#------------------------------------------------------------------------------#
# -----------------------A primer on bud existence------------------------------
# A bud may either be terminal or lateral (axillary). Terminal buds only exist
# at the end of a shoot (a 'leaf node' in terms of graph theory). Lateral buds
# exist also at the end of a shoot, but also at nodes (points where internodes
# connect) where there is only 1 child internode (so there is no branching
# point, just an internode-internode connection [-- instead of -<]).
# Once an internode has 2 child internodes (-<), no more buds can exist there.
#
# If a new metamer (internode w/ leaf+bud) grows out of a lateral bud, that
# lateral bud becomes the terminal bud of the newly grown metamer.
#
# A lateral bud can have 1 or no child internode.
# A terminal bud must have no child internode.
# Both must have a parent internode. The only exception is a terminal bud at the
# tree's seedling on an axis of order 0, from which the main trunk forms.
#------------------------------------------------------------------------------#

'''
'' Declare bud type enum
'''
def enum(*args):
    enums = dict(zip(args, range(len(args))))
    return type('Enum', (), enums)
BudType = enum('TERMINAL', 'LATERAL')

'''
'' Stem Bud Class for storing bud information
'''
class StemBud():

  def __init__(self, budType=BudType.TERMINAL, parentInternode=None, childInternode=None):
    self.mBudType = budType
    self.mInternodeParent = parentInternode
    self.mInternodeChild = childInternode
    self.mQLightAmount = 0
    self.mVResourceAmount = 0

    budTypeName = ''
    if (self.mBudType == BudType.TERMINAL):
      budTypeName = 'terminal bud'
    elif (self.mBudType == BudType.LATERAL):
      budTypeName = 'lateral bud'

    st = parentInternode.mStart
    coordString = '<' + str(st[0]) + ',' + str(st[1]) + ',' + str(st[2]) + '>'
    print 'Successfully created ' + budTypeName + ' for ' + coordString