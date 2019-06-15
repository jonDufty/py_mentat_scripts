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
# directory = "FPM/flat_panel/4"
# skip = 57
directory = "FPM/cylinder/2"
skip = 74
# directory = "FPM/cylinder/1"
# skip = 75

for f in os.listdir(directory):
    tows.append(Tow(tow_width,tow_t, num_el))
    file = "".join([directory,"/",f])
            
    df = pandas.read_csv(file,delimiter="[\t]{1,}",skiprows=skip, engine='python', na_values="NaN")
    df = df.dropna(how='any')
    for index,row in df.iterrows():
        if int(row['InBounds'][-2]) is 1:
            tows[i].add_point(import_point(row))
            # print(tows[i].points[index-1])
    if len(tows[i].points) is 0:
        continue
    i += 1

print("Tows = ", len(tows))




