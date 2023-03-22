import os
import numpy as np
import re
import glob
from string import Template
from input_template import input_template

class material:
	def __init__(self, id, subid, dbasedir, destdir, psdir):
		# For example, mp-21511 has id = "21511", also material project id
		self.id = id
		self.subid = subid # usually 1
		self.dbasedir = dbasedir # work the nomad is
		self.destdir = destdir # directory to slurm job 
		self.psdir = psdir # directory of pseudopotential files
	def get_abinit_vars(self): 
        # We assume a linux file system
		self.dfiledir = os.path.join(self.dbasedir,'mp-'+self.id+'_scf_'+self.subid)
		f = open(os.path.join(self.dfiledir,'run.abi'),'r')
		lines = f.readlines()
		self.entries = {}
		for lin in lines:
			if (len(lin.split()))>1:
				if lin.split()[0]!='#':
					self.entries[lin.split()[0]] = lin.split()[1]
		# read k grids
		self.kgrid = np.zeros((3,),dtype=int)
		for lin in lines:
			if (len(lin.split()))>1:
				if lin.split()[0] == 'ngkpt':
					self.kgrid[:] = np.array(lin.split()[1:4],dtype=int)
					break
		# read k shifts
		self.kshift = np.zeros((3,),dtype=float)
		for i,lin in enumerate(lines):
			if lin.split() == ['shiftk']:
				self.kshift[:] = np.array(lines[i+1].split()[0:3],dtype=float)
				break

		# read positions
		self.natm = int(self.entries['natom']) # number of atoms
		self.pos = np.zeros((self.natm,3),dtype=float) # fractional coordinates

		# locate the postion section
		for i,lin in enumerate(lines):
			if lin.split() == ['xred']:
				break
		i = i + 1

		# save positions
		for j in range(i,i+self.natm):
			self.pos[j-i,:] = np.array(lines[j].split()[:],dtype=float)

		# locate the cell section
		for i,lin in enumerate(lines):
			if lin.split() == ['rprim']:
				break
		i = i + 1
		self.cell = np.zeros((3,3)) # lattice cell vectors
		for j in range(i,i+3):
			self.cell[j-i,:] = np.array(lines[j].split()[:],dtype=float)

		# locate the atom type section
		self.atype = np.zeros((self.natm,),dtype=int)
		if self.natm>3:
			for i,lin in enumerate(lines):
				if lin.split() == ['typat']:
					break
			i = i + 1
			for j in range(i,i-(self.natm//-3)):
				nc = len(lines[j].split())
				self.atype[(j-i)*3:(j-i)*3+nc] = np.array(lines[j].split()[:],dtype=int)
		else:
			for i,lin in enumerate(lines):
				if len(lin.split())>1:
					if lin.split()[0] == 'typat':
						self.atype[:] = np.array(lin.split()[1:self.natm+1])
						break



		# locate the charge of atom nucleus section
		self.ntypat = int(self.entries['ntypat'])
		self.z = np.zeros((self.ntypat,),dtype=int) # Z values in psps

		if self.ntypat>3:
			for i,lin in enumerate(lines):
				if lin.split() == ['znucl']:
					break
			i = i + 1

			for j in range(i,i-(self.ntypat//-3)):
				nc = len(lines[j].split())
				self.z[(j-i)*3:(j-i)*3+nc] = np.array(lines[j].split()[:],dtype=int)
		else:
			for i,lin in enumerate(lines):
				if len(lin.split())>1:
					if lin.split()[0] == 'znucl':
						self.z[:] = np.array(lin.split()[1:self.ntypat+1])
						break


		# PSEUDO part
		# read the pseudos part. Need to be modified for other type of psps
		for i,lin in enumerate(lines):
			if lin.split() == ['#<JSON>']:
				i1=i
				break
		for i,lin in enumerate(lines):
			if lin.split() == ['#</JSON>']:
				i2=i+1
				break
		linesJ = lines[i1:i2]
		
		newline = []
		for lin in linesJ:
			lin0 = re.sub(r"/global/u1/p/petretto/software/python/mendel/gp_phonons_matgen/codes/pseudo_dojo/pseudo_dojo/pseudos/ONCVPSP-PBEsol-PDv0.3/",
                 self.psdir,lin)
			newline.append(lin0)
		self.psJSON = newline 
		
		

	def gen_header(self,nx,ny,nz):
		# Supercell dimensions 
		self.nx = nx # supercell sizes for phono3py
		self.ny = ny
		self.nz = nz


		# self.workdir = os.path.join(self.destdir, self.id + '_' + self.subid)
		self.workdir = os.path.join(self.destdir, self.id)	#!
		os.system('mkdir -p '+self.workdir) # if not existing, create a new folder

		# Copy the files	
		os.system('cp '+os.path.join(self.dfiledir,'*')+' '+self.workdir)

		self.headerfile = os.path.join(self.workdir,'header.in')
		f = open(self.headerfile,'w')
		f.write('#################\n')
		f.write('paral_kgb 1\n') # parallel
		f.write('chkprim 0\n') # check primitive cell (default: 1)

		# Gaussian smearing
		#f.write('occopt 7\n')
		#f.write('tsmear 0.01\n')
		# end Gaussian smearing

		# tolvrs: The default value implies that this stopping condition is ignored.
		f.write('tolvrs 1.0d-10\n')
		f.write('pp_dirpath ' + f'\"{self.psdir}\"\n')
		# write pseudos
		f.write('pseudos \"')
		idx = np.zeros((self.ntypat,),dtype=int)
		ps = []
		for lin in self.psJSON:
			if re.search("path",lin):
				ps.append(re.split('/|\"|,',lin)[-3])

		count = -1
		for lin in self.psJSON:
			if re.search("\"Z\"",lin):
				ZZ = int(re.split(':|,',lin)[-2])
				count=count+1
				for i in range(self.ntypat):
					if ZZ == self.z[i]:
						idx[i]=count

		count = -1
		for lin in self.psJSON:
			if re.search("path",lin):
				count = count+1
				if count+1 == self.ntypat:
					f.write(ps[idx[count]])
				else:
					f.write(ps[idx[count]]+', ')
		f.write('\"\n')

		# misc settings
		keywd = ['ecut','nstep','nshiftk','nspinor','nspden','charge',
				'nsppol','kptopt','nbdbuf']
		for k in keywd:
			f.write(k+' '+self.entries[k]+'\n')

		# write nbands
		# larger cell, more bands
		f.write('nband '+str(int(self.entries['nband'])*nx*ny*nz)+'\n')

		# write shiftk
		f.write('shiftk\n')
		f.write('{: f} {: f} {: f}\n'.format(self.kshift[0],self.kshift[1],self.kshift[2]))

		# this part need to optimized according to number of atms in u.c.
		# read from .abi file first
		f.write('ngkpt {: d} {: d} {: d}\n'.format(self.kgrid[0]//nx,self.kgrid[1]//ny,self.kgrid[2]//nz))
		f.close()

		self.structfile = os.path.join(self.workdir,'pc.in')
		# This file shares the same header part except the k point grids
		os.system('cp '+self.headerfile+' '+self.structfile)

		# adding position info to the structure file
		f = open(self.structfile,'a')

		keywd = ['ntypat','natom']
		for k in keywd:
			f.write(k+' '+self.entries[k]+'\n')

		f.write('acell    1.0    1.0    1.0\n')
		# write positions
		f.write('xred\n')
		for i in range(self.natm):
			for j in range(3):
				f.write('{:.12f}   '.format(self.pos[i,j]))
			f.write('\n')
		# write cell vectors
		f.write('rprim\n')
		for i in range(3):
			for j in range(3):
				f.write('{:.12f}   '.format(self.cell[i,j]))
			f.write('\n')
		# write atom types
		f.write('typat\n')
		for i in range(-(self.natm//-3)):
			for j in range(3):
				if i*3+j<self.natm:
					f.write('{: d}  '.format(self.atype[i*3+j]))
			f.write('\n')
		# write nucleus charge
		f.write('znucl\n')
		for i in range(-(self.ntypat//-3)):
			for j in range(3):
				if i*3+j<self.ntypat:
					f.write('{: d} '.format(self.z[i*3+j]))
			f.write('\n')

		f.close()
		# make it executeble (not necessary)
		os.system('chmod +x '+ self.structfile)
	
	def run_phono3py(self):
		os.chdir(self.workdir)
        ## run phono3py 
		os.system("phono3py --abinit -d --dim=\""+str(self.nx)+' '\
				+str(self.ny)+' '+str(self.nz)+"\" -c " +self.structfile)
		##

		dirs=glob.glob(os.path.join(self.workdir,"supercell-*.in"))
		# total number of displacement files
		self.n_disp_tot = len(dirs)

	def gen_job_scripts(self,N,n,P):
		# The slurm job name
		# self.jobid = self.id+'_'+self.subid
		self.jobid = self.id# +'_'+self.subid	#!
		# Go to work directory 
		os.chdir(self.workdir)
		# The job should be monitored such that when old
		# jobs are finished, new jobs are submitted immediatedly
		template = Template(input_template)

		template = template.substitute(job=self.jobid,N=N,n=n,P=P)

		self.runscript = os.path.join(self.workdir,'run.sh')
		f = open(self.runscript,'w')
		f.write(template)
		f.write("for i in {{{0:05d}..{1:05d}}}\ndo\n".format(1,self.n_disp_tot))
		f.write("   cat header.in supercell-$i.in >| disp-$i.in;\n")
		if P=='small':
			f.write("   abinit disp-$i.in >& log\ndone\n")
		else:
			f.write("   ibrun abinit disp-$i.in >& log\ndone\n")
		f.close()
		
	def gen_job_scripts_multi(self,N,n,njob,P):	
		os.chdir(self.workdir)
		dirs=glob.glob(os.path.join(self.workdir,"supercell-*.in"))
		ndisp = len(dirs) 
		num_dict = {}
		num = ndisp//njob +1
		indices = range(1, ndisp+1)
		for i in range(njob):
			contents = sorted(list(indices[num*i:num*i+num]))
			if len(contents) != 0:
				num_dict[str(i)]=contents
		njob_ = len(num_dict)
		for idx in range(njob_):
			# self.jobid = self.id+'_'+self.subid + '_' + str(idx)
			self.jobid = self.id + '_' + str(idx)	#!
			start = num_dict[str(idx)][0] 
			end = num_dict[str(idx)][-1] 
			template = Template(input_template)
			template = template.substitute(job=self.jobid,N=N,n=n,P=P)
			self.runscript = os.path.join(self.workdir,f'run_{idx}.sh')
			f = open(self.runscript,'w')
			f.write(template)
			f.write("for i in {{{0:05d}..{1:05d}}}\ndo\n".format(start,end))
			f.write("   cat header.in supercell-$i.in >| disp-$i.in;\n")
			if P=='small':
				f.write("   abinit disp-$i.in >& log\ndone\n")
			else:
				# f.write(f"   mpirun -x {N*n} abinit disp-$i.in >& log\ndone\n")
				f.write(f"   ibrun abinit disp-$i.in >& log\ndone\n")
			f.close()



