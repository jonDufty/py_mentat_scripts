import trimesh
from trimesh import Trimesh, visual
import numpy as np
import time

""" 
Wrapper class for trimesh with custom functions and bookeeping of global mesh
"""
class Mesh():
    def __init__(self, mesh):
        self.mesh = mesh                #the Trimesh object
        self._z_off = self.__init_z()   #CAN REMOVE MAYBE

    def __init_z(self):
        return np.array([0]*len(self.mesh.faces)) #I know this is ugly but I had to force it to zero out

    @property
    def z_off(self):
        return self._z_off

    # Increments z offset mesh at faces index (can parse in array)
    def inc_z_off(self, index):
        self._z_off[index] += 1

    # Retrospectively adjusts the z_offset based on offset_rule
    def adjust_z_off(self, index, array):
        for i in range(len(index)):
            self._z_off[index[i]] = array[i]

    # debugging plot for visualing intersecting faces
    def visualize_mesh(self, faces_to_colour, vector_origins = [], vector_normals=[], scale=2.0):
        
        mesh = self.mesh.copy()
        # unmerge so viewer doesn't smooth
        mesh.unmerge_vertices()
        # make base_mesh white- ish
        mesh.visual.face_colors = [105,105,105,105]
        mesh.visual.face_colors[faces_to_colour] = [255, 0, 0, 255]
        
        if vector_origins != [] and vector_normals != []:
            # stack rays into line segments for visualization as Path3D
            ray_visualize = trimesh.load_path(np.hstack((vector_origins, vector_origins + vector_normals*scale)).reshape(-1, 2, 3))
            scene = trimesh.Scene([mesh, ray_visualize])
        else:
            scene = trimesh.Scene([mesh])
        scene.show()


"""  
Creates mesh from tow coordinates to use for z offset projection
Iterates through points and forms segments from outer points
Return: mesh object
"""
def tow_mesh(tow):
    outer_mesh = Trimesh()
    # inner_mesh = Trimesh()
    [L1, L2, L3, L4, L5] = tow.new_pts
    for i in range(len(tow.new_pts[0]) - 1):
        v1 = L5[i]  # vertices has to be anticlockwise
        v2 = L5[i + 1]
        v3 = L4[i + 1]
        v4 = L4[i]
        v5 = L3[i + 1]
        v6 = L3[i]
        v7 = L2[i + 1]
        v8 = L2[i]
        v9 = L1[i + 1]
        v10 = L1[i]
        outer_mesh_segment = Trimesh(vertices=[v1, v2, v3, v4,v5,v6,v7,v8,v9,v10], faces=[[0,1,2],[2,3,0],
                                                                                          [3,2,4],[3,4,5],
                                                                                          [5,4,6],[6,7,5],
                                                                                          [7,6,8],[8,9,7]])
        # inner_mesh_segment = Trimesh(vertices=[v5, v6, v7, v8], faces=[[0, 1, 2, 3]])
        if i == 0:
            outer_mesh = outer_mesh_segment
            # inner_mesh = inner_mesh_segment
        else:
            outer_mesh = outer_mesh.__add__(outer_mesh_segment)
            # inner_mesh = inner_mesh.__add__(outer_mesh_segment)
    outer_mesh.merge_vertices()

    return outer_mesh

def detect_tow_drop(tow, base_mesh, hash_table):
    
    start = time.clock()
    # Determine if the inner points of the tow intersect (remove edge tolerance)
    tri_index = partial_project_tow(base_mesh, tow)
    nextt = time.clock()
    print(f"----- time_partial = {nextt-start}")
    start = nextt
    # If no intersections, then the tows are adjacent or not in contact, so edge overlap is ignored
    if len(tri_index) == 0:
        return

    # If not, determine which tows it intersects with
    bodies = identify_tow_bodies(hash_table, tri_index.astype('int32'))
    print(bodies)
    nextt = time.clock()
    print(f"----- time_identify = {nextt-start}")
    start = nextt

    # Create a new tow mesh to compare
    intersect_mesh = gen_intersecting_mesh(base_mesh, bodies)
    nextt = time.clock()
    print(f"----- time_meshing = {nextt-start}")
    start = nextt

    # Check if inner + outerpoints intersect with relevant tows to account for tow drops
    full_project_tow(intersect_mesh, tow)
    nextt = time.clock()
    print(f"----- time_projecting = {nextt-start}")
    start = nextt


