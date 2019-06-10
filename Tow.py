#Joins points to create tow path
from Point import Point
from Vector import Vector
import numpy as np

class Tow():
    t_id = 0
    e_id = 1

    def __init__(self, tow_w, tow_t, num_el=10, el_size=1, points=[]):
        self._id = self._gen_id()
        self.points = points
        self.w = tow_w
        self.t = tow_t
        self.L = self._offset(self.w)   #Might remove later
        self.R = self._offset(-self.w)  #Might remove later
        self.num_el = num_el
        self.el_size = el_size          #Remove later most likely
        self._eid = self._gen_index()   #Keep for now, will probably remove later

    def _gen_id(self):
        Tow.t_id += 1
        return Tow.t_id
    
    def _gen_index(self):
        index = Tow.e_id
        Tow.e_id += self.num_el
        return index

    # Add point to tow **Don't calculate offset until interpolating
    def add_point(self, pt):
        if pt is None:
            return False
        else:
            self.points.append(pt)
            # self.L.append(pt.ortho_offset(self.w))
            # self.R.append(pt.ortho_offset(-self.w))
            return True

    #Take tow path and offset in both directions perpendicular to direction vector    
    def ortho_offset(self, w):
        for p in self.points:
            self.L.append(p.ortho_offset(w))
            self.R.append(p.ortho_offset(-w))
            
    # Calculate total length of the tow
    def length(self):
        l = 0
        for i in range(len(self.points)):
            dif = self.points[i+1].coord - self.points[i].coord
            l += dif.magnitude()
        return l
              
        