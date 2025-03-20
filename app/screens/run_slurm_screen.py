import os
from textual.containers import Container, Horizontal
from textual.widgets import Label, Input, Button, Select, DirectoryTree
from app.screens.base_screen import BaseScreen
from textual import on
from app.config import SUCCESS_COLOR, ERROR_COLOR, SLURM_CONFIG_BASE_PATH

class FilteredDirectoryTree(DirectoryTree):
	"""Custom DirectoryTree that filters out dotfiles and dot-directories."""

	def filter_paths(self, paths):
		"""Exclude files and directories that start with '.'"""
		return [path for path in paths if not path.name.startswith(".")]

class RunSlurmJobScreen(BaseScreen):
	"""Screen for running Slurm jobs based on a saved configuration."""

	def __init__(self):
		super().__init__()

		self.configs = []

		self.config_type = Select(
			[("All", "all"), ("CPU", "cpu"), ("GPU", "gpu")], id="config-type"
		)

		self.config_file = Select(self.configs, id="config-file")

		self.time_input = Input(
			placeholder="Hours", id="time-input"
		)
		self.memory_input = Input(
			placeholder="Memory (e.g., 64G)", id="memory-input"
		)
		self.output_file = Input(
			placeholder="Output file name (will override)", id="output-file"
		)
		self.job_name = Input(
			placeholder="Job name", id="job-name"
		)

		self.remote_home = self.app.context.mount_remote_home()

		self.remote_directory_tree = FilteredDirectoryTree(
			self.remote_home, id="remote-directory-tree"
		)

		self.run_button = Button("Run Job", id="submit")
		self.selected_file_path = None

	def compose(self):
		"""Construct the UI layout."""
		yield from super().compose(
			Container(
				Horizontal(Label("Config Type:"), self.config_type),
				Horizontal(Label("Config File:"), self.config_file),
				Horizontal(Label("Time (Hours):"), self.time_input),
				Horizontal(Label("Memory:"), self.memory_input),
				Horizontal(Label("Output File:"), self.output_file),
				Horizontal(Label("Job Name:"), self.job_name),
				Horizontal(self.remote_directory_tree),
				Horizontal(self.run_button),
				id="slurm-run-container"
			),
		)

	def on_mount(self):
		"""Load available Slurm configs & remote directory tree on mount."""
		# self.load_slurm_configs()

	@on(Select.Changed)
	def handle_config_type_change(self, event: Select.Changed):
		"""Reload config files when the user changes the config type."""
		if event.select.id == "config-type":
			self.load_slurm_configs()
			pass
	
	@on(DirectoryTree.FileSelected)
	def handle_file_selected(self, event: DirectoryTree.FileSelected):
		"""Handle file selection event and store the selected path."""
		self.selected_file_path = event.path 
		self.update_status(f"Selected file: {self.selected_file_path}")

	def load_slurm_configs(self):
		"""Fetch available Slurm configuration files from the remote system."""
		config_type = self.config_type.value
		search_path = f"{SLURM_CONFIG_BASE_PATH}/{config_type}" if config_type in ["cpu", "gpu"] else f"{SLURM_CONFIG_BASE_PATH}/cpu"

		try:
			output = self.app.context.run_command(f"ls {search_path}/*.slurmconfig")
			config_files = [os.path.basename(f) for f in output.split("\n") if f.strip()]
			self.config_file.set_options([(f, f) for f in config_files])
		except Exception as e:
			self.update_status(f"Error loading configs: {e}", color=ERROR_COLOR)

	@on(Button.Pressed)
	def handle_run_job(self, event: Button.Pressed):
		"""Handle running the Slurm job."""
		if event.button.id == "submit":
			self.run_slurm_job()

	def run_slurm_job(self):
		"""Run a Slurm job using the selected configuration."""
		config_file = self.config_file.value
		time_val = self.time_input.value.strip()
		memory_val = self.memory_input.value.strip()
		output_file_val = self.output_file.value.strip()
		job_name_val = self.job_name.value.strip()

		# Get script file from remote directory selection
		script_file = self.selected_file_path.relative_to(self.remote_home)

		# Validate input fields
		if not config_file or not time_val or not memory_val or not output_file_val or not job_name_val or not script_file:
			self.update_status("Please fill out all fields.", color=ERROR_COLOR)
			return

		# Build the sbatch command
		remote_script_path = f"{SLURM_CONFIG_BASE_PATH}/{self.config_type.value}/{config_file}"
		email = os.getenv("IDUN_EMAIL", "")

		command = f"./{remote_script_path} {script_file} {output_file_val} {time_val} {memory_val} {job_name_val} {email}"

		try:
			output = self.app.context.run_command(command)
			self.update_status(f"Job submitted:\n{script_file}", color=SUCCESS_COLOR)
		except Exception as e:
			self.update_status(f"Error submitting job: {e}", color=ERROR_COLOR)
