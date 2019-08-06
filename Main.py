from py_mentat import *
from TowMentat import *
import pickle
import os


def main():

	tows = load_tows()
	
	i = 1
	for t in tows[0:1]:
		create_tow_shell(t)
		i += 1
	
	#create_tow_shell(tows[0])
	print("Created Tow Shells")



def load_tows():
	cwd = os.getcwd()
	f = "batched\\cylinder_all.dat"
	file_name = "\\".join([cwd,'dat_files',f])
	# file_name = "/".join([cwd,'tows.dat']) #for linux FS
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



def generate_elements(surf_name, n_elements):
    pass


def create_tow_shell(tow_list):

	# el_size = float((tow_list.w)) #change when batched
	el_size = float((tow_list[0].w)) #change when batched
	print(el_size)
	# surf_set = "".join(["surf",str(tow_list._id)])
	surf_set = "".join(["surf",str(tow_list[0]._id)])
	print(surf_set)

	for tow in tow_list:
		# Generate curves from points on L,R of tow path
		curve_l = generate_curve(tow.pts_L)
		curve_r = generate_curve(tow.pts_R)
		#curve_f = generate_curve([tow.pts_L[0], tow.pts_R[0]])
		#curve_r = generate_curve([tow.pts_L[-1], tow.pts_R[-1]])
			
		# create surface using two guide curves
		p("*set_surface_type skin")
		p("*set_trim_new_surfs y")
		p("*add_surfaces")
		p("%s %s %s" % (curve_l, curve_r, '#'))

		# Store surface in set (just in case)
		# n_surf = int(py_get_float("nsurfaces()"))
		# p("*store_surfaces")
		# p(surf_set)
		# p(str(n_surf))
		# p("#")

	
	p("@set($convert_entities,surfaces)")
	p("@set($convert_surfaces_method,surface_faceted)")
	p("*set_curve_div_type_fix")
	p("*set_curve_div_type_fix_avgl")
	p("*set_curve_div_avgl %s" % str(el_size))
	p("*apply_curve_divisions")
	p("all_existing")
	p("*surface_faceted")
	p("all_existing") 
	p("#")
	return

	p("*renumber_surfaces")
	p("@set($automesh_surface_desc,facets)")
	p("@set($automesh_surface_family,mixed)")
	p("*pt_set_element_size %s" % str(el_size))
	p("*pt_quadmesh_surf")
	p("all_existing")

    
	# Create set for tow
	p("*select_method_flood")
	p("*select_elements")
	print("n_elem = ", py_get_int("nelements()"))
	p(str(py_get_int("nelements()")))
	p("*store_elements")
	p(tow.name())
	p("*all_selected")

	p("*clear_geometry")
	p("select_clear")
	
	# Specify geometry for elements
	p("*new_geometry")
	p("*geometry_type mech_three_shell")
	p("*geometry_param thick %f" %tow.t)
	p("*add_geometry_elements")
	p(tow.name())


def p(s):
    #print(s)
    py_send(s)


if __name__ == "__main__":
    main()
