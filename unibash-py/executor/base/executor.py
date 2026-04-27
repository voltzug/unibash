import platform
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

from .linux.file import LinuxFileTransferExecutor
from .linux.interactive import LinuxInteractiveExecutor
from .linux.network import LinuxNetworkConfigExecutor
from .linux.process import LinuxProcessExecutor
from .linux.raw import LinuxRawCommandExecutor
from .linux.system import LinuxSystemInspectExecutor
from .pure.console import PureConsoleExecutor
from .pure.diagnostic import PureNetworkDiagnosticExecutor
from .pure.file import PureFileTransferExecutor
from .pure.http import PureHttpExecutor
from .windows.diagnostic import WindowsNetworkDiagnosticExecutor
from .windows.file import WindowsFileTransferExecutor
from .windows.interactive import WindowsInteractiveExecutor
from .windows.network import WindowsNetworkConfigExecutor
from .windows.process import WindowsProcessExecutor
from .windows.raw import WindowsRawCommandExecutor
from .windows.system import WindowsSystemInspectExecutor


class BaseExecutor(
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
    The default executor that delegates tasks to platform-specific
    or pure implementations.
    """

    def __init__(self):
        # Pure Python implementations (Platform agnostic)
        self.console = PureConsoleExecutor()
        self.http = PureHttpExecutor()

        # Detect platform and assign OS-backed executors
        if platform.system().lower() == "windows":
            self.diagnostic = WindowsNetworkDiagnosticExecutor()
            self.interactive = WindowsInteractiveExecutor()
            self.system = WindowsSystemInspectExecutor()
            self.process = WindowsProcessExecutor()
            self.file = PureFileTransferExecutor()
            self.network_config = WindowsNetworkConfigExecutor()
            self.raw_command = WindowsRawCommandExecutor()
        else:
            # Default to Linux for everything else
            self.diagnostic = PureNetworkDiagnosticExecutor()
            self.interactive = LinuxInteractiveExecutor()
            self.system = LinuxSystemInspectExecutor()
            self.process = LinuxProcessExecutor()
            self.file = PureFileTransferExecutor()
            self.network_config = LinuxNetworkConfigExecutor()
            self.raw_command = LinuxRawCommandExecutor()

    # --- Delegates ---

    def print(self, data: Any) -> None:
        self.console.print(data)

    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        return self.http.get(url, headers, timeout, verify, follow_redirects)

    def head(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        return self.http.head(url, headers, timeout, verify, follow_redirects)

    def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        return self.http.post(url, headers, body, timeout, verify, follow_redirects)

    def put(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        return self.http.put(url, headers, body, timeout, verify, follow_redirects)

    def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        return self.http.delete(url, headers, timeout, verify, follow_redirects)

    def patch(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        return self.http.patch(url, headers, body, timeout, verify, follow_redirects)

    def ping(self, target: Host, count: int = 4, timeout: int = 5) -> Any:
        return self.diagnostic.ping(target, count, timeout)

    def connect(self, target: Host) -> None:
        self.interactive.connect(target)

    # --- OS-Backed Delegates ---

    def inspect(self, target: Host, category: Optional[str] = None) -> Any:
        return self.system.inspect(target, category)

    def start(self, process_name: str, target: Host) -> Any:
        return self.process.start(process_name, target)

    def stop(self, process_name: str, target: Host) -> Any:
        return self.process.stop(process_name, target)

    def restart(self, process_name: str, target: Host) -> Any:
        return self.process.restart(process_name, target)

    def status(self, process_name: str, target: Host) -> Any:
        return self.process.status(process_name, target)

    def download(self, remote_path: str, local_path: str, target: Host) -> Any:
        return self.file.download(remote_path, local_path, target)

    def upload(self, local_path: str, remote_path: str, target: Host) -> Any:
        return self.file.upload(local_path, remote_path, target)

    def copy(
        self, src_path: str, src_target: Host, dest_path: str, dest_target: Host
    ) -> Any:
        return self.file.copy(src_path, src_target, dest_path, dest_target)

    def set_ip(self, ip: str, interface: str, target: Host) -> Any:
        return self.network_config.set_ip(ip, interface, target)

    def add_ip(self, ip: str, interface: str, target: Host) -> Any:
        return self.network_config.add_ip(ip, interface, target)

    def configure_dhcp(self, config_block: Dict[str, Any], target: Host) -> Any:
        return self.network_config.configure_dhcp(config_block, target)

    def configure_dns(self, config_block: Dict[str, Any], target: Host) -> Any:
        return self.network_config.configure_dns(config_block, target)

    def execute(self, command_list: List[str], target: Host) -> Any:
        return self.raw_command.execute(command_list, target)
