import math
import numpy as np

class Vector:
    def __init__(self,i,j,k):
        self.i = i
        self.j = j
        self.k = k

    def magnitude(self):
        return math.sqrt(self.i**2 + self.j**2 + self.k**2)

    #Returns a new vector
    def add(self, vec):
        i = self.i + vec.i
        j = self.j + vec.j
        k = self.k + vec.k
        return Vector(i,j,k)

    # Modifies original vector
    def scale(self,scale):
        self.i *= scale
        self.j *= scale
        self.k *= scale

    def orthogonal(self,vec):
        a = [self.i, self.j, self.k]
        b = [vec.i, vec.j, vec.k]
        c = np.cross(a,b)
        return Vector(c[0], c[1], c[2])