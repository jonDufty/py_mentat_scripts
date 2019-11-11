import os
import glob
import subprocess

# dir = os.path.join(os.getcwd(), 

for job in glob.glob('*.dat'):
	print(job)

	args = ["run_marc", "-jid", job, "-back", "yes"]
	proc = subprocess.Popen(args = args, shell=True)

	proc.wait()
	print(f"***JOB: {job} finished ***")

# for args in files:
# 	print(args)
# 	# proc.wait()