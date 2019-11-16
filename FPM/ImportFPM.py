import pandas, csv
import numpy as np
import os
from Point import Point
from Tow import Tow
from Ply import Ply

'''
get_tows: Primary function for extracting FPM data
reads in files, line by line and imports vector data
'''
def get_tows(geom):
    plys = []
    tow_t = 0.2
    z = 0 #temporary until z-off works

    ply_dir = "/".join(["FPM",geom])

    # Iterate through ply directories
    for d in sorted(os.listdir(ply_dir)):
        # Get current directory address
        dir = "/".join([ply_dir,d])
        ply = Ply()
        tow_w = tow_width(dir)/2

        # Iterate through every tow pt file in directory and create new tow
        for f in sorted(os.listdir(dir)):
            tow = Tow(tow_w,tow_t, ply._id)
            file = "".join([dir,"/",f])
            skip = start_line(file)
            if skip < 0:
                exit("Start point not found")
            
            # Pandas reads format into python dictionary type
            df = pandas.read_csv(file,delimiter="[\t]{1,}",skiprows=skip, engine='python', na_values="NaN")
            df = df.dropna(how='any')

            for index,row in df.iterrows():
                # Check if point is actually in the boundary
                if int(row['InBounds'][-2]) is 1:
                    tow.add_point(import_point(row))
            # If no points were added drop the tow to keep indexes in check
            if len(tow.points) < 2:
                Tow._dec_id()
                continue
            ply.add_tow(tow)

        plys.append(ply)
        z += 1
        
    return plys

def import_point(row):
    c = np.array([row['X'],row['Y'],row['Z']], dtype='f')
    n = np.array([row['I'],row['J'],row['K']], dtype='f')
    d = np.array([row['Dir X'],row['Dir Y'],row['Dir Z']], dtype='f')
    return Point(c,n,d)

# Fines the amount of lines to skip in tow file
def start_line(file):
    skip = -1
    with open(file, 'r') as f1:
        begin = False
        for line_no, line in enumerate(f1):
            if "begin" in line:
                begin = True
                continue
            elif "strip" in line and begin:
                skip = line_no + 1
                break
    return skip

def tow_width(dir):
    f = os.listdir(dir)[0]
    file = "".join([dir,"/",f])
    with open(file, 'r') as f1:
        for line_no, line in enumerate(f1):
            if "Tow Width" in line:
                thickness = line.split()[3]
                return float(thickness)
    return 6.35