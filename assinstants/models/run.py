"""Run model — represents a single execution of an assistant on a thread."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .shared import StepDetails


class RunStatus(str, Enum):
    """Possible states of a run."""

    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    REQUIRES_ACTION = "requires_action"
    COMPLETED = "completed"
    FAILED = "failed"


class RequiredAction(BaseModel):
    """An action required from the user before the run can continue."""

    type: str
    description: str
    data: Optional[Dict[str, Any]] = None


class Run(BaseModel):
    """Tracks the execution state of an assistant processing a thread."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    assistant_id: str
    thread_id: str
    status: RunStatus = RunStatus.QUEUED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    steps: List[StepDetails] = Field(default_factory=list)
    error: Optional[str] = None
    token_usage: Dict[str, int] = Field(default_factory=dict)
    required_action: Optional[RequiredAction] = None
