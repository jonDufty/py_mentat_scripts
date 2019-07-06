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


tows = []
tow_width = 6.35/2
tow_t = 1.0
num_el = 20
i = 0
# directory = "FPM/flat_strips/1"
# directory = "FPM/cylinder/3"
# directory = "FPM/dome/1"
directory = "FPM/panel/2"
# ply_dir = "FPM/cylinder"

for f in os.listdir(directory):
    tows.append(Tow(tow_width,tow_t, num_el))
    file = "".join([directory,"/",f])
    skip = start_line(file)
    if skip < 0:
        exit("Start point not found")
    
    df = pandas.read_csv(file,delimiter="[\t]{1,}",skiprows=skip, engine='python', na_values="NaN")
    df = df.dropna(how='any')
    for index,row in df.iterrows():
        if int(row['InBounds'][-2]) is 1:
            tows[i].add_point(import_point(row))
            # print(tows[i].points[index-1])
    if len(tows[i].points) is 0:
        tows.pop(i)
        continue
    i += 1

print("Tows = ", len(tows))




