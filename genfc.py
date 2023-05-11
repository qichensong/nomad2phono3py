#%%
import os
from dirs import *	#!
import glob
import pandas as pd
import h5py
import numpy as np
import phono3py
import matplotlib as mpl
import matplotlib.pyplot as plt

# for simple commands
mpid = '149_1_dim2'
job_dir = jobdir
nx_sc = 2
ny_sc = 2
nz_sc = 2
nx = 19
ny = 19
nz = 19
move_files = False
run_phono3py = False
check_completion = True
process_kappa = True
process_fc = True

#%%

mpids1 = ['1000', '1002124', '1002164', '10044', '1008223', '1008786', '1009009', '1009127', '1009129', '1009220', '1009540', '1009750', '1009792', '1009813', '149', '2176', '22895', '252', '370', '406', '422', '463', '66', '682', '830']

mpids2 = ['1009819', '1009820', '1009894', '10627', '10653', '10680', '10695', '10760', '1087', \
    '1138', '11718', '1190', '1253', '1265', '13031', '13032', '13033', '13099', '1315', '1330', \
        '1342', '1415', '1479', '1500', '1519', '1541', '1550', '1639', '1672', '1700', '1778', '1784', \
            '1794', '1958', '19717', '1986', '20351', '2064', '21276', '2172', '2175', '2176', '2201', '2229', \
                '22851', '22862', '22865', '22867', '22875', '22895', '22898', '22899', '22901', '22903', '22905', \
                    '22906', '22913', '22914', '22916', '22919', '22922', '22925', '23167', '23193', '23197', '23231', \
                        '23251', '23259', '23268', '23289', '23295', '23299', '23302', '23303', '23703', '23870', '24084',\
                            '2469', '2472', '24721', '2490', '2534', '2600', '2605', '2624', '2667', '2691', '2693', '2758', \
                                '2853', '30373', '32880', '568560', '569639', '570354', '570891', '571102', '571222', '571386', \
                                    '573697', '614603', '632319', '684580', '8062', '8454', '8455', '866291', '997618']


#%%
if move_files:
    for mpid in mpids1:
        # mpid_dir = os.path.join(jobdir2, mpid)
        os.system(f'cd {jobdir}jobs/; cp -r {mpid}/ ..')
        os.system(f'ls -1 {jobdir}* | wc -l')
    for mpid in mpids2:
        os.system(f'cd {jobdir}/jobs2/; cp -r {mpid}/ ..')
        os.system(f'ls -1 {jobdir}* | wc -l')

#%%
with open('mpid_lists/natm2_scf1.txt', 'r') as f:
    # Read the contents of the file using readlines
    lines = f.readlines()

# Print the contents of the file
mpids_all =sorted([line[:-1] for line in lines])
print('mpids_all: ', mpids_all)

#%%
# run phono3py
if run_phono3py:
    print('run phono3py')
    data_dict = {'jobs': mpids1, 'jobs2': mpids2}
    # jobdir_dict = {'jobs': jobdir, 'jobs2': jobdir2}
    record_path = os.path.join(logs_dir, f'rec_p3py{nx}{ny}{nz}.txt')
    record = []
    for folder, mpids in data_dict.items():
        for mpid in mpids:
            # print('====start gen_hdf5====')
            mp_path = os.path.join(job_dir, str(mpid))
            print(mp_path)
            disps=sorted(glob.glob(os.path.join(mp_path,"disp-*.abo")))
            disps = [disp for disp in disps if len(disp)==len(mp_path)+15]
            forces_fc3=sorted(glob.glob(os.path.join(mp_path,"FORCES_FC3")))
            fc_hdf5=sorted(glob.glob(os.path.join(mp_path,"fc*hdf5")))
            if len(forces_fc3)<1:
                os.system(f"cd {mp_path}; phono3py --cf3 disp-{{00001..{format(len(disps), '05d')}}}.abo")     # output: FORCES_FC3
                print(f"cd {mp_path}; phono3py --cf3 disp-{{00001..{format(len(disps), '05d')}}}.abo")
            # irreducible BZ, lss qpoints by taking the symmetry into account. 
            if len(fc_hdf5)<2:
                os.system(f"cd {mp_path}; phono3py --abinit --dim=\""+str(nx_sc)+" "+str(ny_sc)+" "+str(nz_sc)+"\" -c pc.in --mesh=\""+str(nx)+" "+str(ny)+" "+str(nz)+"\" --sym-fc --br") 


#%%
# check completeness
# [1] FORCE_FC3
# [2] fc*.hdf5 (2 counts)
# [3]  kappa-mxxx.hdf5
# [4] phono3py*yaml (2 counts)

if check_completion:
    checklist = ['FORCES_FC3', 'fc3.hdf5', 'fc2.hdf5', 'phono3py_disp.yaml', 'phono3py_disp.yaml', f'kappa-m{nx}{ny}{nz}.hdf5']
    incomplete  = {mpid:[] for mpid in mpids_all}
    for mpid in mpids_all:
        mp_path = os.path.join(job_dir, str(mpid))
        all_files = os.listdir(mp_path)
        for check in checklist:
            if check not in all_files:
                incomplete[mpid].append(check)

    for mpid in mpids_all:
        value = incomplete[mpid]
        if len(value)==0:
            del incomplete[mpid]

    if len(incomplete)==0:
        print(f'all of {len(mpids_all)} materials are done!')
    else: 
        print(f'{len(incomplete)} materials has some issue: following files are missing')
        print(incomplete)


#%%
# open kappa-mxxx files, get data, assemble into one pandas dataframe
# if process_kappa:

# open kappa file

# dataframe

#%%
if process_kappa:
    df = pd.DataFrame({})
    for mpid in mpids_all:
        Data = dict()
        mp_path = os.path.join(job_dir, str(mpid))
        ph3 = phono3py.load(os.path.join(mp_path, "phono3py_disp.yaml"))
        uc = ph3.unitcell
        ph3.mesh_numbers = [nx, ny, nz]
        name = ('{0:02}{1:02}{2:02}'.format(nx,ny,nz)) 
        f1 = h5py.File(os.path.join(mp_path, "kappa-m"+name+".hdf5"))
        key_list = ['mesh', 'frequency', 'gamma', 'qpoint', 'temperature', 'grid_point', 'group_velocity','gv_by_gv','heat_capacity','kappa', 'mode_kappa', 'weight']
        Data['mpid'] = mpid
        for key in key_list:
            Data[key] = [f1[key][:]]
        Data['kappa_unit_conversion'] = f1['kappa_unit_conversion'][()]
        if process_fc:
            fc3 = h5py.File(os.path.join(mp_path, "fc3.hdf5"))  # ['fc3', 'p2s_map', 'version'] # ['force_constants', 'p2s_map', 'physical_unit', 'version']
            fc2 = h5py.File(os.path.join(mp_path, "fc2.hdf5")) # ['force_constants', 'p2s_map', 'physical_unit', 'version']
            Data['fc3'] = [fc3['fc3'][:]]
            Data['p2s_map_fc3'] = [fc3['p2s_map'][:]]
            Data['fc2'] = [fc2['force_constants'][:]]
            Data['p2s_map_fc2'] = [fc2['p2s_map'][:]]
            Data['physical_unit_fc2'] = fc2['physical_unit'][0]
        dfn = pd.DataFrame(data = Data)
        df = pd.concat([df, dfn], ignore_index = True)
    # df.to_csv(os.path.join(job_dir, 'anharmonic2.csv'), index=False)
    df.to_pickle(os.path.join(job_dir, 'anharmonic_fc_2.pkl'))
