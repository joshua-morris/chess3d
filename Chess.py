from OpenGL.GL import *
import math
import numpy as np
import time
import imgui

import magic
# We import the 'lab_utils' module as 'lu' to save a bit of typing while still clearly marking where the code came from.
import Util as lu
from ObjModel import ObjModel
import glob
import os

WIDTH, HEIGHT = 1280, 800
WINDOW_TITLE = 'Chess'
# this is just a constant that was found through trial and error
# to find what height to draw the pieces at
BOARD_HEIGHT = 0.46

# Lighting
g_lightYaw = 25.0
g_lightYawSpeed = 0.0
g_lightPitch = -30.0
g_lightPitchSpeed = 0.0
g_lightDistance = 500.0
g_lightColourAndIntensity = lu.vec3(0.9, 0.9, 0.6)
g_ambientLightColourAndIntensity = lu.vec3(0.1)

# Camera
g_camera = lu.OrbitCamera([0,0,0], 10.0, -25.0, -35.0)
g_yFovDeg = 45.0
g_worldSpaceLightDirection = [-1, -1, -1]
g_cameraDistance = 15.0
g_cameraYaw = 270.0
g_cameraPitch = 60.0
g_lookTargetHeight = -1.0

# Models
g_currentModelName = "board.obj"
g_boardModel = None
g_whitePawnModels = None
g_blackPawnModels = None
g_whiteKingModel = None
g_blackKingModel = None
g_whiteQueenModel = None
g_blackQueenModel = None
g_whiteBishopModels = None
g_blackBishopModels = None
g_whiteKnightModels = None
g_blackKnightModels = None
g_whiteRookModels = None
g_blackRookModels = None

# Shaders
g_vertexShaderSource = ObjModel.defaultVertexShader
g_fragmentShaderSource = ObjModel.defaultFragmentShader
g_currentFragmentShaderName = 'fragmentShader.glsl'

g_environmentCubeMap = None

# Set the texture unit to use for the cube map to the next free one
# (free as in not used by the ObjModel)
TU_EnvMap = ObjModel.TU_Max

def buildShader(vertexShaderSource, fragmentShaderSource):
    shader = lu.buildShader(vertexShaderSource, fragmentShaderSource, ObjModel.getDefaultAttributeBindings())
    if shader:
        glUseProgram(shader)
        ObjModel.setDefaultUniformBindings(shader)
        glUseProgram(0)
    return shader



g_reloadTimeout = 1.0
def update(dt, keys, mouseDelta):
    global g_camera
    global g_reloadTimeout
    global g_lightYaw
    global g_lightYawSpeed
    global g_lightPitch
    global g_lightPitchSpeed

    g_lightYaw += g_lightYawSpeed * dt
    g_lightPitch += g_lightPitchSpeed * dt

    g_reloadTimeout -= dt
    if g_reloadTimeout <= 0.0:
        reLoadShader();
        g_reloadTimeout = 1.0

    g_camera.update(dt, keys, mouseDelta)

