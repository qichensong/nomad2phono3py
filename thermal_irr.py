#%%
import h5py
import numpy as np
import phono3py
from gen_hdf5 import nx,ny,nz, mpid
from matplotlib.collections import LineCollection
from matplotlib.cm import ScalarMappable
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
from dirs import *	#!
print('====start processhd5====')

# mpid = '149_1_dim2'	#1
job_dir = jobdir	#!
path = os.path.join(job_dir, str(mpid))	#!
T_index = 30 # temperature index, 30 = 300 K
nTemp = 101 # temperature grid points
#%%

ph3 = phono3py.load(os.path.join(path, "phono3py_disp.yaml"))	#!
uc = ph3.unitcell
ph3.mesh_numbers = [nx, ny, nz]
name = ('{0:02}{1:02}{2:02}'.format(nx,ny,nz)) 
f1 = h5py.File(os.path.join(path, "kappa-m"+name+".hdf5"))	#!
nx, ny, nz = f1['mesh'][:]
grid_point = f1['grid_point'][:]
gamma = f1['gamma'][:]
temp = f1['temperature'][:]
weight = f1['weight'][:]
t_max = temp.max()

print(list(f1))
print(grid_point)
print(gamma.shape)
freq_ibz = f1['frequency'][:]
q_ibz = f1['qpoint'][:]		# irreducible bz
q_ibz_integer = np.zeros(q_ibz.shape,dtype=int)
nb = freq_ibz.shape[-1]
for i in range(len(q_ibz)):
	q_ibz_integer[i,0] = q_ibz[i,0]* nx		#  why do we multiply this? -> to make fractional -> integer
	q_ibz_integer[i,1] = q_ibz[i,1]* ny
	q_ibz_integer[i,2] = q_ibz[i,2]* nz
#%%
Tm = temp[T_index]
gt = gamma[T_index]
g = np.where(gt > 0, gt, -1)
lifetime = np.where(g > 0, 1.0 / (2 * 2 * np.pi * g), 0)

#%%
b_idx = 0
fig, axs = plt.subplots(1,1, figsize=(6,6))
ax = axs
ax.scatter(np.linalg.norm(q_ibz, axis=-1), lifetime[:, b_idx])
fig.show()
fig.savefig(os.path.join(path, f'{mpid}_lifetime_{Tm}K_b{b_idx}.png'))

#%%
# band -dependent
gs = np.where(gamma > 0, gamma, -1)
lifetimes = np.where(gs > 0, 1.0 / (2 * 2 * np.pi * gs), 0)
cmap = mpl.cm.jet
for i in range(0, len(temp), 10):
	fig, ax = plt.subplots(1,1, figsize=(6,5))
	for b_idx in range(0, nb):
		t = temp[i]
		lifetime = lifetimes[i]
		pl=ax.scatter(np.linalg.norm(q_ibz, axis=-1), lifetime[:, b_idx], color=cmap(b_idx/nb), label=f'Band{b_idx}')
		# print(f'T={t}')
		ax.set_title(f'T={t}')
	ax.set_xlabel('$\|\|qpt\|\|$')
	ax.set_ylabel('lifetime [ps]')
	sm = plt.cm.ScalarMappable(cmap='jet', norm=plt.Normalize(vmin=0, vmax=nb-1))
	sm.set_array([])
	fig.colorbar(sm, ax=ax, label='band idx')
	fig.show()
	fig.savefig(os.path.join(path, f'{mpid}_lifetime_b_T{t}K.png'))


