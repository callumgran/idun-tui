# IDUN-TUI
A text-based user interface for the IDUN cluster at NTNU. The interface is designed to make it easier to interact with compute clusters, and to simplify generation of slurm jobs.

## Requirements
- Python
- UNIX environment

## Setting up mount.cifs to run passwordless ⚠️😵‍💫
- Find the path to mount.cifs by running `which mount.cifs` in terminal
- Run `sudo visudo` in terminal
- Add the following line to the end of the file:
```
<username> ALL=(ALL) NOPASSWD: /sbin/mount.cifs /bin/umount
```
Now you should be able to run mount.cifs without needing to enter your password, which is necessary for the remote file tree used when running slurm jobs.

## Installation
- Clone the repository
- Create a virtual environment by running `python -m venv venv`
- Activate the virtual environment by running `source venv/bin/activate`
- Run `pip install -r requirements.txt` to install dependencies
- Create a `.env` file based on `.env.example` and fill in the necessary information
- Run `python app/main.py` to start the interface

## Usage
- Use the arrow keys, tab or the mouse to navigate the interface
- Press enter to select an option
- Further you can access screens using the following shortcuts:
  - `h` to go to the home screen
  - `Ctrl + y` to go to the history screen
  - `s` to go to the slurm config creation screen
  - `j` to go to the jobs runner screen
  - `n` to go to the compute node request screen
  - `Ctrl + l` to logout and return to the login screen
  - `Ctrl + q` to quit the application

### Home screen
The home screen displays the current user and a table of current running jobs. If you have jobs that are currently running, you can select them in the table and perform the following operations:
- `r` to refresh the job table.
- `c` to cancel the selected job.
- `t` to setup a local tunnel to the selected node. This is useful if you want to use vscode remote ssh or similar.
- `Ctrl + t` to close the local tunnel to the node.
It is worth mentioning that tunnels are connected to compute nodes and not the job itself. This means that if you have multiple jobs running on the same node it will be the same tunnel.

### History screen
The history screen displays a table of all recent jobs that have been run by the user. At the moment there is no more functionality than to view the history. Although if any useful features are requested, feel free to open an issue or a pull request.

### Slurm config creation screen
In this screen you can create a slurm config file that can be used to run jobs on the cluster. The screen will guide you through the process of creating a config file, and will save the file in the `/cluster/home/<username>/slurm_configs` directory, in either `/cpu` or `/gpu` based on the config type. The config files themselves are intermediate shell files meant to be used in the <b>Run slurm job screen</b>. Examples of how the config files will look can be found in the `examples` directory.

### Jobs runner screen
In this screen you can run jobs on the cluster. The screen will guide you through the process of selecting a slurm config file, and will queue a slurm job on the cluster. The output files will be found in `slurm_logs` folder on IDUN. If you switch back to the home screen, you can view the job in the table.

### Compute node request screen
In this screen you can request a compute node on the cluster. The screen will guide you through the process of selecting a node type and the amount of nodes you want. The request will be sent to the cluster and you can view the status of the request in the home screen. Once a node has been allocated, you can use the `t` shortcut to setup a local tunnel to the node for further use.