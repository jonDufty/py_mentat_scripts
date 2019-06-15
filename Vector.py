import math
import numpy as np

class Vector:
    def __init__(self,i,j,k):
        self._vec = np.array([i,j,k], dtype='f')

    @property
    def vec(self):
        return self._vec

    def magnitude(self):
        return np.linalg.norm(self._vec)
    
    # Modifies original vector
    def scale(self,scale):
        self._vec *= scale

    # Move to Import Files
    def cross(self,vec):
        a = self._vec
        b = vec.vec
        return np.cross(a, b)
'''
    #Returns a new vector
    def add(self, vec):
        return self._vec + vec
'''