import pickle
import sys
import FPM.ImportFPM as fpm
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
from geomdl import fitting as fit
from geomdl.visualization import VisMPL as vis


def main(plys, geom, stl=None):
    """
    Main function for pre-processing. Follows the following steps
    1 - Interpolate points transversely
    2 - Interpolate points longitudinally
    2a - Adjust points based off base stl file if specified
    3 - Check for z-offset through detect_tow_drop
    4 - Add tow mesh to bash mesh and update hash table
    5 - Trim boundaries if required
    6 - Export plies in Marc compatible form
    """

    print(f"FILE: {geom}")
    
    # Initialise plot axis - for Matplotlib
    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')

    # Import stl file if needed
    base_stl = None
    if stl:
        base_stl = load_stl(stl)

    # Create a base_mesh to represent currently laid down tows
    base_mesh = Trimesh()
    base_mesh_hash_table = np.array([], dtype='int32')

    # Optionally generate boundary mesh if required
    boundary = get_boundary()


    for p in plys:
        
        print(f"\n{geom} -->PLY: {p._id}")
        
        # Iterate through each tow
        for t in p.tows:
            print(f"{geom} > tow {t._id}", end="\t")
            
            # Add additional points and vector information
            #Create offsets in transverse directions
            t.ortho_offset(t.w) 

            # Interpolate between the points, with the target point distance being t.w/2
            t.interpolate_tow_points()  
            t.get_new_normals()


            # Step 2 adjust for curvature using base_stl
            if base_stl:
                transverse_adjust(t, base_stl)
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
            
            base_mesh_hash_table = np.append(base_mesh_hash_table, t_mesh_faces)

            # Optionally plot points for visuals
            plot_surface(t.new_pts[0],t.new_pts[-1], ax)

            # Optionally trim tow points based on boundary mesh. Comment out if not planned, otherwise uncomment line below
            # trim_boundary(t, boundary)
            t.trimmed_pts = t.new_pts.tolist()

    # Plot surfaces for debugging
    plt.figure(fig.number)
    plt.show()
    
    # save base mesh
    stl_out = geom+"_base.stl"
    print("...saving mesh at", stl_out)
    base_mesh.export(stl_out)

    # Export tow data to be compatible with Marc, so no package dependencies
    m_plys = create_mentat_tows(plys)
    
    return m_plys


def create_mentat_tows(plys):
    """ Create Marc/py_mentat compatible class
    returns: PlyMentat(TowMentat(PointMentat)) classes
    
    Parameters
    ----------
    plys : list(Ply)
        list of all plys with adjusted tow data
    
    Returns
    -------
    list(PlyMentat)
        list of compatabile Ply/Tow/Point data
    """    
    m_plys = []
    tow_idx = 1
    length = 200

    for p in plys:
        m_tows = []
        for t in p.tows:

            tow_sections = []

            # Create start trimmed points
            points = t.trimmed_pts["start"]
            m_pts = [[],[],[],[],[]]
            for i in range(len(points)):

                m_pts[i] = [Point_Mentat(points[i][j]) for j in range(len(points[i]))]

            tow_sections.append(Tow_Mentat(t._id, m_pts, t.t, t.w, trimmed=True))

            # Add middle (untrimmed) points
            points = t.trimmed_pts["middle"]
            m_pts = [[],[],[],[],[]]
            for i in range(len(points)):
                m_pts[i] = [Point_Mentat(points[i][j]) for j in range(len(points[i]))]

            tow_sections.append(Tow_Mentat(t._id, m_pts, t.t, t.w, trimmed=False))

            # Add end trimmed points
            points = t.trimmed_pts["end"]
            m_pts = [[],[],[],[],[]]
            for i in range(len(points)):
                m_pts[i] = [Point_Mentat(points[i][j]) for j in range(len(points[i]))]

            tow_sections.append(Tow_Mentat(t._id, m_pts, t.t, t.w, trimmed=True))
            m_tows.append(tow_sections)

        new_ply = Ply_Mentat(p._id, m_tows)
        m_plys.append(new_ply)

    return m_plys   

def batch_tows(tow, length):
    """Batches TowMentat classes into batches containing $length number of poitns
    This is to prevent Marc from crashing when passing in too many points
    
    Parameters
    ----------
    tow : TowMentat
        Tow to split into batches
    length : int
        maximum amount of points in each tow
    
    Returns
    -------
    list(TowMentat)
        list of tows representing split up tow
    """    
    if len(tow.pts[0]) < length:
        return [tow]

    batch = []
    i = 0
    while i + length < len(tow.pts[0]):
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
Dump ply/tow data into pickle object
"""
def save_tows(obj, name):
    """Dumpy ply/tow data into pickle object
    
    Parameters
    ----------
    obj : list(Ply) 
        object to save
    name : string
        fileame to save it as
    """    

    file_end = name + ".dat"
    file_name = '/'.join(['dat_files','batched',file_end])
    print(f"...saving at {file_name}")
    with open(file_name, 'wb') as f:
        pickle.dump(obj, f)
    print("save successful")



def plot_surface(L, R, ax):
    lx = np.array(L)
    rx = np.array(R)
    xx = np.vstack((lx[:,0], rx[:,0]))
    yy = np.vstack((lx[:,1], rx[:,1]))
    zz = np.vstack((lx[:,2], rx[:,2]))

    surf = ax.plot_surface(xx,yy,zz)


def get_boundary():
    """Helper function to generate boundary mesh. Currently
    just hardcoded in. Comment out the shape you want to produce
    
    Returns
    -------
    Trimesh
        boundary mesh volume
    """    
    
    # Random rectangle
    vecs = [[605.5, 54.5], [744.5, 54.5], [744.5, 5.5], [605.5, 5.5]]
    faces = [[0,1,2],[2,3,0]]
    height = 50

    # Weave specimen
    vecs = [[740, 70],[765,70],[765,-70],[740,-70]]
    faces = [[0,1,2],[2,3,0]]
    height = 50
    bound = trimesh.creation.extrude_triangulation(vecs,faces,height)
    return bound


if __name__ == '__main__':
    if len(sys.argv) is 1:
        exit("Specify file name to import")

    # Take in argument with geometry name (used for file lookup)
    geom = sys.argv[1]
    stl = None
    if len(sys.argv) > 2:
        stl=sys.argv[2]
    # Import the tow date
    plys = fpm.get_tows(geom)
    # get ply/tow/point data and manipulate accordingly
    marc_ply = main(plys, geom, stl=stl)

    save_tows(marc_ply, sys.argv[1])




    
