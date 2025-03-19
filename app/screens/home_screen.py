from app.screens.base_screen import BaseScreen
from textual import on
from textual.containers import Container
from textual.widgets import Static, Input, DataTable
from textual.binding import Binding
from rich.text import Text
from app.utils.job_parser import parse_squeue_output
from app.config import INFO_COLOR, WARNING_COLOR, PORT_COLOR, SUCCESS_COLOR, ERROR_COLOR

class HomeScreen(BaseScreen):
    BINDINGS = [
        Binding("r", "refresh_jobs", "Refresh Jobs", tooltip="Refetch your job list"),
        Binding("c", "cancel_selected_job", "Cancel Selected Job", tooltip="Cancel the selected job"),
        Binding("t", "setup_tunnel", "Setup SSH Tunnel", tooltip="Create an SSH tunnel", priority=False),
        Binding("ctrl+t", "close_tunnel", "Close SSH Tunnel", tooltip="Close SSH tunnel for a given node", priority=False),
    ]

    def __init__(self):
        super().__init__()
        self.username = self.app.context.username
        self.job_table = DataTable(id="job-table", cursor_type="row")
        self.job_table_container = Container(self.job_table, id="job-table-container")
        self.job_table.add_columns("JOBID", "PARTITION", "NAME", "USER", "ST", "TIME", "NODES", "NODELIST(REASON)", "Tunnel Port")
        self.content = Container(
            Static(f"[bold]Welcome, {self.username}![/bold]", classes="welcome-message"),
            self.job_table_container,
            id="home-container"
        )
        self.selected_row_key = None
        self.selected_job_id = None
        self.selected_node = None
        self.port_input = Input(placeholder="Enter local port", id="port-input")
        self.port_input.display = False

    @on(DataTable.RowSelected)
    def on_row_clicked(self, event):
        table = event.data_table
        row = table.get_row(event.row_key)
        self.selected_row_key = event.row_key
        self.selected_job_id = row[0]
        self.selected_node = row[7] if str(row[7]).startswith("idun") else None
        self.update_status(f"Selected job: {self.selected_job_id} on node {self.selected_node or 'not allocated'}", color=INFO_COLOR)

    def compose(self):
        yield from super().compose(self.content)
        yield self.port_input

    def on_mount(self):
        self.fetch_queue()

    def action_refresh_jobs(self):
        self.fetch_queue()

    def action_cancel_selected_job(self):
        if self.selected_job_id:
            self.cancel_job(self.selected_job_id)
        else:
            self.update_status("No job selected.", color=WARNING_COLOR)

    def action_setup_tunnel(self):
        if not self.selected_node:
            self.update_status("No node selected for tunnel setup.", color=WARNING_COLOR)
            return
        self.port_input.display = True
        self.port_input.focus()

    def action_close_tunnel(self):
        if not self.selected_node:
            self.update_status("No node selected for tunnel closure.", color=WARNING_COLOR)
            return
        self.update_status(f"Closing SSH tunnel to {self.selected_node}...", color=INFO_COLOR)
        try:
            result = self.app.tunnel_manager.close_tunnel(str(self.selected_node))
            self.update_status(f"{result}", color=SUCCESS_COLOR)
        except Exception as e:
            self.update_status(f"Tunnel closure failed: {e}", color=ERROR_COLOR)
        self.fetch_queue()
        self.refresh()

    def on_input_submitted(self, event):
        if event.input.id == "port-input":
            local_port = event.value
            if local_port.isdigit():
                self.create_ssh_tunnel(local_port)
            else:
                self.update_status("Invalid port number.", color=ERROR_COLOR)
            self.port_input.display = False

    def fetch_queue(self):
        self.job_table.clear()
        self.app.call_later(self.refresh)
        result = self.app.context.run_command(f"squeue -u {self.username}")
        parsed_jobs = parse_squeue_output(result)
        if parsed_jobs:
            for job in parsed_jobs:
                row_style = INFO_COLOR if "CPUQ" in job["PARTITION"] else SUCCESS_COLOR if "GPUQ" in job["PARTITION"] else "white"
                styled_row = [Text(str(job[col]), style=f"bold {row_style}", justify="right") for col in job.keys()]
                if self.app.tunnel_manager.tunnels.get(job["NODELIST(REASON)"]):
                    (local_port, _, _, _) = self.app.tunnel_manager.tunnels[job["NODELIST(REASON)"]]
                    styled_row.append(Text(str(local_port), style=f"bold {PORT_COLOR}", justify="left"))
                else:
                    styled_row.append(Text("N/A", style=f"bold {row_style}", justify="left"))
                self.job_table.add_row(*styled_row)
            self.update_status("Job queue updated.", color=SUCCESS_COLOR)
        else:
            self.update_status("No jobs found.", color=WARNING_COLOR)

    def cancel_job(self, job_id):
        self.update_status(f"Canceling job {job_id}...", color=INFO_COLOR)
        try:
            self.app.context.run_command(f"scancel {job_id}")
            self.update_status(f"Job {job_id} canceled!", color=SUCCESS_COLOR)
            self.fetch_queue()
        except Exception as e:
            self.update_status(f"Error canceling job: {e}", color=ERROR_COLOR)
        self.refresh()

    def create_ssh_tunnel(self, local_port):
        self.update_status(f"Setting up SSH tunnel on port {local_port}...", color=INFO_COLOR)
        try:
            result = self.app.tunnel_manager.setup_tunnel(str(self.selected_node), local_port)
            self.fetch_queue()
            self.update_status(f"{result}", color=SUCCESS_COLOR)
        except Exception as e:
            self.update_status(f"Tunnel setup failed: {e} {local_port}", color=ERROR_COLOR)
        self.refresh()

