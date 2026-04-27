import socket
import time
from typing import Any

from executor.interfaces import INetworkDiagnosticExecutor
from runtime.models import Host


class PureNetworkDiagnosticExecutor(INetworkDiagnosticExecutor):
    """
    Platform-agnostic "ping" using TCP connect attempts.
    This is not ICMP; it checks reachability on target.port.
    """

    def ping(self, target: Host, count: int = 4, timeout: int = 5) -> Any:
        port = target.port or 22
        success = 0
        failure = 0
        timings = []

        for _ in range(max(1, count)):
            start = time.monotonic()
            try:
                with socket.create_connection(
                    (target.address, int(port)), timeout=timeout
                ):
                    success += 1
            except OSError:
                failure += 1
            finally:
                elapsed_ms = int((time.monotonic() - start) * 1000)
                timings.append(elapsed_ms)

        avg_ms = int(sum(timings) / len(timings)) if timings else 0
        return (
            f"tcp ping {target.address}:{port} "
            f"count={count} success={success} failure={failure} avg_ms={avg_ms}"
        )
