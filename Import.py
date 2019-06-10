import pickle
# from Majestic.ImportMaj import tows
from FPM.ImportFPM import tows
from TowMentat import *
import Vector
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy


def main():

    
    # Iterate through each tow
    for t in tows:
        # Interpolate for additional points in tow paths
        interpolate_tow_points(t.points)

        '''Apply Z offset'''

        t.ortho_offset(t.w)        
        
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
    ''' User scipy 2D interpolation - find equidistant points along curve, insert in between points'''
    pass

# Tump new tow data
def save_tows(tows):
    file_name = 'tows.dat'
    with open(file_name, 'wb') as f:
        pickle.dump(tows, f)

 