import pickle
from Mesh import intersect_ray, subdivide_it
import trimesh
# from trimesh import remesh, bounds, creation, ray
import pyglet
# import stl
import numpy as np

def adjacent(mesh,face):
    faces = []
    for a in list(mesh.face_adjacency):
        if face in a:
            faces.append(a[a!=face][0])
    return np.array(faces)

with open("tows.dat", 'rb') as fp:
    tows = pickle.load(fp)

# trimesh.util.attach_to_log()

# mesh = trimesh.Trimesh(vertices=[[500,-100,25.4],[900,-100,25.4],[900,100,25.4],[500,100,25.3]],
                        # faces = [[0,1,2,3]])
                    
mesh = trimesh.Trimesh(vertices=[[500,-100,25.4],[900,-100,25.4],[900,100,25.4],[500,100,25.3]],
                        faces = [[0,1,2,3]])

mesh = subdivide_it(mesh,10)

# print("mesh", mesh.faces, "\n\n")
# print("mesh", mesh.faces, "\n\n")
# print(mesh.face_adjacency)

# mesh = trimesh.Trimesh(vertices=[[0,0,0], [1,0,0],[1,1,0],[0,1,0]], faces = [[0,1,2,3]])
# mesh2 = trimesh.Trimesh(vertices=[[0,0,1], [1,0,1],[1,1,1],[0,1,1]], faces = [[0,1,2,3]])
print(len(mesh.faces))
print(max(mesh.edges_unique_length))
# adj = adjacent(mesh,3)
# print(mesh.vertices[adj])
# print("normals", mesh.face_normals[0])
c = np.array([0.8,0.8,0])
n = np.array([0,0,-1])
print(intersect_ray(c,n,mesh.vertices[mesh.faces[0]]))
# mesh = mesh.subdivide()
# print(mesh.vertices[mesh.faces[0:2]])
mesh.show()

mesh.export('stl_files/panel.stl')
