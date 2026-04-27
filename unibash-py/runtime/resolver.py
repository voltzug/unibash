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

    def _expand_range_entry(self, entry: str, range_name: str) -> List[str]:
        if ".." not in entry:
            return [entry]

        start_str, end_str = entry.split("..", 1)
        try:
            start_ip = ipaddress.ip_address(start_str)
            end_ip = ipaddress.ip_address(end_str)
        except ValueError:
            return [entry]

        if start_ip.version != end_ip.version:
            raise InvalidTargetError(range_name, "Range IP versions do not match.")

        start_int = int(start_ip)
        end_int = int(end_ip)
        if start_int > end_int:
            start_int, end_int = end_int, start_int

        return [str(ipaddress.ip_address(i)) for i in range(start_int, end_int + 1)]

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
            expanded_ips: List[str] = []
            for ip_entry in entity.ips:
                expanded_ips.extend(self._expand_range_entry(ip_entry, entity.name))
            return [Host(name=ip, address=ip) for ip in expanded_ips]

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