""" 
Generates mesh of tows that are intersecting with ray offset
"""
def gen_intersecting_mesh(base_mesh, bodies):
    # Create copy of mesh so to not change any face data
    mesh_copy = base_mesh
    # Body count should be equivalent to the number of tows - make sure not
    # To merge vertices
    body_count = mesh_copy.body_count
    # Split mesh modies into individual tow meshes
    mesh_bodies = mesh_copy.split(only_watertight=False)

    # Based on interesting bodies, create new mesh with only those bodies
    intersecting = Trimesh()
    for i in bodies:
        intersecting = intersecting.__add__(mesh_bodies[i-1])
    
    # intersecting.show()
    return intersecting


"""  
Identifies tow bodies intersecting with tow based off tri_index and hash table.
Hash table used for constant time lookup.
Return as a set to remove duplicates
"""
def identify_tow_bodies(hash_table, tri_index):
    bodies = hash_table[tri_index]
    return set(bodies)


"""  
Projects just the inner points (exluding edge points)
This values are normally disregarded in edge-edge contact
"""
def partial_project_tow(base_mesh, tow):
    tow_normals = tow.new_normals
    # Check whether the tow data is large enough to contain "inner pts"
    if len(tow.new_pts[0]) > 2:
        inner = True 
    else:
        inner=False
    
    # Create tow points above the surface to project 'down'
    # Inner = True --> Inner rows only, False --> All points
    project_origins = tow.projection_origins(inner=inner)
    if len(project_origins) == 0:
        return None
    
    # Adjust normal array to match project_origins
    project_normals = tow_normals * -1
    if inner is True:
        project_normals = project_normals[1:-1]
    
    # Cumulative index of triangles with ray intersectinos. Duplicates allowed
    all_tri_index = np.array([], dtype='int32')

    # Itterate through to find intersecting triangles. Other data not necessary
    for i in range(len(project_origins)):
        origins = project_origins[i][:]
        start = time.clock()
        vec_index, tri_index = base_mesh.ray.intersects_id(origins, project_normals, multiple_hits=False)
        print(f"----- time_ray = {time.clock() - start}")
        all_tri_index = np.append(all_tri_index,tri_index)

    return all_tri_index


"""  
Projects all 5 rows of points against the relevant intersecting mesh
With edge tows removed now, the edge values can be included
"""
def full_project_tow(base_mesh, tow):
    tow_normals = tow.new_normals
    
    # Generate tow points above to project down. Inner=Fallse --> all points returned
    project_origins = tow.projection_origins(inner=False)
    if len(project_origins) == 0:
        return None
    
    project_normals = tow_normals * -1
    
    # Create array to track offsets of each tow point
    tow_z_array = np.zeros_like(project_origins)

    for i in range(len(project_origins)):
        origins = project_origins[i][:]
        locations, vec_index, tri_index = base_mesh.ray.intersects_location(origins, project_normals, multiple_hits=False)
        
        if(len(vec_index) == 0):
            return None
        
        offsets = tow_normals[vec_index]*tow.t
        new_locations = locations + offsets         #location of pts after offset
        offset_dist = new_locations - tow.new_pts[i][vec_index]     # Overall distance to offset from starting pt
        
        # Check offset distance against distance it was projected to check for 
        # outlier intersections (i.e a cylinder projecting against its inner surface)
        error_pts = check_offset_distance(offset_dist, tow.proj_dist)
        tow_z_array[i][vec_index] = offset_dist

    # Adjust the z array for any transverse outliers
    adjusted_z_array = outliers_rule(tow_z_array)
    # adjusted_z_array = edge_offset_rule(adjusted_z_array)

    for i in range(len(adjusted_z_array)):
        adjusted_off_dist = np.linalg.norm(adjusted_z_array[i], axis=1)     #distance of offsets
        adjust_pts = np.where(adjusted_z_array[i] > tow.t/2)[0]             #Only adjust pts with non-zero offset
        offsets = adjusted_z_array[i][adjust_pts]   
        tow.new_pts[i][adjust_pts] = tow.new_pts[i][adjust_pts] + offsets   #Update tow data with offsets

    
    # Mesh(base_mesh).visualize_mesh(tri_index,vector_origins=origins[vec_index], vector_normals=project_normals[vec_index], scale=10)
    
    return tow_z_array


