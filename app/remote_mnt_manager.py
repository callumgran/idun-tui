import os
import subprocess
from dotenv import load_dotenv
from app.config import REMOTE_MNT_HOST, REMOTE_MNT_DOMAIN

class CIFSMountError(Exception):
    pass

class RemoteMntManager:
    def __init__(self):
        load_dotenv()
        self.username = os.getenv("IDUN_USERNAME")
        self.password = os.getenv("IDUN_PASSWORD")
        self.mount_point = f"/tmp/smb_mnt_{self.username}"
        self.remote_path = f"//{REMOTE_MNT_HOST}/{self.username}"

    def mount(self):
        if not self.username or not self.password:
            raise CIFSMountError("Missing SMB credentials.")

        try:
            if os.path.exists(self.mount_point):
                if os.path.ismount(self.mount_point):
                    return self.mount_point
            else:
                os.makedirs(self.mount_point, exist_ok=True)

            command = [
                "sudo", "mount.cifs",
                self.remote_path,
                self.mount_point,
                "-o", f"username={self.username},domain={REMOTE_MNT_DOMAIN},password={self.password},uid={os.getuid()},gid={os.getgid()}"
            ]
            subprocess.run(command, check=True)
            return self.mount_point
        except subprocess.CalledProcessError as e:
            raise CIFSMountError(f"Failed to mount SMB share: {e}")

    def unmount(self):
        try:
            if os.path.ismount(self.mount_point):
                subprocess.run(["sudo", "umount", self.mount_point], check=True)
        except subprocess.CalledProcessError as e:
            raise CIFSMountError(f"Failed to unmount SMB share: {e}")
