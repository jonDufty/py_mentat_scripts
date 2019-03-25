import math

class Vector:
    def __init__(self,i,j,k):
        self.i = i
        self.j = j
        self.k = k

    def magnitude(self):
        return math.sqrt(self.i**2 + self.j**2 + self.k**2)

    def add_vec(self, vec):
        self.i += vec.i
        self.j += vec.j
        self.k += vec.k

    def scale_vec(self,scale):
        self.i *= scale
        self.j *= scale
        self.k *= scale