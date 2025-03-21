from app.screens.base_screen import BaseScreen
from textual.containers import Container, Horizontal
from textual.widgets import Label, Input, Button, Select
from app.config import ERROR_COLOR, SUCCESS_COLOR, INFO_COLOR, GPU_TYPES


class NodeRequestScreen(BaseScreen):
    """Screen for requesting CPU or GPU nodes."""

    def __init__(self):
        super().__init__()

        self.request_type = Select(
            [("CPU Node", "cpu"), ("GPU Node", "gpu")], id="request-type"
        )
        self.time_input = Input(placeholder="Hours", id="time")
        self.cpu_cores_input = Input(placeholder="CPU Cores", id="cpu-cores")
        self.memory_input = Input(
            placeholder="Memory (e.g., 64G)", id="memory"
        )
        self.node_count_input = Input(placeholder="Nodes", id="nodes")

        # GPU fields
        self.gpu_count_input = Input(placeholder="GPUs", id="gpu-count")
        self.gpu_type_input = Select(GPU_TYPES, id="gpu-type")

        self.gpu_count_label = Label("GPU Count:")
        self.gpu_type_label = Label("GPU Type:")

        self.submit_button = Button("Request Node", id="submit")

    def compose(self):
        """Construct UI layout."""
        yield from super().compose(Container(
            Horizontal(Label("Node Type:"), self.request_type),
            Horizontal(Label("Time (Hours):"), self.time_input),
            Horizontal(Label("Nodes:"), self.node_count_input),
            Horizontal(Label("Memory:"), self.memory_input),
            Horizontal(Label("CPU Cores:"), self.cpu_cores_input),
            Horizontal(self.gpu_count_label, self.gpu_count_input),
            Horizontal(self.gpu_type_label, self.gpu_type_input),
            Horizontal(self.submit_button),
            id="node-request-container"
        ))

    def on_mount(self):
        """Ensure GPU fields are hidden initially."""
        self.update_ui_based_on_selection()

    def on_select_changed(self, event):
        """Show GPU-specific fields only when 'GPU' is selected."""
        self.update_ui_based_on_selection()

    def update_ui_based_on_selection(self):
        """Toggle visibility of CPU vs. GPU-specific fields."""
        selected_type = self.request_type.value
        if selected_type == "gpu":
            self.gpu_count_input.display = True
            self.gpu_type_input.display = True
            self.gpu_count_label.display = True
            self.gpu_type_label.display = True
        else:
            self.gpu_count_input.display = False
            self.gpu_type_input.display = False
            self.gpu_count_label.display = False
            self.gpu_type_label.display = False

    def on_button_pressed(self, event):
        """Handle node request submission."""
        if event.button.id == "submit":
            self.request_node()

    def request_node(self):
        """Send the node request command to the HPC and update the UI."""
        self.update_status("Requesting node...", color=INFO_COLOR)
        self.refresh()

        node_type = self.request_type.value
        time_val = self.time_input.value
        nodes = self.node_count_input.value
        memory = self.memory_input.value
        cpu_cores = self.cpu_cores_input.value

        gpu_count = self.gpu_count_input.value
        gpu_type = self.gpu_type_input.value

        if not time_val or not nodes or not memory or not cpu_cores or \
           (node_type == "gpu" and (not gpu_count or not gpu_type)):
            self.update_status(
                "Please fill out all fields.", color=ERROR_COLOR)
            return

        try:
            time_int = int(time_val)
            days = time_int // 24
            hours = time_int % 24
            request_time = f"{days}-{hours}:00:00"
        except ValueError:
            self.update_status("Invalid time value.", color=ERROR_COLOR)
            return

        if node_type == "cpu":
            command = f"salloc --nodes={nodes} --cpus-per-task={cpu_cores} --mem={memory} --partition=CPUQ --time={request_time}"
        else:
            command = f"salloc --nodes={nodes} --gres=gpu:{gpu_type}:{gpu_count} --mem={memory} --partition=GPUQ --time={request_time}"

        try:
            self.app.context.run_async_command(command)
        except Exception as e:
            self.update_status(
                f"Error requesting node: {e}", color=ERROR_COLOR)
            return

        self.update_status("Requested a node!", color=SUCCESS_COLOR)
        self.refresh()
