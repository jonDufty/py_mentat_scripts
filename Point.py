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

    #Copies a point by translating by a given coordinate
    def copy_translate(self, v):
        coord = self.coord + v
        return Point(coord, self.normal, self.dir)
    
    def move_translate(self, v):
        self.coord += v

    def ortho_offset(self, offset):
        if offset > 0:
            ortho = self.normal.cross(self.dir)
        elif offset < 0:
            ortho = self.dir.cross(self.normal)
        ortho.scale(abs(offset))
        return self.copy_translate(ortho)

    def z_offset(self, offset):
        normal_vec = self.normal.scale(offset)
        self.coord = self.coord.translate(normal_vec)

    def send_coord(self):
        return " ".join([str(self.coord.i), str(self.coord.j), str(self.coord.k)])


    