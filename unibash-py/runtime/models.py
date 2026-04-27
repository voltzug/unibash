from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Union


class Protocol(str, Enum):
    SSH = "ssh"
    TELNET = "telnet"


@dataclass
class Host:
    name: str
    address: str
    protocol: Union[Protocol, str] = Protocol.SSH
    port: int = 22
    user: Optional[str] = None
    password: Optional[str] = None
    key: Optional[str] = None
    os_type: Optional[str] = None

    def protocol_name(self) -> str:
        if isinstance(self.protocol, Protocol):
            return self.protocol.value
        return str(self.protocol)

    def backend_process_name(self) -> str:
        proto = self.protocol_name().lower()
        if proto == "ssh":
            return "sshd"
        if proto == "telnet":
            return "telnetd"
        return proto


@dataclass
class Range:
    name: str
    ips: List[str] = field(default_factory=list)


@dataclass
class Group:
    name: str
    members: List[str] = field(default_factory=list)


@dataclass
class HttpResponse:
    status_code: int
    headers: Dict[str, str]
    text: str

    def __str__(self) -> str:
        return self.text
