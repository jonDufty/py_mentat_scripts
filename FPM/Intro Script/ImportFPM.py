import pandas, csv
from Point import Point
from Vector import Vector
from Tow import Tow

df = pandas.read_csv('tow_paths/1.adcfpt',delimiter="[\t]{1,}",skiprows=53, engine='python', na_values="NaN")
df = df.dropna(how='any')
# print(df)
def import_point(row):
    c = Vector(row['X'],row['Y'],row['Z'])
    n = Vector(row['I'],row['J'],row['K'])
    d = Vector(row['Dir X'],row['Dir Y'],row['Dir Z'])
    return Point(c,n,d)

tows = []
tow_width = 6
tows.append(Tow(tow_width))
i = 0
for index,row in df.iterrows():
    # print(f"x={row['X']} y={row['Y']} z={row['Z']}")
    tows[i].add_point(import_point(row))
    print(tows[i].points[index-1])

#Create Offset Curves
offset = tows[i].offset_points()

#Create Points

#Create Curves

#Create Surface using spine

#Create Elements etc...

#Create set for each ply



