import glob
import subprocess as sp
import os
from collections import defaultdict
import time

def managing_job(workdir,jobid):
	# Go to work directory
	os.chdir(workdir)
	while True:
		# keep monitoring
		dirs=glob.glob(os.path.join(workdir,"supercell-*.in"))
		# total number of displacements that need to be computed
		ndisp = len(dirs) 
		# 1. Find out current job overall progress 
		dirs=glob.glob(os.path.join(workdir,"Si.abo"))
		# number of finished displacements
		ncurrent = len(dirs)
		if ncurrent == 0:
			ncurrent = 1
		print('{:.2f}'.format((ncurrent-1)/(ndisp))+' % finished')

		# Talk to slurm
		## query scheduler for running jobs
		cmd = os.path.expandvars("squeue -u $USER")
		piper = sp.Popen(cmd, stdout = sp.PIPE, stderr = sp.PIPE, shell = True)
		STAT_CODE = [ "PD","R","CG"]
		STAT_DESC = [ "pending","running","complet" ]
		## slurp off header line
		jobs = iter(piper.stdout.readline, "")
		_ = next(jobs)


		## loop on jobs
		counts = defaultdict(int)
		runtimes = defaultdict(list)
		for line in jobs:
			pieces = line.decode().strip().split()
			if not len(pieces):
				break
			counts[ pieces[2] ] += 1
		
		# number of jobs associated with this jobid
		# if zero, need to submit a new one
		if counts[jobid] == 0:
			f = open(os.path.join(workdir,"run.sh"),'r')
			lines = f.readlines()
			f.close()

			for i,lin in enumerate(lines):
				if '}' in lin:
					print(lin)
					break

			# update the new starting file
			lines[i]=("for i in {{{0:05d}..{1:05d}}}\n".format(ncurrent,ndisp))
			f = open(os.path.join(workdir,"run.sh"),'w')
			f.writelines(lines)
			f.close()
		time.sleep(1800)


if __name__ == "__main__":
	managing_job('/work2/09337/qcsong/frontera/nomad2phono3py/jobs/4961_1','4961_1')	 
	




