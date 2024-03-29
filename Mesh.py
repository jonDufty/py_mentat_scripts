import trimesh
from trimesh import Trimesh, visual
import numpy as np
import time
import os

class Mesh():
    """ 
    Wrapper class for trimesh with custom functions and bookeeping of global mesh
    Mostly helper functions, not heavily used at the moment
    """
    def __init__(self, mesh):
        self.mesh = mesh                #the Trimesh object


    @property
    def z_off(self):
        return self._z_off


    def visualize_mesh(self, faces_to_colour, vector_origins = [], vector_normals=[], scale=2.0):
        """ Debugging plot for visualizing intersecting faces and vectors
        
        Parameters
        ----------
        faces_to_colour : (n,1) array
            array of face indexes that need to be coloured differently
        vector_origins : (n,3) np.array
            set of vector origins to plot
        vector_normals : (n,3) np.array
            List of normal vectors corresponding to vector_origins
        scale: float, optional
            Amount to scale the vector normal plot by
        
        """


        mesh = self.mesh.copy()
        # unmerge so viewer doesn't smooth
        mesh.unmerge_vertices()
        # make base_mesh white- ish
        mesh.visual.face_colors = [105,105,105,105]
        mesh.visual.face_colors[faces_to_colour] = [255, 0, 0, 255]
        
        if vector_origins != [] and vector_normals != []:
            # stack rays into line segments for visualization as Path3D
            ray_visualize = trimesh.load_path(np.hstack((vector_origins, vector_origins + vector_normals*scale)).reshape(-1, 2, 3))
            ray_visualize.merge_vertices()
            scene = trimesh.Scene([mesh, ray_visualize])
        else:
            scene = trimesh.Scene([mesh])
        scene.show()



def tow_mesh(tow):
    """Creates mesh from tow coordinates to use for z offset projection
    Iterates through points and forms segments from outer points
    
    Parameters
    ----------
    tow : Tow object
        Tow object to be converted to mesh
    
    Returns
    -------
    Trimesh
        mesh representation of all points in tow
    """
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
        else:
            outer_mesh = outer_mesh.__add__(outer_mesh_segment)
    outer_mesh.merge_vertices()

    return outer_mesh

def detect_tow_drop(tow, base_mesh, hash_table):
    """
    Overall function for determining z offsets. Predominantly
    calls a number of sub functions. Operates by first checking if there
    is any intersections of the inner points, extracting those bodies into a
    separate mesh and then checking all intersections with this new mesh
    
    Parameters
    ----------
    tow : Tow object
        Incoming tow to be laid down
    base_mesh : Trimesh
        Existing mesh containing all currently laid tows
    hash_table: (n,1) integer array
        Lookup table of all faces in base mesh, associated to a particular mesh body 
    
    """
    
    # Determine if the inner points of the tow intersect (remove edge tolerance)
    tri_index = partial_project_tow(base_mesh, tow)
    
    # If no intersections, then the tows are adjacent or not in contact, so edge overlap is ignored
    if len(tri_index) == 0:
        return

    # If not, determine which tows it intersects with
    bodies = identify_tow_bodies(hash_table, tri_index.astype('int32'))
    print(bodies)

    # Create a new tow mesh to compare
    intersect_mesh = gen_intersecting_mesh(base_mesh, bodies)

    # Check if inner + outerpoints intersect with relevant tows to account for tow drops
    full_project_tow(intersect_mesh, tow)


""" 
"""
def gen_intersecting_mesh(base_mesh, bodies):
    """Generates mesh of tows that are intersecting with ray offset

    
    Parameters
    ----------
    base_mesh : Trimesh
        Mesh of exisiting tows already laid down
    bodies: set(int)
        Indexes of bodies intersecting with the new tow
    
    Returns
    -------
    Trimesh
        Subset of base_mesh, containing only the tows from bodies
        
    """
    
    # Create copy of mesh so to not change any face data
    mesh_copy = base_mesh
    # Body count should be equivalent to the number of tows - make sure not to merge vertices
    body_count = mesh_copy.body_count
    # Split mesh modies into individual tow meshes
    mesh_bodies = mesh_copy.split(only_watertight=False)
    if (len(bodies) is 0):
        return Trimesh()

    # Based on interesting bodies, create new mesh with only those bodies
    intersecting = Trimesh()
    for i in bodies:
        if intersecting.is_empty:
            intersecting = mesh_bodies[i-1]
        else:
            intersecting = intersecting.__add__(mesh_bodies[i-1])
        
    return intersecting


