import trimesh
from trimesh import Trimesh, visual
import numpy as np

""" 
Wrapper class for trimesh with custom functions and bookeeping of global mesh
"""
class Mesh():
    def __init__(self, mesh):
        self.mesh = mesh
        self._z_off = self.__init_z()

    def __init_z(self):
        return np.empty(len(self.mesh.faces),dtype='int32')

    @property
    def z_off(self):
        return self._z_off

    def inc_z_off(self, index):
        self._z_off[index] += 1

    def adjust_z_off(self, index, array):
        index = index.flatten()
        index = index.astype('int32')
        print(index.max())
        self._z_off[index.flatten()] = array.flatten()

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


def tow_mesh(t):
    vertices = []
    mesh = Trimesh()
    for i in range(len(t.new_pts[0])-1):
        v1 = t.new_pts[0][i]
        v2 = t.new_pts[0][i+1]
        v3 = t.new_pts[-1][i+1]
        v4 = t.new_pts[-1][i]
        mesh_segment = Trimesh(vertices=[v1,v2,v3,v4], faces = [[0,1,2,3]])
        mesh = mesh.__add__(mesh_segment)
    return mesh




""" 
Projects down from tow points using vectors from FPM data
onto base mesh using similar method to project up
"""
def project_down(base_mesh, t):
    normals = t.new_normals
    tow_z_array = np.empty((5,len(normals))).astype('int32')
    face_z_index = np.empty((5,len(normals))).astype('int32')
    face_z_index_flat = face_z_index.flatten().astype('int32')
    for i in range(len(t.new_pts)):
        tow_origins = t.new_pts[i][:]
        locations, vec_index, tri_index = base_mesh.mesh.ray.intersects_location(tow_origins, normals, multiple_hits=False)
        hits = base_mesh.z_off[tri_index]
        tow_z_array[i][vec_index] = base_mesh.z_off[tri_index]
        face_z_index[i][vec_index] = tri_index.copy()
        face_z_index_flat[i*len(normals) + vec_index] = tri_index

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
Performs Breadth-first search based on adjacent faces
"""
def project_up(base_mesh, tow_mesh):

    mesh = base_mesh.mesh
    base_vectors = mesh.face_normals
    base_origins = mesh.triangles_center
    locations, vec_index, tri_index = tow_mesh.ray.intersects_location(base_origins, base_vectors, multiple_hits=False)

    base_mesh.inc_z_off(vec_index)
    return vec_index
            
            
def adjacent(mesh,face):
    faces = []
    for a in list(mesh.face_adjacency):
        if face in a:
            faces.append(a[a!=face][0])
    return np.array(faces)

def subdivide_it(mesh, min_length):
        new_mesh = mesh
        while(min(new_mesh.edges_unique_length) > min_length):
            print(f"length = {min(new_mesh.edges_unique_length)} ... subdividing...")
            new_mesh = new_mesh.subdivide()
            print(len(new_mesh.faces))
        return new_mesh

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
'''     
def spare_project():
    mesh = base_mesh.mesh
    base_vectors = mesh.face_normals
    tow_faces = tow_mesh.faces
    visited_faces = [False]*len(mesh.faces)
    face_queue = [0] #start with first face
    start_tow = 0

    while(len(face_queue)>0):
        face = face_queue.pop(0)
        face_queue.append(adjacent(mesh, face))
        vec = base_vectors[face]
        tow_queue = [start_tow]
        for tow in tow_faces:
            vertices = tow_mesh.vertices[tow]
            coord = face_centroid(mesh, face)
            res = intersect_ray(coord, vec, vertices)
            if res:
                base_mesh.inc_z_off(face)
                break

    # Iterate through every face normal and check for intersection with tow (check each face)
    for i in range(len(base_vectors)):
        vec = base_vectors[i]
        res = False
        face = tow_faces[0]
        while(res is False):
            pass
'''