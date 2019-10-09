import pickle
import sys
import FPM.ImportFPM as fpm
# import FPM.ImportFPM as fpm
from TowMentat import *
from Vector import Vector
from Point import Point
from Mesh import *
import trimesh
import pyglet
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import scipy as sp
from scipy import interpolate as ip
from geomdl import fitting as fit
from geomdl.visualization import VisMPL as vis

def main(plys, geom):
    
    # Initialise plot axis
    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')

    # Initialise base mesh for offset
    base_stl = trimesh.load("/".join(["stl_files","panel" + ".stl"]))
    base_mesh = Mesh(base_stl)
    # base_mesh.mesh.show()
    for p in plys:
        top_mesh = Trimesh()
        
        # Iterate through each tow
        for t in p.tows:
            # for now do z offset before ortho offset
            # t.z_offset()
            t.ortho_offset(t.w)

            '''
            Insert interpolating feature once fixed
            '''
            for i in range(len(t.new_pts)):
                t.new_pts[i] = interpolate_tow_points(t.new_pts[i], t.w/2)
            t.get_new_normals()
            # t.coords = interpolate_tow_points(t.coords, t.w/2)
            # t.L_out = interpolate_tow_points(t.L_out, t.w/2)
            # t.L_in = interpolate_tow_points(t.L_in, t.w/2)
            # t.R_in = interpolate_tow_points(t.R_in, t.w/2)
            # t.R_out = interpolate_tow_points(t.R_out, t.w/2)

            t_mesh = tow_mesh(t)
            top_mesh = top_mesh.__add__(t_mesh)

            tow_z_array, face_z_index = project_down(base_mesh, t)
            offset_rule(base_mesh, tow_z_array, face_z_index)
            # base_mesh.adjust_z_off(face_z_index, tow_z_array)
            t.z_offset(tow_z_array)

            # plot_points(t.points, ax)
            plot_surface(t.new_pts[0],t.new_pts[-1], ax)
            # plot_offset(t.L,t.R, ax)

        base_vectors = project_up(base_mesh, top_mesh)
        for v in base_vectors:
            base_mesh.inc_z_off(v)
        
        base_mesh.visual(base_vectors)
    
    # top_mesh = top_mesh.__add__(base_mesh.mesh)
    
    plt.figure(fig.number)
    plt.show()
        
    m_plys = create_mentat_tows(plys)
    
    return m_plys

def create_ply_index(m_tows):
    ply = {}
    for t in m_tows:
        if t[0].ply in ply.keys():
            ply[t[0].ply].append(t[0].name())
        else:
            ply[t[0].ply] = [t[0].name()]
    return ply


# Create Marc/py_mentat compatible class
def create_mentat_tows(plys):
    m_plys = []
    tow_idx = 1
    length = 100

    for p in plys:
        m_tows = []
        for t in p.tows:
            m_points = [[],[],[],[],[]]
            for i in range(len(t.new_pts[0])):
                for j in range(len(m_points)):
                    m_points[j].append(Point_Mentat(t.new_pts[j][i]))

            new_tow = Tow_Mentat(t._id, m_points, t.t, t.w, ply=t.ply)
            new_tow = batch_tows(new_tow, length)
            m_tows.append(new_tow)

        new_ply = Ply_Mentat(p._id, m_tows)
        m_plys.append(new_ply)

    return m_plys   

def batch_tows(tow, length):
    if len(tow.pts[0]) < length:
        return [tow]

    batch = []
    i = 0
    while i + length < len(tow.pts):
        batch_tow = [[],[],[],[],[]]
        for j in range(len(batch_tow)):
            batch_tow[j] = tow.pts[j][i:i+length]
            
        new = Tow_Mentat(tow._id, batch_tow,tow.t,tow.w)
        batch.append(new)
        i += length - 1
    # Add remaining points from end of tow
    batch_tow = [[],[],[],[],[]]
    for j in range(len(batch_tow)):
        batch_tow[j] = tow.pts[j][i:]
    new = Tow_Mentat(tow._id, batch_tow,tow.t,tow.w)
    batch.append(new)

    return batch


def print_tow_batch(tow):
    print(f"batches = {len(tow)}")
    for t in tow:
        print(f"tow {t._id}", f"length = {len(t.pts)}")


# Interpolate for additional points between each curve
def interpolate_tow_points(points, target_length):
    
    # Batch up for large tows
    batch = []
    new_batch = []
    i = 0
    batch_sz = 100
    while(i + batch_sz < len(points)):
        batch.append(points[i:i+batch_sz])
        i += batch_sz -1
    batch.append(points[i:])
    # print([len(i) for i in batch])

    for b in batch:
        if len(b) <= 2:
            order = 1
        elif len(b) == 3:
            order = 2
        else:
            order = 3

        # get length of batch curve
        v1s = np.array(b[1:])
        v2s = np.array(b[:-1])
        diff = v2s - v1s
        length = sum([np.linalg.norm(x) for x in diff])
        delta = min(target_length/length,0.99)
        
        # print(f"length = {length} batch = {len(b)} d={delta}")

        curve = fit.interpolate_curve(b,order)
        curve.delta = delta
        evalpts = curve.evalpts
        new_batch += evalpts
        # print(f"length new = {len(evalpts)}")
    
        # for i in range(len(evalpts)-1):
            # print(f"l = {np.linalg.norm(np.array(evalpts[i+1]) - np.array(evalpts[i]))}")

    # stitch new batch back together
    
    return np.array(new_batch)


    """ INTERP BETWEEN POINTS TO KEEP CURRENT POINTS """

    pass      


# Dump new tow data
def save_tows(obj, name):
    file_end = name + ".dat"
    file_name = '/'.join(['dat_files','batched',file_end])
    print(f"...saving at {file_name}")
    with open(file_name, 'wb') as f:
        pickle.dump(obj, f)
    print("save successful")


def plot_spline(tck):
    xn, yn = np.mgrid[-100:100:500j, -100:100:500j]
    zn = ip.bisplev(xn[:,0], yn[0,:], tck)

    plt.figure()
    plt.pcolor(xn, yn, zn)
    plt.colorbar()
    plt.show()

def plot_points(points, ax):
    #transform all coordinates
    coords = []
    for p in points:
        coords.append(p.coord.vec)

    axes = np.array(coords)
    xx = axes[:,0]
    yy = axes[:,1]
    zz = axes[:,2]

    ax.plot(xx, yy, zz) 
    # ax.scatter(xx, yy, zz) 

def plot_surface(L, R, ax):
    lx = np.array(L)
    rx = np.array(R)
    xx = np.vstack((lx[:,0], rx[:,0]))
    yy = np.vstack((lx[:,1], rx[:,1]))
    zz = np.vstack((lx[:,2], rx[:,2]))

    surf = ax.plot_surface(xx,yy,zz)

def plot_offset(L, R, ax):
    lx = np.array(L)
    rx = np.array(R)

    xx = lx[:,0]
    yy = lx[:,1]
    zz = lx[:,2]
    plot = ax.plot(xx,yy,zz)

    xx = rx[:,0]
    yy = rx[:,1]
    zz = rx[:,2]
    plot = ax.plot(xx,yy,zz)


if __name__ == '__main__':
    if len(sys.argv) is 1:
        exit("Specify file name to import")

    geom = sys.argv[1]
    plys = fpm.get_tows(geom)
    marc_ply = main(plys, geom)

    save_tows(marc_ply, sys.argv[1])





    
