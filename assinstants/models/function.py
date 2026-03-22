"""Function models — define callable tools for assistants."""

from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field


class FunctionParameter(BaseModel):
    """A single parameter for a function definition."""

    type: str
    description: str
    enum: Optional[List[str]] = None


class FunctionDefinition(BaseModel):
    """Defines a function that an assistant can call, including its implementation."""

    name: str = Field(..., max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    description: str
    parameters: Dict[str, FunctionParameter]
    implementation: Callable

    class Config:
        arbitrary_types_allowed = True


class FunctionResult(BaseModel):
    """The result of a function call."""

    name: str
    result: Any
