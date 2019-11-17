from py_mentat import *
from TowMentat import *
from Material import *
import pickle
import os
import winsound


def main():

	files = [
			# "test_flat",
			"test_flat_090_6",
			"test_flat_8",
			"test_flat_quasi_16",
			# 'test_cylinder',
			# 'test_cylinder_8',
			# 'test_cylinder_45',
			# 'test_dome',
			# 'test_weave',
		]

	print(files)

	for file_name in files:
		p("*new_model yes")
		save_file(file_name)
		generate_model(file_name)

	winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS)

def generate_model(file):

	plys = load_tows(file)
	print("geom = ", file, "plies = ", len(plys))
	for i in range(len(plys)):
		p("*store_elements")
		p("ply"+str(i+1))
		p("#")

	# General variables
	thick = plys[0].tows[0][0].t
	width = plys[0].tows[0][0].w
	'''
	'''

	for ply in plys:
		ply_name = "ply" + str(ply.id)
		for t in ply.tows:
			create_tow_shell(t)
			p("*store_elements")
			p(ply_name)
			p(t[0].name())
	p("*visible_elements")
	p("all_existing")
	
	assign_geometry(thick)

	standard_material(T300, "all_existing")

	assign_orientation()

	
	cb_index = cbody_index(plys)
	create_contact_bodies(plys)

	# ctable = edge_contact(cb_index, 0.1)

	contact_table(0.01)

	create_table(0,0.5)

	p("*save_model")

	return


def edge_contact(cb_index, tolerance):
	print("contact")
	ctable_name = "ct_edge_face"
	p("*new_contact_table")
	p("*contact_table_name %s" % ctable_name)
	p("*prog_option ctable:criterion:contact_distance")
	p("*prog_param ctable:contact_distance %f" % tolerance)
	p("*prog_option ctable:add_replace_mode:both")
	print("*prog_option ctable:add_replace_mode:both")
	p("*prog_option ctable:contact_type:glue")
	print("*prog_option ctable:contact_type:glue")
	p("@set($cta_crit_dist_action,list)")
	
	for c in cb_index.keys():
		cb = " ".join(cb_index[c])
		p("*ctable_add_replace_entries_body_list")
		print("*ctable_add_replace_entries_body_list")
		p("%s %s" % (cb, "#"))
		print("%s %s" % (cb, "#"))
		p("*interact_option retain_gaps:on")
	return ctable_name


def contact_table(tolerance):
	print("contact")
	ctable_name = "ct_edge_face"
	p("*new_contact_table")
	p("*contact_table_name %s" % ctable_name)
	p("*prog_option ctable:criterion:contact_distance")
	p("*prog_param ctable:contact_distance %f" % tolerance)
	p("*prog_option ctable:add_replace_mode:both")
	p("*prog_option ctable:contact_type:glue")
	p("@set($cta_crit_dist_action,all_pairs)")
	p("*ctable_add_replace_entries_all")
	p("*interact_option retain_gaps:on")


def assign_geometry(t):
	print("assign_geom")

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


def create_boundary(geometry):
	boundaries = {
		"flat": [
			"625 60 0",
			"625 5 0",
			"725 5 0",
			"725 60 0",
		]
	}
	boundary = boundaries[geometry]
	pi = py_get_int("npoints()")
	pts = " ".join(boundary)
	p("*add_points")
	p(pts)
	pf = py_get_int("npoints()")
	
	p("*set_curve_type polyline")
	p("*add_curves")
	pt_to_add = [str(i) for i in list(range(pi+1,pf+1))]
	pt_to_add.append(str(pi+1))
	p("%s #" % " ".join(pt_to_add))

	p("@set($expand_entities,curves)")
	p("*expand_remove")
	p("*set_expand_translation z 200")
	p("*expand_curves all_existing 1")

	p("@set($move_entities,surfaces)")
	p("@set($move_application,standard) *prog_option move:mode:translate")
	p("*set_move_translation z -100")
	p("*move_surfaces")
	p("all_existing")

	p("*store_surfaces")
	p("boundary")
	p("all_existing")



def create_contact_bodies(plys):
	p("*remove_empty_sets")
	nsets = py_get_int("nsets()")
	for i in range(1, nsets+1):
		# iterate through tow sets
		si = py_get_int("set_id(%d)" % i)
		sn = py_get_string("set_name(%d)" % si)
		if "ply" in sn:
			continue
		cn = sn.replace("tow","cb")
		# Create contact body for tow
		p("*new_cbody mesh *contact_option state:solid *contact_option skip_structural:off")
		p("*contact_body_name %s" % cn)
		p("*add_contact_body_elements")
		p(sn)
	return py_get_int("ncbodys()")


def cbody_index(plys):	
	cb_index = {}
	for p in plys:
		cb_index[p.id] = []
		for s in p.list_tows():
			cb_index[p.id].append(s.replace("tow","cb"))
	return cb_index


