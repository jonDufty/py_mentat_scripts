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
    def copy(self, v):
        coord = self.coord.add(v)
        return Point(coord, self.normal, self.dir)

    def _ortho_offset(self, offset):
        if offset > 0:
            ortho = self.normal.orthogonal(self.dir)
        elif offset < 0:
            ortho = self.dir.orthogonal(self.normal)
        ortho.scale(abs(offset))
        return self.copy(ortho)

    def z_offset(self, offset):
        normal_vec = self.normal.scale(offset)
        self.coord = self.coord.translate(normal_vec)

    def send_coord(self):
        return " ".join([str(self.coord.i), str(self.coord.j), str(self.coord.k)])


    