import glob
import subprocess as sp
import os
from collections import defaultdict
import time
import re
from datetime import datetime

# jobdir='/work2/09337/ryotaro/frontera/abinit_ro/nomad2phono3py/jobs/'
# mpid = '149'
# idx = 5

def abo_done(workdir, idx):
    abo = os.path.join(workdir, ("disp-{0:05d}.abo".format(idx)))
    if os.path.exists(abo):
        f = open(abo,'r')
        lines = f.readlines()
        for x in ['', '\n', ' \n']:
            if x in lines:
                lines.remove(x)
        # return lines[-1].startswith('+Overall')
        return re.search("Overall time",lines[-1])
    else:
        return False

def screen_incomplete(workdir0, jobid, run_job=False):
    unfinished = True
    record = []
    # Go to work directory
    workdir = os.path.join(workdir0,jobid)
    os.chdir(workdir)
    allfinish =False
    dirs=glob.glob(os.path.join(workdir,"supercell-*.in"))
    # total number of displacements that need to be computed
    ndisp = len(dirs) 
    while unfinished:
        incomplete_list=[]
        for idx in range(1, ndisp+1):
            if not abo_done(workdir, idx):
                incomplete_list.append(idx)
        incomplete_list=sorted(incomplete_list)
        if len(incomplete_list)==0:
            print('all jobs are complete!')
            allfinish=True
        else:
            allfinish=False
            idx_current = incomplete_list[0]
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        record.append(f'[{current_time}] ({jobid}) {incomplete_list}\n')
        print(f'[{now}] ({jobid}) incomplete: ', incomplete_list)
        with open(f'{workdir}/{jobid}_log_rerun.txt', 'w') as ff:
            for r in record:
                    ff.write(r)
        cmd = os.path.expandvars("squeue -u $USER")
        piper = sp.Popen(cmd, stdout = sp.PIPE, stderr = sp.PIPE, shell = True)
        STAT_CODE = [ "PD","R","CG"]
        STAT_DESC = [ "pending","running","complet" ]
        ## slurp off header line
        jobs = iter(piper.stdout.readline, "")
        _ = next(jobs)
        counts = defaultdict(int)
        runtimes = defaultdict(list)
        for line in jobs:
            pieces = line.decode().strip().split()
            if not len(pieces):
                break
            counts[ pieces[2] ] += 1

        if allfinish:
            unfinished = 0
        if counts[jobid] == 0 and not allfinish:
            if run_job:
                f = open(os.path.join(workdir,"run.sh"),'r')
                lines = f.readlines()
                f.close()
                for i,lin in enumerate(lines):
                    if '}' in lin:
                        break
                incomplete_seq = ''
                for idx in incomplete_list:
                    incomplete_seq += "{0:05d},".format(idx)
                lines[i]=("for i in {"+incomplete_seq[:-1]+"}\n")
                f = open(os.path.join(workdir,"run.sh"),'w')
                f.writelines(lines)
                f.close()
                os.system('sbatch run.sh')

        x = 90
        time.sleep(x)
        # print(unfinished)
