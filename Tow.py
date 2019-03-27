#Joins points to create tow path
from Point import Point
from Vector import Vector

class Tow():
    t_id = 0
    e_id = 1

    def __init__(self, tow_w, tow_t, num_el=10, points=[]):
        self._id = self._gen_id()
        self.points = points
        self.w = tow_w
        self.t = tow_t
        self.L = self._offset(self.w)
        self.R = self._offset(-self.w)
        self.num_el = num_el
        self._eid = self._gen_index()


    def _gen_id(self):
        Tow.t_id += 1
        return Tow.t_id
    
    def _gen_index(self):
        index = Tow.e_id
        Tow.e_id += self.num_el
        return index

    def name(self):
        return "".join(['tow', str(self._id)])

    def add_point(self, point):
        if point is None:
            return False
        else:
            self.points.append(point)
            self.L.append(point._ortho_offset(self.w))
            self.R.append(point._ortho_offset(-self.w))
            return True

    def length(self):
        for i in range(self.points-1):
            x = self.points[i+1].coord.x - self.points[i].coord.x
            y = self.points[i+1].coord.y - self.points[i].coord.y
            z = self.points[i+1].coord.z - self.points[i].coord.z
            vec = Vector(x,y,z)
            return vec.magnitude()

    #Take tow path and offset in both directions perpendicular to direction vector    
    def _offset(self, w):
        off = []
        for point in self.points:
            off.append(point._ortho_offset(w))
        return off

    # def create_surface(self):

            
              
        