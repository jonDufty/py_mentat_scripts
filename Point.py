#Point class
from Vector import Vector
import numpy as np

class Point:
    pt_id = 0
    
    def __init__(self, coord, normal, dir):
        self._id = self._gen_id()
        self.coord = coord
        self.normal = normal
        self.dir = dir

    def _gen_id(self):
        """ 
        Increments the Class id variable
        """
        Point.pt_id += 1
        return Point.pt_id

    def copy_translate(self, v):
        """ 
        Copies a point by translating by a given coordinate by copying
        the original point
        
        Parameters
        ----------
        v : (3,1) array 
            translation vector
        
        """
        c = self.coord + v
        return c
    
    def move_translate(self, v):
        """ 
        Copies a point by translating by a given coordinate by modifying
        the original point
        
        Parameters
        ----------
        v (3,1) array - translation vector
        
        """
        new_v = self.coord + v
        return new_v

    # Creates new point for L/R offset
    def ortho_offset(self, offset):
        """Creates a new point offset in the transverse direction
        
        Parameters
        ----------
        offset : float
            offset magnitude
        
        Returns
        -------
        np.array(3,1)
            New coordinate vector
        """
        ortho = np.cross(self.normal,self.dir)
        ortho *= offset
        return self.copy_translate(ortho)

    