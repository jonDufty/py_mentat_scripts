#Joins points to create tow path
from Point import Point
from Vector import Vector
import numpy as np
import Mesh
from trimesh import Trimesh
from geomdl import fitting as fit


class Tow():
    """
    Class for representing tow obects
    
    Attributes
    -------
    _id : int
        Tow id
    points : list(Point)
        Original point/vector data
    w : float
        Tow width (actually entered as w/2)
    t : float
        Tow thickness
    new_pts : np.array(5,n,3)
        Initially empty - used to contain all the updated/adjusted tow points
        after interpolation/offsetting
    new_normals : np.array(5,n,3)
        Array of normal vectors associated with new_pts
    trimmed points : dict{start,middle,end}\
        Contains trimmed points where start/end contain rows of points with points partially
        out of bounds, and middle contains points entirely inbounds
    prev_pts : np.array(5,n,3)
        stored points before interpolation in case of excpetion thrown in Mesh.py
    pid : int
        index of parent ply class
    proj_dist : float
        default distance to project tow points above base_mesh by
    interp_dist : float
        default distance to interpoalte between the tow poits
    """
    t_id = 0

    def __init__(self, tow_w, tow_t, pid):
        self._id = self._gen_id()
        self.points = []
        self.w = tow_w
        self.t = tow_t
        self.coords = [] 
        self.new_pts = [[],[],[],[],[]]
        self.new_normals = []
        self.trimmed_pts = {"start":[], "middle":[], "end":[]}
        self.prev_pts = []
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

    def add_point(self, pt):
        """Add a point to a tow
        
        Parameters
        ----------
        pt : Point
            point to add
        
        Returns
        -------
        boolean
            point was succesfully added or not
        """
        if pt is None:
            return False
        else:
            self.points.append(pt)
            return True

      
    def ortho_offset(self, w):
        """Take tow path and offset in both directions perpendicular to direction vector
        Points stored in 5xn array  
        
        Parameters
        ----------
        w : float
            width of outer boundary to offset by
        """

        for p in self.points:
            self.new_pts[0].append(p.ortho_offset(w))
            self.new_pts[1].append(p.ortho_offset(w/2))
            self.new_pts[2].append(p.coord)
            self.new_pts[3].append(p.ortho_offset(-w/2))
            self.new_pts[4].append(p.ortho_offset(-w))


    def get_inner_points(self):
        """Returns only inner points, excluding edge points
        
        Returns
        -------
        np.array(3,n-2,3)
            inner points array
        """
        return self.new_pts[1:-2][1:-2]

    def get_inner_normals(self):
        """returns normals associated with inner points
        
        Returns
        -------
        np.array(3,n-2,3)
            normal vector array
        """
        return self.new_normals[1:-2]
    
    
    def get_new_normals(self):
        """
        Calculate new normal vectors for interpolated points based on 
        the points in front and beside. Normals are facing down now
        Assuming the normal is constant along transverse points
        """

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
        """Convert into a unit vector
        
        Parameters
        ----------
        v : np.array(3,1)
            vector to convert
        
        Returns
        -------
        np.array(3,1)
            adjsuted vector
        """
        norm = np.linalg.norm(v)
        if norm == 0:
            return v
        return v / norm 

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

    
    def interpolate_tow_points(self, target=None):
        """Takes in array of points, and interpolates in between them using geomdl package
        Interpoaltes to a level such that the distance between points is roughly equal to 
        $target_length (by default is t.w/2). Interpolates in batches, as large arrays can cause errors
        
        Parameters
        ----------
        target : float, optional
            target distance for point spacing, by default None
        
        """
        
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




        