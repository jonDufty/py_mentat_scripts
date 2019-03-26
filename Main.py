from Tow import Tow
from Point import Point
import pickle
# from py_mentat import *


file_name = 'tows.dat'
with open(file_name,'rb') as f:
    tows = pickle.load(f)

tow = tows[0]
print(tow)


def main():
    create_tow_shell(tow)

def create_tow_shell(tow):
    points = " ".join([str(p._id) for p in tow.points])
    # Create curve from list of pt_id's
    p("*set_curve_type polyline")
    p("*add_curves")
    p(points)
    p("#")

    # filling gaps for offset
    p("*set_duplicate_translation z 10")
    p("*set_duplicate_repitions 1")
    p("*duplicate_curves")
    p("*all_existing")
    
    # create surface using two guide curves
    p("*set_surface_type skin")
    p("*add_srfaces")
    p("%s %s %s" % (2*tow._id-1, 2*tow._id, '#'))
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


if __name__ == "__main__":
    main()
