from utils.screen import *
from dirs import *

subid = '1'
ndim = 2
njob = 1    # number of parallel jobs
N=1
n=32
cluster='ornl'
queue='batch'
maxdisps = None	# 3    # stop running job if certain number of disp-*abo are completed.
maxjobs = 30    # max number of jobs to submit at one time. 
screen='X'
other_screens = ['_']
generate_scripts=False
all_jobdirs = [jobdir, jobdir2]
# the mpids which has already run in ryotaro's account. We exclude these from job lists. 
skips = []

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
    get_scripts(mpids,subid,nomaddir,jobdir2,psdir,ndim,N,n,queue,screen=screen,njob=1,cluster=cluster)
screen_mpids(mpids, maxdisps, maxjobs, skips, jobdir2, logs_dir, screen, queue, other_screens, all_jobdirs)
