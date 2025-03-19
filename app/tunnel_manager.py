import socket
import select
import threading
import time

class TunnelManager:
    def __init__(self, ssh_manager: object):
        """
        :param ssh_manager: An instance of SSHConnectionManager.
        """
        self.ssh_manager = ssh_manager
        # Store active tunnels as a dict: node -> (local_port, local_socket, tunnel_thread, channels)
        self.tunnels = {}

    def forward_socket(self, client_socket, remote_channel):
        """Bidirectionally forward data between the local socket and the remote SSH channel."""
        try:
            while True:
                r, _, _ = select.select([client_socket, remote_channel], [], [])
                if client_socket in r:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    remote_channel.send(data)
                if remote_channel in r:
                    data = remote_channel.recv(1024)
                    if not data:
                        break
                    client_socket.send(data)
        finally:
            client_socket.close()
            remote_channel.close()

    def setup_tunnel(self, node, local_port):
        """Create an SSH tunnel to a remote node using port forwarding.
           Returns a success message or raises an Exception.
        """
        if node in self.tunnels:
            return f"Tunnel to {node} already exists."

        transport = self.ssh_manager.ssh_client.get_transport()
        if not transport:
            raise Exception("SSH transport is not available.")

        local_port = int(local_port)
        local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        local_socket.bind(("127.0.0.1", local_port))
        local_socket.listen(1)
        channels = []  # to store active remote channels

        def tunnel_forward():
            while True:
                try:
                    client_socket, _ = local_socket.accept()
                    remote_channel = transport.open_channel(
                        "direct-tcpip",
                        (node, 22),
                        ("127.0.0.1", local_port)
                    )
                    if remote_channel is None:
                        break
                    channels.append(remote_channel)
                    self.forward_socket(client_socket, remote_channel)
                except Exception as e:
                    print(f"Tunnel error: {e}")
                    break

        tunnel_thread = threading.Thread(target=tunnel_forward, daemon=True)
        tunnel_thread.start()
        self.tunnels[node] = (local_port, local_socket, tunnel_thread, channels)
        # Optionally, wait a short time and check that the port is open:
        time.sleep(3)
        return f"Tunnel established to {node} on localhost:{local_port}."

    def close_tunnel(self, node):
        """Properly close an SSH tunnel to the given node.
           Returns a message indicating success or failure.
        """
        if node not in self.tunnels:
            raise Exception(f"No active tunnel to {node}.")

        _, local_socket, tunnel_thread, channels = self.tunnels[node]

        # Close all active remote channels associated with the tunnel
        for ch in channels:
            try:
                if ch.active:
                    ch.close()
            except Exception as e:
                print(f"Error closing channel: {e}")

        # Close the local listening socket
        try:
            local_socket.close()
        except Exception as e:
            print(f"Error closing local socket: {e}")

        # Wait briefly for the thread to finish
        if tunnel_thread.is_alive():
            tunnel_thread.join(timeout=1)

        del self.tunnels[node]
        return f"Tunnel to {node} closed."

    def close_all_tunnels(self):
        for node in list(self.tunnels.keys()):
            try:
                self.close_tunnel(node)
            except Exception as e:
                print(f"Error closing tunnel for {node}: {e}")
