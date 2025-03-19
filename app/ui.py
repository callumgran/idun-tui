from textual.app import App
from app.tunnel_manager import TunnelManager
from app.ssh_connection import SSHConnectionManager
from app.screens.history_screen import HistoryScreen
from app.screens.home_screen import HomeScreen
from app.screens.login_screen import LoginScreen
from app.screens.request_node_screen import NodeRequestScreen
from app.config import UIBindings

class IDUNTUI(App):

    CSS_PATH = "app.css"
    BINDINGS = UIBindings().get_bindings()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = SSHConnectionManager()
        self.tunnel_manager = TunnelManager(self.context)

    def on_mount(self):
        """Start on login screen."""
        self.push_screen(LoginScreen())

    def action_switch_to_home(self):
        """Navigate to the home screen."""
        self.pop_screen()
        self.push_screen(HomeScreen())

    def action_switch_to_history(self):
        """Navigate to the history screen."""
        self.pop_screen()
        self.push_screen(HistoryScreen())

    def action_logout(self):
        """Logout user and return to login screen."""
        self.context.close()
        self.context.password = None
        self.pop_screen()
        self.push_screen(LoginScreen())
    
    def action_switch_to_node_request(self):
        """Navigate to the node request screen."""
        self.pop_screen()
        self.push_screen(NodeRequestScreen())

    def action_quit(self):
        """Quit the app."""
        self.tunnel_manager.close_all_tunnels()
        self.context.close()
        self.exit()


if __name__ == "__main__":
    app = IDUNTUI()
    app.run()
