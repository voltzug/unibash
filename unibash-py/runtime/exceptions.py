class UnibashRuntimeError(Exception):
    """Base exception for Unibash runtime errors."""

    pass


class DuplicateNameError(UnibashRuntimeError):
    """Raised when an entity (host, group, var) is defined more than once."""

    def __init__(self, name: str, entity_type: str = "entity"):
        self.name = name
        self.entity_type = entity_type
        super().__init__(
            f"Duplicate {entity_type} definition: '{name}' already exists."
        )


class MissingReferenceError(UnibashRuntimeError):
    """Raised when referencing an undefined entity."""

    def __init__(self, name: str, expected_type: str = "entity"):
        self.name = name
        self.expected_type = expected_type
        super().__init__(f"Missing reference: {expected_type} '{name}' is not defined.")


class InvalidTargetError(UnibashRuntimeError):
    """Raised when a target is not valid for a given operation."""

    def __init__(self, name: str, reason: str):
        self.name = name
        self.reason = reason
        super().__init__(f"Invalid target '{name}': {reason}")
