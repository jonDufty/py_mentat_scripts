import pickle
from Majestic.ImportMaj import tows
# from FPM.ImportFPM import tows

# Generalise data types in tow in separate class

file_name = 'tows.dat'
with open(file_name, 'wb') as f:
    pickle.dump(tows, f)

