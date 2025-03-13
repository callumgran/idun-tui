from textual.screen import Screen
from textual.widgets import Header, Footer, Label

class BaseScreen(Screen):
    """Base screen with bindings."""
    def __init__(self):
        super().__init__()
        self.status_label = Label("", id="status-message")

    def compose(self, children):
        yield Header()
        yield children
        yield self.status_label
        yield Footer()

    def update_status(self, message: str, color: str = "#22af4b"):
        """Update the status message."""
        self.status_label.update(f"[bold {color}]{message}[/bold {color}]")
