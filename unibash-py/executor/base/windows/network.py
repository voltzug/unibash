from __future__ import annotations

import ipaddress
from typing import Any, Dict

from executor.interfaces import INetworkConfigExecutor
from runtime.models import Host


class WindowsNetworkConfigExecutor(INetworkConfigExecutor):
    def _ip_parts(self, ip: str) -> tuple[str, str]:
        interface = ipaddress.ip_interface(ip)
        return str(interface.ip), str(interface.network.netmask)

    def set_ip(self, ip: str, interface: str, target: Host) -> Any:
        address, mask = self._ip_parts(ip)
        return {
            "command": (
                f'netsh interface ip set address name="{interface}" '
                f"static {address} {mask}"
            ),
            "applied": False,
        }

    def add_ip(self, ip: str, interface: str, target: Host) -> Any:
        address, mask = self._ip_parts(ip)
        return {
            "command": (
                f'netsh interface ip add address name="{interface}" '
                f"{address} {mask}"
            ),
            "applied": False,
        }

    def configure_dhcp(self, config_block: Dict[str, Any], target: Host) -> Any:
        raise NotImplementedError("Windows DHCP configuration not yet implemented")

    def configure_dns(self, config_block: Dict[str, Any], target: Host) -> Any:
        raise NotImplementedError("Windows DNS configuration not yet implemented")
