from material import material
from job_manage import managing_job

nomaddir='/work2/09337/qcsong/frontera/scf/'
jobdir='/work2/09337/qcsong/frontera/nomad2phono3py/jobs/'
psdir='/work2/09337/qcsong/frontera/ONCVPSP-PBEsol-PDv0.3/'
mpid = '21511' # 12 atom uc
mpid = '4961' # 5 atom uc
mpid = '1000' # 2 atomc uc
subid = '1'
queue='normal'
njob = 6    # number of parallel jobs
N=3
n=3
m1 = material(mpid,subid,nomaddir,jobdir,psdir)
m1.get_abinit_vars()
# nx, ny, nz
m1.gen_header(2,2,2)
m1.run_phono3py()
# -N nodes -n cores
m1.gen_job_scripts(N=N,n=n,P=queue)
m1.gen_job_scripts_multi(N=N,n=n,njob=njob,P=queue)
managing_job(jobdir,mpid+'_'+subid,njob)
