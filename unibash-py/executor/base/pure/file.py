from __future__ import annotations

import ipaddress
import os
import shutil
from pathlib import Path
from typing import Any

from executor.interfaces import IFileTransferExecutor
from runtime.models import Host


class PureFileTransferExecutor(IFileTransferExecutor):
    """
    Local-only file transfer. Operates on filesystem when target is local/loopback
    or protocol is "local". Otherwise no-op (returns None).
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

    def download(self, remote_path: str, local_path: str, target: Host) -> Any:
        if not self._is_local_target(target):
            return None

        src = Path(remote_path)
        if not src.exists():
            raise FileNotFoundError(str(src))

        dest = self._resolve_dest_path(src, Path(local_path))
        self._copy_path(src, dest)
        return None

    def upload(self, local_path: str, remote_path: str, target: Host) -> Any:
        if not self._is_local_target(target):
            return None

        src = Path(local_path)
        if not src.exists():
            raise FileNotFoundError(str(src))

        dest = self._resolve_dest_path(src, Path(remote_path))
        self._copy_path(src, dest)
        return None

    def copy(
        self, src_path: str, src_target: Host, dest_path: str, dest_target: Host
    ) -> Any:
        if not (
            self._is_local_target(src_target) and self._is_local_target(dest_target)
        ):
            return None

        src = Path(src_path)
        if not src.exists():
            raise FileNotFoundError(str(src))

        dest = self._resolve_dest_path(src, Path(dest_path))
        self._copy_path(src, dest)
        return None
