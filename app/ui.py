from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Label, Button, Static
from textual.screen import Screen
from app.context import AppContext
from app.screens.home_screen import HomeScreen
from app.screens.login_screen import LoginScreen
from app.screens.request_node_screen import NodeRequestScreen
from app.config import UIBindings

class IDUNTUI(App):

    CSS_PATH = "app.css"
    BINDINGS = UIBindings().get_bindings()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = AppContext()

    def on_mount(self):
        """Start on login screen."""
        self.push_screen(LoginScreen())

    def action_switch_to_home(self):
        """Navigate to the home screen."""
        self.pop_screen()
        self.push_screen(HomeScreen())

    def action_logout(self):
        """Logout user and return to login screen."""
        self.context.close_ssh()
        self.context.password = None
        self.pop_screen()
        self.push_screen(LoginScreen())

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
    
    def action_switch_to_node_request(self):
        """Navigate to the node request screen."""
        self.pop_screen()
        self.push_screen(NodeRequestScreen())

    def action_quit(self):
        """Quit the app."""
        self.context.close_ssh()
        self.exit()


if __name__ == "__main__":
    app = IDUNTUI()
    app.run()
