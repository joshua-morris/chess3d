import math
import Util as lu

from OpenGL.GL import *
from ObjModel import ObjModel
import magic

WIDTH, HEIGHT = 1280, 800
WINDOW_TITLE = 'Chess'
# this is just a constant that was found through trial and error
# to find what height to draw the pieces at
BOARD_HEIGHT = 0.46

class View:
    def __init__(self):
        self.lighting = Lighting()
        self.camera = Camera()
        self.shader = None

        self.vertexShaderSource = ObjModel.defaultVertexShader
        self.fragmentShaderSource = ObjModel.defaultFragmentShader
        self.currentFragmentShaderName = 'fragmentShader.glsl'

        self.reloadTimeout = 1.0

        self.models = {}
        self.highlightOffset = [0.0, 0.0]

    def initModels(self):
        pass

    def initResources(self):
        self.models["highlight"] = ObjModel('model/highlight.obj')

        self.models["boardModel"] = ObjModel('model/board.obj');
        self.models["whiteKingModel"] = ObjModel('model/whiteKing.obj')
        self.models["blackKingModel"] = ObjModel('model/blackKing.obj')
        self.models["whiteQueenModel"] = ObjModel('model/whiteQueen.obj')
        self.models["blackQueenModel"] = ObjModel('model/blackQueen.obj')

        self.models["whitePawnModels"] = []
        self.models["blackPawnModels"] = []
        for i in range(8):
            self.models["whitePawnModels"].append(ObjModel('model/whitePawn.obj'))
            self.models["blackPawnModels"].append(ObjModel('model/blackPawn.obj'))

        self.models["whiteBishopModels"] = []
        self.models["blackBishopModels"] = []
        self.models["whiteKnightModels"] = []
        self.models["blackKnightModels"] = []
        self.models["whiteRookModels"] = []
        self.models["blackRookModels"] = []
        for i in range(2):
            self.models["whiteBishopModels"].append(ObjModel('model/whiteBishop.obj'))
            self.models["blackBishopModels"].append(ObjModel('model/blackBishop.obj'))
            self.models["whiteKnightModels"].append(ObjModel('model/whiteKnight.obj'))
            self.models["blackKnightModels"].append(ObjModel('model/blackKnight.obj'))
            self.models["whiteRookModels"].append(ObjModel('model/whiteRook.obj'))
            self.models["blackRookModels"].append(ObjModel('model/blackRook.obj'))

        self.camera.target = self.models["boardModel"].centre
        self.camera.distance = lu.length(self.models["boardModel"].centre - self.models["boardModel"].aabbMin) * 3.1
        self.lighting.lightDistance = lu.length(self.models["boardModel"].centre - self.models["boardModel"].aabbMin) * 1.3

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glEnable(GL_TEXTURE_CUBE_MAP_SEAMLESS)
        glEnable(GL_FRAMEBUFFER_SRGB)

        # Build with default first since that really should work, so then we have some fallback
        self.shader = buildShader(self.vertexShaderSource, self.fragmentShaderSource)

        self.reLoadShader()

    def renderFrame(self, xOffset, width, height):
        lightRotation = lu.Mat3(lu.make_rotation_y(math.radians(self.lighting.lightYaw))) * lu.Mat3(lu.make_rotation_x(math.radians(self.lighting.lightPitch))) 
        lightPosition = self.models["boardModel"].centre + lightRotation * lu.vec3(0,0,self.lighting.lightDistance)

        # This configures the fixed-function transformation from Normalized Device Coordinates (NDC)
        # to the screen (pixels - called 'window coordinates' in OpenGL documentation).
        #   See: https://www.khronos.org/registry/OpenGL-Refpages/gl4/html/glViewport.xhtml
        glViewport(xOffset, 0, width, height)
        # Set the colour we want the frame buffer cleared to, 
        glClearColor(66/255, 179/255, 245/255, 1.0)
        # Tell OpenGL to clear the render target to the clear values for both depth and colour buffers (depth uses the default)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

        eyePos = lu.Mat3(lu.make_rotation_y(math.radians(self.camera.cameraYaw)) * lu.make_rotation_x(-math.radians(self.camera.cameraPitch))) * [0.0, 0.0, self.camera.cameraDistance]

        worldToViewTfm = magic.make_lookAt(eyePos, [0,self.camera.lookTargetHeight,0], [0, 1, 0])
        viewToClipTfm = magic.make_perspective(45.0, width / height, 0.1, 1000.0)
        
        # Bind the shader program such that we can set the uniforms (model.render sets it again)
        glUseProgram(self.shader)

        lu.setUniform(self.shader, "viewSpaceLightPosition", lu.transformPoint(worldToViewTfm, lightPosition))
        lu.setUniform(self.shader, "lightColourAndIntensity", self.lighting.lightColourAndIntensity)
        lu.setUniform(self.shader, "ambientLightColourAndIntensity", self.lighting.ambientLightColourAndIntensity)

        lu.setUniform(self.shader, "viewToWorldRotationTransform", lu.inverse(lu.Mat3(worldToViewTfm)))
        # transform (rotate) light direction into view space (as this is what the ObjModel shader wants)
        
        boardModelToWorldTransform = lu.Mat4()
        self.drawObjModel(viewToClipTfm, worldToViewTfm, boardModelToWorldTransform, self.models["boardModel"])

        whiteKingModelToWorldTransform = lu.make_translation(3.5, BOARD_HEIGHT, -0.5)
        self.drawObjModel(viewToClipTfm, worldToViewTfm, whiteKingModelToWorldTransform, self.models["whiteKingModel"])

        blackKingModelToWorldTransform = lu.make_translation(-3.5, BOARD_HEIGHT, -0.5)
        self.drawObjModel(viewToClipTfm, worldToViewTfm, blackKingModelToWorldTransform, self.models["blackKingModel"])

        whiteQueenModelToWorldTransform = lu.make_translation(3.5, BOARD_HEIGHT, 0.5)
        self.drawObjModel(viewToClipTfm, worldToViewTfm, whiteQueenModelToWorldTransform, self.models["whiteQueenModel"])

        blackQueenModelToWorldTransform = lu.make_translation(-3.5, BOARD_HEIGHT, 0.5)
        self.drawObjModel(viewToClipTfm, worldToViewTfm, blackQueenModelToWorldTransform, self.models["blackQueenModel"])

        whitePawnModelToWorldTransforms = []
        blackPawnModelToWorldTransforms = []
        for i in range(8):
            whitePawnModelToWorldTransforms.append(lu.make_translation(2.5, BOARD_HEIGHT, -3.5+1*i))
            self.drawObjModel(viewToClipTfm, worldToViewTfm, whitePawnModelToWorldTransforms[i], self.models["whitePawnModels"][i])

            blackPawnModelToWorldTransforms.append(lu.make_translation(-2.5, BOARD_HEIGHT, -3.5+1*i))
            self.drawObjModel(viewToClipTfm, worldToViewTfm, blackPawnModelToWorldTransforms[i], self.models["blackPawnModels"][i])

        whiteBishopModelToWorldTransforms = []
        blackBishopModelToWorldTransforms = []
        whiteKnightModelToWorldTransforms = []
        blackKnightModelToWorldTransforms = []
        whiteRookModelToWorldTransforms = []
        blackRookModelToWorldTransforms = []
        for i in range(-1, 2, 2):
            whiteBishopModelToWorldTransforms.append(lu.make_translation(3.5, BOARD_HEIGHT, 1.5*i))
            self.drawObjModel(viewToClipTfm, worldToViewTfm, whiteBishopModelToWorldTransforms[i], self.models["whiteBishopModels"][i])

            blackBishopModelToWorldTransforms.append(lu.make_translation(-3.5, BOARD_HEIGHT, 1.5*i))
            self.drawObjModel(viewToClipTfm, worldToViewTfm, blackBishopModelToWorldTransforms[i], self.models["blackBishopModels"][i])

            whiteKnightModelToWorldTransforms.append(lu.make_translation(3.5, BOARD_HEIGHT, 2.5*i))
            self.drawObjModel(viewToClipTfm, worldToViewTfm, whiteKnightModelToWorldTransforms[i], self.models["whiteKnightModels"][i])

            blackKnightModelToWorldTransforms.append(lu.make_translation(-3.5, BOARD_HEIGHT, 2.5*i))
            self.drawObjModel(viewToClipTfm, worldToViewTfm, blackKnightModelToWorldTransforms[i], self.models["blackKnightModels"][i])

            whiteRookModelToWorldTransforms.append(lu.make_translation(3.5, BOARD_HEIGHT, 3.5*i))
            self.drawObjModel(viewToClipTfm, worldToViewTfm, whiteRookModelToWorldTransforms[i], self.models["whiteRookModels"][i])

            blackRookModelToWorldTransforms.append(lu.make_translation(-3.5, BOARD_HEIGHT, 3.5*i))
            self.drawObjModel(viewToClipTfm, worldToViewTfm, blackRookModelToWorldTransforms[i], self.models["blackRookModels"][i])

        highlightTransform = lu.make_translation(-3.5 + self.highlightOffset[0], BOARD_HEIGHT, 3.5-self.highlightOffset[1])
        self.drawObjModel(viewToClipTfm, worldToViewTfm, highlightTransform, self.models["highlight"])

    def drawObjModel(self, viewToClipTfm, worldToViewTfm, modelToWorldTfm, model):
        """Render a model in the world."""

        modelToViewTransform = worldToViewTfm * modelToWorldTfm
        
        # this is a special transform that ensures that normal vectors remain orthogonal to the 
        # surface they are supposed to be even in the prescence of non-uniform scaling.
        # It is a 3x3 matrix as vectors don't need translation anyway and this transform is only for vectors,
        # not points. If there is no non-uniform scaling this is just the same as Mat3(modelToViewTransform)
        modelToViewNormalTransform = lu.inverse(lu.transpose(lu.Mat3(modelToViewTransform)));

        # Bind the shader program such that we can set the uniforms (model.render sets it again)
        glUseProgram(self.shader)

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

        model.render(self.shader, ObjModel.RF_Opaque, transforms)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        model.render(self.shader, ObjModel.RF_Transparent| ObjModel.RF_AlphaTested, transforms)
        glDisable(GL_BLEND)

    def reLoadShader(self):        
        vertexShader = ""
        with open('vertexShader.glsl') as f:
            vertexShader = f.read()
        fragmentShader = ""
        with open(self.currentFragmentShaderName) as f:
            fragmentShader = f.read()

        if self.vertexShaderSource != vertexShader or fragmentShader != self.fragmentShaderSource:
            newShader = buildShader(vertexShader, fragmentShader)
            if newShader:
                if self.shader:
                    glDeleteProgram(self.shader)
                self.shader = newShader
                print("Reloaded shader, ok!")
            else:
                pass
            self.vertexShaderSource = vertexShader
            self.fragmentShaderSource = fragmentShader

    
    def update(self, dt, keys, mouseDelta):
        self.lighting.lightYaw += self.lighting.lightYawSpeed * dt
        self.lighting.lightPitch += self.lighting.lightPitchSpeed * dt

        self.highlightOffset[0] = (self.highlightOffset[0] + 1) % 8
        self.highlightOffset[1] = (self.highlightOffset[1] + 2) % 8

        self.reloadTimeout -= dt
        if self.reloadTimeout <= 0.0:
            self.reLoadShader();
            g_reloadTimeout = 1.0

        self.camera.camera.update(dt, keys, mouseDelta)

class Camera:
    def __init__(self):
        self.camera = lu.OrbitCamera([0,0,0], 10.0, -25.0, -35.0)
        self.yFovDeg = 45.0
        self.worldSpaceLightDirection = [-1, -1, -1]
        self.cameraDistance = 15.0
        self.cameraYaw = 270.0 #+ 180.0
        self.cameraPitch = 60.0
        self.lookTargetHeight = -1.0

class Lighting:
    def __init__(self):
        self.lightYaw = 25.0
        self.lightYawSpeed = 0.0
        self.lightPitch = -30.0
        self.lightPitchSpeed = 0.0
        self.lightDistance = 500.0
        self.lightColourAndIntensity = lu.vec3(0.9, 0.9, 0.6)
        self.ambientLightColourAndIntensity = lu.vec3(0.1)

def buildShader(vertexShaderSource, fragmentShaderSource):
    shader = lu.buildShader(vertexShaderSource, fragmentShaderSource, ObjModel.getDefaultAttributeBindings())
    if shader:
        glUseProgram(shader)
        ObjModel.setDefaultUniformBindings(shader)
        glUseProgram(0)
    return shader