from py_mentat import *

# Dimension
length = 400  # length
width = 80  # width
depth = 8  # depth

# Short beam shear specimen
# length = 24
# width = 8
# depth = 4

# Mesh division
h_mesh = 10
v_mesh = 2
nodes_per_ply = 33

# h_mesh = 6
# v_mesh = 2
# nodes_per_ply = 21

# Laminate
n_ply = 16
stack = [[0], [0], [45], [45], [90], [90], [-45], [-45], [-45], [-45], [90], [90], [45], [45], [0], [0]]
#stack = [[0], [0], [0], [0], [0], [0], [90], [90], [90], [90], [0], [0], [0], [0], [0], [0]]
t_ply = 1.0
is_solid = False

# Material properties
name = "T300"
E1 = 135e03
E2 = 7.5e03
E3 = 7.5e03
Nu12 = 0.25
Nu23 = 0.45
Nu31 = 0.0139
G12 = 3.5e03
G23 = 2.76e03
G31 = 3.5e03



# Create table (displacement)
initial = 0
final = 2

def main():
    p('*clear_geometry')
    p("*clear_mesh")
    create_shell(length, width, stack, t_ply, h_mesh, v_mesh, nodes_per_ply)
    #create_solid(length, width, stack, h_mesh, v_mesh, t_ply)
    standard_material(E1, E2, E3, Nu12, Nu23, Nu31, G12, G23, G31, name)
    composite(stack)
    create_table(initial, final)
    n = 1
    while n <= len(stack):
        p("*new_cbody mesh")
        p("*contact_option state:solid")
        p("*contact_option skip_structural:off")
        p("*add_contact_body_elements")
        p("ply%s" % n)
        n += 1
    p("*new_contact_table")
    p("*ctable_set_default_glued")
    p("@set($eltypemode,element)")
    p("*element_type 185")
    p("all_existing")
    return


def create_shell(length, width, stack, t_ply, h_mesh, v_mesh, nodes_per_ply):
    p("*add_points")
    p("%f %f 0" % (0, 0))
    p("%f %f 0" % (length, 0))
    p("%f %f 0" % (length, width))
    p("%f %f 0" % (0, width))
    p('*set_surface_type quad')
    p("*add_surfaces")
    p("1 2 3 4")
    n = 1
    while len(stack) > 1 and n < len(stack):          # duplicate surface one by one
        p("*set_duplicate_repetitions 1")
        p("*set_duplicate_translations")
        p("0 0 %f" % float((len(stack[n-1]) + len(stack[n])) * -t_ply/2))
        p("*duplicate_surfaces")
        p("%s" % n)
        p("# | End of List")
        n += 1
    p("*surfaces_solid")
    p("*regenerate")
    p("*set_convert_uvdiv u %s" % h_mesh)
    p("*set_convert_uvdiv v %s" % v_mesh)
    p("*convert_surfaces")
    p("all_existing")
    p("*select_method_flood")
    ply = 1
    node = 1
    while ply < len(stack) + 1:
        p("*select_elements")
        p("%s" % node)
        p("*store_elements")
        p("ply%s" % ply)
        p("all_selected")
        p("*select_clear_elements")
        node += nodes_per_ply
        ply += 1
    n = 1
    for i in stack:
        p("*new_geometry")
        p("*geometry_type mech_three_shell")
        p("*geometry_param thick %f" % float(len(i)*t_ply))
        p("*add_geometry_elements")
        p("ply%s" % n)
        n += 1
    return

def create_solid(length, width, stack, h_mesh, v_mesh, t_ply):
    p("*add_nodes")
    p("%f %f 0" % (0, 0))
    p("%f %f 0" % (length, 0))
    p("%f %f 0" % (length, width))
    p("%f %f 0" % (0, width))
    p('*set_element_type quad')
    p("*add_elements")
    p("1 2 3 4")
    ply = 1
    if len(stack) == 1:
        p("*set_expand_repetitions 1")
        p("*expand_remove")
        p("*set_expand_translations")
        p("0 0 %f" % float(-t_ply * n_ply))
        p("*expand_elements")
        p("%s" % 1)
        p("# | End of List")
        p("*select_method_user_box")
        p("*select_elements")
        p("%s %s" % (0, length))
        p("%s %s" % (0, width))
        p("%s %s" % (-len(stack[0]) - 0.1, 0.1))
        p("*store_elements")
        p("ply%s" % ply)
        p("all_selected")
        p("*select_clear_elements")
    else:
        i = 0
        while ply < len(stack) + 1:  # expand element one by one
            p("*set_expand_repetitions 1")
            p("*expand_shift")
            p("*set_expand_translations")
            p("0 0 %f" % float((len(stack[ply-1]) * -t_ply)))
            p("*expand_elements")
            p("%s" % 1)
            p("# | End of List")
            ply += 1
        p("*remove_elements")
        p("%s" % 1)
        p("# | End of List")
        ply = 1
        while ply < len(stack) + 1:
            p("*select_method_user_box")
            p("*select_elements")
            p("%s %s" % (0, length))
            p("%s %s" % (0, width))
            p("%s %s" % (-len(stack[ply - 1]) - i - 0.1, -i + 0.1))
            p("*store_elements")
            p("ply%s" % ply)
            p("all_selected")
            p("*select_clear_elements")
            i += len(stack[ply - 1])
            ply += 1
    p("*sub_divisions")
    p("%s %s 1" % (h_mesh, v_mesh))
    p("*subdivide_elements")
    p("all_existing")
    p("*sweep_all")
    p("*new_geometry")
    p("*geometry_type mech_three_solid_shell")
    p("*add_geometry_elements")
    p("all_existing")
    return

def composite(stack): 
    n = 1  # count the index of ply, because the same angle in stack will count the first index
    for i in stack:
        ply = 1
        p("*new_mater composite")
        p("*mater_option general:state:solid")
        p("*mater_option general:skip_structural:off")
        p("*mater_name composite_%s" % n)
        p("*mater_option general:compos_ply_thick:absolute")
        while ply < len(i) + 1:
            p("*mater_append_var_submat layers")
            p("T300")
            p("*mater_submat_param layers:%s general:compos_ply_thick %s" % (ply, t_ply))
            p("*mater_submat_param layers:%s general:compos_ply_orient_angle_deg %s" % (ply, i[ply - 1]))
            ply += 1
        p("*add_mater_elements")
        p("ply%s" % n)
        n += 1
    return

def standard_material(E1, E2, E3, Nu12, Nu23, Nu31, G12, G23, G31, name):
    p("*new_mater standard")
    p("*mater_option general:state:solid")
    p("*mater_option general:skip_structural:off")
    p('*mater_name ' + name)
    p("*mater_option structural:type:elast_plast_ortho")
    p("*mater_param structural:youngs_modulus1 %f" % E1)
    p("*mater_param structural:youngs_modulus2 %f" % E2)
    p("*mater_param structural:youngs_modulus3 %f" % E3)
    p("*mater_param structural:poissons_ratio12 %f" % Nu12)
    p("*mater_param structural:poissons_ratio23 %f" % Nu23)
    p("*mater_param structural:poissons_ratio31 %f" % Nu31)
    p("*mater_param structural:shear_modulus12 %f" % G12)
    p("*mater_param structural:shear_modulus23 %f" % G23)
    p("*mater_param structural:shear_modulus31 %f" % G31)
    return

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
	py_send(s)