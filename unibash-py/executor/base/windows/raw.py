from typing import Any, List, Optional

from executor.interfaces import IRawCommandExecutor
from runtime.models import Host

from .transport import WindowsTransport


class WindowsRawCommandExecutor(IRawCommandExecutor):
    def __init__(self, transport: Optional[WindowsTransport] = None):
        self.transport = transport or WindowsTransport()

    def _ps_quote(self, command: str) -> str:
        return command.replace("'", "''")

    def _wrap_command(self, command: str) -> str:
        return f"powershell -NoProfile -Command '{self._ps_quote(command)}'"

    def _format_result(self, command: str, result) -> str:
        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        return (
            f">>command<<: {command}\n"
            f">>exit_code<<: {result.returncode}\n"
            f">>stdout<<:\n{stdout if stdout else '(empty)'}\n"
            f">>stderr<<:\n{stderr if stderr else '(empty)'}\n\n"
        )

    def execute(self, command_list: List[str], target: Host) -> Any:
        results: List[str] = []
        for command in command_list:
            wrapped = self._wrap_command(command)
            result = self.transport.run(wrapped, target)
            results.append(self._format_result(command, result))
        return results
