import glob
import subprocess as sp
import os
from collections import defaultdict
import time
import re
from datetime import datetime
from read_abo import abo_done, screen_incomplete
import numpy as np

def managing_job(workdir0,jobid,njob):
    starttime = datetime.now()
    unfinished = 1
    record = []
    workdir = os.path.join(workdir0,jobid)
    os.chdir(workdir)
    dirs=glob.glob(os.path.join(workdir,"supercell-*.in"))
    ndisp = len(dirs) 
    num_dict = {}
    num = ndisp//njob +1
    indices = range(1, ndisp+1)
    for i in range(njob):
        contents = sorted(list(indices[num*i:num*i+num]))
        if len(contents) != 0:
            num_dict[i]=contents
    njob_ = len(num_dict)
    unfinish_list = [True for i in range(njob_)]
    while unfinished:
        dirs=glob.glob(os.path.join(workdir,"disp-*.abo"))
        disp_indices = sorted([int(dir[-9:-4]) for dir in dirs])
        dirs_dict = {}
        for k in range(njob_):
            contents = num_dict[k]
            dirs_dict[k] = [] 
            for c in contents:
                if c not in disp_indices:
                    dirs_dict[k].append(c)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        ncurrent = len(dirs)
        if ncurrent == 0:
            ncurrent = 1
        print(f'[{current_time}] ({jobid}) ' +' {:.2f}'.format((ncurrent-1)/(ndisp)*100)+' % finished')
        record.append(f'[{now}] ({jobid}) ' +' {:.2f}'.format((ncurrent-1)/(ndisp)*100)+ f' % finished, remaining {dirs_dict}\n')		#!!
        with open(f'{workdir}/{jobid}_log_{starttime}.txt', 'w') as ff:
            for r in record:
                    ff.write(r)
        for j in range(njob_):
            if len(dirs_dict[j]) >0:
                unfinish_jobs = True
            else:
                unfinish_jobs = False
            unfinish_list[j] = unfinish_jobs
            cmd = os.path.expandvars("squeue -u $USER")
            piper = sp.Popen(cmd, stdout = sp.PIPE, stderr = sp.PIPE, shell = True)
            STAT_CODE = [ "PD","R","CG"]
            STAT_DESC = [ "pending","running","complet" ]
            ## slurp off header line
            jobs = iter(piper.stdout.readline, "")
            # print(jobs) 
            _ = next(jobs)
            # print(jobs) 


            ## loop on jobs
            counts = defaultdict(int)
            runtimes = defaultdict(list)
            for line in jobs:
                pieces = line.decode().strip().split()
                # print(pieces)   
                if not len(pieces):
                    break
                counts[ pieces[2] ] += 1
                # print(f'counts[ pieces[2] ]: for {pieces[2]}', counts[ pieces[2] ])
            # print(counts)   #!
            if counts[jobid+'_'+str(j)] == 0 and not unfinish_jobs:
                unfinish_list[j] = False
            elif counts[jobid+'_'+str(j)] == 0 and unfinish_jobs:
                a = jobid+'_'+str(j)
                # print(f'count ({a}): ', counts[jobid+'_'+str(j)]) #!
                f = open(os.path.join(workdir,f"run_{j}.sh"),'r')
                lines = f.readlines()
                f.close()

                for i,lin in enumerate(lines):
                    if '}' in lin:
                        break

                # update the new starting file
                idx_from = dirs_dict[j][0]
                idx_to = dirs_dict[j][-1]
                lines[i]=("for i in {{{0:05d}..{1:05d}}}\n".format(idx_from,idx_to))
                f = open(os.path.join(workdir,f"run_{j}.sh"),'w')
                f.writelines(lines)
                f.close()
                os.system(f'sbatch run_{j}.sh')
                # running_file.append(idx_from)

        # check job status every x seconds
        x = 30
        time.sleep(x)
		

if __name__ == "__main__":
    jobdir = '/work2/09337/qcsong/frontera/nomad2phono3py/jobs/'
    mpid = '149'
    njob = 6 
    managing_job(jobdir,mpid+'_1',njob)	 
    screen_incomplete(jobdir, f'{mpid}_1', run_job=True)	# check if all the jobs are completed and re-run if any of them is not perfect. 




