import os
from dirs import *
import glob

# for simple commands
mpid = '149_1_dim2'
job_dir = jobdir
nx_sc = 2
ny_sc = 2
nz_sc = 2
nx = 19
ny = 19
nz = 19
if __name__ == "__main__":
    print('====start gen_hdf5====')
    path = os.path.join(job_dir, str(mpid))
    disps=sorted(glob.glob(os.path.join(path,"disp-*.abo")))
    disps = [disp for disp in disps if len(disp)==len(path)+15]
    os.system(f"cd {path}; phono3py --cf3 disp-{{00001..{format(len(disps), '05d')}}}.abo")     # output: FORCES_FC3
    print(path)
    # irreducible BZ, lss qpoints by taking the symmetry into account. 
    os.system(f"cd {path}; phono3py --abinit --dim=\""+str(nx_sc)+" "+str(ny_sc)+" "+str(nz_sc)+"\" -c pc.in --mesh=\""+str(nx)+" "+str(ny)+" "+str(nz)+"\" --sym-fc --br") 
    # --sym-fc: output=phono3py.yaml, fc3.hdf5, fc2.hdf5 / -br: output = kappa-mnxnynz.hdf5
    temp = ""
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                temp = temp+str(i)+" "+str(j)+" "+str(k)+" "
    print(temp)
    # full mesh of 3D qpoints
    os.system(f"cd {path}; phono3py --abinit --dim=\""+str(nx_sc)+" "+str(ny_sc)+" "+str(nz_sc)+"\" -c pc.in --mesh=\""+str(nx)+" "+str(ny)+" "+str(nz)+"\" --sym-fc --fc3 --fc2 --br --write-phonon --write-gamma --loglevel=2 --ga=\""+temp+"\"") 
