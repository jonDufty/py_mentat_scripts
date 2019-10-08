import pickle
from Mesh import *
import trimesh
# from trimesh import remesh, bounds, creation, ray
import pyglet
# import stl
import numpy as np


with open("tows.dat", 'rb') as fp:
    tows = pickle.load(fp)

# trimesh.util.attach_to_log()

# mesh = trimesh.Trimesh(vertices=[[500,-100,25.4],[900,-100,25.4],[900,100,25.4],[500,100,25.3]],
                        # faces = [[0,1,2,3]])
                    
mesh = trimesh.creation.cylinder(radius=5.0, height=20.0)
mesh = subdivide_it(mesh,0.5)


# print("mesh", mesh.faces, "\n\n")

# mesh = trimesh.Trimesh(vertices=[[0,0,0], [1,0,0],[1,1,0],[0,1,0]], faces = [[0,1,2,3]])
# mesh2 = trimesh.Trimesh(vertices=[[0,0,1], [1,0,1],[1,1,1],[0,1,1]], faces = [[0,1,2,3]])
# print((mesh.face_normals), mesh.face_normals.shape)
# print(mesh.vertex_neighbors[5])
# print(max(mesh.edges_unique_length))
# adj = adjacent(mesh,5000)
# print(mesh.vertices[adj])
# print("normals", mesh.face_normals[0])

# print(mesh.triangles_center)

origins = np.array([[10,0,0]])
vectors = np.array([[-1,0,0]])

index_ray, index_tri = mesh.ray.intersects_id(origins, vectors,multiple_hits=False)
print('The rays with index: {} hit the triangles stored at mesh.faces[{}]'.format(index_ray, index_tri))
print(index_ray)

locations, index_ray, index_tri = mesh.ray.intersects_location(origins, vectors, multiple_hits=False)
print('The rays with index: {} hit the triangles stored at mesh.faces[{}]'.format(index_ray, index_tri))


# mesh = mesh.subdivide()
# m3 = mesh.__add__(m2)
#  unmerge so viewer doesn't smooth
mesh.unmerge_vertices()
# make mesh white- ish
mesh.visual.face_colors = [255,255,255,255]
mesh.visual.face_colors[index_tri] = [255, 0, 0, 255]

mesh.show()

# stack rays into line segments for visualization as Path3D
ray_visualize = trimesh.load_path(np.hstack((origins,
                                             origins + vectors*20.0)).reshape(-1, 2, 3))

scene = trimesh.Scene([mesh,
                       ray_visualize])

scene.show()

# mesh.export('stl_files/panel.stl')


