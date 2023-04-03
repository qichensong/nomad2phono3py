from material import material
from job_manage import managing_job
from read_abo import abo_done
import os
import glob
import subprocess as sp
from collections import defaultdict
import time
import re
from datetime import datetime
import numpy as np
from get_supercells import get_median


def need_action(mpid, jobdir, maxdisps):    # check if the $maxdisps files of disp-*.abo are completed in one workdir
    workdir = os.path.join(jobdir,str(mpid))
    lst = os.listdir(workdir) 
    disps=glob.glob(os.path.join(workdir,"disp-*.abo"))
    score = 0
    for dfile in disps:
        idx = int(dfile[-9:-4])
        if abo_done(workdir, idx): # if disp-$idx.abo is completed
            score += 1
    return score<maxdisps

def get_scripts(mpids,subid,nomaddir,jobdir,psdir,ndim,N,n,queue,screen,njob=1):
    for mpid in mpids: 
        mpid = str(mpid)
        m1 = material(mpid,subid,nomaddir,jobdir,psdir)
        m1.get_abinit_vars()
        m1.gen_header(ndim,ndim,ndim)
        m1.run_phono3py()
        m1.gen_job_scripts(N=N,n=n,P=queue,screen=screen)
        m1.gen_job_scripts_multi(N=N,n=n,njob=njob,P=queue,screen=screen)

def screen_mpids(mpids, maxdisps, maxjobs, skips, jobdir, logs_dir, screen):
    unfinished = True
    record = []
    len_all = len(mpids)    # total num of mpids to run
    starttime = datetime.now()
    while unfinished:
        mpids_unfinished = []
        for mpid in mpids: 
            if int(mpid) not in skips:  # exclude mpids in skips
                if need_action(mpid, jobdir, maxdisps): # check if 
                    mpid = str(mpid)
                    mpids_unfinished.append(mpid)
        mpids_unfinished = sorted(mpids_unfinished)
        # print('unfinished mpids: ', len(mpids_unfinished))
        if len(mpids_unfinished)==0:
            unfinished=False
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
        running_jobs = sorted(list(counts.keys()))  # list of all running job names in sq
        xjobs = [jb[:len(screen)] for jb in running_jobs if jb.endswith(screen)]    # list of all job names submitted by this program (ends with X)
        job_dict = {mpid:[] for mpid in xjobs}
        cmd = os.path.expandvars("squeue -u $USER")
        piper = sp.Popen(cmd, stdout = sp.PIPE, stderr = sp.PIPE, shell = True)
        jobs = iter(piper.stdout.readline, "")
        _ = next(jobs)
        # List the JOBID(s) of each mpid.
        for line in jobs:
            pieces = line.decode().strip().split()
            if not len(pieces):
                break
            mpid_sq = pieces[2][:-2]    #mpid from job name
            sqid = int(pieces[0])   #JOBID in squeue
            if mpid_sq in xjobs:
                job_dict[mpid_sq].append(sqid)

        completions = {}    # show how many disp files are done for each of running mpids in sq.
        for mpid in xjobs:
            workdir = os.path.join(jobdir,mpid)
            ddirs=glob.glob(os.path.join(workdir,"disp-*.abo"))
            completions[mpid]=len(ddirs)
            if not need_action(mpid, jobdir, maxdisps):
                score = 0
                for dfile in ddirs:
                    idx = int(dfile[-9:-4]) # idx of disp files. 
                    if abo_done(workdir, idx):
                        score += 1

                if score >= maxdisps:   # if aassigned number of disp files are generated stop running the job.
                    print(f"[{mpid}] scancel {np.min([job_dict[mpid]])}")
                    os.system(f"scancel {np.min([job_dict[mpid]])}")

            
        print('job_dict: ', job_dict)
        # keep the record
        now = datetime.now()
        record.append(f'[{now}] {len(mpids_unfinished)} materials remaining. Done: {completions}\n')
        with open(f'{logs_dir}/log_{starttime}.txt', 'w') as ff:
            for r in record:
                ff.write(r)

        if len(xjobs) < maxjobs: # keep submitting the job up to $maxjobs.
            xmpids = [] # list of mpids meeting the conditions: (1) existing in mpids_unfinished (2) not existing in xjobs
            for mpid in mpids_unfinished:
                if str(mpid) not in xjobs:
                    xmpids.append(mpid)
            if len(xmpids)==0:
                pass
            else: 
                mpid = xmpids[0]
                print(mpid)
                workdir = os.path.join(jobdir,mpid)
                sdirs=glob.glob(os.path.join(workdir,"supercell-*.in"))
                os.chdir(workdir)
            
                # find from which disp-*.abo to run.
                idx_from = 1
                for idx in range(1, maxdisps+1):
                    if not abo_done(workdir, idx):  # find the first unfinished disp*abo file.
                        idx_from = idx
                        break
                    else: 
                        continue                 
                idx_to = len(sdirs)

                f = open(os.path.join(workdir,f"run_0.sh"),'r')
                lines = f.readlines()
                f.close()

                for i,lin in enumerate(lines):
                    if '}' in lin:
                        break
                lines[i]=("for i in {{{0:05d}..{1:05d}}}\n".format(idx_from,idx_to))
                f = open(os.path.join(workdir,f"run_0.sh"),'w')
                f.writelines(lines)
                f.close()
                print()
                os.system(f'sbatch run_0.sh')
        x = 60
        time.sleep(x)
        
