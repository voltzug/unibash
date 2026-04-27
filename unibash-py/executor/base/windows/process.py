from typing import Any, Optional

from executor.interfaces import IProcessExecutor
from runtime.models import Host

from .transport import WindowsTransport


class WindowsProcessExecutor(IProcessExecutor):
    def __init__(self, transport: Optional[WindowsTransport] = None):
        self.transport = transport or WindowsTransport()

    def _ps_quote(self, text: str) -> str:
        return text.replace("'", "''")

    def _run_service_action(self, action: str, process_name: str, target: Host) -> Any:
        quoted_name = self._ps_quote(process_name)

        if action == "status":
            command = (
                "powershell -NoProfile -Command "
                f"\"(Get-Service -Name '{quoted_name}').Status\""
            )
        else:
            command = (
                "powershell -NoProfile -Command "
                f'\"{action.title()}-Service -Name \'{quoted_name}\'\"'
            )

        result = self.transport.run(command, target)
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            return stderr or stdout or None

        return (result.stdout or result.stderr or "").strip() or None

    def start(self, process_name: str, target: Host) -> Any:
        return self._run_service_action("start", process_name, target)

    def stop(self, process_name: str, target: Host) -> Any:
        return self._run_service_action("stop", process_name, target)

    def restart(self, process_name: str, target: Host) -> Any:
        return self._run_service_action("restart", process_name, target)

    def status(self, process_name: str, target: Host) -> Any:
        return self._run_service_action("status", process_name, target)
