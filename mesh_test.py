import pickle
from Mesh import intersect_ray
import trimesh
from trimesh import remesh, bounds, creation, ray
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

mesh = trimesh.Trimesh(vertices=[[0,0,0],[3,0,0],[0,3,0],[3,3,0],[6,0,0],[6,3,0]],
                        faces = [[1,2,0],[3,2,1],[4,5,3],[4,3,1]])
mesh = mesh.subdivide()
print("mesh1",mesh.faces)
mesh2 = trimesh.Trimesh(vertices=[[0,0,1],[3,0,1],[0,3,1],[3,3,1],[0,6,1],[3,6,1]], faces = [[1,2,0],[3,2,1],[4,2,5],[5,2,3]])
mesh2 = mesh2.subdivide()
print("mesh2",mesh2.faces)
mesh = mesh.__add__(mesh2)
# print("mesh", mesh.faces, "\n\n")
mesh.remove_duplicate_faces()
# print("mesh", mesh.faces, "\n\n")
# print(mesh.face_adjacency)

# mesh = trimesh.Trimesh(vertices=[[0,0,0], [1,0,0],[1,1,0],[0,1,0]], faces = [[0,1,2,3]])
# mesh2 = trimesh.Trimesh(vertices=[[0,0,1], [1,0,1],[1,1,1],[0,1,1]], faces = [[0,1,2,3]])
# print(mesh.face_adjacency)
# adj = adjacent(mesh,3)
# print(mesh.vertices[adj])
# print("normals", mesh.face_normals[0])
c = np.array([0.8,0.8,0])
n = np.array([0,0,-1])
print(intersect_ray(c,n,mesh.vertices[mesh.faces[0]]))
# mesh = mesh.subdivide()
# print(mesh.vertices[mesh.faces[0:2]])
mesh.show()

