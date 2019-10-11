import trimesh
from trimesh import Trimesh, visual
import numpy as np

""" 
Wrapper class for trimesh with custom functions and bookeeping of global mesh
"""
class Mesh():
    def __init__(self, mesh):
        self.mesh = mesh                #the Trimesh object
        self._z_off = self.__init_z()   #Array the same size as faces, keeping track of z-offsets

    def __init_z(self):
        return np.array([0]*len(self.mesh.faces)) #I know this is ugly but I had to force it to zero out

    @property
    def z_off(self):
        return self._z_off

    # Increments z offset mesh at faces index (can parse in array)
    def inc_z_off(self, index):
        self._z_off[index] += 1

    # Retrospectively adjusts the z_offset based on offset_rule
    def adjust_z_off(self, index, array):
        for i in range(len(index)):
            self._z_off[index[i]] = array[i]

    # debugging plot for visualing intersecting faces
    def visual(self, faces_to_colour, vector_origins = [], vector_normals=[], scale=2.0):
        # unmerge so viewer doesn't smooth
        self.mesh.unmerge_vertices()
        # make base_mesh white- ish
        self.mesh.visual.face_colors = [255,255,255,255]
        self.mesh.visual.face_colors[faces_to_colour] = [255, 0, 0, 255]
        
        if vector_origins != [] and vector_normals != []:
            # stack rays into line segments for visualization as Path3D
            ray_visualize = trimesh.load_path(np.hstack((vector_origins, vector_origins + vector_normals*scale)).reshape(-1, 2, 3))
            scene = trimesh.Scene([self.mesh, ray_visualize])
        else:
            scene = trimesh.Scene([self.mesh])
        scene.show()

"""  
Creates mesh from tow coordinates to use for z offset projection
Iterates through points and forms segments from outer points
Return: mesh object
"""
def tow_mesh(t):
    vertices = []
    mesh = Trimesh()
    for i in range(len(t.new_pts[0])-1):
        v1 = t.new_pts[0][i]
        v2 = t.new_pts[0][i+1]
        v3 = t.new_pts[-1][i+1]
        v4 = t.new_pts[-1][i]

        # Form mesh square from 4 coordinates
        mesh_segment = Trimesh(vertices=[v1,v2,v3,v4], faces = [[0,1,2,3]])
        # Add segment to overall tow mesh
        mesh = mesh.__add__(mesh_segment)
    return mesh


""" 
Projects down from tow points using vectors from FPM data
onto base mesh using similar method to project up
returns:    array mapping z_offset values to tow points
            array mapping base_mesh faces to z_offset array
"""
def project_down(base_mesh, t):
    normals = t.new_normals
    tow_z_array = np.array([[0]*len(normals)]*5)
    face_z_index = np.array([[-1]*len(normals)]*5)
    for i in range(len(t.new_pts)):
        tow_origins = t.new_pts[i][:]
        print("Before")
        print(base_mesh.mesh.vertices[base_mesh.mesh.faces[0]])
        locations, vec_index, tri_index = base_mesh.mesh.ray.intersects_location(tow_origins, normals, multiple_hits=False)
        print("After")
        print(base_mesh.mesh.vertices[base_mesh.mesh.faces[0]])
        hits = base_mesh.z_off[tri_index]
        # tow_z_array.append(base_mesh.z_off[tri_index])
        tow_z_array[i][vec_index] = base_mesh.z_off[tri_index]
        # face_z_index.append(tri_index.copy())
        face_z_index[i][vec_index] = tri_index.copy()

        '''for j in range(len(vec_index)):
            t.new_pts[i][vec_index[j]] -= normals[i]*base_mesh.z_off[tri_index[j]]
            pass'''
    return tow_z_array, face_z_index
        

"""
Checks each offset with neighbouring points to determine whether to include
it or not.
Returns index of array entries that were modified from the rul
"""
def offset_rule(base_mesh, z_array, face_index):
    length = len(z_array[0])
    width = len(z_array)
    z_initial = z_array.copy()
    # Start with top row - index [0]
    z_array[0][[0,-1]] = z_array[1][[1,-2]] # corner pts first
    z_array[0][1:-2] = z_array[1][1:-2] #remaining top row

    # bottom edge
    z_array[-1][[0,-1]] = z_array[-2][[1,-2]] # corner pts first
    z_array[-1][1:-2] = z_array[-2][1:-2] #remaining pts

    #side edges
    z_array[1:-2][0] = z_array[1:-2][1] #left edge
    z_array[1:-2][-1] = z_array[1:-2][-2] #left edge

    # remaining points - can't use indexing so have to iterrate
    for i in range(width -1):
        j = 0
        for j in range(length - 1):
            top = z_array[i-1][j]
            bot = z_array[i+1][j]
            left = z_array[i][j-1]
            right = z_array[i][j+1]
            if j == 2: #middle row
                z_array[i][j] = max(top,bot,left,right)
            elif j ==1:
                z_array[i][j] = max(bot,left,right)
            else:
                z_array[i][j] = max(top,left,right)
    return    


"""
Checks the face normals projected up towards the tows
Utilises trimesh intersects_location ray tracing. Only detects first hit
returns: List of indexes for base_mesh faces that lie beneath tow
"""
def project_up(base_mesh, tow_mesh):

    mesh = base_mesh.mesh
    base_vectors = mesh.face_normals        #ray vectors
    base_origins = mesh.triangles_center    #ray origins - centroids of mesh faces
    locations, vec_index, tri_index = tow_mesh.ray.intersects_location(base_origins, base_vectors, multiple_hits=False)

    # Increment the z-offset value if the faces lie underneath a tow, this is refined later
    base_mesh.inc_z_off(vec_index)
    return vec_index
            
"""  
Finds index's of faces adjacent to $face
Possible REMOVE
"""      
def adjacent(mesh,face):
    faces = []
    for a in list(mesh.face_adjacency):
        if face in a:
            faces.append(a[a!=face][0])
    return np.array(faces)


"""  
Given a mesh, it uses subdivide() method iteratively until the minimum
mesh size is less than $min_length.
**Currently not used in main script but for mesh generation
"""
def subdivide_it(mesh, min_length):
        new_mesh = mesh
        while(min(new_mesh.edges_unique_length) > min_length):
            print(f"length = {min(new_mesh.edges_unique_length)} ... subdividing...") #debug print
            new_mesh = new_mesh.subdivide()
        return new_mesh


"""  
Most likely will REMOVE this
"""
def intersect_ray(coord, ray, vertices):
    """ 
    Implementation of Moller-trombore ray
    intersection algorithm.
    Inputs: Coord - location of ray
            Ray - direction vector of ray
            Vertices - 1x3 array of 3 vertices of triangle
    """
    # Find vectors 
    e1 = vertices[1] - vertices[0]
    e2 = vertices[2] - vertices[0]
    t_vec = coord - vertices[0]

    eps = 0.00001

    # Calculate P to determine if ray is parallel to face
    p = np.cross(ray, e2)
    det = np.dot(e1, p)
    inv_det = 1.0/det

    # If parallel then return early
    if abs(det) < eps:
        return False

    u = np.dot(t_vec,p)
    u *= inv_det

    # Check bounds of u
    if u < 0. or u > 1.:
        return False

    Q = np.cross(t_vec,e1)
    v = np.dot(ray,Q)
    v *= inv_det

    # Check bounds of v
    if v < 0.:
        return False
    elif u + v > 1.:
        return False

    # Calculate t and scale
    t = np.dot(e2, Q)
    t *= inv_det

    return True
