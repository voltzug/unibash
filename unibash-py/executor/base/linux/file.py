from __future__ import annotations

import ipaddress
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from executor.interfaces import IFileTransferExecutor
from runtime.models import Host


class LinuxFileTransferExecutor(IFileTransferExecutor):
    """
    Linux file transfer via scp with local fallback.

    - If target protocol is "local" or address is loopback, use local copy.
    - For SSH targets, use scp.
    - Telnet not supported for file transfer.
    """

    def _protocol_name(self, target: Host) -> str:
        if hasattr(target, "protocol_name"):
            return target.protocol_name().lower()
        return str(getattr(target, "protocol", "")).lower()

    def _is_loopback_address(self, address: str) -> bool:
        if address in ("localhost", "127.0.0.1", "::1"):
            return True
        try:
            return ipaddress.ip_address(address).is_loopback
        except ValueError:
            return False

    def _is_local_target(self, target: Host) -> bool:
        if self._protocol_name(target) == "local":
            return True
        return self._is_loopback_address(target.address)

    def _resolve_dest_path(self, src: Path, dest: Path) -> Path:
        dest_str = str(dest)
        if dest_str.endswith(os.sep) or dest_str.endswith("/"):
            dest.mkdir(parents=True, exist_ok=True)
            return dest / src.name
        if dest.exists() and dest.is_dir():
            return dest / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        return dest

    def _copy_path(self, src: Path, dest: Path) -> None:
        if src.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    def _scp_base_args(self, target: Host) -> list[str]:
        use_key = bool(target.key)
        use_password = bool(target.password) and not use_key

        base = ["scp", "-q", "-r"]
        if not use_password:
            base.extend(["-o", "BatchMode=yes"])

        if use_password:
            sshpass = shutil.which("sshpass")
            if not sshpass:
                raise RuntimeError("sshpass required for password auth")
            args = [sshpass, "-p", target.password] + base
        else:
            args = base

        if target.key:
            args.extend(["-i", target.key])
        if target.port:
            args.extend(["-P", str(target.port)])
        return args

    def _scp_host_prefix(self, target: Host) -> str:
        user = target.user
        if user:
            return f"{user}@{target.address}"
        return target.address

    def download(self, remote_path: str, local_path: str, target: Host) -> Any:
        if self._is_local_target(target):
            src = Path(remote_path)
            if not src.exists():
                raise FileNotFoundError(str(src))
            dest = self._resolve_dest_path(src, Path(local_path))
            self._copy_path(src, dest)
            return None

        proto = self._protocol_name(target)
        if proto != "ssh":
            raise NotImplementedError(f"Unsupported protocol for download: {proto}")

        src = f"{self._scp_host_prefix(target)}:{remote_path}"
        dest = str(Path(local_path))
        cmd = self._scp_base_args(target) + [src, dest]
        subprocess.run(cmd, check=True)
        return None

    def upload(self, local_path: str, remote_path: str, target: Host) -> Any:
        if self._is_local_target(target):
            src = Path(local_path)
            if not src.exists():
                raise FileNotFoundError(str(src))
            dest = self._resolve_dest_path(src, Path(remote_path))
            self._copy_path(src, dest)
            return None

        proto = self._protocol_name(target)
        if proto != "ssh":
            raise NotImplementedError(f"Unsupported protocol for upload: {proto}")

        src = str(Path(local_path))
        dest = f"{self._scp_host_prefix(target)}:{remote_path}"
        cmd = self._scp_base_args(target) + [src, dest]
        subprocess.run(cmd, check=True)
        return None

    def copy(
        self, src_path: str, src_target: Host, dest_path: str, dest_target: Host
    ) -> Any:
        if self._is_local_target(src_target) and self._is_local_target(dest_target):
            src = Path(src_path)
            if not src.exists():
                raise FileNotFoundError(str(src))
            dest = self._resolve_dest_path(src, Path(dest_path))
            self._copy_path(src, dest)
            return None

        src_proto = self._protocol_name(src_target)
        dest_proto = self._protocol_name(dest_target)

        if src_proto != "ssh" or dest_proto != "ssh":
            raise NotImplementedError(
                f"Unsupported protocol for copy: {src_proto} -> {dest_proto}"
            )

        if (src_target.password and not src_target.key) or (
            dest_target.password and not dest_target.key
        ):
            raise NotImplementedError(
                "Remote copy with password auth not supported; use key auth"
            )

        src = f"{self._scp_host_prefix(src_target)}:{src_path}"
        dest = f"{self._scp_host_prefix(dest_target)}:{dest_path}"

        # scp -3 enables source -> local -> dest transfer
        cmd = ["scp", "-3", "-q", "-r"]

        if src_target.key:
            cmd.extend(["-i", src_target.key])
        if src_target.port:
            cmd.extend(["-P", str(src_target.port)])

        # dest-specific options appended as well
        if dest_target.key and dest_target.key != src_target.key:
            cmd.extend(["-i", dest_target.key])
        if dest_target.port and dest_target.port != src_target.port:
            cmd.extend(["-P", str(dest_target.port)])

        cmd.extend([src, dest])
        subprocess.run(cmd, check=True)
        return None
