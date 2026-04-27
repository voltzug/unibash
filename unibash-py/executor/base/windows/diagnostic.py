from __future__ import annotations

from typing import Any, Optional

from executor.interfaces import INetworkDiagnosticExecutor
from runtime.models import Host

from .transport import WindowsTransport


class WindowsNetworkDiagnosticExecutor(INetworkDiagnosticExecutor):
    def __init__(self, transport: Optional[WindowsTransport] = None):
        self.transport = transport or WindowsTransport()

    def ping(self, target: Host, count: int = 4, timeout: int = 5) -> Any:
        command = f'powershell -NoProfile -Command "Test-Connection -Count {count} -Quiet -TimeoutSeconds {timeout} {target.address}"'
        result = self.transport.run(command, target)

        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            return stderr or stdout or None

        output = (result.stdout or result.stderr or "").strip()
        if output:
            return output
        return f"ping {target.address} count={count} timeout={timeout}"
