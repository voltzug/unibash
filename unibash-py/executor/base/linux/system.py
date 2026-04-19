from typing import Any, Optional

from executor.interfaces import ISystemInspectExecutor
from runtime.models import Host


class LinuxSystemInspectExecutor(ISystemInspectExecutor):
    def inspect(self, target: Host, category: Optional[str] = None) -> Any:
        raise NotImplementedError("Linux inspect not yet implemented")
