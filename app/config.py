from textual.binding import Binding

SSH_BASE_HOST = "idun-login2.hpc.ntnu.no"

class UIBindings():
	def __init__(self):
		self.quit = Binding("ctrl+q", "quit", "Quit", tooltip="Quit the application", priority=False)
		self.home = Binding("h", "switch_to_home", "Home", tooltip="Go to the home screen", priority=False)
		self.request_node = Binding("n", "switch_to_node_request", "Request Node", tooltip="Go to the node request screen", priority=False)
		self.logout = Binding("ctrl+l", "logout", "Logout", tooltip="Logout and return to login screen", priority=False)
		self.bindings = [
			self.quit,
			self.home,
			self.request_node,
			self.logout
		]

	def get_bindings(self):
		return self.bindings