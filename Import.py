import pickle
import sys

from TowMentat import *
from Vector import Vector
from Point import Point
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import scipy as sp
from scipy import interpolate as ip


def main(tows):
    
    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')

    # Iterate through each tow
    for t in tows:
        # for now do z offset before ortho offset
        t.z_offset()
        t.ortho_offset(t.w)
        
        # Interpolate for additional points in tow paths
        d =  t.length()/len(t.points)
        # print("d = ", d, "p = ", len(t.points))
        
        """ if t.length()/len(t.points) > 0.5*t.w:
            n = int(t.length()/0.5*t.w)
            print("n = ", n)
            # interpolate_tow_points(t.points)
            t.L = interpolate_tow_points(t.L, n)
            t.R = interpolate_tow_points(t.R, n)
         """
        plot_points(t.points, ax)
        # plot_surface(t.L,t.R, ax)
        # plot_offset(t.L,t.R, ax)

        '''Apply Z offset'''

    plt.figure(fig.number)
    plt.show()
        
    m_tows = create_mentat_tows(tows)
    save_tows(m_tows)



# Create Marc/py_mentat compatible class
def create_mentat_tows(tows):
    m_tows = []
    tow_idx = 1
    pt_idx = 1

    for t in tows:
        m_points = []
        m_points_R = []
        m_points_L = []
        m_in_L = []
        m_in_R = []

        for i in range(len(t.points)):
            m_points.append(Point_Mentat(t.points[i].coord.vec.tolist()))
            m_points_L.append(Point_Mentat(t.L[i].tolist()))
            m_points_R.append(Point_Mentat(t.R[i].tolist()))
            m_in_L.append(pt_idx)
            m_in_R.append(pt_idx + 1)
            pt_idx += 2

        new_tow = Tow_Mentat(tow_idx, m_points, m_points_L, m_in_L, m_points_R, m_in_R, t.t, t.w)
        m_tows.append(new_tow)
        tow_idx += 1

    return m_tows   



# Interpolate for additional points between each curve
def interpolate_tow_points(coords, n):
    
    axes = np.array(coords)
    xs = axes[:,0]
    ys = axes[:,1]
    zs = axes[:,2]

    tck, u = ip.splprep([xs,ys,zs])
    u1 = np.linspace(0,1,n)
    xx, yy, zz = ip.splev(u1, tck)
    
    """ INTERP BETWEEN POINTS TO KEEP CURRENT POINTS """

    ins = np.array([xx,yy,zz]).T
    new = []
    for row in ins:
        new.append(row)

    return new        


# Dump new tow data
def save_tows(tows):
    file_name = 'tows.dat'
    with open(file_name, 'wb') as f:
        pickle.dump(tows, f)


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
    # if len(sys.argv) is 1:
    #     exit("Specify file name to import")
    # fn = 
    # from Majestic.ImportMaj import tows
    # from FPM.ImportFPM import tows
    from FPM.ImportFPM_stack import tows

    main(tows)





    
