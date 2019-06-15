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
    
    # Iterate through each tow

    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')

    for t in tows:
        show_points(t.points, fig)
        
        t.ortho_offset(t.w)        
        
        # Interpolate for additional points in tow paths
        # interpolate_tow_points(t.points)

        '''Apply Z offset'''

        
    # m_tows = create_mentat_tows(tows)
    plt.figure(fig.number)
    plt.show()
    # save_tows(m_tows)



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
            m_points.append(Point_Mentat(t.points[i].coord.tolist()))
            m_points_L.append(Point_Mentat(t.L[i].coord.tolist()))
            m_points_R.append(Point_Mentat(t.R[i].coord.tolist()))
            m_in_L.append(pt_idx)
            m_in_R.append(pt_idx + 1)
            pt_idx += 2

        new_tow = Tow_Mentat(m_points, m_points_L, m_in_L, m_points_R, m_in_R)
        m_tows.append(new_tow)
        tow_idx += 1

    return m_tows   



# Interpolate for additional points between each curve
def interpolate_tow_points(pt_array):
    coords = []
    for p in pt_array:
        coords.append(p.coord.vec)

    axes = np.array(coords)
    xs = axes[:,0]
    ys = axes[:,1]
    zs = axes[:,2]

    tck = ip.bisplrep(xs, ys, zs)
    # f = ip.interp2d(xs,ys,zs, kind='cubic')
    dir = pt_array[0].dir
    n = pt_array[0].normal
    i = 0

    xx = np.linspace(xs[0], xs[-1], 20)
    yy = np.linspace(ys[0], ys[-1], 20)
    xe = np.argsort(xx, kind='mergesort')
    ye = np.argsort(yy, kind='mergesort')

    spline_ev = ip.bisplev(xx[xe],yy[ye],tck)
    zz = np.empty((0,1))
    for i in range(len(xe)):
        v = spline_ev[xe[i],ye[i]]
        zz = np.append(zz, spline_ev[xe[i],ye[i]])
    
    ins = np.array([xx,yy,zz]).T
    

    for row in ins:
        print(row, end='\n\n')
        new_p = Point(Vector(row[0],row[1],row[2]), n, dir)
        pt_array.insert(i+j, new_p)

    ''' either insert or replace points - maybe refactor first'''



# Dump new tow data
def save_tows(tows):
    file_name = 'tows.dat'
    with open(file_name, 'wb') as f:
        pickle.dump(tows, f)

def show_points(points, fig):
    #transform all coordinates
    if len(points) is 0:
        return

    coords = []
    for p in points:
        coords.append(p.coord.vec)

    axes = np.array(coords)
    xx = axes[:,0]
    yy = axes[:,1]
    zz = axes[:,2]
    plt.figure(fig.number)
    ax = plt.gca()
    ax.plot(xx, yy, zz) 
    # ax.scatter(xx, yy, zz) 


if __name__ == '__main__':
    # if len(sys.argv) is 1:
    #     exit("Specify file name to import")
    # fn = 
    # from Majestic.ImportMaj import tows
    from FPM.ImportFPM import tows

    main(tows)





    
