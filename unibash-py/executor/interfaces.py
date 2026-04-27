from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from runtime.models import Host


# --- Base ---
class IExecutor(ABC):
    """Base marker interface for all executors."""

    pass


# --- Mixins (Traits) ---
class IHelpProvider(ABC):
    @abstractmethod
    def get_help(self) -> str:
        """Returns documentation and usage examples."""
        pass


class IDryRunCapable(ABC):
    @abstractmethod
    def plan_only(self) -> str:
        """Shows what WOULD happen, skips execution."""
        pass


class IProgressReporter(ABC):
    @abstractmethod
    def register_callback(self, callback: Callable[[float, int], None]) -> None:
        """Callback receives (percentage, bytes_transferred)."""
        pass


class IRollbackCapable(ABC):
    @abstractmethod
    def rollback(self, target: Host) -> bool:
        """Undo failed operations."""
        pass


# --- Pure Python Interfaces (Platform Agnostic) ---
class IConsoleExecutor(IExecutor):
    @abstractmethod
    def print(self, data: Any) -> None:
        pass


class IHttpExecutor(IExecutor):
    @abstractmethod
    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        pass

    @abstractmethod
    def head(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        pass

    @abstractmethod
    def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        pass

    @abstractmethod
    def put(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        pass

    @abstractmethod
    def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        pass

    @abstractmethod
    def patch(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        pass


class INetworkDiagnosticExecutor(IExecutor):
    @abstractmethod
    def ping(self, target: Host, count: int = 4, timeout: int = 5) -> Any:
        pass


class IInteractiveExecutor(IExecutor):
    @abstractmethod
    def connect(self, target: Host) -> None:
        pass


# --- OS-Backed Interfaces (Need Switcher) ---
class ISystemInspectExecutor(IExecutor):
    @abstractmethod
    def inspect(self, target: Host, category: Optional[str] = None) -> Any:
        """category: os, cpu, memory, disk, network, etc."""
        pass


class IProcessExecutor(IExecutor):
    @abstractmethod
    def start(self, process_name: str, target: Host) -> Any:
        pass

    @abstractmethod
    def stop(self, process_name: str, target: Host) -> Any:
        pass

    @abstractmethod
    def restart(self, process_name: str, target: Host) -> Any:
        pass

    @abstractmethod
    def status(self, process_name: str, target: Host) -> Any:
        pass


class IFileTransferExecutor(IExecutor):
    @abstractmethod
    def download(self, remote_path: str, local_path: str, target: Host) -> Any:
        pass

    @abstractmethod
    def upload(self, local_path: str, remote_path: str, target: Host) -> Any:
        pass

    @abstractmethod
    def copy(
        self, src_path: str, src_target: Host, dest_path: str, dest_target: Host
    ) -> Any:
        pass


class INetworkConfigExecutor(IExecutor):
    @abstractmethod
    def set_ip(self, ip: str, interface: str, target: Host) -> Any:
        pass

    @abstractmethod
    def add_ip(self, ip: str, interface: str, target: Host) -> Any:
        pass

    @abstractmethod
    def configure_dhcp(self, config_block: Dict[str, Any], target: Host) -> Any:
        pass

    @abstractmethod
    def configure_dns(self, config_block: Dict[str, Any], target: Host) -> Any:
        pass


class IRawCommandExecutor(IExecutor):
    @abstractmethod
    def execute(self, command_list: List[str], target: Host) -> Any:
        pass
