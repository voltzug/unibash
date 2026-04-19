import ipaddress
from typing import List, Set

from .context import RuntimeContext
from .exceptions import InvalidTargetError, MissingReferenceError
from .models import Group, Host, Range


def is_valid_ip(val: str) -> bool:
    try:
        ipaddress.ip_address(val)
        return True
    except ValueError:
        return False


class TargetResolver:
    """Resolves abstract targets (names, groups, ranges, variables) into concrete Host objects."""

    def __init__(self, context: RuntimeContext):
        self.context = context

    def resolve(self, target_identifier: str) -> List[Host]:
        """
        Resolves a given identifier into a flat list of Host objects.
        Handles direct IP literals, known Hosts, Ranges, and nested Groups.
        """
        visited: Set[str] = set()
        resolved_hosts = self._resolve_recursive(target_identifier, visited)
        return self._deduplicate(resolved_hosts)

    def _resolve_recursive(self, identifier: str, visited: Set[str]) -> List[Host]:
        # Prevent infinite loops in self-referencing groups or variables
        if identifier in visited:
            return []

        visited.add(identifier)

        # 1. Check if it's a literal IP address string
        if is_valid_ip(identifier):
            return [Host(name=identifier, address=identifier)]

        # 2. Look up the entity in the runtime context
        try:
            entity = self.context.get_entity(identifier)
        except MissingReferenceError:
            # If not in context and not an IP, it's invalid
            raise InvalidTargetError(
                identifier, "Not a known entity or valid IP address."
            )

        # 3. Handle different entity types
        if isinstance(entity, Host):
            return [entity]

        elif isinstance(entity, Range):
            # Convert range IPs to generic Host objects
            return [Host(name=ip, address=ip) for ip in entity.ips]

        elif isinstance(entity, Group):
            # Recursively resolve all members of the group
            group_hosts = []
            for member in entity.members:
                group_hosts.extend(self._resolve_recursive(member, visited))
            return group_hosts

        elif isinstance(entity, str):
            # If it's a variable holding a string, resolve that string
            return self._resolve_recursive(entity, visited)

        elif isinstance(entity, list):
            # If it's a variable holding a list of strings, resolve each
            list_hosts = []
            for item in entity:
                if isinstance(item, str):
                    # Use a copy of visited to allow parallel sibling paths
                    list_hosts.extend(self._resolve_recursive(item, set(visited)))
                else:
                    raise InvalidTargetError(
                        identifier,
                        f"List variable contains non-string item: {type(item).__name__}",
                    )
            return list_hosts

        else:
            raise InvalidTargetError(
                identifier,
                f"Cannot resolve target from entity type '{type(entity).__name__}'.",
            )

    def _deduplicate(self, hosts: List[Host]) -> List[Host]:
        """Removes duplicate hosts based on name and address."""
        seen: Set[str] = set()
        unique_hosts: List[Host] = []

        for host in hosts:
            identifier = f"{host.name}::{host.address}"
            if identifier not in seen:
                seen.add(identifier)
                unique_hosts.append(host)

        return unique_hosts
