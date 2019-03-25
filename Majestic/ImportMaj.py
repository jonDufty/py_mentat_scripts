from Vector import Vector
from Point import Point
from Tow import Tow

def import_point(row):
    c = Vector(row[0],row[1],row[2])
    n = Vector(row[3],row[4],row[5])
    d = Vector(row[6],row[7],row[8])
    return Point(c,n,d)

new_tow = "NewBand"
new_pt = "AddPoint2"

tows = []
tow_width = 6
tow_t = 1.0
element_size = 5.0
i = 0

with open('Majestic/tow_sample','r') as m:
    for line in m:
        
        if new_tow in line:
            print("Create New Tow")
            #Create a new tow
            tows.append(Tow(tow_width,tow_t,element_size))

        if new_pt in line:
            values = line.split(f"{new_pt}(")
            v = values[1].split(",")[1:10]
            v = [float(i) for i in v]
            #add points to end tow
            tows[-1].add_point(import_point(v))

for tow in tows:
    print(tow.points[0].coord.i)
