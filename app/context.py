import os
import paramiko
from dotenv import load_dotenv
from config import SSH_BASE_HOST
import time
import psutil
import threading
import socket
import select

class SSHConnectionError(Exception):
    """Custom exception for SSH connection failures."""
    pass


class AppContext:
    def __init__(self):
        load_dotenv()
        self.username = os.getenv("IDUN_USERNAME")
        self.password = os.getenv("IDUN_PASSWORD")
        self.ssh_client = None
        self.error_message = None
        self.shell = None
        self.local_tunnels = {}

    def connect_ssh(self):
        """Establish an SSH connection when the user logs in."""
        if not self.username or not self.password:
            self.error_message = "Missing SSH credentials in .env file."
            return False

        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                SSH_BASE_HOST, username=self.username, password=self.password)
            self.error_message = None
            self.shell = self.ssh_client.invoke_shell()
            return True
        except paramiko.AuthenticationException:
            self.error_message = "Invalid username or password."
        except paramiko.SSHException as e:
            self.error_message = f"SSH error: {e}"
        except Exception as e:
            self.error_message = f"Unexpected error: {e}"

        self.ssh_client = None
        self.shell = None
        return False

    def run_command(self, command):
        """Run a command on the remote SSH server and return the output."""
        if not self.ssh_client:
            return "SSH connection is not established."

        try:
            _, stdout, stderr = self.ssh_client.exec_command(command)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            return output if output else error
        except Exception as e:
            return f"Error running command: {e}"

    def run_async_command(self, command):
        """Run a long-running command (e.g., sbatch, salloc, scancel) via the persistent SSH session."""
        if not self.ssh_client:
            self.error_message = "SSH connection is not established."
            return

        if not self.shell:
            self.error_message = "SSH shell is not available."
            return

        try:
            self.shell.send(command + "\n")
            self.error_message = None
        except Exception as e:
            self.error_message = f"Error running command: {e}"

    def forward_socket(self, client_socket, remote_channel):
        """Bidirectionally forward data between local socket and SSH remote."""
        try:
            while True:
                r, _, _ = select.select([client_socket, remote_channel], [], [])
                if client_socket in r:
                    data = client_socket.recv(1024)
                    if len(data) == 0:
                        break
                    remote_channel.send(data)
                if remote_channel in r:
                    data = remote_channel.recv(1024)
                    if len(data) == 0:
                        break
                    client_socket.send(data)
        finally:
            client_socket.close()
            remote_channel.close()

    def setup_tunnel(self, node, local_port):
        """Create an SSH tunnel using Paramiko forwarding."""
        if node in self.local_tunnels:
            return f"Tunnel to {node} already exists."

        try:
            transport = self.ssh_client.get_transport()
            if not transport:
                return "SSH transport is not available."
            
            local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            local_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            local_socket.bind(("127.0.0.1", int(local_port)))
            local_socket.listen(1)

            def tunnel_forward():
                """Forward local port traffic to the remote node."""
                while True:
                    try:
                        client_socket, _ = local_socket.accept()
                        remote_channel = transport.open_channel(
                            "direct-tcpip",
                            (node, 22),
                            ("127.0.0.1", int(local_port))
                        )
                        if remote_channel is None:
                            break
                        self.forward_socket(client_socket, remote_channel)
                    except Exception as e:
                        print(f"Tunnel error: {e}")
                        break

            tunnel_thread = threading.Thread(target=tunnel_forward, daemon=True)
            tunnel_thread.start()

            
            self.local_tunnels[node] = (local_port, local_socket, tunnel_thread)
            return f"Tunnel established to {node} on localhost:{local_port}."

        except Exception as e:
            return f"Error establishing tunnel: {e}"

    def close_tunnel(self, node):
        """Properly close an SSH tunnel."""
        if node in self.local_tunnels:
            _, local_socket, tunnel_thread = self.local_tunnels[node]

            # Close the local socket
            local_socket.close()

            if tunnel_thread.is_alive():
                tunnel_thread.join(timeout=1)

            # Stop the thread
            del self.local_tunnels[node]
            return f"Tunnel to {node} closed."

        self.error_message = f"No active tunnel to {node}."

    def close_all_tunnels(self):
        """Close all active SSH tunnels."""
        for node in self.local_tunnels.keys():
            self.close_tunnel(node)
        self.local_tunnels.clear()

    def close_ssh(self):
        """Close the Paramiko SSH connection and the background SSH process."""
        self.close_all_tunnels()
        if self.ssh_client:
            self.shell.close()
            self.ssh_client.close()
            self.ssh_client = None
            self.shell = None