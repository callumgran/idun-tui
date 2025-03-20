from app.screens.base_screen import BaseScreen
from textual.widgets import Input, Button
from textual.containers import Container, Vertical
from app.config import ERROR_COLOR, SUCCESS_COLOR

class LoginScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.login_form = Vertical(
            Input(placeholder="Username", id="username", value=self.app.context.username),
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
        username = self.query_one("#username", Input).value
        password = self.query_one("#password", Input).value

        self.app.context.username = username
        self.app.context.password = password

        try:
            self.app.context.connect()
            self.app.action_switch_to_home()
            self.update_status("Logged in successfully.", color=SUCCESS_COLOR)
        except Exception as e:
            self.update_status(str(e), color=ERROR_COLOR)
