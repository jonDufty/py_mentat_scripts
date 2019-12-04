class Ply():
    """Class representing ply structure
    More so relevant for ply based designs, but used for
    tow based designs as well.
    
    Attributes
    -------
    id: int
        generated id based on order of layup

    tows: List(Tow)
        Array of tow classes - initially empty
        
    """
    p_id = 0
    def __init__(self):
        self._id = self.gen_id()
        self.tows = []

    def gen_id(self):
       Ply.p_id += 1
       return Ply.p_id

    def add_tow(self, t):
        self.tows.append(t)

    

