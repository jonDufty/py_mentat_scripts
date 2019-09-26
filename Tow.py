#Joins points to create tow path
from Point import Point
from Vector import Vector
import numpy as np

class Tow():
    t_id = 0

    def __init__(self, tow_w, tow_t, z_off=0, ply=None):
        self._id = self._gen_id()
        self.points = []
        self.w = tow_w
        self.t = tow_t
        self.L = [] #self._offset(self.w)
        self.R = [] #self._offset(-self.w)
        self.z = z_off #TO REMOVE
        self.ply = ply #TO REMOVE

    def _gen_id(self):
        Tow.t_id += 1
        return Tow.t_id

    # Add point to tow **Don't calculate offset until interpolating
    def add_point(self, pt):
        if pt is None:
            return False
        else:
            self.points.append(pt)
            return True

    #Take tow path and offset in both directions perpendicular to direction vector    
    def ortho_offset(self, w):
        for p in self.points:
            self.L.append(p.ortho_offset(w))
            self.R.append(p.ortho_offset(-w))

    def z_offset(self, arr=None):
        if arr:
            for i in range(len(arr)):
                print(self.points[i].coord)
                self.points[i].z_offset(arr[i]*self.t)
        else:
            for p in self.points:
                p.z_offset(self.t*self.z)
            
    # Calculate total length of the tow
    def length(self):
        l = 0
        for i in range(len(self.points)-1):
            dif = self.points[i+1].coord - self.points[i].coord
            l += np.linalg.norm(dif)
        return l
              
        