# Agent Instructions

## Project Overview

This is a Streamlit-based chatbot using Google's Gemini Flash 2.5 model and Mem0 for long-term memory. The bot remembers key facts about users across conversations.

**Tech Stack**: Python, Streamlit, Google Gemini API, Mem0

## Build & Run Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py

# Run with auto-reload (for development)
streamlit run app.py --server.runOnSave true
```

## Linting & Testing Commands

```bash
# Install dev dependencies (recommended)
pip install pytest ruff black mypy

# Run linter (ruff - preferred for speed)
ruff check .
ruff check . --fix  # Auto-fix issues

# Run formatter
black .

# Run type checker
mypy .

# Run tests
pytest
pytest -v              # Verbose output
pytest tests/test_memory.py  # Single test file
pytest -k test_name    # Run specific test by name

# Run all quality checks
ruff check . && black --check . && mypy . && pytest
```

## Code Style Guidelines

### Imports
- Group imports: standard library → third-party → local
- Sort alphabetically within groups
- Use absolute imports for project files
- Example from codebase:
```python
import os
import re
from dotenv import load_dotenv
import streamlit as st
from google import genai
from google.genai import types
from mem0 import MemoryClient
from memory import retrieve_relevant_memory, store_user_fact
```

### Formatting
- **Indentation**: 4 spaces (standard Python)
- **Line length**: 88 characters (Black default)
- **Quotes**: Use double quotes for strings
- **Blank lines**: 2 lines between top-level functions/classes, 1 line between methods
- **Trailing whitespace**: Remove it

### Naming Conventions
- **Functions/variables**: `snake_case` (e.g., `store_user_fact`, `user_input`)
- **Constants**: `UPPER_CASE` (e.g., `IMPORTANT_TRIGGERS`)
- **Classes**: `PascalCase` (when needed)
- **Modules**: `lowercase.py` (e.g., `memory.py`, `app.py`)

### Type Hints
- Use type hints for function parameters and return values
- Use `Optional` for values that can be None
- Example:
```python
from typing import Optional, List

def retrieve_relevant_memory(user_text: str, user_id: str = "default_user") -> str:
    ...
```

### Error Handling
- Use specific exception types, avoid bare `except:`
- Log errors with context before re-raising if needed
- Handle API failures gracefully with user-friendly messages
- Example:
```python
try:
    response = chat.send_message(user_input)
except Exception as e:
    st.error(f"Failed to get response: {str(e)}")
    return None
```

### Environment Variables
- Always use `python-dotenv` to load `.env` file
- Access via `os.getenv()` with defaults when appropriate
- Never commit `.env` files (keep in `.gitignore`)
- Example:
```python
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
```

### Streamlit Patterns
- Use `st.session_state` for chat history persistence
- Use `st.cache_resource` for expensive initializations (e.g., API clients)
- Structure UI with `st.chat_message()` and `st.write()`

### Testing Standards
- Use pytest for all tests
- Name test files: `test_<module>.py`
- Name test functions: `test_<function_name>_<scenario>`
- Use fixtures for shared setup
- Mock external API calls (Gemini, Mem0)
- Example:
```python
def test_is_fact_important_detects_name():
    assert is_fact_important("My name is John") is True
    assert is_fact_important("Hello") is False
```

### Documentation
- Add docstrings to all public functions
- Use Google-style or NumPy-style docstrings
- Keep README.md updated with setup instructions

### Security
- Never hardcode API keys
- Use `.env` for all secrets
- Validate user input before processing
- Sanitize outputs displayed in UI

### Dependencies
- Pin versions in `requirements.txt` for reproducibility
- Use `pip freeze > requirements.txt` to capture exact versions
- Keep dependencies minimal
