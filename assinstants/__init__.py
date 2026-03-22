"""Assinstants — a provider-agnostic LLM assistant framework."""

from typing import List

from .core.assistant_manager import AssistantManager
from .core.run_manager import RunManager
from .core.thread_manager import ThreadManager
from .models.tool import Tool
from .utils.exceptions import (
    AssistantNotFoundError,
    BaseAIFrameworkError,
    FunctionExecutionError,
    FunctionNotFoundError,
    RunExecutionError,
    ThreadNotFoundError,
)
from .utils.logging_utils import set_logging

try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0"

__all__: List[str] = [
    "AssistantManager",
    "ThreadManager",
    "RunManager",
    "Tool",
    "set_logging",
    "BaseAIFrameworkError",
    "AssistantNotFoundError",
    "ThreadNotFoundError",
    "RunExecutionError",
    "FunctionExecutionError",
    "FunctionNotFoundError",
    "__version__",
]
