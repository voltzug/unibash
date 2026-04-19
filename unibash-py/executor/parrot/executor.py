from typing import Any, Dict, List, Optional

from executor.interfaces import (
    IConsoleExecutor,
    IFileTransferExecutor,
    IHttpExecutor,
    IInteractiveExecutor,
    INetworkConfigExecutor,
    INetworkDiagnosticExecutor,
    IProcessExecutor,
    IRawCommandExecutor,
    ISystemInspectExecutor,
)
from runtime.models import Host

_NAME = "[PARROT]"


class ParrotExecutor(
    IConsoleExecutor,
    IHttpExecutor,
    INetworkDiagnosticExecutor,
    IInteractiveExecutor,
    ISystemInspectExecutor,
    IProcessExecutor,
    IFileTransferExecutor,
    INetworkConfigExecutor,
    IRawCommandExecutor,
):
    """
    A mock executor that acts like a parrot, echoing all actions to stdout
    instead of actually executing them. Useful for testing and dry-runs.
    """

    def _fmt_target(self, target: Host) -> str:
        return f"{target.name}({target.address})"

    # --- IConsoleExecutor ---
    def print(self, data: Any) -> None:
        print(f"{_NAME} PRINT: {data}")

    # --- IHttpExecutor ---
    def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Any:
        print(f"{_NAME} HTTP GET: {url} | Headers: {headers}")
        return "200 OK"

    def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
    ) -> Any:
        print(f"{_NAME} HTTP POST: {url} | Headers: {headers} | Body: {body}")
        return "201 Created"

    def put(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
    ) -> Any:
        print(f"{_NAME} HTTP PUT: {url} | Headers: {headers} | Body: {body}")
        return "200 OK"

    def delete(self, url: str, headers: Optional[Dict[str, str]] = None) -> Any:
        print(f"{_NAME} HTTP DELETE: {url} | Headers: {headers}")
        return "204 No Content"

    def patch(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
    ) -> Any:
        print(f"{_NAME} HTTP PATCH: {url} | Headers: {headers} | Body: {body}")
        return "200 OK"

    # --- INetworkDiagnosticExecutor ---
    def ping(self, target: Host, count: int = 4, timeout: int = 5) -> Any:
        print(
            f"{_NAME} PING {self._fmt_target(target)} | count={count} timeout={timeout}"
        )
        return "ping success"

    # --- IInteractiveExecutor ---
    def connect(self, target: Host) -> None:
        print(f"{_NAME} CONNECT to {self._fmt_target(target)}")

    # --- ISystemInspectExecutor ---
    def inspect(self, target: Host, category: Optional[str] = None) -> Any:
        print(f"{_NAME} INSPECT {self._fmt_target(target)} | category={category}")
        return f"inspect data for {category}"

    # --- IProcessExecutor ---
    def start(self, process_name: str, target: Host) -> Any:
        print(f"{_NAME} PROCESS START '{process_name}' on {self._fmt_target(target)}")
        return "started"

    def stop(self, process_name: str, target: Host) -> Any:
        print(f"{_NAME} PROCESS STOP '{process_name}' on {self._fmt_target(target)}")
        return "stopped"

    def restart(self, process_name: str, target: Host) -> Any:
        print(
            f"{_NAME} PROCESS RESTART '{process_name}' on {self._fmt_target(target)}"
        )
        return "restarted"

    def status(self, process_name: str, target: Host) -> Any:
        print(f"{_NAME} PROCESS STATUS '{process_name}' on {self._fmt_target(target)}")
        return "running"

    # --- IFileTransferExecutor ---
    def download(self, remote_path: str, local_path: str, target: Host) -> Any:
        print(
            f"{_NAME} DOWNLOAD {remote_path} -> {local_path} from {self._fmt_target(target)}"
        )
        return "downloaded"

    def upload(self, local_path: str, remote_path: str, target: Host) -> Any:
        print(
            f"{_NAME} UPLOAD {local_path} -> {remote_path} to {self._fmt_target(target)}"
        )
        return "uploaded"

    def copy(
        self, src_path: str, src_target: Host, dest_path: str, dest_target: Host
    ) -> Any:
        print(
            f"{_NAME} COPY {src_path} (from {self._fmt_target(src_target)}) -> "
            f"{dest_path} (to {self._fmt_target(dest_target)})"
        )
        return "copied"

    # --- INetworkConfigExecutor ---
    def set_ip(self, ip: str, interface: str, target: Host) -> Any:
        print(f"{_NAME} SET IP {ip} on {interface} at {self._fmt_target(target)}")
        return "ip set"

    def add_ip(self, ip: str, interface: str, target: Host) -> Any:
        print(f"{_NAME} ADD IP {ip} on {interface} at {self._fmt_target(target)}")
        return "ip added"

    def configure_dhcp(self, config_block: Dict[str, Any], target: Host) -> Any:
        print(
            f"{_NAME} CONFIGURE DHCP on {self._fmt_target(target)} | config={config_block}"
        )
        return "dhcp configured"

    def configure_dns(self, config_block: Dict[str, Any], target: Host) -> Any:
        print(
            f"{_NAME} CONFIGURE DNS on {self._fmt_target(target)} | config={config_block}"
        )
        return "dns configured"

    # --- IRawCommandExecutor ---
    def execute(self, command_list: List[str], target: Host) -> Any:
        cmds = ", ".join(command_list)
        print(f"{_NAME} EXECUTE [{cmds}] on {self._fmt_target(target)}")
        return "executed"
