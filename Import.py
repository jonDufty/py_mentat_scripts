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

def main(plys, geom, stl=None):
    
    # Initialise plot axis
    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')

    # Import stl file if needed
    base_stl = None
    if stl:
        base_stl = load_mesh(stl)


    # Create a base_mesh to represent currently laid down tows
    base_mesh = Trimesh()
    base_mesh_hash_table = np.array([], dtype='int32')

    for p in plys:
        
        # Iterate through each tow
        for t in p.tows:
            
            # Add additional points and vector information
            t.ortho_offset(t.w) #Create offsets in transverse directions
            
            # Interpolate between the points, with the target point distance being t.w/2
            # Where t.w = 3.25 currently.

            t.interpolate_tow_points()  
            t.get_new_normals()


            # Step 2 adjust for curvature using base_stl
            if base_stl:
                tranverse_adjust(t, base_stl)
                t.get_new_normals()


            # If no base_mesh exists, skip projection. Otheriwse detect whether to offset
            if not base_mesh.is_empty:
                detect_tow_drop(t,base_mesh,base_mesh_hash_table)
                t_mesh = tow_mesh(t)
                base_mesh = base_mesh.__add__(t_mesh)
            else:
                t_mesh = tow_mesh(t)
                base_mesh = t_mesh

            # Mesh tow with offset data
            t_mesh_faces = np.array([t._id]*len(t_mesh.faces), dtype='int32')
            
            # Add tow to base mesh (i.e. lay down tow). Update hash table
            if base_mesh.is_empty:
                base_mesh = t_mesh
            else:
                base_mesh = base_mesh.__add__(t_mesh)
            base_mesh_hash_table = np.append(base_mesh_hash_table, t_mesh_faces)

            # Plot points for visuals
            plot_surface(t.new_pts[0],t.new_pts[-1], ax)

        base_mesh.show()
    
    # Plot surfaces for debugging
    plt.figure(fig.number)
    plt.show()
    
    # Export tow data to be compatible with Marc, so no package dependencies
    m_plys = create_mentat_tows(plys)
    
    return m_plys

""" 
REDUNANT CLASS: Will remove
"""
def create_ply_index(m_tows):
    ply = {}
    for t in m_tows:
        if t[0].ply in ply.keys():
            ply[t[0].ply].append(t[0].name())
        else:
            ply[t[0].ply] = [t[0].name()]
    return ply


""" 
Create Marc/py_mentat compatible class
returns: PlyMentat(TowMentat(PointMentat)) classes
"""
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
                    m_points[j].append(Point_Mentat(t.new_pts[j][i].tolist()))

            new_tow = Tow_Mentat(t._id, m_points, t.t, t.w)
            new_tow = batch_tows(new_tow, length)
            m_tows.append(new_tow)

        new_ply = Ply_Mentat(p._id, m_tows)
        m_plys.append(new_ply)

    return m_plys   

"""  
Batches TowMentat classes into batches containing $length number of poitns
This is to prevent Marc from crashing when passing in too many points
"""
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

""" 
Takes in array of points, and interpolates in between them using geomdl package
Interpoaltes to a level such that the distance between points is roughly equal to 
$target_length
Interpolates in batches, as large arrays can cause errors
"""
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

    for b in batch:
        if len(b) <= 2:     #If only two points - linear interpolation
            order = 1
        elif len(b) == 3:   #If 3 poits - quadratic interpolation
            order = 2
        else:               # if > 3 pts - cubic interpolation
            order = 3

        # get length of batch curve
        v1s = np.array(b[1:])
        v2s = np.array(b[:-1])
        diff = v2s - v1s
        lengths = [np.linalg.norm(x) for x in diff]
        length = sum([np.linalg.norm(x) for x in diff]) #Get total length of distances between each point
        
        # Delta dictates how many 'evenly' spaced points the interpolation funciton will output.
        # Roughly equal to 1/n_points-1 - (e.g. delta = 0.01 --> 1/100 --> 101 points).
        # Delta must be < 1, so min() statement is too ensure this (bit hacky atm)
        delta = min(target_length/length,0.99) 
        
        # call the interpolate curve function

        # curve = fit.interpolate_curve(b,order)
        curve.delta = delta
        evalpts = curve.evalpts     #evalpts is the new list of interpolated points
        new_batch += evalpts        #stich batches back together as created
    v1s = np.array(new_batch[1:])
    v2s = np.array(new_batch[:-1])
    diff = v2s - v1s
    lengths = [np.linalg.norm(x) for x in diff]
    # Evalpts is of type list, need to return as numpy array
    return np.array(new_batch)

""" 
Dump ply/tow data into pickle object
"""
def save_tows(obj, name):
    file_end = name + ".dat"
    file_name = '/'.join(['dat_files','batched',file_end])
    print(f"...saving at {file_name}")
    with open(file_name, 'wb') as f:
        pickle.dump(obj, f)
    print("save successful")



"""  
Plot spline, surface, points are all just different plot functions
Mainly used for debugging
"""
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

    # Take in argument with geometry name (used for file lookup)
    geom = sys.argv[1]
    # Import the tow date
    plys = fpm.get_tows(geom)
    # get ply/tow/point data and manipulate accordingly
    marc_ply = main(plys, geom)

    save_tows(marc_ply, sys.argv[1])





    