if __name__=='__main__':
    mpids_file = '/work2/09337/ryotaro/frontera/abinit_ro/save/natm3_scf1.txt'
    nomaddir='/work2/09337/ryotaro/frontera/abinit_ro/scf/'
    jobdir='/work2/09337/ryotaro/frontera/abinit_ro/nomad2phono3py/jobs/'
    psdir = "/work2/09337/ryotaro/frontera/abinit_ro/ONCVPSP-PBEsol-PDv0.3/"
    logs_dir = '/work2/09337/ryotaro/frontera/abinit_ro/nomad2phono3py/logs/'
    subid = '1'
    ndim = 2
    njob = 1    # number of parallel jobs
    N=1
    n=1
    queue='small'
    maxdisps = 3    # stop running job if certain number of disp-*abo are completed.
    maxjobs = 3#20    # max number of jobs to submit at one time. 
    screen='Y'
    generate_scripts=False
    # the mpids which has already run in ryotaro's account. We exclude these from job lists. 
    skips1 = sorted([1002124, 1087, 149, 1672, 21511, 315, 441, 5072, 632319, 866291, 
                    10044, 1253, 149, 1700, 241, 370, 463, 571386, 684580, 9564, 
                    10627, 1315, 1500, 2064, 30373, 370, 4961, 573697, 8455])
    # the mpids which has already run in qcsong's account. We exclude these from job lists. 
    skips2 = sorted([1000, 149, 21511, 22862, 22919, 406, 568560, 8062, 8455, 997618_1, 
                    1022, 149, 2251, 22865, 2758, 422, 614603, 830, 866291, 
                    1029, 2074, 22851, 22916, 2853, 4961, 682, 8454, 997618])
    skips = skips1+skips2

    # prepare mpids to run
    with open(mpids_file, 'r') as f:
        mpids = f.readlines()
    mpids = sorted([int(mpid[:-1]) for mpid in mpids])
    print(mpids)
    print('mpid: ', len(mpids))
    # mpids = sorted([int(mpid) for mpid in mpids if mpid <= get_median(mpids)])  # split the job into half for ryotaro and qcsong account. 
    print(mpids)
    print('mpid: ', len(mpids))
    
    if generate_scripts:
        get_scripts(mpids,subid,nomaddir,jobdir,psdir,ndim,N,n,queue,screen=screen,njob=1)
    screen_mpids(mpids, maxdisps, maxjobs, skips, jobdir, logs_dir, screen)