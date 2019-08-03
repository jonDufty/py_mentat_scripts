from trimesh import Trimesh
import numpy as np

""" 
Wrapper class for trimesh with custom functions
"""
class Mesh(Trimesh):
    def __init__(self, vertices=None, faces=None, face_normals=None, vertex_normals=None, face_colors=None, vertex_colors=None, metadata=None, process=True, validate=False, use_embree=True, initial_cache={}, visual=None, **kwargs):
        super().__init__(vertices=vertices, faces=faces, face_normals=face_normals, vertex_normals=vertex_normals, face_colors=face_colors, vertex_colors=vertex_colors, metadata=metadata, process=process, validate=validate, use_embree=use_embree, initial_cache=initial_cache, visual=visual, **kwargs)
        z_off = None



def intersect_ray(coord, ray, vertices):
    """ 
    Implementation of Moller-trombone ray
    intersection algorithm.
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

    
    
    


