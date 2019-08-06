import pandas, csv
from Point import Point
from Vector import Vector
from Tow import Tow
import os


def import_point(row):
    c = Vector(row['X'],row['Y'],row['Z'])
    n = Vector(row['I'],row['J'],row['K'])
    d = Vector(row['Dir X'],row['Dir Y'],row['Dir Z'])
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

def get_tows(geom):
    tows = []
    tow_width = 6.35/2
    tow_t = 0.1
    num_el = 20
    i = 0
    # directory = "FPM/flat_strips/1"
    # directory = "FPM/cylinder/3"
    # directory = "FPM/dome/1"
    # directory = "FPM/cone/2"
    # ply_dir = "FPM/cylinder"
    ply_dir = "/".join(["FPM",geom])

    z = 0
    # Iterate through ply directories
    for d in os.listdir(ply_dir):
        # Get current directory address
        dir = "/".join([ply_dir,d])
        # Iterate through every tow pt file in directory and create new tow
        for f in os.listdir(dir):
            tows.append(Tow(tow_width,tow_t, num_el, z_off=z))
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
                    tows[i].add_point(import_point(row))
            # If no pointes were added drop the tow to keep indexes in check
            if len(tows[i].points) is 0:
                tows.pop(i)
                continue
            i += 1
        print("Tows = ", len(tows))
        z += 1
    return tows