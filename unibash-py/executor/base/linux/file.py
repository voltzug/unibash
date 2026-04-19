from typing import Any

from executor.interfaces import IFileTransferExecutor
from runtime.models import Host


class LinuxFileTransferExecutor(IFileTransferExecutor):
    def download(self, remote_path: str, local_path: str, target: Host) -> Any:
        raise NotImplementedError("Linux download not yet implemented")

    def upload(self, local_path: str, remote_path: str, target: Host) -> Any:
        raise NotImplementedError("Linux upload not yet implemented")

    def copy(
        self, src_path: str, src_target: Host, dest_path: str, dest_target: Host
    ) -> Any:
        raise NotImplementedError("Linux copy not yet implemented")