""" 
Projects down from tow points using vectors from FPM data
onto base mesh using similar method to project up
returns:    array mapping z_offset values to tow points
            array mapping base_mesh faces to z_offset array
"""
def project_tow_points(base_mesh, tow):
    tow_normals = tow.new_normals
    if len(tow.new_pts[0]) > 2:
        inner = True 
    else:
        inner=False
    project_origins = tow.projection_origins(inner=inner)
    if len(project_origins) == 0:
        return None
    
    project_normals = tow_normals * -1
    if inner is True:
        project_normals = project_normals[1:-1]
    
    tow_z_array = np.zeros_like(project_origins)
    next_pts = np.zeros_like(project_origins)

    # base_mesh.merge_vertices()
    for i in range(len(project_origins)):
        origins = project_origins[i][:]
        locations, vec_index, tri_index = base_mesh.ray.intersects_location(origins, project_normals, multiple_hits=False)
        
        if(len(vec_index) == 0):
            return None
        
        offsets = tow_normals[vec_index]*tow.t
        new_locations = locations + offsets
        offset_dist = new_locations - tow.new_pts[i][vec_index]
        error_pts = check_offset_distance(offset_dist, tow.proj_dist)
        tow_z_array[i][vec_index] = offset_dist

    if inner is True:
        tow_z_array = inner_edge_rule(tow_z_array, np.zeros_like(tow.new_pts))

    # adjusted_z_array = outliers_rule(tow_z_array)
    adjusted_z_array = offset_rule(tow_z_array)

    for i in range(len(adjusted_z_array)):
        tmp = np.where(adjusted_z_array[i] > tow.t/2)
        adjust_pts = np.where(adjusted_z_array[i] > tow.t/2)[0]
        offsets = tow_normals[adjust_pts]*adjusted_z_array[i][adjust_pts]
        # next_pts[i][adjust_pts] = tow.new_pts[i][adjust_pts] + offsets
        tow.new_pts[i][adjust_pts] = tow.new_pts[i][adjust_pts] + offsets
    
    # Mesh(base_mesh).visualize_mesh(tri_index,vector_origins=origins[vec_index], vector_normals=project_normals[vec_index], scale=10)
    
    return tow_z_array


"""  
Sanity check for revolute cases that may project into themselves
Compares the intersection disatnce with the projection difference and ignores
if they are too different
"""
def check_offset_distance(row, dist):
    offset_dist_norm = np.array([np.linalg.norm(i) for i in row])
    error_pts = np.where(offset_dist_norm > dist)
    row[error_pts] = np.array([0,0,0])
    return row
                    

"""  
Iterrates through Z array, and if a value does not equal its
surrounding values, will be equated to surrounding values (to avoid random outliers)
Currently loops thorugh, will find more efficient solution later
"""
def outliers_rule(z_array):     # Loop the columns
    new_z = z_array.copy()
    numerical_error = 0.01
    for i in range(len(z_array[0])):
        if abs(z_array[1][i][2] - z_array[2][i][2]) < numerical_error and abs(z_array[1][i][2] - z_array[3][i][2])< numerical_error:
            new_z[0][i][2] = z_array[2][i][2]
            new_z[4][i][2] = z_array[2][i][2]
    return new_z


