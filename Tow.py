#Joins points to create tow path
from Point import Point
from Vector import Vector
import numpy as np
from geomdl import fitting as fit

class Tow():
    t_id = 0

    def __init__(self, tow_w, tow_t, z_off=0, ply=None):
        self._id = self._gen_id()
        self.points = []
        self.w = tow_w
        self.t = tow_t
        self.coords = [] #This is for the interpolated values
        self.L_in = [] #TO REMOVE
        self.L_out = [] #TO REMOVE
        self.R_in = []#TO REMOVE
        self.R_out = [] #TO REMOVE
        self.new_pts = [[],[],[],[],[]]
        self.new_normals = []
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
            self.new_pts[0].append(p.ortho_offset(w))
            self.new_pts[1].append(p.ortho_offset(w/2))
            self.new_pts[2].append(p.coord)
            self.new_pts[3].append(p.ortho_offset(-w/2))
            self.new_pts[4].append(p.ortho_offset(-w))

    # After new z_array is calculated, offsets each point in tow based
    # on z_array value
    def z_offset(self, z_array):
        for i in range(len(self.new_pts)):
            for j in range(len(self.new_normals)):
                offset = self.new_normals[j] * z_array[i][j]
                self.new_pts[i][:] -= offset
            
    # Calculate total length of the tow section
    def length(self):
        l = 0
        for i in range(len(self.points)-1):
            dif = self.points[i+1].coord - self.points[i].coord
            l += np.linalg.norm(dif)
        return l

    # Calculate new normal vectors for internal points based on 
    # the points in front and beside. Normals are facing down now
    def get_new_normals(self):
        normals = []
        vecs = self.new_pts[2]
        right = self.new_pts[1]
        for i in range(len(vecs)-1):
            v1 = self.normalize(vecs[i+1] - vecs[i])
            v2 = self.normalize(right[i] - vecs[i])
            normals.append(np.cross(v2,v1).tolist())
        v1 = self.normalize(right[-1]-vecs[-1])
        v2 = self.normalize(vecs[-1]-vecs[-2])
        normals.append(np.cross(v2,v1).tolist())
        self.new_normals = np.array(normals)
        return np.array(normals)

    def normalize(self,v):
        norm = np.linalg.norm(v)
        if norm == 0:
            return v
        return v / norm          
        