from dirs import *
import os

def completed_jobs(jobdir):
    jfolders = os.listdir(jobdir)
    print(jfolders)
    completed = []
    for jfolder in jfolders:
        jdir = os.path.join(jobdir, jfolder)
        print(jdir)
        nspcells = len(sorted([f for f in os.listdir(jdir) if f.startswith('supercell-') and f.endswith('.in') and len(f)==18]))
        ndisps = len(sorted([f for f in os.listdir(jdir) if f.startswith('disp-') and f.endswith('.abo')]))
        if ndisps >= nspcells:
            completed.append(jfolder)
    return completed

delete_heavy = False
jobdir_dict = {'jobs': jobdir, 'jobs2': jobdir2}
keys = list(jobdir_dict.keys())
completed1 = sorted(completed_jobs(jobdir))
print(f'completed in jobs/ ({len(completed1)}):', completed1)
completed2 = []
completed= completed1+completed2
print('total: ', len(completed))




