#%%
import h5py
import numpy as np
import phono3py
from gen_hdf5 import nx,ny,nz, mpid
from matplotlib.collections import LineCollection
import os
from dirs import *	#!
print('====start processhd5====')

# mpid = '149_1_dim2'	#1
job_dir = jobdir	#!
path = os.path.join(job_dir, str(mpid))	#!
T_index = 30 # temperature index, 30 = 300 K
#nx = 11
#ny = 11
#nz = 11
nTemp = 101 # temperature grid points
#%%

ph3 = phono3py.load(os.path.join(path, "phono3py_disp.yaml"))	#!


uc = ph3.unitcell
ph3.mesh_numbers = [nx, ny, nz]
name = ('{0:02}{1:02}{2:02}'.format(nx,ny,nz)) 
f1 = h5py.File(os.path.join(path, "kappa-m"+name+".hdf5"))	#!
f2 = h5py.File(os.path.join(path, "phonon-m"+name+".hdf5"))	#!

print(list(f1))
print(f1['grid_point'][:])
print(f1['gamma'][:].shape)
print(list(f2))
freq_ibz = f1['frequency'][:]
freq_full = f2['frequency'][:]
q_full = f2['grid_address'][:]
#print(freq_full.shape)
q_ibz = f1['qpoint'][:]		# irreducibl bz
q_ibz_integer = np.zeros(q_ibz.shape,dtype=int)
for i in range(len(q_ibz)):
	q_ibz_integer[i,0] = q_ibz[i,0]* nx		#  why do we multiply this?
	q_ibz_integer[i,1] = q_ibz[i,1]* ny
	q_ibz_integer[i,2] = q_ibz[i,2]* nz
#%%
# Mesh sampling grids in reciprocal space are generated with the specified numbers. This mesh is made along reciprocal axes and is always Gamma-centered. 

#Here the number of phonons may not be equal to product of mesh numbers (
#		). This is because all q-points on Brillouin zone boundary are included, i.e., even if multiple q-points are translationally equivalent, those phonons are stored separately though these phonons are physically equivalent within the equations employed in phono3py. Here Brillouin zone is defined by Wigner–Seitz cell of reciprocal primitive basis vectors. This is convenient to categorize phonon triplets into Umklapp and Normal scatterings based on the Brillouin zone.

nb = freq_full.shape[1]
omega_full_3d = np.zeros((nx,ny,nz,nb),dtype=int)
gamma_full_3d = np.zeros((nTemp,nx,ny,nz,nb),dtype=float)

for i in range(len(q_full)):
	idx = (ph3.grid.get_indices_from_addresses(q_full[i,:]))
	omega_full_3d[q_full[i,0],q_full[i,1],q_full[i,2],:]=freq_full[idx,:]
	f3 = h5py.File(os.path.join(path, "kappa-m"+name+"-g"+str(idx)+".hdf5"))	#!
	gamma_full_3d[:,q_full[i,0],q_full[i,1],q_full[i,2],:]=f3['gamma'][:]

import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator

x = np.arange(nx)
y = np.arange(ny)
z = np.arange(nz)
ibranch = 0
fig, axs = plt.subplots(1,2, figsize=(10, 5))
for ibranch in range(nb):
	interp_fw = RegularGridInterpolator((x, y, z), omega_full_3d[:,:,:,ibranch])	# Interpolationn of omega
	interp_fg = RegularGridInterpolator((x, y, z), gamma_full_3d[T_index,:,:,:,ibranch])	# Interpolationn of gamma

	GXx = np.linspace(0,(nx+1)//2,100)
	GXy = np.zeros(GXx.shape)
	GXz = np.zeros(GXx.shape)
	GX = np.array([GXx,GXy,GXz]).transpose()
	print(GX)


	# plt.figure(1)
	ax1 = axs[0]
	freqs = interp_fw(GX)
	ax1.plot(GXx,freqs)
	ax1.set_ylabel('Omega (THz)')
	# plt.figure(2)
	ax2 = axs[1]
	lwidths=interp_fg(GX)
	#points = np.array([freqs, lwidths]).T.reshape(-1, 1, 2)
	#segments = np.concatenate([points[:-1], points[1:]], axis=1)
	#lc = LineCollection(segments, linewidths=lwidths,color='blue')
	#fig,a = plt.subplots()
	#a.add_collection(lc)
	ax2.plot(GXx,lwidths)
	ax2.set_ylabel('Gamma (THz)')
fig.show()
fig.savefig(os.path.join(path, f'{mpid}_plot{nx}{ny}{nz}.png'))

#%%



