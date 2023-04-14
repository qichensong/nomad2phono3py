from utils.job_manage import managing_job
from utils.read_abo import screen_incomplete
from dirs import jobdir
mpid = '866291' #'149'
njob =6
managing_job(jobdir,mpid,njob)	 
screen_incomplete(jobdir, f'{mpid}', run_job=True)	# check if all the jobs are completed and re-run if any of them is not perfect. 

