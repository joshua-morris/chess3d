from OpenGL.GL import *
import imgui

import glfw
import sys

import magic

from Chess.View import initGlFwAndResources, View, WIDTH, HEIGHT, WINDOW_TITLE
from Chess.Model import Game

def main():
    view = View()
    game = Game()

    if not glfw.init():
        sys.exit(1)

    window, impl = initGlFwAndResources(WINDOW_TITLE, WIDTH, HEIGHT, view)

    currentTime = glfw.get_time()
    prevMouseX,prevMouseY = glfw.get_cursor_pos(window)

    hasClicked = False
    while not glfw.window_should_close(window):
        prevTime = currentTime
        currentTime = glfw.get_time()
        dt = currentTime - prevTime

        keyStateMap = {}
        for name,id in magic.g_glfwKeymap.items():
            keyStateMap[name] = glfw.get_key(window, id) == glfw.PRESS

        for name,id in magic.g_glfwMouseMap.items():
            keyStateMap[name] = glfw.get_mouse_button(window, id) == glfw.PRESS

        if keyStateMap["MOUSE_BUTTON_LEFT"]:
            hasClicked ^= True

        mouseX,mouseY = glfw.get_cursor_pos(window)
        view.mousePos = [mouseX,mouseY]
        
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
        view.highlightPosition(mouseX, mouseY)
        glfw.swap_buffers(window)
        # Poll for and process events
        glfw.poll_events()
        impl.process_inputs()

    glfw.terminate()

if __name__ == '__main__':
  main()