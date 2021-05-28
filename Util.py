from OpenGL.GL import glUniformMatrix3fv, glUniformMatrix4fv, GL_TRUE
import numpy as np
import math



class Mat4:
    matData = None
    # Construct a Mat4 from a python array
    def __init__(self, p = [[1,0,0,0],
                            [0,1,0,0],
                            [0,0,1,0],
                            [0,0,0,1]]):
        if isinstance(p, Mat3):
            self.matData = np.matrix(np.identity(4))
            self.matData[:3,:3] = p.matData
        else:
            self.matData = np.matrix(p)

    # overload the multiplication operator to enable sane looking transformation expressions!
    def __mul__(self, other):
        # if it is a list, we let numpy attempt to convert the data
        # we then return it as a list also (the typical use case is 
        # for transforming a vector). Could be made more robust...
        if isinstance(other, list):
            return list(self.matData.dot(other).flat)
        # Otherwise we assume it is another Mat4 or something compatible, and just multiply the matrices
        # and return the result as a new Mat4
        return Mat4(self.matData.dot(other.matData))
    
    # Helper to get data as a contiguous array for upload to OpenGL
    def getData(self):
        return np.ascontiguousarray(self.matData, dtype=np.float32)

    # note: returns an inverted copy, does not change the object (for clarity use the global function instead)
    #       only implemented as a member to make it easy to overload based on matrix class (i.e. 3x3 or 4x4)
    def _inverse(self):
        return Mat4(np.linalg.inv(self.matData))

    def _transpose(self):
        return Mat4(self.matData.T)

    def _set_open_gl_uniform(self, loc):
        glUniformMatrix4fv(loc, 1, GL_TRUE, self.getData())



class Mat3:
    matData = None
    # Construct a Mat4 from a python array
    def __init__(self, p = [[1,0,0],
                            [0,1,0],
                            [0,0,1]]):
        if isinstance(p, Mat4):
            self.matData = p.matData[:3,:3]
        else:
            self.matData = np.matrix(p)

    # overload the multiplication operator to enable sane looking transformation expressions!
    def __mul__(self, other):
        # if it is a list, we let numpy attempt to convert the data
        # we then return it as a list also (the typical use case is 
        # for transforming a vector). Could be made more robust...
        if isinstance(other, list):
            return list(self.matData.dot(other).flat)
        # Otherwise we assume it is another Mat3 or something compatible, and just multiply the matrices
        # and return the result as a new Mat3
        return Mat3(self.matData.dot(other.matData))
    
    # Helper to get data as a contiguous array for upload to OpenGL
    def getData(self):
        return np.ascontiguousarray(self.matData, dtype=np.float32)

    # note: returns an inverted copy, does not change the object (for clarity use the global function instead)
    #       only implemented as a member to make it easy to overload based on matrix class (i.e. 3x3 or 4x4)
    def _inverse(self):
        return Mat3(np.linalg.inv(self.matData))

    def _transpose(self):
        return Mat3(self.matData.T)

    def _set_open_gl_uniform(self, loc):
        glUniformMatrix3fv(loc, 1, GL_TRUE, self.getData())


#
# matrix consruction functions
#

def make_translation(x, y, z):
    return Mat4([[1,0,0,x],
                 [0,1,0,y],
                 [0,0,1,z],
                 [0,0,0,1]])


def make_translation(x, y, z):
    return Mat4([[1,0,0,x],
                 [0,1,0,y],
                 [0,0,1,z],
                 [0,0,0,1]])

 
def make_scale(x, y, z):
    return Mat4([[x,0,0,0],
                 [0,y,0,0],
                 [0,0,z,0],
                 [0,0,0,1]])


def make_rotation_y(angle):
    return Mat4([[math.cos(angle), 0, -math.sin(angle),0],
                 [0,1,0,0],
                 [math.sin(angle),0, math.cos(angle),0],
                 [0,0,0,1]])


def make_rotation_x(angle):
    return Mat4([[1,0,0,0],
                 [0, math.cos(angle), -math.sin(angle),0],
                 [0, math.sin(angle), math.cos(angle),0],
                 [0,0,0,1]])


def make_rotation_z(angle):
    return Mat4([[math.cos(angle),-math.sin(angle),0,0],
                 [math.sin(angle),math.cos(angle),0,0],
                 [0,0,1,0],
                 [0,0,0,1]])


# 
# Matrix operations
#

# note: returns an inverted copy, does not change the object (for clarity use the global function instead)
def inverse(mat):
    return mat._inverse()

def transpose(mat):
    return mat._transpose()



#
# vector operations
#

def normalize(v):
    norm = np.linalg.norm(v)
    return v / norm
