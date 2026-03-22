# Assinstants — Provider-Agnostic LLM Assistant Framework

## Overview
A lightweight Python library for building AI assistants with tool/function calling. Works with any LLM provider (OpenAI, Anthropic, Ollama, etc.) via a custom LLM function pattern.

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
├── __init__.py              # Public API: AssistantManager, ThreadManager, RunManager, Tool
├── core/
│   ├── assistant_manager.py # Create/retrieve assistants with tools
│   ├── thread_manager.py    # Create threads, add messages, manage conversations
│   └── run_manager.py       # Execute runs: LLM planning → function calls → response
├── models/
│   ├── assistant.py         # Assistant (name, instructions, model, tools, temperature)
│   ├── thread.py            # Thread (messages, assistants)
│   ├── message.py           # Message (role: user|assistant, content)
│   ├── run.py               # Run (status, steps, token_usage)
│   ├── tool.py              # Tool, FunctionTool wrappers
│   ├── function.py          # FunctionDefinition, FunctionParameter
│   └── shared.py            # FunctionCall, StepDetails
└── utils/
    ├── exceptions.py        # 5 exception types (AssistantNotFound, ThreadNotFound, etc.)
    └── logging_utils.py     # Colored console logging
```

## Key Patterns

### Usage Flow
```python
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

### Custom LLM Function
```python
async def my_llm_function(model: str, prompt: str, **kwargs) -> str:
    # Call any LLM provider and return the response text
    ...
```

### Two-Phase Execution
1. **Planning**: LLM analyzes query → returns JSON with steps and function calls
2. **Response**: LLM generates conversational response using function results

### Storage
All data is in-memory (Dict[str, Model]). No persistence layer — the consuming application handles that.

## Running Tests
```bash
mypy --ignore-missing-imports assinstants  # Type checking (CI)
```
