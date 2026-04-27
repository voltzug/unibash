import subprocess

from executor.interfaces import IInteractiveExecutor
from runtime.models import Host


class LinuxInteractiveExecutor(IInteractiveExecutor):
    def connect(self, target: Host) -> None:
        cmd = []
        protocol = (
            target.protocol_name()
            if hasattr(target, "protocol_name")
            else target.protocol
        )

        if protocol == "ssh":
            cmd = ["ssh"]
            if target.key:
                cmd.extend(["-i", target.key])
            if target.port:
                cmd.extend(["-p", str(target.port)])

            auth_target = target.address
            if target.user:
                auth_target = f"{target.user}@{target.address}"
            cmd.append(auth_target)

        elif protocol == "telnet":
            cmd = ["telnet", target.address]
            if target.port:
                cmd.append(str(target.port))
        else:
            print(f"Unsupported protocol: {protocol}")
            return

        print(f"Connecting to {target.address} via {protocol}...")
        subprocess.call(cmd)