"""  

"""
def identify_tow_bodies(hash_table, tri_index):
    """Identifies tow bodies intersecting with tow based off tri_index and hash table.
    Hash table used for constant time lookup.
    Return as a set to remove duplicates
    
    Parameters
    ----------
    hash_table : list(int)
        lookup table of all faces in the base mesh and their corresponding bodies
    
    Returns
    -------
    Set(int)
        Set of intersecting bodies indexes (no duplicates)
    """
    

    bodies = hash_table[tri_index]
    return set(bodies)


"""  

"""
def partial_project_tow(base_mesh, tow):
    """Projects just the inner points (exluding edge points)
    These values are normally disregarded in edge-edge contact
    
    Parameters
    ----------
    base_mesh: Trimesh
        mesh of exisitng tows that have already been laid down
    tow : Tow object
        incoming tow to be projected down
    
    Returns
    -------
    np.array(n,1)
        array of all intersecting face indexes
    """
    
    tow_normals = tow.new_normals[1:-1,1:-1]
    project_origins = tow.projection_origins()[1:-1,1:-1]
    project_normals = tow_normals * -1

    # Cumulative index of triangles with ray intersectinos. Duplicates allowed
    all_tri_index = np.array([], dtype='int32')

    # Itterate through to find intersecting triangles. Other data not necessary
    for i in range(len(project_origins)):
        if len(project_origins[i]) == 0:
            continue
        try:
            tri_index, vec_index = base_mesh.ray.intersects_id(project_origins[i,:], project_normals[i,:], multiple_hits=False)
        except:
            tow.new_pts = np.array(tow.prev_pts)
            tow.get_new_normals()
            return partial_project_tow(base_mesh, tow)

        all_tri_index = np.append(all_tri_index,tri_index)

    return all_tri_index


"""  

"""
def full_project_tow(base_mesh, tow):
    """Projects all 5 rows of points against the relevant intersecting mesh
    With edge tows removed now, the edge values can be included
    
    Parameters
    ----------
    base_mesh: Trimesh
        mesh of exisitng tows that have already been laid down
    tow : Tow object
        incoming tow to be projected down
    
    Returns
    -------
    np.array(n,5,3)
        array of all offset vector for each tow point (redundant return)
    """

    tow_normals = tow.new_normals
    
    # Generate tow points above to project down. Inner=Fallse --> all points returned
    project_origins = tow.projection_origins()
    project_normals = tow_normals * -1

    # Create array to track offsets of each tow point
    tow_z_array = np.zeros_like(project_origins)

    for i in range(len(project_origins)):
        if len(project_origins[i]) == 0:
            continue

        locations, vec_index, tri_index = base_mesh.ray.intersects_location(project_origins[i,:], project_normals[i,:], multiple_hits=False)
        
        if(len(vec_index) == 0):
            return None
        
        offsets = tow_normals[i][vec_index]*tow.t
        new_locations = locations + offsets             #location of pts after offset
        offset_dist = new_locations - tow.new_pts[i][vec_index]     # Overall distance to offset from starting pt
        
        # Check offset distance against distance it was projected to check for 
        # outlier intersections (i.e a cylinder projecting against its inner surface)
        error_pts = check_offset_distance(offset_dist, tow.proj_dist)
        tow_z_array[i][vec_index] = offset_dist

    adjusted_z_array = offset_rule(tow_z_array)

    for i in range(len(adjusted_z_array)):
        adjusted_off_dist = np.linalg.norm(adjusted_z_array[i], axis=1)     #distance of offsets
        adjust_pts = np.where(adjusted_off_dist > tow.t/2)[0]               #Only adjust pts with non-zero offset
        offsets = adjusted_z_array[i][adjust_pts]
        tow.new_pts[i][adjust_pts] = tow.new_pts[i][adjust_pts] + offsets   #Update tow data with offsets

    return tow_z_array



