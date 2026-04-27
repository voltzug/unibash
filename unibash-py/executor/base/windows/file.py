from __future__ import annotations

import ipaddress
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from executor.interfaces import IFileTransferExecutor
from runtime.models import Host


def _protocol_name(target: Host) -> str:
    if hasattr(target, "protocol_name"):
        return target.protocol_name().lower()
    return str(getattr(target, "protocol", "")).lower()


def _is_loopback_address(address: str) -> bool:
    if address in ("localhost", "127.0.0.1", "::1"):
        return True
    try:
        return ipaddress.ip_address(address).is_loopback
    except ValueError:
        return False


def _is_local_target(target: Host) -> bool:
    if _protocol_name(target) == "local":
        return True
    return _is_loopback_address(target.address)


def _resolve_dest_path(src: Path, dest: Path) -> Path:
    dest_str = str(dest)
    if dest_str.endswith(os.sep) or dest_str.endswith("/"):
        dest.mkdir(parents=True, exist_ok=True)
        return dest / src.name
    if dest.exists() and dest.is_dir():
        return dest / src.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    return dest


def _copy_path(src: Path, dest: Path) -> None:
    if src.is_dir():
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dest, dirs_exist_ok=True)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def _scp_base_args(target: Host) -> list[str]:
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


def _scp_host_prefix(target: Host) -> str:
    if target.user:
        return f"{target.user}@{target.address}"
    return target.address


class WindowsFileTransferExecutor(IFileTransferExecutor):
    def download(self, remote_path: str, local_path: str, target: Host) -> Any:
        if _is_local_target(target):
            src = Path(remote_path)
            if not src.exists():
                raise FileNotFoundError(str(src))
            dest = _resolve_dest_path(src, Path(local_path))
            _copy_path(src, dest)
            return None

        proto = _protocol_name(target)
        if proto != "ssh":
            raise NotImplementedError(f"Unsupported protocol for download: {proto}")

        src = f"{_scp_host_prefix(target)}:{remote_path}"
        dest = str(Path(local_path))
        cmd = _scp_base_args(target) + [src, dest]
        subprocess.run(cmd, check=True)
        return None

    def upload(self, local_path: str, remote_path: str, target: Host) -> Any:
        if _is_local_target(target):
            src = Path(local_path)
            if not src.exists():
                raise FileNotFoundError(str(src))
            dest = _resolve_dest_path(src, Path(remote_path))
            _copy_path(src, dest)
            return None

        proto = _protocol_name(target)
        if proto != "ssh":
            raise NotImplementedError(f"Unsupported protocol for upload: {proto}")

        src = str(Path(local_path))
        dest = f"{_scp_host_prefix(target)}:{remote_path}"
        cmd = _scp_base_args(target) + [src, dest]
        subprocess.run(cmd, check=True)
        return None

    def copy(
        self, src_path: str, src_target: Host, dest_path: str, dest_target: Host
    ) -> Any:
        if _is_local_target(src_target) and _is_local_target(dest_target):
            src = Path(src_path)
            if not src.exists():
                raise FileNotFoundError(str(src))
            dest = _resolve_dest_path(src, Path(dest_path))
            _copy_path(src, dest)
            return None

        src_proto = _protocol_name(src_target)
        dest_proto = _protocol_name(dest_target)

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

        src = f"{_scp_host_prefix(src_target)}:{src_path}"
        dest = f"{_scp_host_prefix(dest_target)}:{dest_path}"
        cmd = ["scp", "-3", "-q", "-r"]

        if src_target.key:
            cmd.extend(["-i", src_target.key])
        if src_target.port:
            cmd.extend(["-P", str(src_target.port)])
        if dest_target.key and dest_target.key != src_target.key:
            cmd.extend(["-i", dest_target.key])
        if dest_target.port and dest_target.port != src_target.port:
            cmd.extend(["-P", str(dest_target.port)])

        cmd.extend([src, dest])
        subprocess.run(cmd, check=True)
        return None
