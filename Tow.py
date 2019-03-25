#Joins points to create tow path
from Point import Point
from Vector import Vector

class Tow():
    t_id = 0
    e_id = 1

    def __init__(self, tow_w, tow_t, num_el):
        self._id = self._gen_id()
        self.points = []
        self.w = tow_w
        self.t = tow_t
        self.num_el = num_el
        self._el_index = self._gen_index()

    def _gen_id(self):
        Tow.t_id += 1
        return Tow.t_id
    
    def _gen_index(self):
        index = Tow.e_id
        Tow.e_id += self.num_el
        return index

    def add_point(self, point):
        if point is None:
            return False
        else:
            self.points.append(point)
            return True

    def length(self):
        for i in range(self.points-1):
            x = self.points[i+1].coord.x - self.points[i].coord.x
            y = self.points[i+1].coord.y - self.points[i].coord.y
            z = self.points[i+1].coord.z - self.points[i].coord.z
            vec = Vector(x,y,z)
            return vec.magnitude()

    #Take tow path and offset in both directions perpendicular to direction vector
    def offset_points(self):
        x = []
        y = []
        for p in self.points:
            off_x = p.offset_pt_x
            off_x.scale(self.w)
            off_y = p.offset_pt_y
            off_y.scale(self.w)
            x.append(p.translate(off_x))
            y.append(p.translate(off_y))
        return [x,y]

    # def create_surface(self):


            
              
        