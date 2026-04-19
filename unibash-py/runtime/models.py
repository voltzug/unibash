from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Host:
    name: str
    address: str
    protocol: str = "ssh"
    port: int = 22
    user: Optional[str] = None
    password: Optional[str] = None
    key: Optional[str] = None
    os_type: Optional[str] = None


@dataclass
class Range:
    name: str
    ips: List[str] = field(default_factory=list)


@dataclass
class Group:
    name: str
    members: List[str] = field(default_factory=list)
