def mail_check(mail: bool, mail_types: str) -> str:
	mail_check = ""
	if mail:
		if mail_types == "":
			mail_types = "ALL"
		mail_check = f"""
if [ -n "$mail" ]; then
	mail_option="#SBATCH --mail-user=${{mail}}
#SBATCH --mail-type={mail_types}"
fi
		"""

	return mail_check

def node_line(nodes: str) -> str:
	node_line = ""
	if nodes != "":
		node_line = f"#SBATCH --nodelist={nodes}"

	return node_line

def generate_cpu_slurm_config(
	mail: bool = False,
	mail_types: str = "ALL",
	num_nodes: int = 1,
	num_cores: int = 1,
	nodes: str = ""
) -> str:
	"""
	Generate a CPU Slurm script template as a string.

	Parameters:
		mail (bool): Whether to send mail notifications.
		mail_types (str): A comma-separated string for the --mail-type option (e.g. "BEGIN,END,FAIL").
		num_nodes (int): Number of nodes for the job.
		num_cores (int): Number of cores per task.
		nodes (str): Specific node names (e.g., "idun-04-[01-02]") to be used in --nodelist.
					 If empty, the --nodelist line will still be present (set to an empty string).

	Returns:
		str: The full contents of the generated Slurm config.
	"""

	script = f"""#!/bin/bash

if [ "$#" -lt 5 ]; then
	echo "Usage: $0 <python_script> <output_file> <time> <mem> <job_name> [mail]"
	exit 1
fi

python_script=$1
output_file=$2
time=$3
mem=$4
job_name=$5
mail=$6

mail_option=""
{mail_check(mail, mail_types)}

script_dir=$(dirname "$(realpath "$python_script")")
script_basename=$(basename "$python_script")

sbatch <<EOF
#!/bin/sh
#SBATCH --output=${{output_file}}
#SBATCH -N {num_nodes}
#SBATCH -c {num_cores}
#SBATCH -t ${{time}}
#SBATCH --partition=CPUQ
#SBATCH --mem=${{mem}}
#SBATCH --job-name="${{job_name}}"
{node_line(nodes)}
${{mail_option}}

cd ${{script_dir}}

module purge
module load Anaconda3/2024.02-1

python ${{script_basename}}
EOF
"""
	return script

def generate_gpu_slurm_config(
	mail: bool = False,
	mail_types: str = "ALL",
	num_nodes: int = 1,
	num_cores: int = 1,
	nodes: str = "",
	gpu_type: str = "any",
	num_gpus: int = 1
) -> str:
	"""
	Generate a GPU Slurm config as a string.

	Parameters:
		mail (bool): Whether to send mail notifications.
		mail_types (str): A comma-separated string for the --mail-type option (e.g. "BEGIN,END,FAIL").
		num_nodes (int): Number of nodes for the job.
		num_cores (int): Number of cores per task.
		nodes (str): Specific node names (e.g., "idun-04-[01-02]") to be used in --nodelist.
					 If empty, the --nodelist line will still be present (set to an empty string).
		gpu_type (str): The type of GPU to request (e.g., "a100"), default is "any".
		gpu_count (int): Number of GPUs to request.
					 
	Returns:
		str: The full contents of the generated Slurm config.
	"""

	script = f"""
#!/bin/bash

if [ "$#" -lt 5 ]; then
	echo "Usage: $0 <python_script> <output_file> <time> <mem> <job_name> [mail]"
	exit 1
fi

python_script=$1
output_file=$2
time=$3
mem=$4
job_name=$5
mail=$6

mail_option=""
{mail_check(mail, mail_types)}

script_dir=$(dirname "$(realpath "$python_script")")
script_basename=$(basename "$python_script")

sbatch <<EOF
#!/bin/sh
#SBATCH --output=${{output_file}}
#SBATCH -N {num_nodes}
#SBATCH -c {num_cores}
#SBATCH -t ${{time}}
#SBATCH --partition=GPUQ
#SBATCH --gres=gpu:{gpu_type}:{num_gpus}
#SBATCH --mem=${{mem}}
#SBATCH --job-name="${{job_name}}"
{node_line(nodes)}
${{mail_option}}

cd ${{script_dir}}

module purge
module load Anaconda3/2024.02-1

python ${{script_basename}}
EOF
"""
	return script