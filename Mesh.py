import trimesh
from trimesh import Trimesh, visual
import numpy as np

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

    return outer_mesh


""" 
Projects down from tow points using vectors from FPM data
onto base mesh using similar method to project up
returns:    array mapping z_offset values to tow points
            array mapping base_mesh faces to z_offset array
"""
def project_tow_points(base_mesh, tow):
    tow_normals = tow.new_normals
    start_mesh = tow_mesh(tow)
    # tow_z_array = np.zeros((len(tow.new_pts),len(tow.new_pts[0])))
    project_normals = tow_normals * -1
    project_origins = tow.projection_origins(inner=False)
    tow_z_array = np.zeros_like(project_origins)
    next_pts = np.zeros_like(project_origins)

    base_mesh.merge_vertices()
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

    adjusted_z_array = outliers_rule(tow_z_array)
    adjusted_z_array = edge_offset_rule(adjusted_z_array)

    for i in range(len(adjusted_z_array)):
        tmp = np.where(adjusted_z_array[i] > tow.t/2)
        adjust_pts = np.where(adjusted_z_array[i] > tow.t/2)[0]
        offsets = tow_normals[adjust_pts]*adjusted_z_array[i][adjust_pts]
        next_pts[i][adjust_pts] = tow.new_pts[i][adjust_pts] + offsets
        tow.new_pts[i][adjust_pts] = next_pts[i][adjust_pts]
    
    # Mesh(base_mesh).visualize_mesh(tri_index,vector_origins=origins[vec_index], vector_normals=project_normals[vec_index], scale=10)
    
    return tow_z_array


"""  
Iterrates through Z array, and if a value does not equal its
surrounding values, will be equated to surrounding values (to avoid random outliers)
Currently loops thorugh, will find more efficient solution later
"""
# def outliers_rule(z):
#     numerical_error = 0.01
#     for i in range(1,len(z)-1):
#         for j in range(1,len(z[i])-1):
#             norm = np.linalg.norm
#             truth1 = norm(z[i,j] - z[i,j-1]) < numerical_error
#             truth2 = norm(z[i,j] - z[i,j+1]) < numerical_error
#             if(norm(z[i,j,-1] - z[i,j-1,-1]) < numerical_error) and (norm(z[i,j,-1] - z[i,j+1,-1]) < numerical_error):
#                 z[i,j] = z[i,j+1]
#     return z
def check_offset_distance(row, dist):
    offset_dist_norm = np.array([np.linalg.norm(i) for i in row])
    error_pts = np.where(offset_dist_norm > dist)
    row[error_pts] = np.array([0,0,0])
    return row
                    

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

# def offset_rule(z_values):
#     offset_z = z_values.copy()
#     length = len(z_values[0])
#     # points = np.array(tow.tow_points)
#     # normals = tow.new_normals

#     # Define corner point
#     offset_z[0,0] = max_z((z_values[0,0],z_values[1,0],z_values[0,1]))
#     offset_z[0,length-1] = max_z((z_values[0,length-1], z_values[1, length-1], z_values[0, length-2]))
#     offset_z[4, 0] = max_z((z_values[4, 1], z_values[3, 0], z_values[4, 0]))
#     offset_z[4, length-1] = max_z((z_values[4, length-1], z_values[3,length-1], z_values[4, length-2]))

#     # Define top edge (without corner points)
#     for i in range(5):
#         for j in range(length):
#             if [i, j] not in [[0, 0], [0, length-1], [4, 0], [4, length-1]]:        # not corner points
#                 if i == 0:      # top edge
#                     left_z = z_values[0, j-1]
#                     right_z = z_values[0, j+1]
#                     bot_z = z_values[1, j]
#                     current_z = z_values[i, j]
#                     offset_z[i,j] = max_z((left_z, right_z, bot_z, current_z))

#                 elif j == 0:        # left edge
#                     top_z = z_values[i - 1, 0]
#                     right_z = z_values[i, 1]
#                     bot_z = z_values[i + 1, 0]
#                     offset_z[i, j] = max_z((top_z, right_z, bot_z))

#                 elif j == length - 1:  # right edge
#                     left_z = z_values[i, j - 1]
#                     top_z = z_values[i - 1, j]
#                     bot_z = z_values[i + 1, j]
#                     offset_z[i, j] = max_z((top_z, bot_z, left_z))

#                 elif i == 4:       # bot edge
#                     left_z = z_values[4, j - 1]
#                     right_z = z_values[4, j + 1]
#                     top_z = z_values[3, j]
#                     current_z = z_values[i, j]
#                     offset_z[i, j] = max_z((left_z, right_z, top_z, current_z))

#                 else:               # mid points
#                     top_z = z_values[i-1, j]
#                     bot_z = z_values[i+1,j]
#                     left_z = z_values[i,j-1]
#                     right_z = z_values[i,j+1]
#                     offset_z[i,j] = max_z((top_z,bot_z,left_z,right_z))

#     return offset_z

"""
Checks the face normals projected up towards the tows
Utilises trimesh intersects_location ray tracing. Only detects first hit
returns: List of indexes for base_mesh faces that lie beneath tow
"""
def project_up(base_mesh, tow_mesh):

    mesh = base_mesh.mesh
    base_vectors = mesh.face_normals        #ray vectors
    base_origins = mesh.triangles_center    #ray origins - centroids of mesh faces
    locations, vec_index, tri_index = tow_mesh.ray.intersects_location(base_origins, base_vectors, multiple_hits=False)

    # Increment the z-offset value if the faces lie underneath a tow, this is refined later
    base_mesh.inc_z_off(vec_index)
    return vec_index
            
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

