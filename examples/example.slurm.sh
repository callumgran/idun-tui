#!/bin/sh

#SBATCH -N 1                                # Node count 
#SBATCH -c 20                               # CPU core count
#SBATCH -t 00-00:01:00                      # Upper time limit for the job (DD-HH:MM:SS)
#SBATCH --partition=GPUQ                    # Which queue the job should be posted in
#SBATCH --gres=gpu:a100:1                   # Processing unit type and amount (PROC_UNIT:MODEL:COUNT)
#SBATCH --mem=32G                           # How much memory (32G -> 32 gigabyte)
#SBATCH --job-name="Job name"               # The name of the job for finding it later
#SBATCH --output=model-output.txt           # Where stdout should be redirected, this should be specified when running the slurm job.
#SBATCH --nodelist=idun-<xx>-[xx]           # Which node to run the job on
#SBATCH --mail-user=email@ntnu.no           # Email to send the job status to
#SBATCH --mail-type=ALL                     # When to send the email (ALL, BEGIN, END, FAIL, REQUEUE, INVALID_DEPEND, STAGE_OUT, ...)
                                            # There are more options, see the documentation (https://slurm.schedmd.com/sbatch.html)

if [ $# -eq 0 ]; then                       # Basic check to see if there are any arguments
    echo "No file arguments"                # There needs to be a file inputted to run on
    exit 1
fi

file_path=$1                                # The file to run

WORKDIR=$(dirname $(realpath ${file_path})) # Working directory for the slurm job -> If you submit from home, workdir will be home 
cd ${WORKDIR}                               # Enter the working directory

module purge                                # Remove any existing module loaded
module load Anaconda3/2024.03               # Load the module which IDUN should use to run the code, Anaconda3 would be python etc.
                                            # module load intel/2023b could be used for running C or C++ code with a compiler

python $file_path                           # Perform the run command, for C one could use (intel compiler) icc $file_path -o main && ./main