class Material():
	def __init__(self, name):
		self.name = name

class Orthotropic(Material):
	def __init__(self,E1, E2, E3, Nu12, Nu23, Nu31, G12, G23, G31, name):
		super().__init__(name)
		self.E1 = E1
		self.E2 = E2
		self.E3 = E3
		self.Nu12 = Nu12
		self.Nu23 = Nu23
		self.Nu31 = Nu31
		self.G12 = G12
		self.G23 = G23
		self.G31 = G31


# Initialise Materials
name = "T300"
E1 = 135e03
E2 = 7.5e03
E3 = 7.5e03
Nu12 = 0.25
Nu23 = 0.45
Nu31 = 0.0139
G12 = 3.5e03
G23 = 2.76e03
G31 = 3.5e03
T300 = Orthotropic(E1, E2, E3, Nu12, Nu23, Nu31, G12, G23, G31, name)

