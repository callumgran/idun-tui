from app.screens.base_screen import BaseScreen
from textual import on
from textual.containers import Container
from textual.widgets import Static, Input, DataTable
from textual.binding import Binding
from rich.text import Text
import re


class HomeScreen(BaseScreen):
    """Main home screen with a personalized welcome message."""

    BINDINGS = [
        Binding("r", "refresh_jobs", "Refresh Jobs",
                tooltip="Refetches your job list", priority=False),
        Binding("c", "cancel_selected_job", "Cancel Selected Job",
                tooltip="Cancels the selected job running on IDUN", priority=False),
        Binding("t", "setup_tunnel", "Setup SSH Tunnel",
                tooltip="Create an SSH tunnel (needed for vscode etc)", priority=False),
        Binding("ctrl+t", "close_tunnel", "Close SSH Tunnel",
                tooltip="Close SSH tunnel for a given node", priority=False),
    ]

    def __init__(self):
        super().__init__()
        self.username = self.app.context.username
        self.job_table = DataTable(id="job-table", cursor_type="row")
        self.job_table_container = Container(
            self.job_table, id="job-table-container")
        self.job_table.add_columns(
            "JOBID", "PARTITION", "NAME", "USER", "ST", "TIME", "NODES", "NODELIST(REASON)", "Tunnel Port")
        self.content = Container(
            Static(f"[bold]Welcome, {self.username}![/bold]",
                   classes="welcome-message"),
            self.job_table_container,
            id="home-container"
        )
        self.selected_row_key = None
        self.selected_job_id = None
        self.selected_node = None
        self.port_input = Input(
            placeholder="Enter local port", id="port-input")
        self.port_input.display = False

    @on(DataTable.RowSelected)
    def on_row_clicked(self, event: DataTable.RowSelected) -> None:
        table = event.data_table
        row = table.get_row(event.row_key)
        self.selected_row_key = event.row_key
        self.selected_job_id = row[0]
        if (str(row[7]).startswith("idun")):
            self.selected_node = str(row[7])
        else:
            self.selected_node = None
        self.update_status(
            f"Selected job: {self.selected_job_id} on node {self.selected_node if self.selected_node is not None else 'not allocated'}", color="#0f89ca")

    def compose(self):
        yield from super().compose(self.content)
        yield self.port_input

    def on_mount(self):
        """Fetch initial job queue output on mount."""
        self.fetch_queue()

    def action_refresh_jobs(self):
        """Refresh job queue."""
        self.fetch_queue()

    def action_cancel_selected_job(self):
        """Cancel the selected job."""
        if self.selected_job_id:
            self.cancel_job(self.selected_job_id)
        else:
            self.update_status("No job selected.", color="#fee851")

    def action_setup_tunnel(self):
        """Prompt user for a local port and setup SSH tunnel."""
        if not self.selected_node:
            self.update_status(
                "No node selected for tunnel setup.", color="#fee851")
            return

        self.port_input.display = True
        self.port_input.focus()

    def action_close_tunnel(self):
        if not self.selected_node:
            self.update_status(
                "No node selected for tunnel closure.", color="#fee851")
            return

        self.update_status(
            f"Closing SSH tunnel to {self.selected_node}...", color="#0f89ca")
        result = self.app.context.close_tunnel(self.selected_node)
        if self.app.context.error_message:
            self.update_status(self.app.context.error_message, color="#ee2524")
        self.update_status(f"{result}", color="#22af4b")
        self.fetch_queue()

    def on_input_submitted(self, event):
        """Handle user input for SSH tunnel setup."""
        if event.input.id == "port-input":
            local_port = event.value
            if local_port.isdigit():
                self.create_ssh_tunnel(local_port)
            else:
                self.update_status("Invalid port number.", color="#ee2524")

            self.port_input.display = False

    def fetch_queue(self):
        """Fetch and update the job queue output."""
        self.job_table.clear()
        self.app.call_later(self.refresh)

        result = self.app.context.run_command(f"squeue -u callumg")
        parsed_jobs = self.parse_squeue_output(result)

        if parsed_jobs and len(parsed_jobs) > 0:
            for job in parsed_jobs:
                row_style = "#0f89ca" if "CPUQ" in job[
                    "PARTITION"] else "#22af4b" if "GPUQ" in job["PARTITION"] else "white"

                styled_row = [
                    Text(str(job[col]),
                         style=f"bold {row_style}", justify="right")
                    for col in job.keys()
                ]

                if (self.app.context.local_tunnels.get(job["NODELIST(REASON)"])):
                    (local_port, _, _) = self.app.context.local_tunnels[job["NODELIST(REASON)"]]
                    styled_row.append(Text(
                        str(local_port), style=f"bold #f05123", justify="left"))
                else:
                    styled_row.append(Text("N/A", style=f"bold {row_style}", justify="left"))

                self.job_table.add_row(*styled_row)
            self.update_status("Job queue updated.", color="#22af4b")
        else:
            self.update_status("No jobs found.", color="#fee851")

    def parse_squeue_output(self, output):
        """Parse raw squeue output into structured data."""
        lines = output.strip().split("\n")

        if len(lines) < 2:
            return []

        header = re.split(r'\s+', lines[0].strip())
        jobs = []

        for line in lines[1:]:
            row = re.split(r'\s+', line.strip(), maxsplit=len(header) - 1)
            if len(row) == len(header):
                job_entry = dict(zip(header, row))
                jobs.append(job_entry)

        return jobs

    def cancel_job(self, job_id):
        """Send scancel command to cancel a job."""
        self.update_status(f"Canceling job {job_id}...", color="#0f89ca")
        self.app.call_later(self.refresh)

        command = f"scancel {job_id}"

        self.app.context.run_async_command(command)

        if self.app.context.error_message:
            self.update_status(self.app.context.error_message, color="#ee2524")
        else:
            self.update_status(f"Job {job_id} canceled!", color="#22af4b")

        self.fetch_queue()

    def create_ssh_tunnel(self, local_port):
        """Create an SSH tunnel to the selected node."""
        self.update_status(
            f"Setting up SSH tunnel on port {local_port}...", color="#0f89ca")

        try:
            result = self.app.context.setup_tunnel(
                self.selected_node, local_port)
            if self.app.context.error_message:
                self.update_status(
                    self.app.context.error_message, color="#ee2524")
            else:
                self.fetch_queue()
                self.update_status(f"{result}", color="#22af4b")
        except Exception as e:
            self.update_status(f"Tunnel setup failed: {e} {local_port}", color="#ee2524")

        self.refresh()
