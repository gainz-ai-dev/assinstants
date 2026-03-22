"""Base model with auto-generated UUID."""

import uuid

from pydantic import BaseModel, Field


class BaseModelWithID(BaseModel):
    """Base Pydantic model that auto-generates a UUID id field."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
