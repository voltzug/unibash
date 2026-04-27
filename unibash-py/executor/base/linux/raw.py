import ipaddress
import shutil
import subprocess
from typing import Any, Dict, List

from executor.interfaces import IRawCommandExecutor
from runtime.models import Host


class LinuxRawCommandExecutor(IRawCommandExecutor):
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

    def _build_ssh_base(self, target: Host) -> List[str]:
        use_key = bool(target.key)
        use_password = bool(target.password) and not use_key

        cmd: List[str] = ["ssh"]
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
        return cmd

    def _run_local(self, command: str) -> Dict[str, Any]:
        proc = subprocess.run(
            ["sh", "-c", command],
            capture_output=True,
            text=True,
        )
        return {
            "command": command,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }

    def _run_ssh(self, command: str, target: Host) -> Dict[str, Any]:
        base = self._build_ssh_base(target)
        cmd = base + [command]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        return {
            "command": command,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }

    def _format_result(self, result: Dict[str, Any]) -> str:
        command = result.get("command", "")
        exit_code = result.get("exit_code", "")
        stdout = result.get("stdout", "")
        stderr = result.get("stderr", "")
        return (
            f">>command<<: {command}\n"
            f">>exit_code<<: {exit_code}\n"
            f">>stdout<<:\n{stdout if stdout else '(empty)'}\n"
            f">>stderr<<:\n{stderr if stderr else '(empty)'}\n\n"
        )

    def execute(self, command_list: List[str], target: Host) -> Any:
        results: List[str] = []
        if not command_list:
            return results

        if self._is_local_target(target):
            for cmd in command_list:
                results.append(self._format_result(self._run_local(cmd)))
            return results

        protocol = self._protocol_name(target)
        if protocol == "ssh":
            for cmd in command_list:
                results.append(self._format_result(self._run_ssh(cmd, target)))
            return results

        return [
            self._format_result(
                {
                    "command": cmd,
                    "exit_code": 1,
                    "stdout": "",
                    "stderr": f"Unsupported protocol: {protocol}",
                }
            )
            for cmd in command_list
        ]