def trim_boundary(tow, boundary_mesh):
    """Given a boundary mesh (must be watertight volume), removes any tow
    points that lie outside of this volumes.
    Breaks the points into start, middle and end. Where the middle points are rows
    that contain all 5 points within the boundary, start and end or the sets of points on
    either side. This is so as much of the mesh can be made uniform.
    
    Parameters
    ----------
    tow : Tow object
        incoming tow (already adjusted points)
    boundary_mesh : Trimesh
        Mesh of boundary volume. Must be watertight for contains function to work

    """
    start = []
    middle = []
    end = []
    print(len(tow.new_pts[0]))
    for i in range(len(tow.new_pts[0])):
        in_bounds = boundary_mesh.contains(tow.new_pts[:,i])
            
        if any(in_bounds == False):
            if len(middle) == 0:
                start.append(i)
            else:
                end.append(i)
        else:
            middle.append(i)
    
    if len(middle) <= 1:
        return 

    tow.trimmed_pts["middle"] = tow.new_pts[:,middle].tolist()

    # Add inside points to start an end so there is at least one point inside
    if len(start) > 0: 
        start.append(max(start) + 1)
        tow.trimmed_pts["start"] = boundary_intersect(tow.new_pts[:,start], boundary_mesh, start_flag=True)
    if len(end) > 0: 
        end.insert(0,min(end) -1)
        tow.trimmed_pts["end"] = boundary_intersect(tow.new_pts[:,end], boundary_mesh, start_flag=False)



def boundary_intersect(trim_array, boundary_mesh, start_flag=True):
    """Finds location of points interesecting with the boundary mesh,
    such that the trimming goes right up to the boundary.
    
    Parameters
    ----------
    trim_array : np.array((5,n,3))
        Point array of section with partial points outside of the boundary mesh
    boundary_mesh : Trimesh
        Boundary mesh volume
    start_flag : boolean
        Determines if the section is at the start or end of the tow to determine the 
        order to insert new points
    
    Returns
    -------
    np.array(5,n,3)
        Updated array of points including boundary intersecting points
    """

    trimmed_array = [[],[],[],[],[]]
    origins = []
    rays = []
    start = []
    end = []
    indexes = []

    for i in range(len(trim_array)):
        trim = []
        in_bound = np.where(boundary_mesh.contains(trim_array[i,:].tolist()) == True)[0]
        out_bound = np.where(boundary_mesh.contains(trim_array[i,:].tolist()) == False)[0]

        if len(out_bound) == 0 or len(in_bound) == 0:
            continue
        
        # Determine whether to insert new points at the start or end of the array.
        # Trim array contains one point on either side of the boundary, so create vector between points
        if start_flag is True:
            start.append(trim_array[i,min(in_bound)])
            end.append(trim_array[i,max(out_bound)])
        else:
            start.append(trim_array[i,max(in_bound)])
            end.append(trim_array[i,min(out_bound)])
        trimmed_array[i] = trim_array[i][in_bound].tolist()
        indexes.append(i)
    
    if len(start) == 0:
        return trimmed_array
    origins = np.array(start)
    rays = (np.array(end)-np.array(start)).tolist()
    
    # Determine intersection locations - project direcetion vector of end points
    location, vec, tri = boundary_mesh.ray.intersects_location(origins, rays, multiple_hits=False)
    for j in range(len(vec)):
        loc = location[j]
        i = vec[j]
        if start_flag is True:
            trimmed_array[i].insert(0,loc.tolist())
        else:
            trimmed_array[i].append(loc.tolist())

    return trimmed_array


"""  

"""
def check_offset_distance(row, dist):
    """Sanity check for revolute cases that may project into themselves
    Compares the intersection disatnce with the projection difference and ignores
    if they are too different
    
    Parameters
    ----------
    row : np.array(5,3)
        Single row of points
    dist : float
        Distance tolerance
    
    Returns
    -------
    np.array(5,3)
        adjusted row points
    """
    offset_dist_norm = np.array([np.linalg.norm(i) for i in row])
    error_pts = np.where(offset_dist_norm > dist)
    row[error_pts] = np.array([0,0,0])
    return row
                    

