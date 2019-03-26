#Point class
from Vector import Vector

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

    def __str__(self):
        return(f"id = {self._id} x={self.coord.i}, y={self.coord.j}")

    #Copies a point by translating by a given coordinate
    def translate(self, v):
        x = self.coord.i + v.i
        y = self.coord.j + v.j
        z = self.coord.k + v.k
        return Point(Vector(x,y,z), self.normal, self.dir)

    def z_offset(self, offset):
        normal_vec = self.normal.scale_vec(offset)
        self.coord = self.coord.translate(normal_vec)


    