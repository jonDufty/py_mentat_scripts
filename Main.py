from py_mentat import *
from TowMentat import *
import pickle
import os


def main():

	tows = load_tows()
	'''
	i = 1
	for t in tows[51:60]:
		if i > 30:
			break
		create_tow_shell(t)
		i += 1
	'''
	create_tow_shell(tows[7])
	print("Created Tow Shells")



def load_tows():
	cwd = os.getcwd()
	f = "flat_4.dat"
	file_name = "\\".join([cwd,'dat_files',f])
	# file_name = "/".join([cwd,'tows.dat'])
	with open(file_name,'rb') as f:
		tows = pickle.load(f)
	return tows


def generate_points(point):
    p(point.send_coord())


def generate_curve(pts):
	
	ni = int(py_get_float("npoints()"))
	p("*add_points")
	for i in pts:
		generate_points(i)
	nf = int(py_get_float("npoints()"))
	pt_to_add = [str(i) for i in list(range(ni+1,nf+1))]
	pt_to_add = " ".join(pt_to_add)
	
	# Form curve
	p("*set_curve_type polyline")
	p("*add_curves")
	p(pt_to_add)
	p("#")
	id = int(py_get_float("ncurves()"))
	
	return str(id)	


def generate_surf(id,L, Li, R, Ri):
    
	# Find index of points generated
    p("*add_points")
    for i in range(len(L)):
        generate_points(L[i])
        generate_points(R[i])
    
    pts_L = [str(i) for i in Li]
    pts_L = " ".join(pts_L)
    pts_R = [str(i) for i in Ri]
    pts_R = " ".join(pts_R)
    
    # Form curve
    p("*set_curve_type polyline")
    p("*add_curves")
    p(pts_L)
    p("#")
    lc = int(py_get_float("ncurves()"))
    
    p("*set_curve_type polyline")
    p("*add_curves")
    p(pts_R)
    p("#")
    rc = int(py_get_float("ncurves()"))
    
    return [str(lc), str(rc)]

def generate_elements(surf_name, n_elements):
    pass


def create_tow_shell(tow):
    # Generate curves from points on L,R of tow path
    #surf = generate_surf(tow._id, tow.pts_L, tow.index_L, tow.pts_R, tow.index_R)
    #curve_r = generate_curves(tow.pts_R, tow.index_R)
    curve_l = generate_curve(tow.pts_L)
    curve_r = generate_curve(tow.pts_R)
	
    
    # create surface using two guide curves
    p("*set_surface_type skin")
    p("*add_surfaces")
    p("%s %s %s" % (curve_l, curve_r, '#'))
    #p("%s %s %s" % (surf[0], surf[1], '#'))

    # Store surface in set (just in case)
    p("*store_surfaces")
    p("surf%s" % str(tow._id))
    p(str(tow._id))

    '''
    # Convert surface into elements
    n_div = len(tow.pts_L)
    p("*set_convert_uvdiv u %s" % n_div)
    p("*set_convert_uvdiv v %s" % 2)
    p("*convert_surfaces")
    p(" ".join([str(tow._id),"#"]))

    # Create set for tow
    n_el = int(py_get_float("nelements()"))
    p("*select_method_flood")
    p("*select_elements")
    p(str(n_el))
    p("*store_elements")
    p(tow.name())
    p("*all_selected")

    # Specify geometry for elements
    p("*new_geometry")
    p("*geometry_type mech_three_shell")
    p("*geometry_param thick %f" %tow.t)
    p("*add_geometry_elements")
    p(tow.name())
    '''


def p(s):
    #print(s)
    py_send(s)

def py_get_int(s):
    return len(s)


if __name__ == "__main__":
    main()
