"""Domain-specific exceptions for the DcoY platform."""

class DcoYException(Exception):
    """Base exception for all domain errors."""
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class EntityNotFoundError(DcoYException):
    """Raised when a requested database entity does not exist."""
    pass


class ValidationError(DcoYException):
    """Raised when data input payload validation fails."""
    pass


class AuthenticationFailedError(DcoYException):
    """Raised when user registration or login verification fails."""
    pass


class ServiceUnavailableError(DcoYException):
    """Raised when a dependency engine (e.g. Ollama model) is unreachable."""
    pass
