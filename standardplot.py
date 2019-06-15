import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

a = np.array([0,0,0])
b = np.array([1,2,1])
c = np.array([3,3,3])
d = np.array([1,6,2])
e = np.array([7,3,2])

ar = np.array([a,b,c,d,e])
xx = ar[:,0]
yy = ar[:,1]
zz = ar[:,2]

fig = plt.figure()
ax = fig.add_subplot(111,projection='3d')


# x = np.linspace(0, 20, 100)  # Create a list of evenly-spaced numbers over the range
plt.scatter(xx, yy, zz)       # Plot the sine of each x point
plt.show()                   # Display the plot

