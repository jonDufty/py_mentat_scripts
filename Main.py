from py_mentat import *
from TowMentat import *
from Material import *
import pickle
import os


def main():

	tows,ply_index = load_tows()
	
	for t in tows:
		create_tow_shell(t)
	
	assign_geometry(tows[0][0].t)

	cbody_index = create_contact_bodies(ply_index)

	assign_orientation()

	standard_material(T300, "all_existing")
	
	'''
	Note: This is only working for ply-wise models at the moment
	not generalised yet
	'''
	cb_index = cbody_index(ply_index)
	print(cb_index)

	edge_contact(cb_index, 0.5)
	

	# face_contact()



def edge_contact(cb_index, tolerance):

	p("*new_contact_table")
	p("*contact_table_name ct_edege")
	p("*prog_option ctable:criterion:contact_distance")
	p("*prog_param ctable:contact_distance %f" % tolerance)
	p("*prog_option ctable:add_replace_mode:both")
	p("*prog_option ctable:contact_type:glue")
	p("@set($cta_crit_dist_action,list)")
	
	for c in cb_index.keys():
		cb = " ".join(cb_index[c])
		p("*ctable_add_replace_entries_body_list")
		p("%s %s" % (cb, "#"))


def assign_geometry(t):

	# Specify geometry for elements
	p("*new_geometry")
	p("*geometry_type mech_three_shell")
	p("*geometry_param thick %f" %t)
	p("*add_geometry_elements")
	p("all_existing")


def standard_material(m, elements):
    p("*new_mater standard")
    p("*mater_option general:state:solid")
    p("*mater_option general:skip_structural:off")
    p('*mater_name ' + m.name)
    p("*mater_option structural:type:elast_plast_ortho")
    p("*mater_param structural:youngs_modulus1 %f" % m.E1)
    p("*mater_param structural:youngs_modulus2 %f" % m.E2)
    p("*mater_param structural:youngs_modulus3 %f" % m.E3)
    p("*mater_param structural:poissons_ratio12 %f" % m.Nu12)
    p("*mater_param structural:poissons_ratio23 %f" % m.Nu23)
    p("*mater_param structural:poissons_ratio31 %f" % m.Nu31)
    p("*mater_param structural:shear_modulus12 %f" % m.G12)
    p("*mater_param structural:shear_modulus23 %f" % m.G23)
    p("*mater_param structural:shear_modulus31 %f" % m.G31)

    p("*add_mater_elements")
    p(elements)
    return

def create_contact_bodies(ply_index):
	nsets = py_get_int("nsets()")
	for i in range(1, nsets+1):
		# iterate through tow sets
		si = py_get_int("set_id(%d)" % i)
		sn = py_get_string("set_name(%d)" % si)
		# Create contact body for tow
		p("*new_cbody mesh *contact_option state:solid *contact_option skip_structural:off")
		p("*contact_body_name %s" % ("cb"+str(i)))
		p("*add_contact_body_elements")
		p(sn)
	return py_get_int("ncbodys()")

def cbody_index(ply_index):
	
	for k in ply_index.keys():
		for s in ply_index[k]:
			s = s.replace("tow","cb")
	return ply_index


def assign_orientation():
	p("*new_orient *orent_type edge23")
	p("*add_orient_elements")
	p("all_existing")


def load_tows():
	cwd = os.getcwd()
	f = "batched\\panel_double.dat"
	file_name = "\\".join([cwd,'dat_files',f])
	# file_name = "/".join([cwd,'tows.dat']) #for linux FS
	with open(file_name,'rb') as f:
		tows,ply = pickle.load(f)
	return tows,ply


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

	n_prev = py_get_int("nelements()")

	p("@set($convert_entities,surfaces)")
	p("@set($convert_surfaces_method,surface_faceted)")
	p("*set_curve_div_type_fix")
	p("*set_curve_div_type_fix_avgl")
	p("*set_curve_div_avgl %s" % str(el_size))
	p("*apply_curve_divisions")
	p("all_existing")
	p("*surface_faceted")
	p("all_existing") 

	# p("*renumber_surfaces")
	p("@set($automesh_surface_desc,facets)")
	p("@set($automesh_surface_family,mixed)")
	p("*pt_set_element_size %s" % str(el_size))
	p("*pt_quadmesh_surf")
	p("all_existing")

	# Create set for tow
	n_curr = py_get_int("nelements()")
	elements = [str(i) for i in list(range(n_prev+1,n_curr+1))]
	elements = " ".join(elements)
	p("*select_method_single")
	p("*select_elements")
	p("%s %s" % (elements, "#"))
	
	p("*store_elements")
	p(tow.name())
	p("*all_selected")

	p("*clear_geometry")
	p("select_clear")
	

def p(s):
    #print(s)
    py_send(s)


if __name__ == "__main__":
    main()
