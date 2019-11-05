#Joins points to create tow path
from Point import Point
from Vector import Vector
import numpy as np
import Mesh
from trimesh import Trimesh
from geomdl import fitting as fit


class Tow():
    t_id = 0

    def __init__(self, tow_w, tow_t, pid):
        self._id = self._gen_id()
        self.points = []
        self.w = tow_w
        self.t = tow_t
        self.coords = [] #This is for the interpolated values
        self.new_pts = [[],[],[],[],[]] #Will eventually rename
        self.new_normals = []
        self.prev_pts = []
        self.mesh = None
        self.pid = pid
        self.proj_dist = 5*pid
        self.interp_dist = tow_w/2 

    def __repr__(self):
        return repr("tow" + str(self._id))

    def _gen_id(self):
        Tow.t_id += 1
        return Tow.t_id

    def _dec_id():
        Tow.t_id -= 1

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
            
    def get_inner_points(self):
        return self.new_pts[1:-2][1:-2]

    def get_inner_normals(self):
        return self.new_normals[1:-2]
    
    # Calculate new normal vectors for interpolated points based on 
    # the points in front and beside. Normals are facing down now
    # Assuming the normal is constant along transverse points
    def get_new_normals(self):
        normals = [[],[],[],[],[]]
        for i in range(len(self.new_pts)-1):
            vecs = self.new_pts[i]      #current row
            right = self.new_pts[i+1]   #next row
            for j in range(len(vecs) -1):
                v1 = self.normalize(vecs[j+1] - vecs[j])    #Orientation vector
                v2 = self.normalize(right[j] - vecs[j])     #Transverse vector
                normals[i].append(np.cross(v2,v1).tolist()) #Normal vector as list(not np)
            #Append Final point
            v1 = self.normalize(vecs[-1] - vecs[-2])
            v2 = self.normalize(right[-1] - vecs[-1])
            normals[i].append(np.cross(v2,v1).tolist())

        # Append final row
        vecs = self.new_pts[-1]
        left = self.new_pts[-2]
        for j in range(len(vecs) -1):
            v1 = self.normalize(vecs[j+1] - vecs[j])
            v2 = self.normalize(vecs[j] - left[j])
            normals[-1].append(np.cross(v2,v1).tolist())
        # Append final point
        v1 = self.normalize(vecs[-1] - vecs[-2])
        v2 = self.normalize(vecs[-1] - left[-1])
        normals[-1].append(np.cross(v2, v1).tolist())
        self.new_normals = np.array(normals)
        return


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

    # Create origins well above base mesh to avoid intersections
    # Inner --> determine whether to return only inner points or all points
    def projection_origins(self):
        normals = self.new_normals
        offset_dist = normals * self.proj_dist

        return self.new_pts + offset_dist
    
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

    
    """  
    Interpolate longitudinally along tow. Makes points as close to evenly spaced
    as possible.
    Target length is 0.25*tow_width
    """
    def interpolate_tow_points(self, target=None):
        self.prev_pts = self.new_pts

        if target:
            target_length = target #w/4
        else:
            target_length = self.interp_dist
        n_pts = len(self.new_pts[2])
        points = np.copy(self.new_pts)
        
        # Batch up sections for large tows
        batch = []
        batch_combine = [[],[],[],[],[]]
    
        i = 0
        batch_sz = 200
        while(i + batch_sz < n_pts):
            tmp = points[:,i:i+batch_sz]
            batch.append(points[:,i:i+batch_sz])
            i += batch_sz -1
        batch.append(points[:,i:])

        for b in batch:
            if len(b[2]) <= 2:      # If only two points - linear interpolation
                order = 1
            elif len(b[2]) == 3:    # If 3 poits - quadratic interpolation
                order = 2
            else:                   # if > 3 pts - cubic interpolation
                order = 3

            # Get length of batch curve. Use middle line as basis
            v1s = np.array(b[2][1:])
            v2s = np.array(b[2][:-1])
            diff = v2s - v1s
            lengths = [np.linalg.norm(x) for x in diff]
            length = sum([np.linalg.norm(x) for x in diff]) #Get total length of distances between each point
        
            # Delta dictates how many 'evenly' spaced points the interpolation funciton will output.
            # Roughly equal to 1/n_points-1 - (e.g. delta = 0.01 --> 1/100 --> 101 points).
            # Delta must be < 1, so min() statement is too ensure this (bit hacky atm)
            delta = min(target_length/length,0.99) 
        
            # call the interpolate curve function
            for j in range(len(b)):
                curve = fit.interpolate_curve(b[j].tolist(),order)
                curve.delta = delta
                evalpts = curve.evalpts         #evalpts is the new list of interpolated points
                batch_combine[j] += evalpts     #stich batches back together as created
        
        # Recheck new lengths for debugging
        v1s = np.array(batch_combine[2][1:])
        v2s = np.array(batch_combine[2][:-1])
        diff = v2s - v1s
        lengths = [np.linalg.norm(x) for x in diff]
        
        # Evalpts is of type list, need to return as numpy array
        self.new_pts = np.array(batch_combine)

    def batch_tow(self, batch_size = 200):
        n_points = len(self.new_normals)
        i = 0
        tows = []
        while(i+batch_size < n_points):
            pts = self.new_pts[:,i:i+batch_size]




        