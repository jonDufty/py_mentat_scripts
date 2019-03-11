#Joins points to create tow path
from Point import Point

class Tow():
    def __init__(self, tow_w):
        self.points = []
        self.w = tow_w

    def add_point(self, point):
        if point is None:
            return
        else:
            self.points.append(point)

    #Take tow path and offset in both directions perpendicular to direction vector
    def offset_points(self):
        x = []
        y = []
        for p in self.points:
            off_x = p.offset_pt_x
            off_x.scale(self.w)
            off_y = p.offset_pt_y
            off_y.scale(self.w)
            x.append(p.translate(off_x))
            y.append(p.translate(off_y))
        return [x,y]
            
              
        