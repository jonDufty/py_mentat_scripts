# from py_mentat import *
from Tow import Tow
from Point import Point
import pickle
import os


cwd = os.getcwd()
# file_name = "\\".join([cwd,'tows.dat'])
file_name = "/".join([cwd,'tows.dat'])
with open(file_name,'rb') as f:
    tows = pickle.load(f)

tow = tows[0]

def main():
    create_tow_shell(tow)

def generate_points(point):
    p(point.send_coord())

def generate_curve(points):
    # Find index of points generated
    ni = py_get_int("npoints()")
    p("*add_points")
    for point in points:
        generate_points(point)
    nf = py_get_int("npoints()")+4
    pt_to_add = [str(i) for i in list(range(ni+1, nf+1))]
    pt_to_add = " ".join(pt_to_add)
    
    # Form curve
    p("*set_curve_type polyline")
    p("*add_curves")
    p(pt_to_add)
    p("#")
    return py_get_int("ncurves()")

def create_tow_shell(tow):
    # Generate curves from points on L,R of tow path
    curve_l = generate_curve(tow.L)
    curve_r = generate_curve(tow.R)
    
    # filling gaps for offset
    # p("*set_duplicate_translation z 10")
    # p("*set_duplicate_repitions 1")
    # p("*duplicate_curves")
    # p("*all_existing")
    


    # create surface using two guide curves
    p("*set_surface_type skin")
    p("*add_surfaces")
    p("%s %s %s" % (curve_l, curve_r, '#'))

    # Store surface in set (just in case)
    p("*store_surfaces")
    p("surf%s" % tow._id)
    p(tow._id)

    # Convert surface into elements
    n_div = tow.num_el
    p("*set_convert_uvdiv u %s" % n_div)
    p("*set_convert_uvdiv v %s" % 1)
    p("*convert_surfaces")
    p(" ".join([str(tow._id),"#"]))

    # Create set for tow
    p("*select_method_flood")
    p("*select_elements")
    p(tow._eid)
    p("*store_elements")
    p(tow.name())
    p("*all_selected")


    # Specify geometry for elements
    p("*new_geometry")
    p("*geometry_type mech_three_shell")
    p("*geometry_param thick %f" %tow.t)
    p("*add_geometry_elements")
    p(tow.name())


def p(s):
    print(s)
    #  py_send(s)

def py_get_int(s):
    return len(s)


if __name__ == "__main__":
    main()
