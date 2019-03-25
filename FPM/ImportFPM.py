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

tows = []
tow_width = 6
tow_t = 1.0
num_el = 20
i = 0
directory = "FPM/tow_paths"

for f in os.listdir(directory):
    tows.append(Tow(tow_width,tow_t, num_el))
    file = "".join([directory,"/",f])
    df = pandas.read_csv(file,delimiter="[\t]{1,}",skiprows=53, engine='python', na_values="NaN")
    df = df.dropna(how='any')
    for index,row in df.iterrows():
        # print(f"x={row['X']} y={row['Y']} z={row['Z']}")
        tows[i].add_point(import_point(row))
        # print(tows[i].points[index-1])
    i += 1

print("Tows = ", len(tows))

#Create Offset Curves
# offset = tows[i].offset_points()

#Create Points

#Create Curves

#Create Surface using spine

#Create Elements etc...

#Create set for each ply



