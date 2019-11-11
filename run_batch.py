import os
import subprocess

for job in os.listdir('./'):
	print(job)

	args = ["run_marc", "-jid", job, "-back", "yes"]
	proc = subprocess.Popen(args = args, shell=True)

	proc.wait()
	print(f"***JOB: {job} finished ***")

# for args in files:
# 	print(args)
# 	# proc.wait()