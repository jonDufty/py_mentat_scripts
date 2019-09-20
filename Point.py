#Point class
from Vector import Vector
import numpy as np

class Point:
    pt_id = 0
    
    def __init__(self, coord, normal, dir):
        self._id = self._gen_id()
        self.coord = coord
        self.normal = normal
        self.dir = dir

    def _gen_id(self):
        Point.pt_id += 1
        return Point.pt_id

    #Copies a point by translating by a given coordinate
    def copy_translate(self, v):
        c = self.coord.vec + v
        return c
    
    #Moves (no copy) a point by translating by a given coordinate
    def move_translate(self, v):
        new_v = self.coord.vec + v
        return Vector(new_v[0], new_v[1], new_v[2])

    # Creates new point for L/R offset
    def ortho_offset(self, offset):
        ortho = self.normal.cross(self.dir)
        ortho *= offset
        return self.copy_translate(ortho)

    # Moves (no copy) along the z-offset direction
    def z_offset(self, offset):
        print("offset z= ",offset)
        normal_vec = self.normal.vec*offset
        self.coord = self.move_translate(normal_vec)
''' 
    def send_coord(self):
        return " ".join([str(self.coord.i), str(self.coord.j), str(self.coord.k)])

'''

    