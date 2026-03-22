# Assinstants — Provider-Agnostic LLM Assistant Framework

## Overview
A lightweight Python library for building AI assistants with tool/function calling. Works with any LLM provider (OpenAI, Anthropic, Ollama, etc.) via a custom LLM function pattern. Published to PyPI.

## Tech Stack
- **Language**: Python 3.8+
- **Data Validation**: Pydantic v2
- **HTTP**: aiohttp (async)
- **Versioning**: Commitizen (semantic versioning)
- **Type Checking**: mypy
- **Publishing**: PyPI (via GitHub Actions)

## Project Structure
```
assinstants/
├── __init__.py              # Public API exports
├── _version.py              # Auto-generated version
├── core/
│   ├── assistant_manager.py # Create/retrieve assistants with tools (94 lines)
│   ├── thread_manager.py    # Create threads, add messages (74 lines)
│   └── run_manager.py       # Execute runs: LLM planning → function calls → response (494 lines)
├── models/
│   ├── assistant.py         # Assistant (name, instructions, model, tools, temperature)
│   ├── thread.py            # Thread (messages, assistants)
│   ├── message.py           # Message (role: user|assistant, content)
│   ├── run.py               # Run (status, steps, token_usage), RunStatus enum
│   ├── tool.py              # Tool, FunctionTool wrappers
│   ├── function.py          # FunctionDefinition, FunctionParameter
│   ├── shared.py            # FunctionCall, StepDetails
│   └── base.py              # Base model config
└── utils/
    ├── exceptions.py        # AssistantNotFoundError, ThreadNotFoundError, RunExecutionError, etc.
    └── logging_utils.py     # Colored console logging with log() function
```

## Key Patterns

### Usage Flow (how the library is consumed)
```python
from assinstants import AssistantManager, ThreadManager, RunManager, Tool

manager = AssistantManager()
threads = ThreadManager()
runs = RunManager(manager, threads)

assistant = await manager.create_assistant(
    name="Coach", instructions="...", model="claude-sonnet-4-20250514",
    custom_llm_function=my_llm_func, tools=[tool]
)
thread = await threads.create_thread()
await threads.add_assistant_to_thread(thread.id, assistant)
await threads.add_message(thread.id, "user", "Create a workout plan")
run = await runs.create_and_execute_run(thread.id)
```

### Custom LLM Function (provider-agnostic interface)
```python
async def my_llm_function(model: str, prompt: str, **kwargs) -> str:
    # Call any LLM provider and return the response text as a string
    ...
```

### Two-Phase Run Execution (in RunManager)
1. **Planning** (`_process_query`): LLM analyzes query → returns JSON with steps and function calls
2. **Execution** (`_execute_step`): Runs each function call from the plan
3. **Response** (`_generate_final_response`): LLM generates conversational response using function results

### Constants (in run_manager.py)
- `CONVERSATION_HISTORY_LIMIT = 5` — messages sent to LLM for context
- `MAX_LLM_RETRIES = 3` — retry attempts for JSON parsing failures

### Storage
All data is in-memory (`Dict[str, Model]`). No persistence layer — the consuming application handles that.

### JSON Response Parsing
Use `_parse_json_response()` for all LLM response parsing. It handles:
- Direct JSON parsing
- Extracting JSON from text that contains extra content around the JSON
- Fallback to raw string if no JSON found

## Common Mistakes to Avoid

- **Never** duplicate JSON extraction logic — always use `_parse_json_response()`.
- **Never** hardcode magic numbers — use the module constants `CONVERSATION_HISTORY_LIMIT`, `MAX_LLM_RETRIES`.
- **Never** add new public exports without updating both `models/__init__.py` AND `__init__.py`.
- **Always** use Pydantic models for data structures — no plain dicts for structured data.
- **Always** raise specific exception types from `utils/exceptions.py`, not generic `Exception`.
- **Always** use `log()` from `utils/logging_utils.py` for logging, not `print()`.

## Public API (exported from `__init__.py`)
```python
AssistantManager, ThreadManager, RunManager, Tool
set_logging
# Exceptions:
BaseAIFrameworkError, AssistantNotFoundError, ThreadNotFoundError,
RunExecutionError, FunctionExecutionError, FunctionNotFoundError
```

## Running Checks
```bash
mypy --ignore-missing-imports assinstants  # Type checking
```
