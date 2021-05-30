import glfw

from copy import deepcopy

import magic
import Util as lu
import math

import imgui

from OpenGL.GL import *
from ObjModel import ObjModel

WIDTH, HEIGHT = 500, 700
WINDOW_TITLE = 'Chess'

g_boardModel = None
g_whiteKingModel = None
g_blackKingModel = None
g_whiteQueenModel = None
g_blackQueenModel = None

g_worldSpaceLightDirection = [-1, -1, -1]
g_cameraDistance = 40.0
g_cameraYaw = 45.0
g_cameraPitch = 40.0
g_lookTargetHeight = 6.0

def renderFrame(width, height):
  global g_boardModel
  global g_whiteKingModel
  global g_blackKingModel
  global g_whiteQueenModel
  global g_blackQueenModel

  global g_worldSpaceLightDirection
  global g_cameraDistance
  global g_cameraYaw
  global g_cameraPitch
  global g_lookTargetHeight
  
  # This configures the fixed-function transformation from Normalized Device Coordinates (NDC)
  # to the screen (pixels - called 'window coordinates' in OpenGL documentation).
  #   See: https://www.khronos.org/registry/OpenGL-Refpages/gl4/html/glViewport.xhtml
  glViewport(0, 0, width, height)
  # Set the colour we want the frame buffer cleared to, 
  glClearColor(0.2, 0.3, 0.1, 1.0)
  # Tell OpenGL to clear the render target to the clear values for both depth and colour buffers (depth uses the default)
  glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

  # Use the camera parameters to calucalte the position of the 'eye' or camera, the viewer location
  eyePos = lu.Mat3(lu.make_rotation_y(math.radians(g_cameraYaw)) * lu.make_rotation_x(-math.radians(g_cameraPitch))) * [0.0, 0.0, g_cameraDistance]

  worldToViewTfm = magic.make_lookAt(eyePos, [0,g_lookTargetHeight,0], [0, 1, 0])
  viewToClipTfm = magic.make_perspective(45.0, width / height, 0.1, 1000.0)

  boardModelToWorldTransform = lu.Mat4()
  drawObjModel(viewToClipTfm, worldToViewTfm, boardModelToWorldTransform, g_boardModel)

  whiteKingModelToWorldTransform = lu.make_translation(3.5, 0.46, -0.5)
  drawObjModel(viewToClipTfm, worldToViewTfm, whiteKingModelToWorldTransform, g_whiteKingModel)

  blackKingModelToWorldTransform = lu.make_translation(-3.5, 0.46, -0.5)
  drawObjModel(viewToClipTfm, worldToViewTfm, blackKingModelToWorldTransform, g_blackKingModel)

def drawUi():
  global g_cameraDistance
  global g_cameraYaw
  global g_cameraPitch
  global g_lookTargetHeight

  if imgui.tree_node("Camera Controls", imgui.TREE_NODE_DEFAULT_OPEN):
      _,g_cameraDistance = imgui.slider_float("CameraDistance", g_cameraDistance, 1.0, 150.0)
      _,g_cameraYaw = imgui.slider_float("CameraYaw", g_cameraYaw, 0.0, 360.0)
      _,g_cameraPitch = imgui.slider_float("CameraPitch", g_cameraPitch, -89.0, 89.0)
      _,g_lookTargetHeight = imgui.slider_float("LookTargetHeight", g_lookTargetHeight, 0.0, 25.0)
      imgui.tree_pop()

def initResources():
  global g_boardModel
  global g_whiteKingModel
  global g_blackKingModel
  global g_whiteQueenModel
  global g_blackQueenModel

  g_boardModel = ObjModel('model/board.obj')
  g_whiteKingModel = ObjModel('model/whiteKing.obj')
  g_blackKingModel = ObjModel('model/blackKing.obj')
  g_whiteQueenModel = ObjModel('model/whiteQueen.obj')
  g_blackQueenModel = ObjModel('model/blackQueen.obj')

  # turn backface culling back on
  glEnable(GL_CULL_FACE)

def drawObjModel(viewToClipTfm, worldToViewTfm, modelToWorldTfm, model):
    """Render a model in the world."""

    modelToViewTransform = worldToViewTfm * modelToWorldTfm
    
    # this is a special transform that ensures that normal vectors remain orthogonal to the 
    # surface they are supposed to be even in the prescence of non-uniform scaling.
    # It is a 3x3 matrix as vectors don't need translation anyway and this transform is only for vectors,
    # not points. If there is no non-uniform scaling this is just the same as Mat3(modelToViewTransform)
    modelToViewNormalTransform = lu.inverse(lu.transpose(lu.Mat3(modelToViewTransform)));

    # Bind the shader program such that we can set the uniforms (model.render sets it again)
    glUseProgram(model.defaultShader)

    # transform (rotate) light direction into view space (as this is what the ObjModel shader wants)
    viewSpaceLightDirection = lu.normalize(lu.Mat3(worldToViewTfm) * g_worldSpaceLightDirection)
    glUniform3fv(glGetUniformLocation(model.defaultShader, "viewSpaceLightDirection"), 1, viewSpaceLightDirection);

    # This dictionary contains a few transforms that are needed to render the ObjModel using the default shader.
    # it would be possible to just set the modelToWorld transform, as this is the only thing that changes between
    # the objects, and compute the other matrices in the vertex shader.
    # However, this would push a lot of redundant computation to the vertex shader and makes the code less self contained,
    # in this way we set all the required parameters explicitly.
    transforms = {
        "modelToClipTransform" : viewToClipTfm * worldToViewTfm * modelToWorldTfm,
        "modelToViewTransform" : modelToViewTransform,
        "modelToViewNormalTransform" : modelToViewNormalTransform,
    }
    
    model.render(None, None, transforms)


def main():
  magic.runProgram(WINDOW_TITLE, WIDTH, HEIGHT, renderFrame, initResources, drawUi) 

if __name__ == '__main__':
  main()
