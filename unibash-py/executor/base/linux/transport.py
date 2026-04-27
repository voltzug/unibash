from __future__ import annotations

import shlex
import shutil
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Sequence

from runtime.models import Host


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str

    def ok(self) -> bool:
        return self.returncode == 0


class LinuxTransport:
    """
    Shared transport helpers for local and SSH/SCP execution.
    This does not attempt to manage interactive auth (password prompts).
    """

    def __init__(self, timeout: Optional[int] = None):
        self.timeout = timeout

    def _protocol_name(self, target: Host) -> str:
        if hasattr(target, "protocol_name"):
            return target.protocol_name().lower()
        return str(getattr(target, "protocol", "")).lower()

    def _is_local_target(self, target: Host) -> bool:
        proto = self._protocol_name(target)
        return proto in ("local", "", None) or target.address in (
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

    def _scp_base_cmd(self, target: Host) -> List[str]:
        use_key = bool(target.key)
        use_password = bool(target.password) and not use_key

        cmd = ["scp"]
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
            cmd.extend(["-P", str(target.port)])
        return cmd

    def run(self, command: str, target: Host) -> CommandResult:
        """
        Run command on target. Local executes directly. SSH executes remotely.
        Returns CommandResult with stdout/stderr captured.
        """
        if self._is_local_target(target):
            proc = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True,
                timeout=self.timeout,
            )
            return CommandResult(proc.returncode, proc.stdout, proc.stderr)

        proto = self._protocol_name(target)
        if proto != "ssh":
            raise ValueError(f"Unsupported protocol for run: {proto}")

        ssh_cmd = self._ssh_base_cmd(target)
        ssh_cmd.append(command)

        proc = subprocess.run(
            ssh_cmd,
            text=True,
            capture_output=True,
            timeout=self.timeout,
        )
        return CommandResult(proc.returncode, proc.stdout, proc.stderr)

    def run_lines(self, commands: Sequence[str], target: Host) -> CommandResult:
        """
        Run multiple commands joined with '&&' to preserve ordering.
        """
        joined = " && ".join(shlex.quote(cmd) for cmd in commands)
        return self.run(joined, target)

    def scp_get(self, remote_path: str, local_path: str, target: Host) -> CommandResult:
        """
        Copy remote -> local via scp. Local target uses cp semantics via shell.
        """
        if self._is_local_target(target):
            cmd = f"cp -a {shlex.quote(remote_path)} {shlex.quote(local_path)}"
            return self.run(cmd, target)

        proto = self._protocol_name(target)
        if proto != "ssh":
            raise ValueError(f"Unsupported protocol for scp_get: {proto}")

        auth_target = target.address
        if target.user:
            auth_target = f"{target.user}@{target.address}"
        src = f"{auth_target}:{remote_path}"

        cmd = self._scp_base_cmd(target) + [src, local_path]
        proc = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            timeout=self.timeout,
        )
        return CommandResult(proc.returncode, proc.stdout, proc.stderr)

    def scp_put(self, local_path: str, remote_path: str, target: Host) -> CommandResult:
        """
        Copy local -> remote via scp. Local target uses cp semantics via shell.
        """
        if self._is_local_target(target):
            cmd = f"cp -a {shlex.quote(local_path)} {shlex.quote(remote_path)}"
            return self.run(cmd, target)

        proto = self._protocol_name(target)
        if proto != "ssh":
            raise ValueError(f"Unsupported protocol for scp_put: {proto}")

        auth_target = target.address
        if target.user:
            auth_target = f"{target.user}@{target.address}"
        dest = f"{auth_target}:{remote_path}"

        cmd = self._scp_base_cmd(target) + [local_path, dest]
        proc = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            timeout=self.timeout,
        )
        return CommandResult(proc.returncode, proc.stdout, proc.stderr)
