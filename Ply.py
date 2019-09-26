class Ply():
    p_id = 0
    def __init__(self):
        self._id = self.gen_id()
        self.tows = []

    def gen_id(self):
       Ply.p_id += 1
       return Ply.p_id

    def add_tow(self, t):
        self.tows.append(t)

    