"""  

"""
def outliers_rule(z_array):
    """Iterrates through Z array, and if a value does not equal its
    surrounding values, will be equated to surrounding values (to avoid random outliers)
    Currently loops thorugh, will find more efficient solution later
    
    Parameters
    ----------
    z_array : np.array(5,n,3)
        Array of point offsets
    
    Returns
    -------
    np.array(5,n,3)
        adjusted z_array
    """

    new_z = z_array.copy()
    numerical_error = 0.01
    for i in range(len(z_array[0])):
        if abs(z_array[1][i][2] - z_array[2][i][2]) < numerical_error and abs(z_array[1][i][2] - z_array[3][i][2])< numerical_error:
            new_z[0][i][2] = z_array[2][i][2]
            new_z[4][i][2] = z_array[2][i][2]
    return new_z


def offset_rule(z_values):
    """Adjusts points to avoid sharp tow drop offs. Adjusts individual points
    to be equal to the maximum neighbouring point offset
    
    Parameters
    ----------
    z_values : np.array(5,n,3)
        Array of tow point offset vectors
    
    Returns
    -------
    np.array(5,n,3)
        Adjusted z array
    """
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
    """Finds the maximum offset magnitude from a list of vectors/arrays
    
    Parameters
    ----------
    vector_lists : np.array(n,3)
        List of neighbouring offset vectors
    
    Returns
    -------
    np,array(1,3)
        maximum offset vector
    """
    magnitude = []
    for i, j in enumerate(vector_lists):
        magnitude.append(np.linalg.norm(j))
    max_value = max(magnitude)
    index = magnitude.index(max_value)

    return vector_lists[index]

"""  

"""      
def adjacent(mesh,face):
    """Finds index's of faces adjacent to $face
    Possible REMOVE
    
    Parameters
    ----------
    mesh : Trimesh
        Mesh object to query
    face : int
        index of face to find adjacent faces of
    
    Returns
    -------
    np.array(n) : int
        List of adjacent face indices
    """
    
    faces = []
    for a in list(mesh.face_adjacency):
        if face in a:
            faces.append(a[a!=face][0])
    return np.array(faces)



def load_stl(stl_file, dir="stl_files"):
    """loads mesh object from a specified *.stl file
    
    Parameters
    ----------
    stl_file : string
        name of stl file
    dir : string, optional
        name of directory of stl_files (relative to Import.py directory)

    Returns
    -------
    Trimesh
        Imported mesh object
    """
    file = os.path.join(dir,stl_file)
    mesh_file = trimesh.load_mesh(file)
    return mesh_file


def transverse_adjust(tow, mesh):
    """If a base mesh is included, projects original points down onto that
    mesh to determine new origins. Essential for double curvature surfaces
    
    Parameters
    ----------
    tow : Tow 
        Tow object to be projected down
    mesh : Trimesh
        original mesh imported from STL file

    """

    normals = tow.new_normals
    project_normals = normals *-1
    project_origins = tow.projection_origins()
    mesh.merge_vertices()

    for i in range(len(tow.new_pts)):

        # Wrap intersection in try/except clause as revolute surfaces can throw an exception, in which
        # case it will revert to the uninterpolated points
        try:
            locations, vec_index, tri_index = mesh.ray.intersects_location(project_origins[i,:], project_normals[i,:], multiple_hits=False)
        except:
            tow.new_pts = np.array(tow.prev_pts)
            tow.get_new_normals()
            return transverse_adjust(tow, mesh)

        if len(tri_index) == 0:
            print('error: stl file and real tow data are not compatible')
        else:
            next_pts = np.copy(tow.new_pts[i])
            offset = normals[i]*tow.t/2
            next_pts[vec_index] = locations
            off_dist = np.linalg.norm(next_pts-tow.new_pts[i], axis=1)
            outliers = np.where(off_dist > 3*tow.t)
            next_pts[outliers] = tow.new_pts[i][outliers]

            tow.new_pts[i] = next_pts

