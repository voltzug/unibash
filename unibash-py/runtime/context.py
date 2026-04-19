from typing import Any, Dict, Union

from .exceptions import DuplicateNameError, MissingReferenceError
from .models import Group, Host, Range


class RuntimeContext:
    """Holds the runtime state for Unibash execution."""

    def __init__(self):
        self.hosts: Dict[str, Host] = {}
        self.ranges: Dict[str, Range] = {}
        self.groups: Dict[str, Group] = {}
        self.variables: Dict[str, Any] = {}

    def _check_duplicate(self, name: str, entity_type: str = "entity") -> None:
        if (
            name in self.hosts
            or name in self.ranges
            or name in self.groups
            or name in self.variables
        ):
            raise DuplicateNameError(name, entity_type)

    def register_host(self, host: Host) -> None:
        self._check_duplicate(host.name, "host")
        self.hosts[host.name] = host

    def register_range(self, rng: Range) -> None:
        self._check_duplicate(rng.name, "range")
        self.ranges[rng.name] = rng

    def register_group(self, group: Group) -> None:
        self._check_duplicate(group.name, "group")
        self.groups[group.name] = group

    def set_variable(self, name: str, value: Any) -> None:
        # Variables can be updated, but cannot shadow existing static entities
        if name in self.hosts or name in self.ranges or name in self.groups:
            raise DuplicateNameError(name, "variable collision with static entity")
        self.variables[name] = value

    def get_host(self, name: str) -> Host:
        if name not in self.hosts:
            raise MissingReferenceError(name, "host")
        return self.hosts[name]

    def get_range(self, name: str) -> Range:
        if name not in self.ranges:
            raise MissingReferenceError(name, "range")
        return self.ranges[name]

    def get_group(self, name: str) -> Group:
        if name not in self.groups:
            raise MissingReferenceError(name, "group")
        return self.groups[name]

    def get_variable(self, name: str) -> Any:
        if name not in self.variables:
            raise MissingReferenceError(name, "variable")
        return self.variables[name]

    def get_entity(self, name: str) -> Union[Host, Range, Group, Any]:
        """Generic resolver for a given identifier."""
        if name in self.hosts:
            return self.hosts[name]
        if name in self.ranges:
            return self.ranges[name]
        if name in self.groups:
            return self.groups[name]
        if name in self.variables:
            return self.variables[name]
        raise MissingReferenceError(name, "entity")

    def has_entity(self, name: str) -> bool:
        return any(
            (
                name in self.hosts,
                name in self.ranges,
                name in self.groups,
                name in self.variables,
            )
        )
