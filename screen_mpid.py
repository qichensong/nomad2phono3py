from utils.screen import *
from dirs import *

subid = '1'
ndim = 2
njob = 1    # number of parallel jobs
N=1
n=32
cluster='tacc'
queue='small'
maxdisps = None	# 3    # stop running job if certain number of disp-*abo are completed.
maxjobs = 5    # max number of jobs to submit at one time. 
screen='_'
generate_scripts=True
# the mpids which has already run in ryotaro's account. We exclude these from job lists. 
skips1 = sorted([1002124, 1087, 149, 1672, 21511, 315, 441, 5072, 632319, 866291, 
                10044, 1253, 149, 1700, 241, 370, 463, 571386, 684580, 9564, 
                10627, 1315, 1500, 2064, 30373, 370, 4961, 573697, 8455])
# the mpids which has already run in qcsong's account. We exclude these from job lists. 
skips2 = sorted([1000, 149, 21511, 22862, 22919, 406, 568560, 8062, 8455, 997618_1, 
                1022, 149, 2251, 22865, 2758, 422, 614603, 830, 866291, 
                1029, 2074, 22851, 22916, 2853, 4961, 682, 8454, 997618])
skips = []	#skips1+skips2

# prepare mpids to run
with open(mpids_file, 'r') as f:
    mpids = f.readlines()
mpids = sorted([int(mpid[:-1]) for mpid in mpids])[:10]
print(mpids)
print('mpid: ', len(mpids))
# mpids = sorted([int(mpid) for mpid in mpids if mpid <= get_median(mpids)])  # split the job into half for ryotaro and qcsong account. 
print(mpids)
print('mpid: ', len(mpids))

if generate_scripts:
    get_scripts(mpids,subid,nomaddir,jobdir,psdir,ndim,N,n,queue,screen=screen,njob=1,cluster=cluster)
screen_mpids(mpids, maxdisps, maxjobs, skips, jobdir, logs_dir, screen)
