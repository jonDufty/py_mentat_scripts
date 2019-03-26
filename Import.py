import pickle
from Majestic.ImportMaj import tows
# from FPM.ImportFPM import tows

file_name = 'tows.dat'
with open(file_name, 'wb') as f:
    pickle.dump(tows, f)

