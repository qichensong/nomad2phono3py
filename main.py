from utils.material import material
from utils.job_manage import managing_job
from dirs import nomaddir, jobdir, psdir

mpid = '149' # 2 atomc uc
# mpid = '1000'
subid = '1'
queue='small'
cluster='tacc'
ndim = 2
njob = 3    # number of parallel jobs
N=1
n=32
m1 = material(mpid,subid,nomaddir,jobdir,psdir)
m1.get_abinit_vars()
# nx, ny, nz
m1.gen_header(ndim,ndim,ndim,cluster)
m1.run_phono3py()
# -N nodes -n cores
# m1.gen_job_scripts(N=N,n=n,P=queue)
m1.gen_job_scripts_multi(N=N,n=n,njob=njob,P=queue,cluster)
# managing_job(jobdir,mpid+'_'+subid,njob)
managing_job(jobdir,mpid,njob)
