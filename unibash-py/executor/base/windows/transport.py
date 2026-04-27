from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence

from runtime.models import Host


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str

    def ok(self) -> bool:
        return self.returncode == 0


class WindowsTransport:
    """
    Minimal Windows transport helper.

    Local execution uses the platform shell, while SSH targets are executed
    through the remote shell. In dry-run mode, it returns simulated results
    instead of executing commands, which is useful for Linux development.
    """

    def __init__(self, timeout: Optional[int] = None, dry_run: bool = False):
        self.timeout = timeout
        self.dry_run = dry_run

    def _protocol_name(self, target: Host) -> str:
        if hasattr(target, "protocol_name"):
            return target.protocol_name().lower()
        return str(getattr(target, "protocol", "")).lower()

    def _is_local_target(self, target: Host) -> bool:
        protocol = self._protocol_name(target)
        return protocol in ("local", "") or target.address in (
            "localhost",
            "127.0.0.1",
            "::1",
        )

    def _ssh_base_cmd(self, target: Host) -> List[str]:
        use_key = bool(target.key)
        use_password = bool(target.password) and not use_key

        cmd = ["ssh"]
        if not use_password:
            cmd.extend(["-o", "BatchMode=yes"])

        if use_password:
            sshpass = shutil.which("sshpass")
            if not sshpass:
                raise RuntimeError("sshpass required for password auth")
            cmd = [sshpass, "-p", target.password] + cmd

        if target.key:
            cmd.extend(["-i", target.key])
        if target.port:
            cmd.extend(["-p", str(target.port)])

        auth_target = target.address
        if target.user:
            auth_target = f"{target.user}@{target.address}"
        cmd.append(auth_target)
        return cmd

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

    def _simulate_run(self, command: str, target: Host) -> CommandResult:
        command_lower = command.lower()

        if "test-connection" in command_lower or command_lower.startswith("ping"):
            return CommandResult(
                0,
                f"Reply from {target.address}: bytes=32 time<1ms ttl=128\n",
                "",
            )

        if "get-computerinfo" in command_lower:
            return CommandResult(
                0,
                "WindowsProductName : Windows 11 Pro\nWindowsVersion : 23H2\nOsArchitecture : 64-bit\n",
                "",
            )

        if "win32_operatingsystem" in command_lower:
            return CommandResult(
                0,
                "Caption : Microsoft Windows 11 Pro\nVersion : 10.0.22631\nOSArchitecture : 64-bit\n",
                "",
            )

        if "win32_processor" in command_lower:
            return CommandResult(
                0,
                "Name : Generic CPU\nNumberOfCores : 4\nNumberOfLogicalProcessors : 8\n",
                "",
            )

        if "totalvisiblememorysize" in command_lower or "freephysicalmemory" in command_lower:
            return CommandResult(
                0,
                "TotalMB : 8192\nFreeMB : 4096\n",
                "",
            )

        if "get-psdrive" in command_lower:
            return CommandResult(0, "Name Used Free\nC 40GB 60GB\n", "")

        if "get-netipaddress" in command_lower:
            return CommandResult(0, "InterfaceAlias IPAddress AddressFamily\nEthernet 127.0.0.1 IPv4\n", "")

        if "get-service" in command_lower:
            return CommandResult(0, "Running\n", "")

        if "start-service" in command_lower or "stop-service" in command_lower or "restart-service" in command_lower:
            return CommandResult(0, "", "")

        if command_lower.startswith("powershell") or command_lower.startswith("pwsh"):
            return CommandResult(0, f"[dry-run] {command}\n", "")

        return CommandResult(0, f"[dry-run] {command}\n", "")

    def run(self, command: str, target: Host) -> CommandResult:
        if self.dry_run:
            return self._simulate_run(command, target)

        if self._is_local_target(target):
            proc = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True,
                timeout=self.timeout,
            )
            return CommandResult(proc.returncode, proc.stdout, proc.stderr)

        protocol = self._protocol_name(target)
        if protocol != "ssh":
            raise ValueError(f"Unsupported protocol for run: {protocol}")

        ssh_cmd = self._ssh_base_cmd(target)
        ssh_cmd.append(command)
        proc = subprocess.run(
            ssh_cmd,
            text=True,
            capture_output=True,
            timeout=self.timeout,
        )
        return CommandResult(proc.returncode, proc.stdout, proc.stderr)

    def scp_get(self, remote_path: str, local_path: str, target: Host) -> CommandResult:
        if self.dry_run:
            return CommandResult(0, f"[dry-run] copy {remote_path} -> {local_path}\n", "")

        if self._is_local_target(target):
            src = Path(remote_path)
            if not src.exists():
                raise FileNotFoundError(str(src))
            dest = self._resolve_dest_path(src, Path(local_path))
            self._copy_path(src, dest)
            return CommandResult(0, "", "")

        protocol = self._protocol_name(target)
        if protocol != "ssh":
            raise ValueError(f"Unsupported protocol for scp_get: {protocol}")

        auth_target = target.address
        if target.user:
            auth_target = f"{target.user}@{target.address}"
        src = f"{auth_target}:{remote_path}"

        scp_cmd = ["scp", "-q", "-r"]
        if target.key:
            scp_cmd.extend(["-i", target.key])
        if target.port:
            scp_cmd.extend(["-P", str(target.port)])
        if not target.password or target.key:
            scp_cmd.extend(["-o", "BatchMode=yes"])
        if target.password and not target.key:
            sshpass = shutil.which("sshpass")
            if not sshpass:
                raise RuntimeError("sshpass required for password auth")
            scp_cmd = [sshpass, "-p", target.password] + scp_cmd
        scp_cmd.extend([src, local_path])
        proc = subprocess.run(
            scp_cmd,
            text=True,
            capture_output=True,
            timeout=self.timeout,
        )
        return CommandResult(proc.returncode, proc.stdout, proc.stderr)

    def scp_put(self, local_path: str, remote_path: str, target: Host) -> CommandResult:
        if self.dry_run:
            return CommandResult(0, f"[dry-run] copy {local_path} -> {remote_path}\n", "")

        if self._is_local_target(target):
            src = Path(local_path)
            if not src.exists():
                raise FileNotFoundError(str(src))
            dest = self._resolve_dest_path(src, Path(remote_path))
            self._copy_path(src, dest)
            return CommandResult(0, "", "")

        protocol = self._protocol_name(target)
        if protocol != "ssh":
            raise ValueError(f"Unsupported protocol for scp_put: {protocol}")

        auth_target = target.address
        if target.user:
            auth_target = f"{target.user}@{target.address}"
        dest = f"{auth_target}:{remote_path}"

        scp_cmd = ["scp", "-q", "-r"]
        if target.key:
            scp_cmd.extend(["-i", target.key])
        if target.port:
            scp_cmd.extend(["-P", str(target.port)])
        if not target.password or target.key:
            scp_cmd.extend(["-o", "BatchMode=yes"])
        if target.password and not target.key:
            sshpass = shutil.which("sshpass")
            if not sshpass:
                raise RuntimeError("sshpass required for password auth")
            scp_cmd = [sshpass, "-p", target.password] + scp_cmd
        scp_cmd.extend([local_path, dest])
        proc = subprocess.run(
            scp_cmd,
            text=True,
            capture_output=True,
            timeout=self.timeout,
        )
        return CommandResult(proc.returncode, proc.stdout, proc.stderr)

    def run_many(self, commands: Sequence[str], target: Host) -> List[CommandResult]:
        return [self.run(command, target) for command in commands]