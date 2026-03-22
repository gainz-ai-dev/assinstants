"""Thread manager — handles creation and management of conversation threads."""

from datetime import datetime
from typing import Dict, List, Literal, Optional, Union

from ..models.assistant import Assistant
from ..models.message import Message
from ..models.thread import Thread
from ..utils.exceptions import ThreadNotFoundError
from ..utils.logging_utils import log


class ThreadManager:
    """Manages conversation threads, their messages, and assigned assistants."""

    def __init__(self) -> None:
        self.threads: Dict[str, Thread] = {}
        log("THREAD", "ThreadManager initialized")

    async def create_thread(self) -> Thread:
        """Create a new empty thread."""
        thread = Thread()
        self.threads[thread.id] = thread
        log("THREAD", f"Thread created with id: {thread.id}")
        return thread

    async def get_thread(self, thread_id: str) -> Thread:
        """Retrieve a thread by ID. Raises ThreadNotFoundError if not found."""
        thread = self.threads.get(thread_id)
        if thread is None:
            raise ThreadNotFoundError(f"Thread with id {thread_id} not found")
        return thread

    async def add_assistant_to_thread(
        self, thread_id: str, assistant: Assistant
    ) -> None:
        """Add an assistant to a thread."""
        thread = await self.get_thread(thread_id)
        thread.assistants.append(assistant)
        log("THREAD", f"Added assistant {assistant.id} to thread {thread_id}")

    async def remove_assistant_from_thread(
        self, thread_id: str, assistant_id: str
    ) -> None:
        """Remove an assistant from a thread by ID."""
        thread = await self.get_thread(thread_id)
        thread.assistants = [
            a for a in thread.assistants if a.id != assistant_id
        ]
        log("THREAD", f"Removed assistant {assistant_id} from thread {thread_id}")

    async def add_message(
        self,
        thread_id: str,
        role: Union[Literal["user"], Literal["assistant"]],
        content: str,
        assistant_id: Optional[str] = None,
    ) -> Message:
        """Add a message to a thread."""
        thread = await self.get_thread(thread_id)
        message = Message(
            role=role,
            content=content,
            assistant_id=assistant_id,
            created_at=datetime.now(),
        )
        thread.messages.append(message)
        log("THREAD", f"Added {role} message to thread {thread_id}")
        return message

    async def get_messages(self, thread_id: str) -> List[Message]:
        """Get all messages in a thread."""
        thread = await self.get_thread(thread_id)
        return thread.messages
