from textual.widgets import Input, Button, Label
from textual.containers import Container, Vertical
from app.screens.base_screen import BaseScreen


class LoginScreen(BaseScreen):
    """Login screen with a better layout and input fields."""

    def __init__(self):
        super().__init__()
        self.login_form = Vertical(
            Input(placeholder="Username", id="username",
                  value=self.app.context.username),
            Input(placeholder="Password", id="password", password=True),
            Button("Login", id="login"),
        )
        self.login_container = Container(self.login_form, id="login-container")

    def compose(self):
        yield from super().compose(self.login_container)

    def on_button_pressed(self, event):
        if event.button.id == "login":
            self.start_login()

    def start_login(self):
        """Attempt SSH connection and update the UI accordingly."""
        username = self.query_one("#username", Input).value
        password = self.query_one("#password", Input).value

        self.app.context.username = username
        self.app.context.password = password

        try:
            success = self.app.context.connect_ssh()
        except Exception as e:
            success = False
            self.app.context.error_message = str(e)

        if success:
            self.app.action_switch_to_home()
            self.update_status("Logged in successfully.", color="#22af4b")
        else:
            self.update_status(self.app.context.error_message or "Login failed.", color="#ee2524")