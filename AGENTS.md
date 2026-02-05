# Agent Instructions

## Project Overview

This is a Streamlit-based chatbot using Google's Gemini Flash 2.5 model and Mem0 for long-term memory. The bot remembers key facts about users across conversations.

**Tech Stack**: Python, Streamlit, Google Gemini API, Mem0, Pydantic

**Key Files**:
- `app.py` - Main Streamlit application
- `memory.py` - Simple rule-based memory classification
- `agentic_memory.py` - AI-powered memory classification using Gemini

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
# Install dev dependencies
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
- Example:
```python
import json
import os
from typing import Literal

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from mem0 import MemoryClient
from pydantic import BaseModel, ValidationError
```

### Formatting
- **Indentation**: 4 spaces (standard Python)
- **Line length**: 88 characters (Black default)
- **Quotes**: Use double quotes for strings
- **Blank lines**: 2 lines between top-level functions/classes, 1 line between methods
- **Trailing whitespace**: Remove it

### Naming Conventions
- **Functions/variables**: `snake_case` (e.g., `store_user_fact`, `user_input`)
- **Constants**: `UPPER_CASE` (e.g., `MEMORY_CLASSIFIER_SYSTEM_PROMPT`)
- **Classes**: `PascalCase` (e.g., `MemoryDecision`)
- **Modules**: `lowercase.py` (e.g., `memory.py`, `app.py`)

### Type Hints
- Use type hints for all function parameters and return values
- Use `Optional` for values that can be None
- Use `Literal` for string enums
- Example:
```python
from typing import Optional, Literal
from pydantic import BaseModel

class MemoryDecision(BaseModel):
    save: Literal["yes", "no"]

def retrieve_relevant_memory(user_text: str, user_id: str = "default_user") -> str:
    ...
```

### Error Handling
- Use specific exception types, avoid bare `except:`
- Use `st.warning()` for user-facing errors in Streamlit
- Log errors with context before returning fallback values
- Handle API failures gracefully
- Example:
```python
try:
    response = client.models.generate_content(...)
except (ValidationError, json.JSONDecodeError) as e:
    st.warning(f"Memory classifier returned invalid JSON: {str(e)}")
    return False
except Exception as e:
    st.warning(f"Memory classifier failed: {str(e)}")
    return False
```

### Environment Variables
- Always use `python-dotenv` to load `.env` file at module level
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
- Use `@st.cache_resource` for expensive initializations (API clients)
- Use Pydantic models for structured JSON responses from LLMs
- Structure UI with `st.chat_message()` and `st.write()`

### Pydantic Models
- Use Pydantic for validating LLM JSON responses
- Define response schemas explicitly
- Handle validation errors gracefully

### Testing Standards
- Use pytest; name files `test_<module>.py` and functions `test_<function_name>_<scenario>`
- Use fixtures for shared setup; mock external API calls (Gemini, Mem0)

### Documentation
- Add docstrings to all public functions using Google-style
- Keep README.md updated with setup instructions

### Security
- Never hardcode API keys; use `.env` for all secrets
- Validate user input before processing
- Sanitize outputs displayed in UI
- Never store sensitive data (passwords, medical, financial)

### Dependencies
- Pin versions in `requirements.txt` for reproducibility
- Keep dependencies minimal
