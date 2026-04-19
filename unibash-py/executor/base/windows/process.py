from typing import Any

from executor.interfaces import IProcessExecutor
from runtime.models import Host


class WindowsProcessExecutor(IProcessExecutor):
    def start(self, process_name: str, target: Host) -> Any:
        raise NotImplementedError("Windows process start not yet implemented")

    def stop(self, process_name: str, target: Host) -> Any:
        raise NotImplementedError("Windows process stop not yet implemented")

    def restart(self, process_name: str, target: Host) -> Any:
        raise NotImplementedError("Windows process restart not yet implemented")

    def status(self, process_name: str, target: Host) -> Any:
        raise NotImplementedError("Windows process status not yet implemented")
