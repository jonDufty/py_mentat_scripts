# Isolated tow class to accomodate py_mentat modules

class Tow_Mentat(object):
    def __init__(self,id, coords, off_L, in_L, off_R, in_R):
        self._id = id
        self.pts = coords
        self.pts_L = off_L
        self.index_L = in_L
        self.pts_R = off_R
        self.index_R = in_R

    def name(self):
        return "".join(['tow', str(self._id)])
    

class Point_Mentat():
    def __init__(self, arr):
        self._vec = arr

    @property
    def vec(self):
        return self._vec

    def send_coord(self):
        return " ".join(self._pt)
    