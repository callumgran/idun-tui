from app.screens.base_screen import BaseScreen
from textual.containers import Container
from textual.widgets import Static, DataTable
from textual.binding import Binding
from rich.text import Text
import re


class HistoryScreen(BaseScreen):
    """History screen."""

    BINDINGS = [
        Binding("r", "refresh_history", "Refresh History",
                tooltip="Refetches your history list", priority=False),
    ]

    def __init__(self):
        super().__init__()
        self.username = self.app.context.username
        self.job_table = DataTable(id="job-table", cursor_type="row")
        self.job_table_container = Container(
            self.job_table, id="job-table-container")
        self.job_table.add_columns("JOBID", "JOBNAME", "STATE", "START", "END", "ELAPSED", "NODELIST", "NA")
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
        self.fetch_history()

    def action_refresh_history(self):
        """Refresh job queue."""
        self.fetch_history()

    def fetch_history(self):
        """Fetch and update the job queue output."""
        self.job_table.clear()
        self.app.call_later(self.refresh)

        result = self.app.context.run_command(f"sacct -u {self.username} --format=JobID,JobName%50,State,Start,End,Elapsed,NodeList")
        parsed_jobs = self.parse_sacct_output(result)[1:]
        if parsed_jobs and len(parsed_jobs) > 0:
            for job in parsed_jobs:
                row_style = "white"

                styled_row = [
                    Text(str(job[col]),
                         style=f"bold {row_style}", justify="right")
                    for col in job.keys()
                ]

                styled_row.append(Text("N/A", style=f"bold {row_style}", justify="left"))

                self.job_table.add_row(*styled_row)
            self.update_status("History updated.", color="#22af4b")
        else:
            self.update_status("No history found.", color="#fee851")

    def parse_sacct_output(self, output):
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