def assign_orientation():
	p("*new_orient *orent_type edge23")
	p("*add_orient_elements")
	p("all_existing")


def load_tows(file):
	cwd = os.getcwd()
	f = "batched\\"+file+".dat"
	file_name = "\\".join([cwd,'dat_files',f])
	# file_name = "/".join([cwd,'tows.dat']) #for linux FS
	with open(file_name,'rb') as f:
		ply = pickle.load(f)
	return ply

def save_file(file):
	print('*set_save_formatted off *save_as_model "%s.mud" yes' % file)
	p('*set_save_formatted off *save_as_model "%s.mud" yes' % file)


def generate_points(point):
    p(point.send_coord())


def generate_curve(pts):
	
	ni = int(py_get_float("npoints()"))
	p("*add_points")
	# for i in pts:
	# 	generate_points(i)
	if len(pts) < 200:
		pts_arr = [i.send_coord() for i in pts]
		pts_arr = " ".join(pts_arr)
		p(pts_arr)
	else:
		k = 0
		while(k < len(pts)):
			pts_arr = [i.send_coord() for i in pts[k:k+100]]
			pts_arr = " ".join(pts_arr)
			p(pts_arr)
			k += 100
		pts_arr = [i.send_coord() for i in pts[k:]]
		pts_arr = " ".join(pts_arr)
		p(pts_arr)

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

	# surf_set = "".join(["surf",str(tow_list[0]._id)])
	print(tow_list[0].name())
	total_divisions = sum([len(t.pts) for t in tow_list])

	p("*invisible_elements")
	p("all_existing")

	for tow in tow_list:
		print("trimmed =",tow.trimmed)
		el_size = tow.w*2/6
		curve_div = tow.w/2
		# Generate curves from points on L,R of tow path
		curves = ""
		for row in tow.pts:
			if len(row) == 0:
				continue
			curve = generate_curve(row)
			curves += (" "+curve)
		if curves == "":
			print("no points")
			return
		print(curves)
		# return
		# trim_boundary(curves)
		print("length of pts = ", " ".join([str(len(i)) for i in tow.pts]))
			
		# create surface using two guide curves
		print("surface")
		p("*set_surface_type skin")
		p("*set_trim_new_surfs y")
		p("*add_surfaces")
		p("%s %s" % (curves, '#'))
		
		n_divisions = max([len(t) for t in tow.pts])
		print("n_divisions = ", n_divisions)
		
		# continue
		if tow.trimmed == True:
			print("facet")
			p("@set($convert_surfaces_method,surface_faceted)")
			p("*set_convert_remove_original off")
			p("*set_curve_div_type_fix")
			p("*set_curve_div_type_fix_avgl")
			p("*set_curve_div_avgl %s" % str(curve_div))
			p("*apply_curve_divisions")
			p("all_existing")
			p("*surface_faceted")
			print("n surfaces ", py_get_int("nsurfaces()"))
			p("%s #" % py_get_int("nsurfaces()")) 
			# p("all_existing")
			p("@set($automesh_surface_desc,facets)")
			p("*pt_set_element_size %s" % str(el_size))
			if n_divisions < 4:
				p("@set($automesh_surface_family,tria)")
				p("*pt_trimesh_surf")
			else:
				p("@set($automesh_surface_family,mixed)")
				p("*pt_quadmesh_surf")
			p("all_visible")

		else:
			print("convert")
			
			
			if total_divisions > 1000:
				n_divisions *= 4
			

			p("@set($convert_entities,surfaces)")
			p("@set($convert_surfaces_method,convert_surface")
			p("*set_convert_uvdiv u %s" % str(n_divisions-1))
			p("*set_convert_uvdiv v %s" % str(len(tow.pts)-1))
			p("*convert_surfaces")
			p("%s #" % py_get_int("nsurfaces()"))

		p("*invisible_surface all_existing") 

	print("set")

	# Create set for tow
	# n_curr = py_get_int("nelements()")
	# elements = [str(i) for i in list(range(n_prev+1,n_curr+1))]
	# elements = " ".join(elements)
	# p("*select_method_single")
	# p("*select_elements")
	# p("%s %s" % (elements, "#"))
		
	# Sweep nodes to remove duplicates at batch boundary
	p("*set_sweep_tolerance 0.001")
	p("*sweep_nodes")
	p("*all_visible")
	
	p("*store_elements")
	p(tow.name())
	p("*all_visible")

	p("*clear_geometry")
	# p("*remove_pts")
	# p("all_existing")
	# p("*remove_curves")
	# p("all_existing")
	p("*invisible_elements")
	p("all_existing")
	
	p("select_clear")


def create_table(initial, final):
    p("*new_md_table 1 1")
    p("*set_md_table_type 1")
    p("time")
    p("*table_add")
    p("0 %s" % initial)
    p("1 %s" % final)
    p("*table_fit")
    return	

def p(s):
    #print(s)
    py_send(s)



