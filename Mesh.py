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
        return np.empty(len(self.mesh.faces))

    @property
    def z_off(self):
        return self._z_off

    def inc_z_off(self, index):
        self._z_off[index] += 1


def tow_mesh(tow):
    vertices = []
    mesh = Trimesh()
    for i in range(len(tow.points)-1):
        v1 = tow.L[i]
        v2 = tow.L[i+1]
        v3 = tow.R[i+1]
        v4 = tow.R[i]
        mesh_segment = Trimesh(vertices=[v1,v2,v3,v4], faces = [[0,1,2,3]])
        mesh = mesh.__add__(mesh_segment)
    return mesh

""" 
Projects down from tow points using vectors from FPM data
onto base mesh using similar method to project up
"""
def project_down(base_mesh, tow):
    mesh_faces = base_mesh.mesh.faces
    z_arr = []
    for p in tow.points:
        coord = p.coord.vec
        normal = p.normal.vec
        z = 0
        for f in range(len(mesh_faces)):
            face = mesh_faces[f]
            vertices = base_mesh.mesh.vertices[face]
            res = intersect_ray(coord,normal,vertices)
            if res:
                # print("hit face = ", f, "z = ", base_mesh.z_off[f])
                z = (base_mesh.z_off[f])
        p.z_offset(z*tow.t)

    return True

    

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
    # print(f"v0 = {vertices[0]}\n v1 = {vertices[1]}\n v2 = {vertices[2]}\n")
    e1 = vertices[1] - vertices[0]
    e2 = vertices[2] - vertices[0]
    t_vec = coord - vertices[0]

    eps = 0.00001
    # print(f"e1 = {e1} e2 = {e2}")

    # Calculate P to determine if ray is parallel to face
    p = np.cross(ray, e2)
    det = np.dot(e1, p)
    inv_det = 1.0/det

    # print("det = ",det, "p  = ", p)

    # If parallel then return early
    if abs(det) < eps:
        # print("Ray parallel to plane")
        return False

    u = np.dot(t_vec,p)
    u *= inv_det

    # print("u = ", u)

    # Check bounds of u
    if u < 0. or u > 1.:
        # print("u out of bounds")
        return False

    Q = np.cross(t_vec,e1)
    v = np.dot(ray,Q)
    v *= inv_det
    # print(f"t = {t_vec} ray = {ray}, q = {Q}")
    # print("v = ", v)

    # Check bounds of v
    if v < 0.:
        # print("v out of bounds")
        return False
    elif u + v > 1.:
        # print("u + v > det")
        return False

    # Calculate t and scale
    t = np.dot(e2, Q)
    t *= inv_det

    # print(f"t = {t} u = {u} v = {v}")

    return True

""" 
Checks the face normals projected up towards the tows
"""
def project_up(base_mesh, tow_mesh):

    mesh = base_mesh.mesh
    base_vectors = mesh.face_normals
    tow_faces = tow_mesh.faces
    
    # Iterate through every face normal and check for intersection with tow (check each face)
    for i in range(len(base_vectors)):
        vec = base_vectors[i]
        for face in tow_faces:
            vertices = tow_mesh.vertices[face]
            coord = face_centroid(mesh, i)
            res = intersect_ray(coord, vec, vertices)
            if res:
                base_mesh.inc_z_off(i)
                break
    colour_faces(base_mesh)

def colour_faces(mesh):
    bmesh = mesh.mesh
    maps = np.array([[0,0,0,255],[255,0,0,255],[0,255,0,255],[0,0,255,255], [0,255,255,255], [255,255,255,255]])
    for f in range(len(bmesh.faces)):
        bmesh.visual.face_colors[f] = maps[int(mesh.z_off[f])]
        

def face_centroid(mesh, i):
    vertices = mesh.vertices[mesh.faces[i]]
    x = vertices[:,0].mean()
    y = vertices[:,1].mean()
    z = vertices[:,2].mean()
    return np.array([x,y,z])


    
    


