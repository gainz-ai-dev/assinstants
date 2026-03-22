# utils/exceptions.py


class BaseAIFrameworkError(Exception):
    """Base exception for all AI framework errors."""

    def __init__(self, message: str):
        super().__init__(message)


class AssistantNotFoundError(BaseAIFrameworkError):
    """Raised when an assistant is not found."""


class ThreadNotFoundError(BaseAIFrameworkError):
    """Raised when a thread is not found."""


class InvalidProviderError(BaseAIFrameworkError):
    """Raised when an invalid provider is specified."""


class RunExecutionError(BaseAIFrameworkError):
    """Raised when there's an error during run execution."""


class MessageNotFoundError(BaseAIFrameworkError):
    """Raised when a message is not found."""


class StorageError(BaseAIFrameworkError):
    """Raised when there's an error with storage operations."""


class ProviderAPIError(BaseAIFrameworkError):
    """Raised when there's an error with the provider's API."""


class InvalidInputError(BaseAIFrameworkError):
    """Raised when invalid input is provided to a function or method."""


class ConfigurationError(BaseAIFrameworkError):
    """Raised when there's an error in the configuration."""


class AuthenticationError(BaseAIFrameworkError):
    """Raised when there's an authentication error."""


class RateLimitError(BaseAIFrameworkError):
    """Raised when a rate limit is exceeded."""


class TimeoutError(BaseAIFrameworkError):
    """Raised when an operation times out."""


class ConcurrencyError(BaseAIFrameworkError):
    """Raised when there's an error related to concurrent operations."""


class ModelNotFoundError(BaseAIFrameworkError):
    """Raised when a specified model is not found."""


class InsufficientPermissionsError(BaseAIFrameworkError):
    """Raised when the operation lacks necessary permissions."""


class DataValidationError(BaseAIFrameworkError):
    """Raised when data fails validation checks."""


class ResourceExhaustedError(BaseAIFrameworkError):
    """Raised when a resource (e.g., tokens, storage) is exhausted."""


class UnsupportedOperationError(BaseAIFrameworkError):
    """Raised when an unsupported operation is attempted."""


class FunctionNotFoundError(BaseAIFrameworkError):
    """Raised when a function is not found."""


class FunctionExecutionError(BaseAIFrameworkError):
    """Raised when there's an error executing a function."""
