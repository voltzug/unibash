from typing import Any, Dict

from executor.interfaces import INetworkConfigExecutor
from runtime.models import Host


class LinuxNetworkConfigExecutor(INetworkConfigExecutor):
    def set_ip(self, ip: str, interface: str, target: Host) -> Any:
        raise NotImplementedError("Linux set_ip not yet implemented")

    def add_ip(self, ip: str, interface: str, target: Host) -> Any:
        raise NotImplementedError("Linux add_ip not yet implemented")

    def configure_dhcp(self, config_block: Dict[str, Any], target: Host) -> Any:
        raise NotImplementedError("Linux configure_dhcp not yet implemented")

    def configure_dns(self, config_block: Dict[str, Any], target: Host) -> Any:
        raise NotImplementedError("Linux configure_dns not yet implemented")
