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
        self.L_in = [] 
        self.L_out = [] 
        self.R_in = []
        self.R_out = [] 
        self.new_pts = [[],[],[],[],[]]
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

    def z_offset(self, arr=None):
        if arr:
            for i in range(len(arr)):
                print(self.points[i].coord)
                self.points[i].z_offset(arr[i]*self.t)
        else:
            for p in self.points:
                p.z_offset(self.t*self.z)
            
    # Calculate total length of the tow section
    def length(self):
        l = 0
        for i in range(len(self.points)-1):
            dif = self.points[i+1].coord - self.points[i].coord
            l += np.linalg.norm(dif)
        return l

    def get_new_normals(self):
        normals = []
        vecs = self.new_pts[2]
        right = self.new_pts[1]
        for i in range(len(vecs)-1):
            v1 = vecs[i+1] - vecs[i]
            v1 /= np.linalg.norm(v1)
            v2 = right[i] - vecs[i]
            v2 /= np.linalg.norm(v2)
            normals.append(np.cross(v2,v1).tolist())
        normals.append(np.cross((right[-1]-vecs[-1]), (vecs[-1]-vecs[-2])).tolist())
        return np.array(normals)

    '''
    def interpolate_points(self, avg_dist, batch_sz):
        length = self.length()
        n_divisions = int(length/avg_dist)
        delta = (1/n_divisions)

        # batch coordinate string to manageable interp size
        new_pts = np.empty()
        i = 0
        while(i < len(self.points)):
            if (i+batch_sz) > len(self.points):
            batch = self.points[i:i+batch_sz]


        

        if len(coords) <= 2:
            order = 1
        elif len(coords) == 3:
            order = 2
        else:
            order = 3

    '''
              
        