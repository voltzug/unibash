from typing import Any, Optional

from executor.interfaces import ISystemInspectExecutor
from runtime.models import Host

from .transport import WindowsTransport


class WindowsSystemInspectExecutor(ISystemInspectExecutor):
    def __init__(self, transport: Optional[WindowsTransport] = None):
        self.transport = transport or WindowsTransport()

    def _ps_command(self, body: str) -> str:
        return f"powershell -NoProfile -Command \"{body}\""

    def _inspect_command(self, category: Optional[str]) -> str:
        key = (category or "").strip().lower()

        if not key:
            return self._ps_command(
                "Get-ComputerInfo | Select-Object OsName, OsVersion, OsArchitecture | Format-List"
            )
        if key == "os":
            return self._ps_command(
                "(Get-CimInstance Win32_OperatingSystem | Select-Object -First 1 Caption, Version, OSArchitecture) | Format-List"
            )
        if key == "cpu":
            return self._ps_command(
                "Get-CimInstance Win32_Processor | Select-Object -First 1 Name, NumberOfCores, NumberOfLogicalProcessors | Format-List"
            )
        if key == "memory":
            return self._ps_command(
                "$os = Get-CimInstance Win32_OperatingSystem; [pscustomobject]@{ TotalMB = [math]::Round($os.TotalVisibleMemorySize / 1024, 2); FreeMB = [math]::Round($os.FreePhysicalMemory / 1024, 2) } | Format-List"
            )
        if key == "disk":
            return self._ps_command(
                "Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free | Format-Table -AutoSize"
            )
        if key == "network":
            return self._ps_command(
                "Get-NetIPAddress | Select-Object InterfaceAlias, IPAddress, AddressFamily | Format-Table -AutoSize"
            )
        return self._ps_command(f"Write-Output 'unknown category: {key}'")

    def inspect(self, target: Host, category: Optional[str] = None) -> Any:
        command = self._inspect_command(category)
        result = self.transport.run(command, target)

        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            return stderr or stdout or None

        output = (result.stdout or result.stderr or "").strip()
        if category and category.strip().lower() == "os":
            normalized = output.casefold()
            if "windows" in normalized:
                return "windows"
            return normalized.splitlines()[0] if normalized else "windows"
        return output or None
