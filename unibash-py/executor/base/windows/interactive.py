import shutil
import subprocess
from typing import Optional

from executor.interfaces import IInteractiveExecutor
from runtime.models import Host

from .transport import WindowsTransport


class WindowsInteractiveExecutor(IInteractiveExecutor):
    def __init__(self, transport: Optional[WindowsTransport] = None):
        self.transport = transport or WindowsTransport()

    def connect(self, target: Host) -> None:
        protocol = (
            target.protocol_name()
            if hasattr(target, "protocol_name")
            else target.protocol
        )

        if protocol in ("local", "") or target.address in ("localhost", "127.0.0.1", "::1"):
            shell = shutil.which("powershell") or shutil.which("pwsh") or shutil.which("cmd")
            if not shell:
                print("Unsupported local shell: no PowerShell or cmd available")
                return

            print(f"Connecting to {target.address} via local shell...")
            if shell.lower().endswith("cmd"):
                subprocess.call([shell])
            else:
                subprocess.call([shell, "-NoLogo", "-NoExit"])
            return

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
