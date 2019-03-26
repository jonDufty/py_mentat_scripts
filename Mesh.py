from Vector import Vector

class Mesh:
    def __init__(self, points):
        self.points = points
        self.centroid = self.calc_centroid()
        self.offset = 0

    def midpoint(self,vec1,vec2):
        x = (vec1.i + vec2.i)/2
        y = (vec1.j + vec2.j)/2
        z = (vec1.k + vec2.k)/2
        return Vector(x,y,z)
    
    def calc_centroid(self):
        mid = self.midpoint(self.points[0], self.points[1])
        o = self.points[2]
        x = o.i + 2/3*(mid.i-o.i)
        y = o.j + 2/3*(mid.j-o.j)
        z = o.k + 2/3*(mid.k-o.k)
        return Vector(x,y,z)

    def under_tow(self):
        pass