# This function is called by the 'magic' to draw a frame width, height are the size of the frame buffer, or window
def renderFrame(xOffset, width, height):
    global g_worldSpaceLightDirection
    global g_cameraDistance
    global g_cameraYaw
    global g_cameraPitch
    global g_lookTargetHeight
    
    global g_whitePawnModels
    global g_blackPawnModels
    global g_whiteKingModel
    global g_blackKingModel
    global g_whiteQueenModel
    global g_blackQueenModel
    global g_whiteBishopModels
    global g_blackBishopModels
    global g_whiteKnightModels
    global g_blackKnightModels
    global g_whiteRookModels
    global g_blackRookModels

    lightRotation = lu.Mat3(lu.make_rotation_y(math.radians(g_lightYaw))) * lu.Mat3(lu.make_rotation_x(math.radians(g_lightPitch))) 
    lightPosition = g_boardModel.centre + lightRotation * lu.vec3(0,0,g_lightDistance)

    # This configures the fixed-function transformation from Normalized Device Coordinates (NDC)
    # to the screen (pixels - called 'window coordinates' in OpenGL documentation).
    #   See: https://www.khronos.org/registry/OpenGL-Refpages/gl4/html/glViewport.xhtml
    glViewport(xOffset, 0, width, height)
    # Set the colour we want the frame buffer cleared to, 
    glClearColor(66/255, 179/255, 245/255, 1.0)
    # Tell OpenGL to clear the render target to the clear values for both depth and colour buffers (depth uses the default)
    glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

    eyePos = lu.Mat3(lu.make_rotation_y(math.radians(g_cameraYaw)) * lu.make_rotation_x(-math.radians(g_cameraPitch))) * [0.0, 0.0, g_cameraDistance]

    worldToViewTfm = magic.make_lookAt(eyePos, [0,g_lookTargetHeight,0], [0, 1, 0])
    viewToClipTfm = magic.make_perspective(45.0, width / height, 0.1, 1000.0)

    # Bind the shader program such that we can set the uniforms (model.render sets it again)
    glUseProgram(g_shader)

    lu.setUniform(g_shader, "viewSpaceLightPosition", lu.transformPoint(worldToViewTfm, lightPosition))
    lu.setUniform(g_shader, "lightColourAndIntensity", g_lightColourAndIntensity)
    lu.setUniform(g_shader, "ambientLightColourAndIntensity", g_ambientLightColourAndIntensity)

    lu.setUniform(g_shader, "viewToWorldRotationTransform", lu.inverse(lu.Mat3(worldToViewTfm)))
    # transform (rotate) light direction into view space (as this is what the ObjModel shader wants)

    # This dictionary contains a few transforms that are needed to render the ObjModel using the default shader.
    # it would be possible to just set the modelToWorld transform, as this is the only thing that changes between
    # the objects, and compute the other matrices in the vertex shader.
    # However, this would push a lot of redundant computation to the vertex shader and makes the code less self contained,
    # in this way we set all the required parameters explicitly.
    
    boardModelToWorldTransform = lu.Mat4()
    drawObjModel(viewToClipTfm, worldToViewTfm, boardModelToWorldTransform, g_boardModel)

    whiteKingModelToWorldTransform = lu.make_translation(3.5, BOARD_HEIGHT, -0.5)
    drawObjModel(viewToClipTfm, worldToViewTfm, whiteKingModelToWorldTransform, g_whiteKingModel)

    blackKingModelToWorldTransform = lu.make_translation(-3.5, BOARD_HEIGHT, -0.5)
    drawObjModel(viewToClipTfm, worldToViewTfm, blackKingModelToWorldTransform, g_blackKingModel)

    whiteQueenModelToWorldTransform = lu.make_translation(3.5, BOARD_HEIGHT, 0.5)
    drawObjModel(viewToClipTfm, worldToViewTfm, whiteQueenModelToWorldTransform, g_whiteQueenModel)

    blackQueenModelToWorldTransform = lu.make_translation(-3.5, BOARD_HEIGHT, 0.5)
    drawObjModel(viewToClipTfm, worldToViewTfm, blackQueenModelToWorldTransform, g_blackQueenModel)

    whitePawnModelToWorldTransforms = []
    blackPawnModelToWorldTransforms = []
    for i in range(8):
        whitePawnModelToWorldTransforms.append(lu.make_translation(2.5, BOARD_HEIGHT, -3.5+1*i))
        drawObjModel(viewToClipTfm, worldToViewTfm, whitePawnModelToWorldTransforms[i], g_whitePawnModels[i])

        blackPawnModelToWorldTransforms.append(lu.make_translation(-2.5, BOARD_HEIGHT, -3.5+1*i))
        drawObjModel(viewToClipTfm, worldToViewTfm, blackPawnModelToWorldTransforms[i], g_blackPawnModels[i])

    whiteBishopModelToWorldTransforms = []
    blackBishopModelToWorldTransforms = []
    whiteKnightModelToWorldTransforms = []
    blackKnightModelToWorldTransforms = []
    whiteRookModelToWorldTransforms = []
    blackRookModelToWorldTransforms = []
    for i in range(-1, 2, 2):
        whiteBishopModelToWorldTransforms.append(lu.make_translation(3.5, BOARD_HEIGHT, 1.5*i))
        drawObjModel(viewToClipTfm, worldToViewTfm, whiteBishopModelToWorldTransforms[i], g_whiteBishopModels[i])

        blackBishopModelToWorldTransforms.append(lu.make_translation(-3.5, BOARD_HEIGHT, 1.5*i))
        drawObjModel(viewToClipTfm, worldToViewTfm, blackBishopModelToWorldTransforms[i], g_blackBishopModels[i])

        whiteKnightModelToWorldTransforms.append(lu.make_translation(3.5, BOARD_HEIGHT, 2.5*i))
        drawObjModel(viewToClipTfm, worldToViewTfm, whiteKnightModelToWorldTransforms[i], g_whiteKnightModels[i])

        blackKnightModelToWorldTransforms.append(lu.make_translation(-3.5, BOARD_HEIGHT, 2.5*i))
        drawObjModel(viewToClipTfm, worldToViewTfm, blackKnightModelToWorldTransforms[i], g_blackKnightModels[i])

        whiteRookModelToWorldTransforms.append(lu.make_translation(3.5, BOARD_HEIGHT, 3.5*i))
        drawObjModel(viewToClipTfm, worldToViewTfm, whiteRookModelToWorldTransforms[i], g_whiteRookModels[i])

        blackRookModelToWorldTransforms.append(lu.make_translation(-3.5, BOARD_HEIGHT, 3.5*i))
        drawObjModel(viewToClipTfm, worldToViewTfm, blackRookModelToWorldTransforms[i], g_blackRookModels[i])

   # lu.drawSphere(lightPosition, 0.5, [1,1,0,1], viewToClipTfm, worldToViewTfm)

