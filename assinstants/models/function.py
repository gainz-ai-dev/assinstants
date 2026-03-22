# models/function.py
from pydantic import BaseModel, Field
from typing import Any, Callable, Dict, List, Optional


class FunctionParameter(BaseModel):
    type: str
    description: str
    enum: Optional[List[str]] = None


class FunctionDefinition(BaseModel):
    name: str = Field(..., max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    description: str
    parameters: Dict[str, FunctionParameter]
    implementation: Callable

    class Config:
        arbitrary_types_allowed = True


class FunctionResult(BaseModel):
    name: str
    result: Any
