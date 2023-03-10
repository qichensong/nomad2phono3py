input_template ="""#!/bin/bash
#SBATCH -J ${job}          # Job name
#SBATCH -o test.o%j       # Name of stdout output file
#SBATCH -e test.e%j       # Name of stderr error file
#SBATCH -p ${P}           # Queue (partition) name
#SBATCH -N ${N}               # Total # of nodes (must be 1 for serial)
#SBATCH -n ${n}              # Total # of mpi tasks (should be 1 for serial)
#SBATCH -t 48:00:00        # Run time (hh:mm:ss)
#SBATCH -A DMR21001      # Project/Allocation name (req'd if you have more than 1)
"""
