from material import material

nomaddir='/work2/09337/qcsong/frontera/scf/'
jobdir='/work2/09337/qcsong/frontera/nomad2phono3py/jobs/'
mpid = '21511'

mpid = '4961'
subid = '1'
m1 = material(mpid,subid,nomaddir,jobdir)
m1.get_abinit_vars()
m1.gen_header()
m1.run_phono3py(1,1,1)
# -N nodes -n cores
m1.gen_job_scripts(1,1)
