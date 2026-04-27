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

    def _guess_os(self, target: Host) -> str:
        name = f"{target.name}".lower()
        if "win" in name or "windows" in name:
            return "windows"
        return "linux"

    # --- IConsoleExecutor ---
    def print(self, data: Any) -> None:
        print(f"{_NAME} PRINT: {data}")

    # --- IHttpExecutor ---
    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        return f"HTTP GET {url} | headers={headers}"

    def head(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        return f"HTTP HEAD {url} | headers={headers}"

    def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        return f"HTTP POST {url} | headers={headers} | body={body}"

    def put(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        return f"HTTP PUT {url} | headers={headers} | body={body}"

    def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        return f"HTTP DELETE {url} | headers={headers}"

    def patch(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        return f"HTTP PATCH {url} | headers={headers} | body={body}"

    # --- INetworkDiagnosticExecutor ---
    def ping(self, target: Host, count: int = 4, timeout: int = 5) -> Any:
        print(
            f"{_NAME} PING {self._fmt_target(target)} | count={count} timeout={timeout}"
        )
        return None

    # --- IInteractiveExecutor ---
    def connect(self, target: Host) -> None:
        print(f"{_NAME} CONNECT to {self._fmt_target(target)}")

    # --- ISystemInspectExecutor ---
    def inspect(self, target: Host, category: Optional[str] = None) -> Any:
        if category and category.lower() == "os":
            return self._guess_os(target)
        if category:
            return f"{category} ok"
        return "ok"

    # --- IProcessExecutor ---
    def start(self, process_name: str, target: Host) -> Any:
        print(f"{_NAME} PROCESS START '{process_name}' on {self._fmt_target(target)}")
        return None

    def stop(self, process_name: str, target: Host) -> Any:
        print(f"{_NAME} PROCESS STOP '{process_name}' on {self._fmt_target(target)}")
        return None

    def restart(self, process_name: str, target: Host) -> Any:
        print(f"{_NAME} PROCESS RESTART '{process_name}' on {self._fmt_target(target)}")
        return None

    def status(self, process_name: str, target: Host) -> Any:
        print(f"{_NAME} PROCESS STATUS '{process_name}' on {self._fmt_target(target)}")
        return None

    # --- IFileTransferExecutor ---
    def download(self, remote_path: str, local_path: str, target: Host) -> Any:
        print(
            f"{_NAME} DOWNLOAD {remote_path} -> {local_path} from {self._fmt_target(target)}"
        )
        return None

    def upload(self, local_path: str, remote_path: str, target: Host) -> Any:
        print(
            f"{_NAME} UPLOAD {local_path} -> {remote_path} to {self._fmt_target(target)}"
        )
        return None

    def copy(
        self, src_path: str, src_target: Host, dest_path: str, dest_target: Host
    ) -> Any:
        print(
            f"{_NAME} COPY {src_path} (from {self._fmt_target(src_target)}) -> "
            f"{dest_path} (to {self._fmt_target(dest_target)})"
        )
        return None

    # --- INetworkConfigExecutor ---
    def set_ip(self, ip: str, interface: str, target: Host) -> Any:
        print(f"{_NAME} SET IP {ip} on {interface} at {self._fmt_target(target)}")
        return None

    def add_ip(self, ip: str, interface: str, target: Host) -> Any:
        print(f"{_NAME} ADD IP {ip} on {interface} at {self._fmt_target(target)}")
        return None

    def configure_dhcp(self, config_block: Dict[str, Any], target: Host) -> Any:
        print(
            f"{_NAME} CONFIGURE DHCP on {self._fmt_target(target)} | config={config_block}"
        )
        return None

    def configure_dns(self, config_block: Dict[str, Any], target: Host) -> Any:
        print(
            f"{_NAME} CONFIGURE DNS on {self._fmt_target(target)} | config={config_block}"
        )
        return None

    # --- IRawCommandExecutor ---
    def execute(self, command_list: List[str], target: Host) -> Any:
        cmds = ", ".join(command_list)
        print(f"{_NAME} EXECUTE [{cmds}] on {self._fmt_target(target)}")
        return None
