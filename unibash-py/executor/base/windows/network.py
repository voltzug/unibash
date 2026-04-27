from typing import Any, Dict

from executor.interfaces import INetworkConfigExecutor
from runtime.models import Host


class WindowsNetworkConfigExecutor(INetworkConfigExecutor):
    def set_ip(self, ip: str, interface: str, target: Host) -> Any:
        raise NotImplementedError("Windows set_ip not yet implemented")

    def add_ip(self, ip: str, interface: str, target: Host) -> Any:
        raise NotImplementedError("Windows add_ip not yet implemented")

    def configure_dhcp(self, config_block: Dict[str, Any], target: Host) -> Any:
        raise NotImplementedError("Windows configure_dhcp not yet implemented")

    def configure_dns(self, config_block: Dict[str, Any], target: Host) -> Any:
        raise NotImplementedError("Windows configure_dns not yet implemented")
