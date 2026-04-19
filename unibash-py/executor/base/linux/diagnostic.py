import subprocess
from typing import Any

from executor.interfaces import INetworkDiagnosticExecutor
from runtime.models import Host


class LinuxNetworkDiagnosticExecutor(INetworkDiagnosticExecutor):
    def ping(self, target: Host, count: int = 4, timeout: int = 5) -> Any:
        cmd = ["ping", "-c", str(count), target.address]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return e.stdout
