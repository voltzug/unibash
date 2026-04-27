from __future__ import annotations

import ipaddress
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from executor.interfaces import INetworkConfigExecutor
from runtime.models import Host


class LinuxNetworkConfigExecutor(INetworkConfigExecutor):
    """
    Linux network configuration executor.

    Behavior:
    - If target is local/loopback or protocol is "local", execute locally.
    - Otherwise no-op (returns None). Transport layer not implemented.
    """

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

    def _run_cmd(self, args: List[str]) -> str:
        result = subprocess.run(args, check=False, capture_output=True, text=True)
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            msg = stderr or stdout or f"Command failed: {' '.join(args)}"
            raise RuntimeError(msg)
        return (result.stdout or "").strip()

    def _config_root(self) -> Path:
        if os.geteuid() == 0:
            return Path("/")
        return Path("/tmp/unibash")

    def _write_text(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def _restart_service(self, candidates: List[str]) -> Optional[str]:
        systemctl = shutil.which("systemctl")
        service = shutil.which("service")

        for name in candidates:
            if systemctl:
                try:
                    self._run_cmd([systemctl, "restart", name])
                    return name
                except Exception:
                    continue
            if service:
                try:
                    self._run_cmd([service, name, "restart"])
                    return name
                except Exception:
                    continue
        return None

    def _render_dhcp_config(self, config_block: Dict[str, Any]) -> str:
        subnet = str(config_block.get("subnet", "")).strip()
        ip_range = config_block.get("range")
        gateway = config_block.get("gateway")
        dns_list = config_block.get("dns", [])

        lines = [
            "default-lease-time 600;",
            "max-lease-time 7200;",
        ]

        subnet_header = None
        if subnet:
            try:
                network = ipaddress.ip_network(subnet, strict=False)
                subnet_header = (
                    f"subnet {network.network_address} netmask {network.netmask}"
                )
            except ValueError:
                subnet_header = f"subnet {subnet}"

        if subnet_header:
            lines.append(f"{subnet_header} {{")
            if ip_range:
                if isinstance(ip_range, list):
                    if any(isinstance(r, str) and ".." in r for r in ip_range):
                        for r in ip_range:
                            if isinstance(r, str) and ".." in r:
                                start, end = r.split("..", 1)
                                lines.append(f"  range {start} {end};")
                    else:
                        flat = [str(r) for r in ip_range]
                        for i in range(0, len(flat) - 1, 2):
                            lines.append(f"  range {flat[i]} {flat[i + 1]};")
                elif isinstance(ip_range, str) and ".." in ip_range:
                    start, end = ip_range.split("..", 1)
                    lines.append(f"  range {start} {end};")
            if gateway:
                lines.append(f"  option routers {gateway};")
            if dns_list:
                dns_values = ", ".join(str(x) for x in dns_list)
                lines.append(f"  option domain-name-servers {dns_values};")
            lines.append("}")
        return "\n".join(lines) + "\n"

    def _render_dns_zone(self, zone: str, records: List[Dict[str, Any]]) -> str:
        serial = int(time.time())
        lines = [
            f"$TTL 3600",
            f"@   IN SOA ns.{zone}. admin.{zone}. (",
            f"        {serial} ; serial",
            f"        3600   ; refresh",
            f"        1800   ; retry",
            f"        604800 ; expire",
            f"        86400  ; minimum",
            f")",
            f"@   IN NS  ns.{zone}.",
            f"ns  IN A   127.0.0.1",
        ]

        for rec in records:
            rtype = str(rec.get("type", "")).upper()
            name = str(rec.get("name", "")).strip()
            value = rec.get("value")
            if not rtype or not name or value is None:
                continue
            if name == "@":
                fqdn = "@"
            elif name.endswith("."):
                fqdn = name
            else:
                fqdn = f"{name}.{zone}."
            if rtype == "A":
                lines.append(f"{fqdn} IN A {value}")
            elif rtype == "CNAME":
                cname_val = value
                if not str(cname_val).endswith("."):
                    cname_val = f"{cname_val}."
                lines.append(f"{fqdn} IN CNAME {cname_val}")
            else:
                lines.append(f"{fqdn} IN {rtype} {value}")
        return "\n".join(lines) + "\n"

    def _render_named_local(self, zone: str, zone_file: Path) -> str:
        return f'zone "{zone}" {{\n    type master;\n    file "{zone_file}";\n}};\n'

    def _render_named_options(self, forwarders: List[str]) -> str:
        if not forwarders:
            return ""
        fwd = ";\n        ".join(str(x) for x in forwarders) + ";"
        return (
            "options {\n"
            '    directory "/var/cache/bind";\n'
            "    forwarders {\n"
            f"        {fwd}\n"
            "    };\n"
            "    dnssec-validation auto;\n"
            "    listen-on-v6 { any; };\n"
            "};\n"
        )

    # --- INetworkConfigExecutor ---

    def set_ip(self, ip: str, interface: str, target: Host) -> Any:
        if not self._is_local_target(target):
            return None
        cmd = ["ip", "addr", "replace", ip, "dev", interface]
        return self._run_cmd(cmd)

    def add_ip(self, ip: str, interface: str, target: Host) -> Any:
        if not self._is_local_target(target):
            return None
        cmd = ["ip", "addr", "add", ip, "dev", interface]
        return self._run_cmd(cmd)

    def configure_dhcp(self, config_block: Dict[str, Any], target: Host) -> Any:
        if not self._is_local_target(target):
            return None

        content = self._render_dhcp_config(config_block)
        root = self._config_root()
        dhcp_path = root / "etc" / "dhcp" / "dhcpd.conf"
        self._write_text(dhcp_path, content)

        return {
            "config_path": str(dhcp_path),
            "applied": os.geteuid() == 0,
        }

    def configure_dns(self, config_block: Dict[str, Any], target: Host) -> Any:
        if not self._is_local_target(target):
            return None

        zone = str(config_block.get("zone", "")).strip()
        records = config_block.get("records", [])
        forwarders = config_block.get("forwarders", [])

        if not zone:
            raise ValueError("DNS config requires 'zone'")

        root = self._config_root()
        bind_dir = root / "etc" / "bind"
        zone_file = bind_dir / f"db.{zone}"
        named_local = bind_dir / "named.conf.local"
        named_options = bind_dir / "named.conf.options"

        zone_content = self._render_dns_zone(zone, records)
        local_content = self._render_named_local(zone, zone_file)
        options_content = self._render_named_options(forwarders)

        self._write_text(zone_file, zone_content)
        self._write_text(named_local, local_content)
        if options_content:
            self._write_text(named_options, options_content)

        return {
            "zone_file": str(zone_file),
            "named_local": str(named_local),
            "named_options": str(named_options) if options_content else None,
            "applied": os.geteuid() == 0,
        }
