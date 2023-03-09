from material import material
from job_manage import managing_job

nomaddir='/work2/09337/qcsong/frontera/scf/'
jobdir='/work2/09337/qcsong/frontera/nomad2phono3py/jobs/'
mpid = '21511' # 12 atom uc
mpid = '4961' # 5 atom uc
mpid = '1000' # 2 atomc uc
subid = '1'
m1 = material(mpid,subid,nomaddir,jobdir)
m1.get_abinit_vars()
# nx, ny, nz
m1.gen_header(2,2,2)
m1.run_phono3py()
# -N nodes -n cores
m1.gen_job_scripts(1,1,'normal')
m1.gen_job_scripts_multi(1,1,'normal')
managing_job(jobdir,mpid+'_'+subid)
