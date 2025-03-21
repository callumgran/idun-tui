import os
import paramiko
from dotenv import load_dotenv
from config import SSH_BASE_HOST

class SSHConnectionError(Exception):
    pass

class SSHConnectionManager:
    def __init__(self):
        load_dotenv()
        self.username = os.getenv("IDUN_USERNAME")
        self.password = os.getenv("IDUN_PASSWORD")
        self.ssh_client = None
        self.shell = None

    def connect(self):
        if not self.username or not self.password:
            raise SSHConnectionError("Missing SSH credentials.")
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(SSH_BASE_HOST,
                                    username=self.username,
                                    password=self.password)
            self.shell = self.ssh_client.invoke_shell()
        except Exception as e:
            raise SSHConnectionError(f"Error connecting via SSH: {e}")

    def run_command(self, command):
        if not self.ssh_client:
            raise SSHConnectionError("SSH connection is not established.")
        _, stdout, stderr = self.ssh_client.exec_command(command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        return output if output else error

    def run_async_command(self, command):
        if not self.ssh_client:
            raise SSHConnectionError("SSH connection is not established.")
        if not self.shell:
            raise SSHConnectionError("SSH shell is not available.")
        try:
            self.shell.send(command + "\n")
        except Exception as e:
            raise SSHConnectionError(f"Error running command: {e}")
    
    def close(self):
        if self.ssh_client:
            self.shell.close()
            self.ssh_client.close()
            self.ssh_client = None
            self.shell = None
