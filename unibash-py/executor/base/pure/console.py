from typing import Any

from executor.interfaces import IConsoleExecutor


class PureConsoleExecutor(IConsoleExecutor):
    def print(self, data: Any) -> None:
        if data is not None:
            # Handle lists/iterables if needed, or just let print handle it
            if isinstance(data, list):
                for item in data:
                    print(item)
            else:
                print(data)
