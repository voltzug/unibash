from typing import Any

from executor.interfaces import IProcessExecutor
from runtime.models import Host


class LinuxProcessExecutor(IProcessExecutor):
    def start(self, process_name: str, target: Host) -> Any:
        raise NotImplementedError("Linux process start not yet implemented")

    def stop(self, process_name: str, target: Host) -> Any:
        raise NotImplementedError("Linux process stop not yet implemented")

    def restart(self, process_name: str, target: Host) -> Any:
        raise NotImplementedError("Linux process restart not yet implemented")

    def status(self, process_name: str, target: Host) -> Any:
        raise NotImplementedError("Linux process status not yet implemented")
