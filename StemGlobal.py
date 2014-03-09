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
STEM_VERSION = '0.1'
STEM_GITHUB_SITE = 'https://github.com/mriveralee/maya-stem/'
STEM_HELP_SITE = 'http://github.com/mriveralee/maya-stem/issues'

# Maya's OpenGL Renderer & Function table api
GL_RENDERER = OpenMayaRender.MHardwareRenderer.theRenderer()
GLFT = GL_RENDERER.glFunctionTable()



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
