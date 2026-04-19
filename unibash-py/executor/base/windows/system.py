from typing import Any, Optional

from executor.interfaces import ISystemInspectExecutor
from runtime.models import Host


class WindowsSystemInspectExecutor(ISystemInspectExecutor):
    def inspect(self, target: Host, category: Optional[str] = None) -> Any:
        raise NotImplementedError("Windows inspect not yet implemented")