def drawObjModel(viewToClipTfm, worldToViewTfm, modelToWorldTfm, model):
    """Render a model in the world."""

    modelToViewTransform = worldToViewTfm * modelToWorldTfm
    
    # this is a special transform that ensures that normal vectors remain orthogonal to the 
    # surface they are supposed to be even in the prescence of non-uniform scaling.
    # It is a 3x3 matrix as vectors don't need translation anyway and this transform is only for vectors,
    # not points. If there is no non-uniform scaling this is just the same as Mat3(modelToViewTransform)
    modelToViewNormalTransform = lu.inverse(lu.transpose(lu.Mat3(modelToViewTransform)));

    # Bind the shader program such that we can set the uniforms (model.render sets it again)
    glUseProgram(g_shader)

    # transform (rotate) light direction into view space (as this is what the ObjModel shader wants)
#    viewSpaceLightDirection = lu.normalize(lu.Mat3(worldToViewTfm) * g_worldSpaceLightDirection)
 #   glUniform3fv(glGetUniformLocation(model.defaultShader, "viewSpaceLightDirection"), 1, viewSpaceLightDirection);

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
    
    model.render(g_shader, ObjModel.RF_Opaque, transforms)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    model.render(g_shader, ObjModel.RF_Transparent| ObjModel.RF_AlphaTested, transforms)
    glDisable(GL_BLEND)

def itemListCombo(currentItem, items, name):
    ind = items.index(currentItem)
    _,ind = imgui.combo(name, ind, items)
    return items[ind]

def reLoadShader():
    global g_vertexShaderSource
    global g_fragmentShaderSource
    global g_shader
    
    vertexShader = ""
    with open('vertexShader.glsl') as f:
        vertexShader = f.read()
    fragmentShader = ""
    with open(g_currentFragmentShaderName) as f:
        fragmentShader = f.read()

    if g_vertexShaderSource != vertexShader or fragmentShader != g_fragmentShaderSource:
        newShader = buildShader(vertexShader, fragmentShader)
        if newShader:
            if g_shader:
                glDeleteProgram(g_shader)
            g_shader = newShader
            print("Reloaded shader, ok!")
        else:
            pass
        g_vertexShaderSource = vertexShader
        g_fragmentShaderSource = fragmentShader


def initResources():
    global g_camera
    global g_lightDistance
    global g_shader

    global g_boardModel
    global g_whitePawnModels
    global g_blackPawnModels
    global g_whiteKingModel
    global g_blackKingModel
    global g_whiteQueenModel
    global g_blackQueenModel
    global g_whiteBishopModels
    global g_blackBishopModels
    global g_whiteKnightModels
    global g_blackKnightModels
    global g_whiteRookModels
    global g_blackRookModels

    g_boardModel = ObjModel('model/board.obj');
    g_whiteKingModel = ObjModel('model/whiteKing.obj')
    g_blackKingModel = ObjModel('model/blackKing.obj')
    g_whiteQueenModel = ObjModel('model/whiteQueen.obj')
    g_blackQueenModel = ObjModel('model/blackQueen.obj')

    g_whitePawnModels = []
    g_blackPawnModels = []
    for i in range(8):
        g_whitePawnModels.append(ObjModel('model/whitePawn.obj'))
        g_blackPawnModels.append(ObjModel('model/blackPawn.obj'))

    g_whiteBishopModels = []
    g_blackBishopModels = []
    g_whiteKnightModels = []
    g_blackKnightModels = []
    g_whiteRookModels = []
    g_blackRookModels = []
    for i in range(2):
        g_whiteBishopModels.append(ObjModel('model/whiteBishop.obj'))
        g_blackBishopModels.append(ObjModel('model/blackBishop.obj'))
        g_whiteKnightModels.append(ObjModel('model/whiteKnight.obj'))
        g_blackKnightModels.append(ObjModel('model/blackKnight.obj'))
        g_whiteRookModels.append(ObjModel('model/whiteRook.obj'))
        g_blackRookModels.append(ObjModel('model/blackRook.obj'))

    g_camera.target = g_boardModel.centre
    g_camera.distance = lu.length(g_boardModel.centre - g_boardModel.aabbMin) * 3.1
    g_lightDistance = lu.length(g_boardModel.centre - g_boardModel.aabbMin) * 1.3

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glEnable(GL_TEXTURE_CUBE_MAP_SEAMLESS)
    glEnable(GL_FRAMEBUFFER_SRGB)

    # Build with default first since that really should work, so then we have some fallback
    g_shader = buildShader(g_vertexShaderSource, g_fragmentShaderSource)

    reLoadShader()    


# This does all the openGL setup and window creation needed
# it hides a lot of things that we will want to get a handle on as time goes by.
magic.runProgram(WINDOW_TITLE, WIDTH, HEIGHT, renderFrame, initResources, None, update)
