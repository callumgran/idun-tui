import os
import platform
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
        self.system = platform.system().lower()
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

            if self.system == "linux":
                self._mount_linux()
            elif self.system == "darwin":
                self._mount_macos()
            else:
                raise CIFSMountError(f"Unsupported platform: {self.system}")

            return self.mount_point
        except subprocess.CalledProcessError as e:
            raise CIFSMountError(f"Failed to mount SMB share: {e}")
        
    def _mount_linux(self):
        command = [
            "sudo", "mount.cifs",
            self.remote_path,
            self.mount_point,
            "-o", f"username={self.username},domain={REMOTE_MNT_DOMAIN},password={self.password},uid={os.getuid()},gid={os.getgid()}"
        ]
        subprocess.run(command, check=True)

    # Don't have a mac so I just yolo'd this based on the docs
    def _mount_macos(self):
        smb_path = f"smb://{REMOTE_MNT_DOMAIN};{self.username}:{self.password}@{REMOTE_MNT_HOST}/{self.username}"
        command = ["mount_smbfs", smb_path, self.mount_point]
        subprocess.run(command, check=True)

    def unmount(self):
        try:
            if os.path.ismount(self.mount_point):
                subprocess.run(["sudo", "umount", self.mount_point], check=True)
        except subprocess.CalledProcessError as e:
            raise CIFSMountError(f"Failed to unmount SMB share: {e}")