#%%
# Temperature-dependent lifetime check
gs = np.where(gamma > 0, gamma, -1)
lifetimes = np.where(gs > 0, 1.0 / (2 * 2 * np.pi * gs), 0)
for b_idx in range(nb):
	cmap = mpl.cm.jet
	fig, ax = plt.subplots(1,1, figsize=(6,5))
	for i in range(0, len(temp)):
		t = temp[i]
		lifetime = lifetimes[i]
		pl=ax.scatter(np.linalg.norm(q_ibz, axis=-1), lifetime[:, b_idx], color=cmap(t/t_max), label=f'T={t}')
		# print(f'T={t}')
		ax.set_title(f'Band{b_idx}')
	ax.set_xlabel('$\|\|qpt\|\|$')
	ax.set_ylabel('lifetime [ps]')
	sm = plt.cm.ScalarMappable(cmap='jet', norm=plt.Normalize(vmin=temp.min(), vmax=temp.max()))
	sm.set_array([])
	fig.colorbar(sm, ax=ax, label='Temp [K]')
	fig.show()
	fig.savefig(os.path.join(path, f'{mpid}_lifetime_T_b{b_idx}.png'))
 
#%%
# group velocity
gvel = f1['group_velocity'][:]	# (qpts, nb, 3) [THz Angstrom]
# heat capacity
hcap = f1['heat_capacity'][:]	# (temp, qpts, nb)
# thermal conductivity
kappa = f1['kappa'][:] 	# (temperature, 6 = (xx, yy, zz, yz, xz, xy)) [W/m-K]
# thermal conductivity
mkappa = f1['mode_kappa'][:] 	# (temperature, 6 = (xx, yy, zz, yz, xz, xy))
ku_conv = f1['kappa_unit_conversion'][()]
#gv_by_gv
gv_by_gv = f1['gv_by_gv'][:] # (irreducible q-point, nb, 6 = (xx, yy, zz, yz, xz, xy)) [THz^2 Angstrom^2]
# weight
weight = f1['weight'][:]

T_index = 30
a= ku_conv * hcap[T_index, 2, 0] * gv_by_gv[2, 0] / (2 * gamma[T_index, 2, 0])
b= ku_conv * hcap[T_index, 2, :] * gv_by_gv[2, :] / (2 * gamma[T_index, 2, :])
# c = ku_conv * hcap[30, :, :] * gv_by_gv[:, :] / (2 * gamma[30, :, :])
c = ku_conv * np.einsum('ij, ijk, ij -> ijk', hcap[T_index], gv_by_gv, 1/(2 * gamma[T_index, :, :]))
d = ku_conv * np.einsum('tij, ijk, tij -> tijk', hcap, gv_by_gv, 1/(2 * gamma))

#%%
# kappa vs mkappa
T_index = 30
idx = 0
tol = 1e-03
for T_index in range(len(temp)):
	for idx in range(nb):
		kappa1 = kappa[T_index][idx]
		kappa2 = mkappa[T_index, :, :, idx].sum()/ weight.sum()
		if np.abs(kappa1-kappa2) > tol:
			print(f'mismatchh at T={temp[T_index]}, band={idx}')

#%%
# kappa (mp-149)
from pymatgen.core.lattice import Lattice
lattice = np.array([[0.0000000000, 5.1318663114, 5.1318663114],
					[5.1318663114, 0.0000000000, 5.1318663114],
					[5.1318663114, 5.1318663114, 0.0000000000]])
lattice = Lattice(lattice)
vol = lattice.volume
hbar = 1.055e-34 # [Js]
kb = 1.380649e-23 # [JK-1]
kcum = 0
T_index = 30
Tm = temp[T_index]
for iq, q in enumerate(q_ibz):
	for ib in range(nb):
		omega = freq_ibz[iq, ib]
		v2 = gv_by_gv[iq, ib, :]
		gs = np.where(gamma > 0, gamma, -1)
		lifetimes = np.where(gs > 0, 1.0 / (2 * 2 * np.pi * gs), 0)
		tau = lifetimes[T_index]
		beta = 1/(kb*Tm)
		kcum += omega*v2*tau*(omega**2*beta)/(Tm**2*(np.exp(beta*hbar*omega)-1)**2)

out = kcum*hbar**3/(3*vol*kb)

#%%
from utils.load import load_band_structure_data
data_dir = './data'
raw_dir = './data/phonon'
data_file = 'DFPT_band_structure.pkl'
data = load_band_structure_data(data_dir, raw_dir, data_file)


#%%

