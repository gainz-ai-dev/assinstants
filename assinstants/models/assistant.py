"""Assistant model — represents an AI assistant with tools and an LLM backend."""

from typing import Any, Callable, Dict, List, Optional

from pydantic import Field

from .base import BaseModelWithID
from .tool import Tool


class Assistant(BaseModelWithID):
    """An AI assistant with a name, instructions, model, and tools."""

    name: str
    instructions: str
    model: str
    custom_llm_function: Callable
    temperature: float = Field(
        default=0.7,
        description="Sampling temperature for the LLM (0.0 to 1.0).",
    )
    provider_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific configuration.",
    )
    tools: List[Tool] = Field(
        default_factory=list,
        description="List of tools available to the assistant.",
    )
