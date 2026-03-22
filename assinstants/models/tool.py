"""Tool models — wrap function definitions for use by assistants."""

from pydantic import BaseModel

from .function import FunctionDefinition


class FunctionTool(BaseModel):
    """A tool backed by a function definition."""

    type: str = "function"
    function: FunctionDefinition


class Tool(BaseModel):
    """Wrapper around a FunctionTool for the assistant's tool list."""

    tool: FunctionTool
