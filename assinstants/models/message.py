"""Message model — represents a single message in a conversation thread."""

from datetime import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel


class Message(BaseModel):
    """A message in a thread, either from the user or an assistant."""

    role: Union[Literal["user"], Literal["assistant"]]
    content: str
    assistant_id: Optional[str] = None
    created_at: Optional[datetime] = None
