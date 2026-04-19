from typing import Any, List

from executor.interfaces import IRawCommandExecutor
from runtime.models import Host


class WindowsRawCommandExecutor(IRawCommandExecutor):
    def execute(self, command_list: List[str], target: Host) -> Any:
        raise NotImplementedError("Windows exec not yet implemented")
