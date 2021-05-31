from OpenGL.GL import *
import math
import imgui

import glfw
import sys

import magic
# We import the 'lab_utils' module as 'lu' to save a bit of typing while still clearly marking where the code came from.
import Util as lu
from ObjModel import ObjModel

from Chess.View import View

WIDTH, HEIGHT = 1280, 800
WINDOW_TITLE = 'Chess'
# this is just a constant that was found through trial and error
# to find what height to draw the pieces at
BOARD_HEIGHT = 0.46

def itemListCombo(currentItem, items, name):
    ind = items.index(currentItem)
    _,ind = imgui.combo(name, ind, items)
    return items[ind]

def initGlFwAndResources(title, startWidth, startHeight, view):
    #glfw.window_hint(glfw.OPENGL_DEBUG_CONTEXT, 1)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.SRGB_CAPABLE, 1)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    #glfw.window_hint(glfw.SAMPLES, g_currentMsaaSamples)


    window = glfw.create_window(startWidth, startHeight, title, None, None)
    if not window:
        glfw.terminate()
        sys.exit(1)

    glfw.make_context_current(window)

    impl = magic.ImGuiGlfwRenderer(window)

    #glDebugMessageCallback(GLDEBUGPROC(debugMessageCallback), None)

    # (although this glEnable(GL_DEBUG_OUTPUT) should not have been needed when
    # using the GLUT_DEBUG flag above...)
    #glEnable(GL_DEBUG_OUTPUT)
    # This ensures that the callback is done in the context of the calling
    # function, which means it will be on the stack in the debugger, which makes it
    # a lot easier to figure out why it happened.
    #glEnable(GL_DEBUG_OUTPUT_SYNCHRONOUS)

    g_simpleShader = magic.buildBasicShader(
    """
    #version 330
    in vec3 positionIn;

    void main() 
    {
	    gl_Position = vec4(positionIn, 1.0);
    }
    """,
    """
    #version 330
    out vec4 fragmentColor;

    void main() 
    {
	    fragmentColor = vec4(1.0);
    }
    """);

    # Create Vertex array object and buffer with dummy data for now, we'll fill it later when rendering the frame
    (g_vertexDataBuffer, g_vertexArrayObject) = magic.createVertexArrayObject([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])

    glDisable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    #glEnable(GL_DEPTH_CLAMP)

    if view.initResources:
        view.initResources()

    g_coordinateSystemModel = None#ObjModel("data/coordinate_system.obj");

    return window,impl

def main():
    global g_mousePos
    global g_coordinateSystemModel
    global g_numMsaaSamples 
    global g_currentMsaaSamples

    view = View()

    if not glfw.init():
        sys.exit(1)

    window, impl = initGlFwAndResources(WINDOW_TITLE, WIDTH, HEIGHT, view)

    currentTime = glfw.get_time()
    prevMouseX,prevMouseY = glfw.get_cursor_pos(window)

    while not glfw.window_should_close(window):
        prevTime = currentTime
        currentTime = glfw.get_time()
        dt = currentTime - prevTime

        keyStateMap = {}
        for name,id in magic.g_glfwKeymap.items():
            keyStateMap[name] = glfw.get_key(window, id) == glfw.PRESS

        for name,id in magic.g_glfwMouseMap.items():
            keyStateMap[name] = glfw.get_mouse_button(window, id) == glfw.PRESS

        mouseX,mouseY = glfw.get_cursor_pos(window)
        g_mousePos = [mouseX,mouseY]
        
        # Udpate 'game logic'
        if view.update:
            imIo = imgui.get_io()
            mouseDelta = [mouseX - prevMouseX,mouseY - prevMouseY]
            if imIo.want_capture_mouse:
                mouseDelta = [0,0]
            view.update(dt, keyStateMap, mouseDelta)
        prevMouseX,prevMouseY = mouseX,mouseY

        width, height = glfw.get_framebuffer_size(window)
            
        view.renderFrame(0, width, height)
    
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()
        impl.process_inputs()

    glfw.terminate()

if __name__ == '__main__':
  main()