import subprocess

files = [
	['python', 'Import.py', 'test_cylinder', 'test_cylinder.stl'],
	['python', 'Import.py', 'test_cylinder_8', 'test_cylinder.stl'],
	['python', 'Import.py','test_dome', 'dome.stl'],
	['python', 'Import.py', 'test_cross'],
	['python', 'Import.py', 'test_flat'],
	['python', 'Import.py', 'test_flat_8'],
	['python', 'Import.py', 'test_flat_090_6'],
	['python', 'Import.py', 'test_flat_quasi_16'],
	['python', 'Import.py', 'test_grid'],
	['python', 'Import.py', 'test_nozzle', 'nozzle.stl'],

]

for args in files:
	print(args)
	proc = subprocess.Popen(args = args, shell=True)
	proc.wait()
print("*** ALL DONE ***")

