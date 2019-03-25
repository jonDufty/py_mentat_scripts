import Majestic.ImportMaj
from Tow import Tow
from py_mentat import *
# import FPM.ImportFPM

def create_tow_shell(tow):
    [L, R] = tow.offset_points()
    # py_send(create curve)
    # py_send(create curve)
    # py_send(set surface to spine)
    # py_send(create curve)
    # n_div = tow.num_el
    # py_send(divide into elements - specify elements)
    # Create set of elements for tow
    
    # py_send("*select_method_flood")
    
    p("*select_elements")
    p("%s" % tow._el_index)
    p("*store_elements")
    p("tow%s" % tow._id)
    p("all_selected")
    p("*select_clear_elements")

    p("*new_geometry")
    p("*geometry_type mech_three_shell")
    p("*geometry_param thick %f" %tow.t)
    p("*add_geometry_elements")
    p("tow%s" % tow._id)


def p(s):
    py_send(s)
