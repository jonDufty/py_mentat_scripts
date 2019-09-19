# Isolated tow class to accomodate py_mentat modules

class Tow_Mentat(object):
    def __init__(self,id, coords, off_L, off_R, t, w, ply=None):
        self._id = id
        self.pts = coords
        self.pts_L = off_L
        self.pts_R = off_R
        self.t = t
        self.w = w
        self.ply = ply

    def name(self):
        return "".join(['tow', str(self._id)])
    

class Point_Mentat():
    def __init__(self, arr):
        self._vec = arr

    @property
    def vec(self):
        return self._vec

    def send_coord(self):
        pts = [str(i) for i in self._vec]
        return " ".join(pts)
    