"""
Checks each offset with neighbouring points to determine whether to include
it or not.
Returns index of array entries that were modified from the rul
"""
def edge_offset_rule(z_array):
    length = len(z_array[0])
    width = len(z_array)
    z_initial = z_array.copy()

    # Start with top row - index [0]
    z_array[0][[0,-1]] = z_array[1][[1,-2]] # corner pts first
    z_array[0][1:-2] = z_array[1][1:-2] #remaining top row

    # bottom edge
    z_array[-1][[0,-1]] = z_array[-2][[1,-2]] # corner pts first
    z_array[-1][1:-1] = z_array[-2][1:-1] #remaining pts

    #side edges
    z_array[1:-2][0] = z_array[1:-2][1] #left edge
    z_array[1:-1][-1] = z_array[1:-1][-2] #left edge

    # remaining points - can't use indexing so have to iterrate
    '''
    for i in range(width -1):
        j = 0
        for j in range(length - 1):
            top = z_array[i-1][j]
            bot = z_array[i+1][j]
            left = z_array[i][j-1]
            right = z_array[i][j+1]
            if j == 2: #middle row
                z_array[i][j] = max(top,bot,left,right)
            elif j ==1:
                z_array[i][j] = max(bot,left,right)
            else:
                z_array[i][j] = max(top,left,right)
    '''

    # return z_array == z_initial
    return z_array

def inner_edge_rule(inner_z, empty_z):
    empty_z[1:-1,1:-1] = inner_z[:,:]
    empty_z[1:-1,[0,-1]] = inner_z[:,[0,-1]] 
    empty_z[[0,-1],:] = empty_z[[1,-2],:] 
    return empty_z


def offset_rule(z_values):
    offset_z = z_values.copy()
    length = len(z_values[0])
    # points = np.array(tow.tow_points)
    # normals = tow.new_normals

    # Define corner point
    offset_z[0,0] = max_z((z_values[0,0],z_values[1,0],z_values[0,1]))
    offset_z[0,length-1] = max_z((z_values[0,length-1], z_values[1, length-1], z_values[0, length-2]))
    offset_z[4, 0] = max_z((z_values[4, 1], z_values[3, 0], z_values[4, 0]))
    offset_z[4, length-1] = max_z((z_values[4, length-1], z_values[3,length-1], z_values[4, length-2]))

    # Define top edge (without corner points)
    for i in range(5):
        for j in range(length):
            if [i, j] not in [[0, 0], [0, length-1], [4, 0], [4, length-1]]:        # not corner points
                if i == 0:      # top edge
                    left_z = z_values[0, j-1]
                    right_z = z_values[0, j+1]
                    bot_z = z_values[1, j]
                    current_z = z_values[i, j]
                    offset_z[i,j] = max_z((left_z, right_z, bot_z, current_z))

                elif j == 0:        # left edge
                    top_z = z_values[i - 1, 0]
                    right_z = z_values[i, 1]
                    bot_z = z_values[i + 1, 0]
                    offset_z[i, j] = max_z((top_z, right_z, bot_z))

                elif j == length - 1:  # right edge
                    left_z = z_values[i, j - 1]
                    top_z = z_values[i - 1, j]
                    bot_z = z_values[i + 1, j]
                    offset_z[i, j] = max_z((top_z, bot_z, left_z))

                elif i == 4:       # bot edge
                    left_z = z_values[4, j - 1]
                    right_z = z_values[4, j + 1]
                    top_z = z_values[3, j]
                    current_z = z_values[i, j]
                    offset_z[i, j] = max_z((left_z, right_z, top_z, current_z))

                else:               # mid points
                    top_z = z_values[i-1, j]
                    bot_z = z_values[i+1,j]
                    left_z = z_values[i,j-1]
                    right_z = z_values[i,j+1]
                    offset_z[i,j] = max_z((top_z,bot_z,left_z,right_z))

    return offset_z


def max_z(vector_lists):
    magnitude = []
    for i, j in enumerate(vector_lists):
        magnitude.append(np.linalg.norm(j))
    max_value = max(magnitude)
    index = magnitude.index(max_value)

    return vector_lists[index]

"""  
Finds index's of faces adjacent to $face
Possible REMOVE
"""      
def adjacent(mesh,face):
    faces = []
    for a in list(mesh.face_adjacency):
        if face in a:
            faces.append(a[a!=face][0])
    return np.array(faces)


"""  
Given a mesh, it uses subdivide() method iteratively until the minimum
mesh size is less than $min_length.
**Currently not used in main script but for mesh generation
"""
def subdivide_it(mesh, min_length):
        new_mesh = mesh
        while(min(new_mesh.edges_unique_length) > min_length):
            print(f"length = {min(new_mesh.edges_unique_length)} ... subdividing...") #debug print
            new_mesh = new_mesh.subdivide()
        return new_mesh

