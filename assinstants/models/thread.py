"""Thread model — a conversation container holding messages and assistants."""

from typing import List

from pydantic import Field

from .assistant import Assistant
from .base import BaseModelWithID
from .message import Message


class Thread(BaseModelWithID):
    """A conversation thread containing messages and assigned assistants."""

    messages: List[Message] = Field(default_factory=list)
    assistants: List[Assistant] = Field(default_factory=list)
