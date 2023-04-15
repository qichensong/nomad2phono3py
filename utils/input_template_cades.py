input_template ="""#!/bin/bash
#SBATCH -J ${job}          # Job name
#SBATCH -o test.o%j       # Name of stdout output file
#SBATCH -e test.e%j       # Name of stderr error file
#SBATCH -p ${P}           # Queue (partition) name
#SBATCH -N ${N}               # Total # of nodes (must be 1 for serial)
#SBATCH -n ${n}              # Total # of mpi tasks (should be 1 for serial)
#SBATCH -t 14-00:00:00       # Run time (hh:mm:ss)
#SBATCH -A sns      # Project/Allocation name (req'd if you have more than 1)
#SBATCH --export=ALL
#SBATCH --mem=0

module purge
module load PE-intel/3.0
module load env/cades-virtues
LBDIR=/lustre/or-scratch/cades-virtues/proj-shared/abinit/opt
LBDIR=/lustre/or-scratch/cades-virtues/proj-shared/abinit/opt
export LD_LIBRARY_PATH=${LBDIR}/libxc/lib:${LBDIR}/hdf5/lib:${LBDIR}/netcdf-fortran/lib:${LBDIR}/netcdf-c/lib:${LD_LIBRARY_PATH}
export OMP_NUM_THREADS=1
ABINIT=/lustre/or-scratch/cades-virtues/proj-shared/abinit/src/abinit-9.8.3/virtues/src/98_main/abinit
"""
