from Point import Point
from Vector import Vector
from Mesh import Mesh
from itertools import *
import os

with open('mesh_files/square_plate_mesh.dat','r') as f:
    nodes = []
    elements = []
    new_pt = "GRID*"
    mesh = "CTRIA3"
    i = 0
    for line in f.readlines():
        if new_pt in line:
            s = line.split()
            nodes.append(Vector(float(s[2]), float(s[3]),0))
        elif line[0] == "*":
            s = line.split()
            nodes[i].k = float(s[1])
            # print(nodes[i])
            i += 1
        elif  mesh in line:
            # print("num nodes = ", len(nodes))
            s = line.split()
            i = [int(s[3])-1, int(s[4])-1, int(s[5])-1]
            try:
                elements.append(Mesh([nodes[i[0]], nodes[i[1]], nodes[i[2]]]))
            except IndexError as ie:
                print(i)
                print("num nodes = ",len(nodes))
                print("num elements = ", len(elements))

print("num nodes = ", len(nodes))
print("num elements = ", len(elements))

print("*** test elements ***")
print(vars(elements[200].points[0]))
print(vars(elements[200].centroid))


