"""Run manager — orchestrates LLM-driven query processing and function execution."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Union

from ..models.assistant import Assistant
from ..models.function import FunctionParameter
from ..models.message import Message
from ..models.run import Run, RunStatus
from ..models.shared import FunctionCall, StepDetails
from ..models.tool import FunctionTool, Tool
from ..utils.exceptions import (
    FunctionExecutionError,
    FunctionNotFoundError,
    RunExecutionError,
)
from ..utils.logging_utils import log
from .assistant_manager import AssistantManager
from .thread_manager import ThreadManager


CONVERSATION_HISTORY_LIMIT = 5
MAX_LLM_RETRIES = 3


class RunManager:
    """Executes runs: plans steps via LLM, calls functions, generates responses."""

    def __init__(
        self, assistant_manager: AssistantManager, thread_manager: ThreadManager
    ) -> None:
        self.assistant_manager = assistant_manager
        self.thread_manager = thread_manager
        self.runs: Dict[str, Run] = {}

    async def create_and_execute_run(self, thread_id: str) -> Run:
        """Create a run from the latest user message in a thread and execute it."""
        log("THREAD", f"Creating and executing run for thread {thread_id}")
        messages = await self.thread_manager.get_messages(thread_id)
        user_query = next(
            (m.content for m in reversed(messages) if m.role == "user"), None
        )
        if not user_query:
            raise RunExecutionError("No user message found in the thread")

        log("THREAD", f"User query: {user_query}")
        thread = await self.thread_manager.get_thread(thread_id)

        if not thread.assistants:
            raise RunExecutionError(
                f"Thread {thread_id} has no assistants. "
                "Add an assistant before executing a run."
            )

        run = Run(thread_id=thread_id, assistant_id=thread.assistants[0].id)
        self.runs[run.id] = run
        return await self.execute_run(
            run.id, user_query, thread.assistants, messages[-CONVERSATION_HISTORY_LIMIT:]
        )

    async def execute_run(
        self,
        run_id: str,
        user_query: str,
        assistants: List[Assistant],
        messages: List[Message],
    ) -> Run:
        """Execute a run: plan steps, call functions, generate final response."""
        log("THREAD", f"Executing run {run_id}")
        run = self.runs.get(run_id)
        if not run:
            raise RunExecutionError(f"Run with id {run_id} not found")

        run.status = RunStatus.IN_PROGRESS
        run.started_at = datetime.now(timezone.utc)
        log("THREAD", f"Run {run_id} started at {run.started_at}")

        try:
            serializable_messages = self._serialize_messages(messages)
            process_result = await self._process_query(
                user_query, serializable_messages, assistants
            )
            run.assistant_id = process_result["assistant_id"]
            run.steps = process_result["steps"]

            selected_assistant = next(
                (a for a in assistants if a.id == run.assistant_id),
                assistants[0],
            )
            log("ASSISTANT", f"Selected assistant: {selected_assistant.name}")

            function_results: List[Dict[str, Any]] = []
            errors: List[str] = []
            for step in run.steps:
                log("STEP", f"Executing step {step.step_number}: {step.description}")
                try:
                    step_results = await self._execute_step(run.assistant_id, step)
                    function_results.extend(step_results)
                    step.results = step_results
                except FunctionExecutionError as e:
                    log("ERROR", f"Function execution error: {e}")
                    errors.append(str(e))

            final_response = await self._generate_final_response(
                selected_assistant,
                user_query,
                function_results,
                serializable_messages,
                errors,
            )

            # Extract the actual response from the JSON
            try:
                response_json = json.loads(final_response)
                if isinstance(response_json, dict) and "response" in response_json:
                    extracted_response = response_json["response"].strip()
                else:
                    extracted_response = final_response.strip()
            except json.JSONDecodeError:
                extracted_response = final_response.strip()

            log("THREAD", f"Final response: {extracted_response}")
            await self.thread_manager.add_message(
                run.thread_id, "assistant", extracted_response, run.assistant_id
            )

            run.status = RunStatus.COMPLETED
            run.completed_at = datetime.now(timezone.utc)
            log("THREAD", f"Run {run_id} completed at {run.completed_at}")
            return run

        except (RunExecutionError, FunctionNotFoundError):
            run.status = RunStatus.FAILED
            raise
        except Exception as e:
            run.status = RunStatus.FAILED
            run.error = str(e)
            log("ERROR", f"Run execution failed: {e}")
            raise RunExecutionError(f"Run execution failed: {e}")

    async def get_run(self, run_id: str) -> Run:
        """Retrieve a run by its ID."""
        run = self.runs.get(run_id)
        if run is None:
            raise RunExecutionError(f"Run with id {run_id} not found")
        return run

    # --- Internal helpers ---

    def _serialize_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        return [
            {
                "role": message.role,
                "content": message.content,
                "created_at": (
                    message.created_at.isoformat() if message.created_at else None
                ),
                "assistant_id": message.assistant_id,
            }
            for message in messages
        ]

    def _serialize_function_parameter(self, param: FunctionParameter) -> Dict[str, Any]:
        return {
            "type": param.type,
            "description": param.description,
            "enum": param.enum,
        }

    def _parse_json_response(self, response: str) -> Union[Dict[str, Any], str]:
        """Try to parse JSON from a response, with fallback extraction."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                try:
                    return json.loads(response[json_start:json_end])
                except json.JSONDecodeError:
                    log("ERROR", "Failed to extract valid JSON from response")
            log("ERROR", "No valid JSON found in response")
            return response.strip()

    async def _process_query(
        self,
        user_query: str,
        messages: List[Dict[str, Any]],
        assistants: List[Assistant],
    ) -> Dict[str, Any]:
        """Use the LLM to plan execution steps based on the user query."""
        available_functions = [
            {
                "name": tool.tool.function.name,
                "description": tool.tool.function.description,
                "parameters": {
                    name: self._serialize_function_parameter(param)
                    for name, param in tool.tool.function.parameters.items()
                },
            }
            for assistant in assistants
            for tool in assistant.tools
            if isinstance(tool.tool, FunctionTool)
        ]

        prompt = f"""
Analyze the following user query and determine the necessary steps to respond:

<user_query>
{user_query}
</user_query>

Recent conversation history:
{self._format_conversation_history(messages[-CONVERSATION_HISTORY_LIMIT:])}

Available assistants and their functions:
{self._format_assistants_and_functions(assistants)}

Task: Determine the steps needed to respond to the user query and select the most appropriate assistant. Use available functions only when required. For general conversation, no function calls are needed.

Your response should be a valid JSON object with the following structure:
{{
    "steps": [
        {{
            "step_number": integer,
            "description": "string",
            "function_calls": [
                {{
                    "name": "string",
                    "arguments": object
                }}
            ]
        }}
    ],
    "selected_assistant_index": integer
}}

Important instructions:
- Respond ONLY with a valid JSON object matching the output format.
- Do not include any text outside the JSON structure.
- Strictly adhere to the function parameters if a function call is needed.
- Always select an appropriate assistant by setting the selected_assistant_index.
- Choose the assistant that has the required functions for the task.
"""

        for attempt in range(MAX_LLM_RETRIES):
            try:
                response = await assistants[0].custom_llm_function(
                    assistants[0].model, prompt
                )
                log("STEP", f"LLM response received (attempt {attempt + 1})")

                parsed = self._parse_json_response(response)
                if isinstance(parsed, str):
                    raise json.JSONDecodeError(
                        "No JSON found in the response", response, 0
                    )
                result = parsed

                steps = result.get("steps", [])
                selected_assistant_index = result.get("selected_assistant_index")

                # Validate function calls against available functions
                available_function_names = {
                    func["name"] for func in available_functions
                }
                steps = [
                    {
                        **step,
                        "function_calls": [
                            call
                            for call in step.get("function_calls", [])
                            if call.get("name") in available_function_names
                        ],
                    }
                    for step in steps
                ]
                steps = [step for step in steps if step.get("function_calls")]

                selected_assistant = (
                    assistants[selected_assistant_index]
                    if selected_assistant_index is not None
                    and 0 <= selected_assistant_index < len(assistants)
                    else assistants[0]
                )

                return {
                    "assistant_id": selected_assistant.id,
                    "steps": [
                        StepDetails(
                            step_number=step["step_number"],
                            description=step["description"],
                            function_calls=[
                                FunctionCall(**call)
                                for call in step["function_calls"]
                            ],
                        )
                        for step in steps
                    ],
                }

            except (json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
                log("ERROR", f"Error processing LLM response (attempt {attempt + 1}): {e}")
                if attempt == MAX_LLM_RETRIES - 1:
                    raise RunExecutionError(
                        f"Failed to get valid response after {MAX_LLM_RETRIES} attempts: {e}"
                    )

        raise RunExecutionError("Unexpected error in _process_query")

    async def _execute_step(
        self, assistant_id: str, step: StepDetails
    ) -> List[Dict[str, Any]]:
        """Execute a single step — runs all function calls in the step."""
        results: List[Dict[str, Any]] = []
        assistant = await self.assistant_manager.get_assistant(assistant_id)
        if step.function_calls:
            for function_call in step.function_calls:
                log("FUNCTION", f"Executing function: {function_call.name}")
                result = await self._execute_function(assistant, function_call)
                results.append({function_call.name: result})
        return results

    async def _execute_function(
        self, assistant: Assistant, function_call: FunctionCall
    ) -> Any:
        """Find and execute a function from the assistant's tools."""
        function_tool = next(
            (
                tool.tool.function
                for tool in assistant.tools
                if isinstance(tool.tool, FunctionTool)
                and tool.tool.function.name == function_call.name
            ),
            None,
        )
        if not function_tool:
            raise FunctionNotFoundError(f"Function {function_call.name} not found")

        try:
            result = await function_tool.implementation(**function_call.arguments)
            log("FUNCTION", f"Function {function_call.name} executed successfully")
            return result
        except FunctionExecutionError:
            raise
        except Exception as e:
            raise FunctionExecutionError(
                f"Error executing function {function_call.name}: {e}"
            )

    async def _generate_final_response(
        self,
        selected_assistant: Assistant,
        user_query: str,
        function_results: List[Dict[str, Any]],
        messages: List[Dict[str, Any]],
        errors: List[str],
    ) -> str:
        """Generate the final conversational response using the LLM."""
        log("STEP", "Generating final response")
        prompt = f"""
Generate a natural, conversational response to the following user query:

<user_query>
{user_query}
</user_query>

Recent conversation history:
{self._format_conversation_history(messages[-CONVERSATION_HISTORY_LIMIT:])}

Function results:
{self._format_function_results(function_results)}

Errors encountered:
{self._format_errors(errors)}

Assistant Instructions:
{selected_assistant.instructions}

Available functions:
{self._format_available_functions(selected_assistant.tools)}

Task: Generate a natural, conversational response to the user's query based on the conversation history, function results, and any errors that occurred. If there were errors, acknowledge them in your response. Use the available functions if necessary.

Your response should be a valid JSON object with the following structure:
{{
    "response": "Your generated response as a string",
    "function_calls": [
        {{
            "name": "function_name",
            "arguments": {{}}
        }}
    ]
}}

Important instructions:
- Respond ONLY with a valid JSON object matching the output format.
- Do not include any text outside the JSON structure.
- Incorporate relevant information from the function results and conversation history.
- If there were errors, acknowledge them in a user-friendly manner.
- Keep the tone conversational and natural.
- Use the available functions if they are relevant to the user's query.
- If no functions are needed, provide an empty list for "function_calls".
"""
        response = await selected_assistant.custom_llm_function(
            selected_assistant.model, prompt
        )

        parsed_response = self._parse_json_response(response)
        if isinstance(parsed_response, dict) and "response" in parsed_response:
            # Execute any additional function calls from the response
            additional_calls = parsed_response.get("function_calls") or []
            for call in additional_calls:
                if call.get("name"):
                    try:
                        result = await self._execute_function(
                            selected_assistant, FunctionCall(**call)
                        )
                        parsed_response["response"] += f"\n\nFunction result: {result}"
                    except (FunctionNotFoundError, FunctionExecutionError) as e:
                        parsed_response["response"] += (
                            f"\n\nError executing function: {e}"
                        )

            return parsed_response["response"]
        else:
            log("STEP", "LLM response was not in expected JSON format, using raw")
            return str(parsed_response)

    # --- Formatting helpers ---

    def _format_conversation_history(self, messages: List[Dict[str, Any]]) -> str:
        if not messages:
            return "No conversation history."
        return "\n".join(
            f"[{m['role']}]: {m['content']}" for m in messages
        )

    def _format_available_functions(self, functions: List[Tool]) -> str:
        if not functions:
            return "No functions available."
        parts = []
        for func in functions:
            lines = [
                f"Function: {func.tool.function.name}",
                f"Description: {func.tool.function.description}",
                "Parameters:",
            ]
            for param_name, param_details in func.tool.function.parameters.items():
                lines.append(
                    f"  - {param_name}: {param_details.type} - {param_details.description}"
                )
            parts.append("\n".join(lines))
        return "\n\n".join(parts)

    def _format_assistants_and_functions(self, assistants: List[Assistant]) -> str:
        parts = []
        for index, assistant in enumerate(assistants):
            lines = [
                f"Assistant {index}: {assistant.name}",
                f"Instructions: {assistant.instructions}",
                "Functions:",
            ]
            for tool in assistant.tools:
                if isinstance(tool.tool, FunctionTool):
                    func = tool.tool.function
                    lines.append(f"  - {func.name}: {func.description}")
                    lines.append("    Parameters:")
                    for param_name, param in func.parameters.items():
                        lines.append(
                            f"      {param_name}: {param.type} - {param.description}"
                        )
                        if param.enum:
                            lines.append(
                                f"      Allowed values: {', '.join(param.enum)}"
                            )
            parts.append("\n".join(lines))
        return "\n\n".join(parts)

    def _format_function_results(self, function_results: List[Dict[str, Any]]) -> str:
        if not function_results:
            return "No function results available."
        parts = []
        for result in function_results:
            for func_name, func_result in result.items():
                parts.append(
                    f"Function: {func_name}\n"
                    f"Result: {json.dumps(func_result, indent=2)}"
                )
        return "\n\n".join(parts)

    def _format_errors(self, errors: List[str]) -> str:
        return "\n".join(errors) if errors else "No errors encountered."
