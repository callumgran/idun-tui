import os
from textual.containers import Container, Horizontal
from textual.widgets import Label, Input, Button, Select, Checkbox, SelectionList
from app.screens.base_screen import BaseScreen
from textual import on
from app.config import SUCCESS_COLOR, ERROR_COLOR, GPU_TYPES, SLURM_CONFIG_BASE_PATH
from app.utils.config_generator import generate_cpu_slurm_config, generate_gpu_slurm_config


class CreateSlurmConfigScreen(BaseScreen):
    """Screen for creating a CPU/GPU Slurm config file and saving it locally."""

    def __init__(self):
        super().__init__()

        self.config_name = Input(
            placeholder="Config file name, e.g. my_config", id="config-name")
        self.slurm_type = Select(
            [("CPU", "cpu"), ("GPU", "gpu")], id="slurm-type"
        )
        self.node_count = Input(placeholder="How many nodes?", id="node-count")
        self.node_names = Input(
            placeholder="(Leave empty for all) Node list e.g. idun-04-[01,02]", id="node-names"
        )
        self.cpu_cores = Input(
            placeholder="How many CPU cores?", id="cpu-cores"
        )

        # GPU fields
        self.gpu_count = Input(placeholder="How many GPUs?", id="gpu-count")
        self.gpu_type = Select(GPU_TYPES, id="gpu-type")

        # GPU labels
        self.gpu_count_label = Label("GPU Count:")
        self.gpu_type_label = Label("GPU Type:")

        # Send mail checkbox
        self.send_mail_checkbox = Checkbox("Send Mail", id="send-mail")

        # Mail types selection list
        self.mail_type_select = SelectionList[str](
            ("BEGIN", "BEGIN"),
            ("END", "END"),
            ("FAIL", "FAIL"),
            ("REQUEUE", "REQUEUE"),
            ("INVALID_DEPEND", "INVALID_DEPEND"),
            ("STAGE_OUT", "STAGE_OUT"),
            ("TIME_LIMIT_50", "TIME_LIMIT_50"),
            ("TIME_LIMIT_80", "TIME_LIMIT_80"),
            ("TIME_LIMIT_90", "TIME_LIMIT_90"),
        )

        # Mail types selection list label
        self.mail_type_label = Label(
            "Mail Types (select none for ALL):", id="mail-type-label")

        # Button to save config
        self.save_button = Button("Save Config", id="submit")

    def compose(self):
        """Construct the UI layout."""
        yield from super().compose(
            Container(
                Horizontal(Label("Slurm Type:"), self.slurm_type),
                Horizontal(Label("Config Name:"), self.config_name),
                Horizontal(Label("Nodes:"), self.node_count),
                Horizontal(Label("Node Names:"), self.node_names),
                Horizontal(Label("CPU Cores:"), self.cpu_cores),

                # GPU-specific row
                Horizontal(self.gpu_count_label, self.gpu_count),
                Horizontal(self.gpu_type_label, self.gpu_type),

                # Mail
                Horizontal(self.send_mail_checkbox),
                Horizontal(self.mail_type_label, self.mail_type_select),

                # Save button
                Horizontal(self.save_button),
                id="slurm-config-container"
            ),
        )

    def on_mount(self):
        """Set initial visibility states."""
        self.update_ui_based_on_slurm_type()
        self.update_ui_based_on_mail_checkbox()

    @on(Select.Changed)
    def handle_select_changed(self, event: Select.Changed):
        """Called when any Select changes (slurm-type or mail-type)."""
        if event.select.id == "slurm-type":
            self.update_ui_based_on_slurm_type()

    @on(Checkbox.Changed)
    def handle_checkbox_changed(self, event: Checkbox.Changed):
        """Called when a checkbox changes (e.g., send-mail)."""
        if event.checkbox.id == "send-mail":
            self.update_ui_based_on_mail_checkbox()

    def update_ui_based_on_slurm_type(self):
        """Show/hide GPU fields if user selects CPU or GPU."""
        if self.slurm_type.value == "gpu":
            self.gpu_count.display = True
            self.gpu_type.display = True
            self.gpu_count_label.display = True
            self.gpu_type_label.display = True
        else:
            self.gpu_count.display = False
            self.gpu_type.display = False
            self.gpu_count_label.display = False
            self.gpu_type_label.display = False

    def update_ui_based_on_mail_checkbox(self):
        """Show/hide the mail-type selector if user wants to send mail."""
        if self.send_mail_checkbox.value:
            self.mail_type_select.display = True
            self.mail_type_label.display = True
        else:
            self.mail_type_select.display = False
            self.mail_type_label.display = False

    def on_button_pressed(self, event: Button.Pressed):
        """Handle the Save Config button."""
        if event.button.id == "submit":
            self.save_slurm_config()

    def save_slurm_config(self):
        """Generate a Slurm script file and save locally to cpu/ or gpu/."""
        name_val = self.config_name.value.strip()
        slurm_type_val = self.slurm_type.value
        node_count_val = self.node_count.value.strip()
        node_names_val = self.node_names.value.strip()
        cpu_cores_val = self.cpu_cores.value.strip()

        # GPU values
        gpu_count_val = self.gpu_count.value.strip()
        gpu_type_val = self.gpu_type.value

        # Mail
        send_mail = self.send_mail_checkbox.value
        mail_types_selected = self.mail_type_select.selected

        # Convert mail types to a single line, e.g. #SBATCH --mail-type=BEGIN,END,FAIL
        mail_type_str = ",".join(
            mail_types_selected) if mail_types_selected else "ALL"

        # Validate required fields
        if not name_val:
            self.update_status(
                "Please enter a config file name.", color=ERROR_COLOR)
            return
        if not node_count_val or not cpu_cores_val:
            self.update_status(
                "Please fill out 'Nodes' and 'CPU Cores'.", color=ERROR_COLOR)
            return

        # If GPU is selected, also check GPU fields
        if slurm_type_val == "gpu":
            if not gpu_count_val or not gpu_type_val:
                self.update_status(
                    "Please fill out GPU Count and GPU Type.", color=ERROR_COLOR)
                return

        folder = "cpu" if slurm_type_val == "cpu" else "gpu"

        # The config file path
        config_dir = f"{SLURM_CONFIG_BASE_PATH}/{folder}"
        config_file_path = os.path.join(config_dir, f"{name_val}.slurmconfig")

        # Generate the config content
        config_content = ""
        if slurm_type_val == "cpu":
            config_content = generate_cpu_slurm_config(
                mail=send_mail,
                mail_types=mail_type_str,
                num_nodes=int(node_count_val),
                num_cores=int(cpu_cores_val),
                nodes=node_names_val
            )
        else:
            config_content = generate_gpu_slurm_config(
                mail=send_mail,
                mail_types=mail_type_str,
                num_nodes=int(node_count_val),
                num_cores=int(cpu_cores_val),
                nodes=node_names_val,
                num_gpus=int(gpu_count_val),
                gpu_type=str(gpu_type_val)
            )

        try:
            self.app.context.run_command(
                f"mkdir -p {config_dir} && touch {config_file_path} && echo '{config_content}' > {config_file_path} && chmod +x {config_file_path}"
            )
            self.update_status(
                f"Config saved successfully to {config_file_path}", color=SUCCESS_COLOR
            )
        except Exception as e:
            self.update_status(f"Error saving config: {e}", color=ERROR_COLOR)
