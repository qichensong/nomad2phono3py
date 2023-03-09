import glob
import subprocess as sp
import os
from collections import defaultdict
import time
import re

def managing_job(workdir0,jobid):
	unfinished = 1
	# Go to work directory
	workdir = os.path.join(workdir0,jobid)
	os.chdir(workdir)
	while unfinished:
		# keep monitoring
		dirs=glob.glob(os.path.join(workdir,"supercell-*.in"))
		# total number of displacements that need to be computed
		ndisp = len(dirs) 
		# 1. Find out current job overall progress 
		dirs=glob.glob(os.path.join(workdir,"disp-*.abo"))
		# number of finished displacements
		ncurrent = len(dirs)
		if ncurrent == 0:
			ncurrent = 1
		print('{:.2f}'.format((ncurrent-1)/(ndisp)*100)+' % finished')

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
		# if zero, meaning that there is no active jobs
		# need to submit a new one
		if counts[jobid] == 0 and ncurrent > ndisp: 
			unfinished = 0
		if counts[jobid] == 0 and ncurrent <= ndisp:
			f = open(os.path.join(workdir,"run.sh"),'r')
			lines = f.readlines()
			f.close()

			for i,lin in enumerate(lines):
				if '}' in lin:
					break

			# update the new starting file
			lines[i]=("for i in {{{0:05d}..{1:05d}}}\n".format(ncurrent,ndisp))
			f = open(os.path.join(workdir,"run.sh"),'w')
			f.writelines(lines)
			f.close()
			finalinput = os.path.join(workdir,'disp-'+'{0:05d}'.format(ndisp)+'.abo')
			if os.path.exists(finalinput):
				f = open(finalinput,'r')
				lines = f.readlines()
				if re.search("Overall time",lines[-1]):
					unfinished = 1	
				else:
					os.system('sbatch run.sh')
			else:
				os.system('sbatch run.sh')

		# check job status every x seconds
		x = 600
		time.sleep(x)

def abo_done(workdir, idx):
    abo = os.path.join(workdir, ("disp-{0:05d}.abo".format(idx)))
    f = open(abo,'r')
    lines = f.readlines()
    for x in ['', '\n', ' \n']:
        if x in lines:
            lines.remove(x)
    # return lines[-1].startswith('+Overall')
    return re.search("Overall time",lines[-1])


def screen_incomplete(workdir0, jobid, run_job=False):
    workdir = os.path.join(workdir0,jobid)
    # keep monitoring
    dirs=glob.glob(os.path.join(workdir,"supercell-*.in"))
    # total number of displacements that need to be computed
    ndisp = len(dirs) 
    incomplete_list=[]
    for idx in range(1, ndisp+1):
        if not abo_done(workdir, idx):
            print("disp-{0:05d}.abo is not completed".format(idx))
            incomplete_list.append(idx)
            if run_job:
                f = open(os.path.join(workdir,"run.sh"),'r')
                lines = f.readlines()
                f.close()
                lines[i]=("for i in {{{0:05d}..{1:05d}}}\n".format(idx,idx))
                f = open(os.path.join(workdir,"run.sh"),'w')
                f.writelines(lines)
                f.close()
                os.system('sbatch run.sh')
    print('incomplete: ', incomplete_list)
		

if __name__ == "__main__":
	jobdir = '/work2/09337/qcsong/frontera/nomad2phono3py/jobs/'
	mpid = '149'
	managing_job(jobdir,mpid+'_1')	 
    	screen_incomplete(jobdir, f'{mpid}_1', run_job=True)	# check if all the jobs are completed and re-run if any of them is not perfect. 




