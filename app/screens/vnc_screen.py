from app.screens.base_screen import BaseScreen
from textual.containers import Container
from textual.widgets import Static, DataTable
from textual.binding import Binding
from rich.text import Text
from utils.parser import parse_vncserver_output
from app.config import ERROR_COLOR, SUCCESS_COLOR, WARNING_COLOR


class VNCScreen(BaseScreen):
    """VNC screen."""

    BINDINGS = [
        Binding("r", "refresh_vnc", "Refresh VNC List",
                tooltip="Refetches your VNC list", priority=False),
    ]

    def __init__(self):
        super().__init__()
        self.username = self.app.context.username
        self.job_table = DataTable(id="job-table", cursor_type="row")
        self.job_table_container = Container(
            self.job_table, id="job-table-container")
        self.job_table.add_columns("X DISPLAY #", "PROCESS ID")
        self.selected_row_key = None
        self.selected_job_id = None
        self.selected_node = None
        self.content = Container(
            Static(f"[bold]Welcome, {self.username}![/bold]",
                   classes="welcome-message"),
            self.job_table_container,
            id="home-container"
        )

    def compose(self):
        yield from super().compose(self.content)

    def on_mount(self):
        """Fetch initial job queue output on mount."""
        self.fetch_vnc()

    def action_refresh_vnc(self):
        """Refresh job queue."""
        self.fetch_vnc()

    def fetch_vnc(self):
        """Fetch and update the job queue output."""
        self.job_table.clear()
        self.app.call_later(self.refresh)

        try:
            result = self.app.context.run_command(f"vncserver -list")
            # raise KeyError(f"{result}")
        except Exception as e:
            self.update_status(str(e), color=ERROR_COLOR)
            self.refresh()
            return

        parsed_jobs = parse_vncserver_output(result)
        # raise KeyError(f"{parsed_jobs}")
        if parsed_jobs and len(parsed_jobs) > 0:
            for job in parsed_jobs:
                row_style = "white"

                styled_row = [
                    Text(str(job[col]),
                         style=f"bold {row_style}", justify="right")
                    for col in job.keys()
                ]

                self.job_table.add_row(*styled_row)
            self.update_status("VNC updated.", color=SUCCESS_COLOR)
        else:
            self.update_status("No vnc found.", color=WARNING_COLOR)