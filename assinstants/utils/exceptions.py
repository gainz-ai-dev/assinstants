"""Custom exceptions for the assinstants framework."""


class BaseAIFrameworkError(Exception):
    """Base exception for all AI framework errors."""

    def __init__(self, message: str):
        super().__init__(message)


class AssistantNotFoundError(BaseAIFrameworkError):
    """Raised when an assistant is not found."""


class ThreadNotFoundError(BaseAIFrameworkError):
    """Raised when a thread is not found."""


class RunExecutionError(BaseAIFrameworkError):
    """Raised when there's an error during run execution."""


class FunctionNotFoundError(BaseAIFrameworkError):
    """Raised when a function is not found in the assistant's tools."""


class FunctionExecutionError(BaseAIFrameworkError):
    """Raised when there's an error executing a function."""
