#Joins points to create tow path
from Point import Point
from Vector import Vector
import numpy as np
import Mesh
from trimesh import Trimesh
from geomdl import fitting as fit


class Tow():
    t_id = 0

    def __init__(self, tow_w, tow_t, z_off=0, ply=None):
        self._id = self._gen_id()
        self.points = []
        self.w = tow_w
        self.t = tow_t
        self.coords = [] #This is for the interpolated values
        self.new_pts = [[],[],[],[],[]] #Will eventually rename
        self.new_normals = []
        self.next_pts = []
        self.mesh = None

    def _gen_id(self):
        Tow.t_id += 1
        return Tow.t_id

    # Add point to tow
    def add_point(self, pt):
        if pt is None:
            return False
        else:
            self.points.append(pt)
            return True

    #Take tow path and offset in both directions perpendicular to direction vector
    # Points stored in 5xn array    
    def ortho_offset(self, w):
        for p in self.points:
            self.new_pts[0].append(p.ortho_offset(w))
            self.new_pts[1].append(p.ortho_offset(w/2))
            self.new_pts[2].append(p.coord)
            self.new_pts[3].append(p.ortho_offset(-w/2))
            self.new_pts[4].append(p.ortho_offset(-w))

    # After new z_array is calculated, offsets each point in tow based
    # on z_array value. Offsets in the direction of the normal vector
    # note: normals in new_normal are pointing down (which is the opposite direction to the original normals)
    def z_offset(self, z_array):
        for i in range(len(self.new_pts)):
            for j in range(len(self.new_normals)):
                offset = self.new_normals[j] * z_array[i][j]
                newpt = self.new_pts[i][j] - offset
                self.new_pts[i][j] -= offset
            
    # Calculate total length of the tow section
    # NOT USED ANYMORE
    def length(self):
        l = 0
        for i in range(len(self.points)-1):
            dif = self.points[i+1].coord - self.points[i].coord
            l += np.linalg.norm(dif)
        return l

    # Calculate new normal vectors for interpolated points based on 
    # the points in front and beside. Normals are facing down now
    # Assuming the normal is constant along transverse points
    def get_new_normals(self):
        normals = []
        vecs = self.new_pts[2]      #Centre points
        right = self.new_pts[1]     #Points to the right of centre 
        
        for i in range(len(vecs)-1):
            v1 = self.normalize(vecs[i+1] - vecs[i])    #Orientation vector
            v2 = self.normalize(right[i] - vecs[i])     #Transverse vector
            normals.append(np.cross(v1,v2).tolist())    #Generate normal vector as list (not numpy yet)
        
        # Append final points
        v1 = self.normalize(right[-1]-vecs[-1])
        v2 = self.normalize(vecs[-1]-vecs[-2])
        normals.append(np.cross(v2,v1).tolist())

        # Now convert into np array so that the form is nparray(n,3) instead of nested array
        self.new_normals = np.array(normals)
        return np.array(normals)

    # Convert into unit vector
    def normalize(self,v):
        norm = np.linalg.norm(v)
        if norm == 0:
            return v
        return v / norm 

    # Once interpolated, generate mesh to represent tow
    def generate_tow_mesh(self):
        mesh = Trimesh()
        pts = np.array(self.new_pts)
        for i in range(len(self.new_pts[0])-1):
            v1 = self.new_pts[0][i]
            v2 = self.new_pts[0][i+1]
            v3 = self.new_pts[-1][i+1]
            v4 = self.new_pts[-1][i]

        # Form mesh square from 4 coordinates
        mesh_segment = Trimesh(vertices=[v1,v2,v3,v4], faces = [[0,1,2,3]])
        # Add segment to overall tow mesh
        mesh = mesh.__add__(mesh_segment)
        mesh = mesh.invert()

        self.mesh = mesh

    
    def adjust_mesh_edges(self, z_array):
        pass

    def projection_origins(self, edge_tolerance=0.3):
        dist = 3 + self._id
        copy = np.array(self.new_pts)
        offsets = self.new_normals*dist
        origins = np.empty_like(copy)
        for i in range(len(copy)):
            origins[i][:] = copy[i][:] + offsets

        # adjust origins to avoid cases
        # origins = self.projection_edge_tolerance(origins, edge_tolerance)
        
        return origins 

    
    """ 
    Adjust outside points to miss edge contacts within tolerance
    """
    def projection_edge_tolerance(self, origins, tolerance):
        outer_r = origins[0]
        outer_l = origins[-1]
        
        offset = origins[1] - origins[0]
        offset_unit = np.array([self.normalize(v) for v in offset])
        origins[0] += offset_unit*tolerance

        offset = origins[-2] - origins[-1]
        offset_unit = np.array([self.normalize(v) for v in offset])
        origins[-1] += offset_unit*tolerance

        return origins





        