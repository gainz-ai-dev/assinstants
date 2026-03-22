# core/thread_manager.py
from ..models.thread import Thread
from ..models.assistant import Assistant
from typing import Dict, List, Literal, Optional, Union
from datetime import datetime
from ..utils.exceptions import ThreadNotFoundError
from ..utils.logging_utils import log
from ..models.message import Message


class ThreadManager:
    def __init__(self) -> None:
        self.threads: Dict[str, Thread] = {}
        log("THREAD", "ThreadManager initialized")

    async def create_thread(self) -> Thread:
        thread = Thread()
        self.threads[thread.id] = thread
        log("THREAD", f"Thread created with id: {thread.id}")
        return thread

    async def get_thread(self, thread_id: str) -> Thread:
        thread = self.threads.get(thread_id)
        if thread is None:
            log("ERROR", f"Thread with id {thread_id} not found")
            raise ThreadNotFoundError(f"Thread with id {thread_id} not found")
        log("THREAD", f"Retrieved thread with id: {thread_id}")
        return thread

    async def add_assistant_to_thread(
        self, thread_id: str, assistant: Assistant
    ) -> None:
        thread = await self.get_thread(thread_id)
        thread.assistants.append(assistant)
        log("THREAD", f"Added assistant {assistant.id} to thread {thread_id}")

    async def remove_assistant_from_thread(
        self, thread_id: str, assistant_id: str
    ) -> None:
        thread = await self.get_thread(thread_id)
        thread.assistants = [
            assistant for assistant in thread.assistants if assistant.id != assistant_id
        ]
        log("THREAD", f"Removed assistant {assistant_id} from thread {thread_id}")

    async def add_message(
        self,
        thread_id: str,
        role: Union[Literal["user"], Literal["assistant"]],
        content: str,
        assistant_id: Optional[str] = None,
    ) -> Message:
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
        thread = await self.get_thread(thread_id)
        log("THREAD", f"Retrieved messages from thread {thread_id}")
        return thread.messages
