from textual.binding import Binding

SSH_BASE_HOST = "idun-login1.hpc.ntnu.no"

REMOTE_MNT_HOST = "idun-samba1.hpc.ntnu.no"
REMOTE_MNT_DOMAIN = "WIN-NTNU-NO"

SUCCESS_COLOR = "#22af4b"
ERROR_COLOR = "#ee2524"
WARNING_COLOR = "#fee851"
INFO_COLOR = "#0f89ca"

PORT_COLOR = "#f05123"

GPU_TYPES = [("Any", "any"), ("P100", "p100"), ("V100", "v100"),
             ("A100", "a100"), ("H100", "h100")]

SLURM_CONFIG_BASE_PATH = "./slurm_configs"
SLURM_OUTPUT_BASE_PATH = "./slurm_output"

class UIBindings():
	def __init__(self):
		self.quit = Binding("ctrl+q", "quit", "Quit", tooltip="Quit the application", priority=False)
		self.home = Binding("h", "switch_to_home", "Home", tooltip="Go to the home screen", priority=False)
		self.history = Binding("ctrl+y", "switch_to_history", "History",tooltip="Go to the history screen", priority=False)
		self.slurm_config = Binding("s", "switch_to_slurm_config", "Slurm Config", tooltip="Go to the SLURM configuration creation screen", priority=False)
		self.run_slurm = Binding("j", "switch_to_run_slurm", "Run Slurm", tooltip="Go to the SLURM job submission screen", priority=False)
		self.request_node = Binding("n", "switch_to_node_request", "Request Node", tooltip="Go to the node request screen", priority=False)
		self.logout = Binding("ctrl+l", "logout", "Logout", tooltip="Logout and return to login screen", priority=False)
		self.bindings = [
			self.quit,
			self.home,
			self.history,
			self.slurm_config,
			self.run_slurm,
			self.request_node,
			self.logout
		]

	def get_bindings(self):
		return self.bindings