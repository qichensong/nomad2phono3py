import os
from os.path import join
mpids_file = '/work2/09337/ryotaro/frontera/abinit_ro/save/natm3_scf1.txt'
nomaddir='/work2/09337/ryotaro/frontera/abinit_ro/scf/'
psdir = "/work2/09337/ryotaro/frontera/abinit_ro/ONCVPSP-PBEsol-PDv0.3/"
savedir = '/work2/09337/ryotaro/frontera/abinit_ro/nomad2phono3py'
jobdir=join(savedir, 'jobs/')
jobdir2=join(savedir, 'jobs2/')
logs_dir = join(savedir, 'logs/')
if not os.path.exists(jobdir):
	os.makedirs(jobdir)
if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
