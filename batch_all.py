"""
Simple batch file that will run Import.py on all sollected test files,
Add/comment our the files you want to or don't want to run
Arguments:
1 + 2: Will always be python, Import.py
3: Test file name
4: [optional] stl file name
"""

import subprocess

files = [
	['python', 'Import.py', 'test_cylinder', 'test_cylinder.stl'],
	['python', 'Import.py', 'test_cylinder_45', 'test_cylinder.stl'],
	['python', 'Import.py', 'test_cylinder_8', 'test_cylinder.stl'],
	# ['python', 'Import.py', 'test_cross'],
	# ['python', 'Import.py', 'test_flat'],
	['python', 'Import.py', 'test_flat_8', 'flat.stl'],
	['python', 'Import.py', 'test_flat_090_6', 'flat.stl'],
	['python', 'Import.py', 'test_flat_quasi_16', 'flat.stl'],
	# ['python', 'Import.py', 'test_grid'],
	# ['python', 'Import.py', 'test_nozzle', 'nozzle.stl'],
	['python', 'Import.py','test_dome', 'dome.stl'],

]

for args in files:
	print(args)
	proc = subprocess.Popen(args = args, shell=True)
proc.wait()	
print("*** ALL DONE ***")

