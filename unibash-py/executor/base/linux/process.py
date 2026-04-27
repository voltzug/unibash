import ipaddress
import shlex
import shutil
import subprocess
from typing import Any, List, Optional, Tuple

from executor.interfaces import IProcessExecutor
from runtime.models import Host


class LinuxProcessExecutor(IProcessExecutor):
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
        proto = self._protocol_name(target)
        return proto == "local" or self._is_loopback_address(target.address)

    def _build_ssh_cmd(self, target: Host, remote_cmd: str) -> List[str]:
        use_key = bool(target.key)
        use_password = bool(target.password) and not use_key

        cmd = ["ssh"]
        if not use_password:
            cmd.extend(["-o", "BatchMode=yes"])
        if use_password:
            sshpass = shutil.which("sshpass")
            if not sshpass:
                raise RuntimeError("sshpass required for password SSH auth")
            cmd = [sshpass, "-p", target.password] + cmd
        if target.key:
            cmd.extend(["-i", target.key])
        if target.port:
            cmd.extend(["-p", str(target.port)])
        auth_target = target.address
        if target.user:
            auth_target = f"{target.user}@{target.address}"
        cmd.append(auth_target)
        cmd.append(remote_cmd)
        return cmd

    def _execute_local(self, cmd: List[str]) -> Tuple[int, str, str]:
        res = subprocess.run(cmd, capture_output=True, text=True)
        return res.returncode, res.stdout.strip(), res.stderr.strip()

    def _execute_remote(self, target: Host, cmd: List[str]) -> Tuple[int, str, str]:
        remote_cmd = " ".join(shlex.quote(part) for part in cmd)
        ssh_cmd = self._build_ssh_cmd(target, remote_cmd)
        res = subprocess.run(ssh_cmd, capture_output=True, text=True)
        return res.returncode, res.stdout.strip(), res.stderr.strip()

    def _execute(self, target: Host, cmd: List[str]) -> Tuple[int, str, str]:
        protocol = self._protocol_name(target)
        if self._is_local_target(target):
            return self._execute_local(cmd)
        if protocol == "ssh":
            return self._execute_remote(target, cmd)
        return 1, "", f"Unsupported protocol: {protocol}"

    def _is_command_missing(self, returncode: int, stderr: str) -> bool:
        if returncode == 127:
            return True
        err = stderr.lower()
        return "command not found" in err or "not found" in err or "no such file" in err

    def _run_service_action(self, action: str, process_name: str, target: Host) -> Any:
        candidates = [
            ["systemctl", action, process_name],
            ["service", process_name, action],
        ]

        last_stdout = ""
        last_stderr = ""
        for cmd in candidates:
            code, stdout, stderr = self._execute(target, cmd)
            last_stdout, last_stderr = stdout, stderr
            if code == 0:
                return stdout or None
            if self._is_command_missing(code, stderr):
                continue
            return stdout or stderr or None

        return last_stdout or last_stderr or None

    def start(self, process_name: str, target: Host) -> Any:
        return self._run_service_action("start", process_name, target)

    def stop(self, process_name: str, target: Host) -> Any:
        return self._run_service_action("stop", process_name, target)

    def restart(self, process_name: str, target: Host) -> Any:
        return self._run_service_action("restart", process_name, target)

    def status(self, process_name: str, target: Host) -> Any:
        return self._run_service_action("status", process_name, target)
