"""  
Isolated classes for use with the Marc Mentat interface
Contian only point coordinate data and id metadata, so any package dependencies are remvoed
"""


class Ply_Mentat():
    def __init__(self, id, tows):
        self.id = id
        self.tows = tows

    def list_tows(self):
        tow_sets = []
        for t in self.tows:
            tow_sets.append(t[0].name())
        return tow_sets
        

class Tow_Mentat(object):
    def __init__(self,id, pts, t, w, ply=None, trimmed=False):
        self._id = id
        self.pts = pts
        self.t = t
        self.w = w
        self.ply = ply
        self.trimmed = trimmed

    def name(self):
        return "".join(['tow', str(self._id)])
    

class Point_Mentat():
    def __init__(self, arr):
        self._vec = arr

    @property
    def vec(self):
        return self._vec

    def send_coord(self):
        """ 
        Returns coordinates as a space separated string for input into Marc
        """
        pts = [str(i) for i in self._vec]
        return " ".join(pts)
    