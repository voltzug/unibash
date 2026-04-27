from __future__ import annotations

import ipaddress
import shutil
import subprocess
from typing import Any, Optional

from executor.interfaces import ISystemInspectExecutor
from runtime.models import Host


class LinuxSystemInspectExecutor(ISystemInspectExecutor):
    def _protocol_name(self, target: Host) -> str:
        if hasattr(target, "protocol_name"):
            return target.protocol_name().lower()
        return str(getattr(target, "protocol", "")).lower()

    def _is_loopback(self, address: str) -> bool:
        if address in ("localhost", "127.0.0.1", "::1"):
            return True
        try:
            return ipaddress.ip_address(address).is_loopback
        except ValueError:
            return False

    def _build_ssh_command(self, target: Host, command: str) -> list[str]:
        use_key = bool(target.key)
        use_password = bool(target.password) and not use_key

        cmd: list[str] = ["ssh"]
        if not use_password:
            cmd.extend(["-o", "BatchMode=yes"])
        if use_key:
            cmd.extend(["-i", target.key])
        if target.port:
            cmd.extend(["-p", str(target.port)])

        if use_password:
            sshpass = shutil.which("sshpass")
            if not sshpass:
                raise RuntimeError("sshpass required for password auth")
            cmd = [sshpass, "-p", target.password] + cmd

        auth_target = target.address
        if target.user:
            auth_target = f"{target.user}@{target.address}"
        cmd.append(auth_target)
        cmd.append(command)
        return cmd

    def _run_local(self, command: str) -> str:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return (result.stderr or result.stdout).strip()

    def _run_remote(self, target: Host, command: str) -> str:
        cmd = self._build_ssh_command(target, command)
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return result.stdout.strip()
        return (result.stderr or result.stdout).strip()

    def _inspect_command(self, category: Optional[str]) -> str:
        if not category:
            return "uname -a"
        key = category.strip().lower()
        if key == "os":
            return "uname -s"
        if key == "cpu":
            return "lscpu"
        if key == "memory":
            return "free -m"
        if key == "disk":
            return "df -h"
        if key == "network":
            return "ip -o addr show"
        return f'echo "unknown category: {category}"'

    def inspect(self, target: Host, category: Optional[str] = None) -> Any:
        command = self._inspect_command(category)
        protocol = self._protocol_name(target)

        if protocol == "local" or self._is_loopback(target.address):
            result = self._run_local(command)
        elif protocol == "ssh":
            result = self._run_remote(target, command)
        else:
            return f"Unsupported protocol: {protocol}"

        if category and category.strip().lower() == "os":
            cleaned = result.strip()
            if not cleaned:
                return "unknown"
            normalized = cleaned.splitlines()[0].strip().lower()
            if "linux" in normalized:
                return "linux"
            if "windows" in normalized:
                return "windows"
            if "darwin" in normalized or "mac" in normalized:
                return "darwin"
            return normalized
        return result
