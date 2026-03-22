# core/assistant_manager.py
from ..models.assistant import Assistant
from typing import Callable, Dict, List, Optional
import uuid
from ..models.tool import Tool
from ..utils.exceptions import AssistantNotFoundError
from ..utils.logging_utils import log


class AssistantManager:
    """
    Manages the creation and retrieval of assistants.
    """

    def __init__(self) -> None:
        """
        Initialize the AssistantManager.
        """
        self.assistants: Dict[str, Assistant] = {}
        self.custom_llm_function: Optional[Callable] = None
        log("ASSISTANT", "AssistantManager initialized")

    def set_custom_llm_function(self, custom_function: Callable) -> None:
        """
        Set the custom LLM function for generating responses.

        Args:
            custom_function (Callable): The custom LLM function.
        """
        self.custom_llm_function = custom_function
        log("ASSISTANT", "Custom LLM function set")

    async def create_assistant(
        self,
        name: str,
        instructions: str,
        model: str,
        custom_llm_function: Callable,
        tools: Optional[List[Tool]] = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> Assistant:
        assistant = Assistant(
            id=str(uuid.uuid4()),
            name=name,
            instructions=instructions,
            model=model,
            custom_llm_function=custom_llm_function,
            tools=tools or [],
            temperature=temperature,
            **kwargs,
        )
        self.assistants[assistant.id] = assistant
        log("ASSISTANT", f"Created assistant with id: {assistant.id}")
        return assistant

    async def get_assistant(self, assistant_id: str) -> Assistant:
        """
        Retrieve an assistant by ID.

        Args:
            assistant_id (str): The ID of the assistant to retrieve.

        Returns:
            Assistant: The retrieved assistant object.

        Raises:
            ValueError: If the assistant with the given ID is not found.
        """
        assistant = self.assistants.get(assistant_id)
        if assistant is None:
            log("ERROR", f"Assistant with id {assistant_id} not found")
            raise AssistantNotFoundError(f"Assistant with id {assistant_id} not found")
        log("ASSISTANT", f"Retrieved assistant with id: {assistant_id}")
        return assistant

    async def add_tool(self, assistant_id: str, tool: Tool) -> Assistant:
        """
        Add a tool to an existing assistant.

        Args:
            assistant_id (str): The ID of the assistant to add the tool to.
            tool (Tool): The tool to add.

        Returns:
            Assistant: The updated assistant object.

        Raises:
            ValueError: If the assistant with the given ID is not found.
        """
        assistant = await self.get_assistant(assistant_id)
        assistant.tools.append(tool)
        log("ASSISTANT", f"Added tool to assistant {assistant_id}")
        return assistant
