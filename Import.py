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
            project_down(base_mesh, t)
            t.ortho_offset(t.w)
            t_mesh = tow_mesh(t)
            top_mesh = top_mesh.__add__(t_mesh)
            # print(base_mesh.z_off)

            # base_mesh.mesh.show()
            '''
            Insert interpolating feature once fixed
            '''
            '''
            avg_dist = t.length()/len(t.points)
            # print(f"avg = {avg_dist} ... ")
            if avg_dist > t.w/4:
                evalpts = interpolate_tow_points(t.L)
            '''
            # plot_points(t.points, ax)
            plot_surface(t.L,t.R, ax)
            # plot_offset(t.L,t.R, ax)

            '''Apply Z offset'''
        top_mesh.show()
        project_up(base_mesh, top_mesh)
    
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
            m_points = []
            m_points_R = []
            m_points_L = []
            for i in range(len(t.points)):
                m_points.append(Point_Mentat(t.points[i].coord.tolist()))
                m_points_L.append(Point_Mentat(t.L[i].tolist()))
                m_points_R.append(Point_Mentat(t.R[i].tolist()))

            new_tow = Tow_Mentat(t._id, m_points, m_points_L, m_points_R, t.t, t.w, ply=t.ply)
            new_tow = batch_tows(new_tow, length)
            m_tows.append(new_tow)

        new_ply = Ply_Mentat(p._id, m_tows)
        m_plys.append(new_ply)

    return m_plys   

def batch_tows(tow, length):
    if len(tow.pts) < length:
        return [tow]

    batch = []
    i = 0
    while i + length < len(tow.pts):
        p = tow.pts[i:i+length]
        l = tow.pts_L[i:i+length]
        r = tow.pts_R[i:i+length]
        new = Tow_Mentat(tow._id, p,l,r,tow.t,tow.w)
        batch.append(new)
        i += length - 1
    # Add remaining points from end of tow
    p = tow.pts[i:]
    l = tow.pts_L[i:]
    r = tow.pts_R[i:]
    new = Tow_Mentat(tow._id, p,l,r,tow.t,tow.w)
    batch.append(new)

    return batch


def print_tow_batch(tow):
    print(f"batches = {len(tow)}")
    for t in tow:
        print(f"tow {t._id}", f"length = {len(t.pts)}")


# Interpolate for additional points between each curve
def interpolate_tow_points(coords):
    print("len orig = ", len(coords))
    points = []
    curve = fit.interpolate_curve(coords, 1)
    curve.delta = 0.005
    print("len eval = ", len(curve.evalpts))

    evalpts = np.array(curve.evalpts)
    
    return evalpts


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





    
