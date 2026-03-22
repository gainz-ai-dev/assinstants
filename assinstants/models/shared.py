"""Shared models used across the framework."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class FunctionCall(BaseModel):
    """Represents a function call with its name and arguments."""

    name: str
    arguments: Dict[str, Any]


class StepDetails(BaseModel):
    """Details of a single execution step within a run."""

    step_number: int
    description: str
    function_calls: Optional[List[FunctionCall]] = None
    results: Optional[Any] = None
