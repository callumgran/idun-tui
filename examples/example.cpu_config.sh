#!/bin/bash

if [ "$#" -lt 6 ]; then
	echo "Usage: $0 <python_script> <output_file> <time> <mem> <job_name> <nodes> [mail]"
	exit 1
fi

python_script=$1
output_file=$2
time=$3
mem=$4
job_name=$5
nodes=$6
mail=$7

nodes_option=""
if [ "$nodes" != "any" ]; then
    nodes_option="#SBATCH --nodelist=${nodes}"
fi

mail_option=""
if [ -n "$mail" ]; then
    mail_option="#SBATCH --mail-user=${mail}
#SBATCH --mail-type=ALL"
fi

script_dir=$(dirname "$(realpath "$python_script")")
script_basename=$(basename "$python_script")

sbatch <<EOF
#!/bin/sh
#SBATCH --output=${output_file}
#SBATCH -N 1
#SBATCH -c 1
#SBATCH -t ${time}
#SBATCH --partition=CPUQ
#SBATCH --mem=${mem}
#SBATCH --job-name="${job_name}"
${nodes_option}
${mail_option}

cd ${script_dir}

module purge
module load Anaconda3/2024.02-1

python ${script_basename}
EOF