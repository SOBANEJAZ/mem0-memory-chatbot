# AGENTS.md - Guidelines for Agentic Coding

This document provides guidelines for AI agents working on this codebase.

## Project Overview

A Streamlit-based chatbot that uses Groq's MoonshotAI Kimi-K2-Instruct model and Mem0 for long-term memory management. The bot remembers user facts across conversations and provides contextual responses.

## Build & Development Commands

### Running the Application

```bash
uv run streamlit run app.py
```

### Development with Auto-Reload

```bash
uv run streamlit run app.py --server.runOnSave true
```

### Dependency Installation

```bash
uv sync
```

### Environment Setup

Copy the example environment file and populate with your API keys:

```bash
cp .env.example .env
```

Required environment variables:
- `GROQ_API_KEY`: Groq Cloud API key
- `MEM0_API_KEY`: Mem0 platform API key

## Code Style Guidelines

### General Principles

- Write clean, self-documenting code
- Keep functions small and focused on a single responsibility
- Use descriptive variable and function names
- Prefer explicit over implicit

### Python Conventions

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values (see `agentic_memory.py:56` for example)
- Write docstrings for all public functions and classes
- Maximum line length: 100 characters

### Imports

Standard library imports first, then third-party, then local:

```python
import os
import json
from typing import Literal

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from mem0 import MemoryClient
from pydantic import BaseModel, ValidationError
```

### Type Hints

Use type hints consistently throughout the codebase:

```python
from typing import Literal

class MemoryDecision(BaseModel):
    save: Literal["yes", "no"]

def retrieve_relevant_memory(user_text: str, user_id: str = "default_user") -> str:
    ...
```

### Naming Conventions

- **Functions**: snake_case (`retrieve_relevant_memory`, `store_user_fact`)
- **Classes**: PascalCase (`MemoryDecision`)
- **Constants**: UPPER_SNAKE_CASE (`MEMORY_CLASSIFIER_SYSTEM_PROMPT`)
- **Variables**: snake_case (`user_input`, `chat_history`)
- **Type aliases**: PascalCase

### Error Handling

- Use try/except blocks for API calls and external service integrations
- Provide informative error messages without exposing sensitive information
- Use Pydantic for input validation (see `agentic_memory.py:14-16`)
- Return `False` or empty values on failure rather than raising exceptions for expected error cases

```python
try:
    decision = _parse_memory_decision(response.choices[0].message.content or "")
    return decision.save == "yes"
except (ValidationError, json.JSONDecodeError) as e:
    st.warning(f"Memory classifier returned invalid JSON: {str(e)}")
    return False
except Exception as e:
    st.warning(f"Memory classifier failed: {str(e)}")
    return False
```

### Docstrings

Write docstrings for all functions using Google-style format:

```python
def retrieve_relevant_memory(user_text: str, user_id: str = "default_user") -> str:
    """Retrieve relevant memory for a user given the current message."""
    ...
```

### Streamlit Patterns

- Use `@st.cache_resource` for expensive initialization (clients, connections)
- Access secrets via `os.getenv()` after `load_dotenv()`
- Use `st.session_state` for chat history persistence

```python
@st.cache_resource
def get_memory_client() -> MemoryClient:
    """Initialize and cache the Mem0 client."""
    return MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
```

### API Integration Guidelines

- Groq API: Use `client.chat.completions.create()` with model `"moonshotai/kimi-k2-instruct"`
- Mem0 API: Use version `"v2"` for all operations
- Set appropriate `temperature` and `max_tokens` for deterministic outputs
- Use JSON response format for classifier tasks

### User Identification

- The application implements name-based user identification
- Users are prompted to enter their name before starting a conversation
- The entered name is used as the user ID for memory storage and retrieval
- This allows users to access their memories across different sessions and devices
- User ID is stored in `st.session_state.user_id` after initial entry

### File Organization

- `app.py`: Main Streamlit application entry point
- `agentic_memory.py`: AI-powered memory classification (preferred)
- `memory.py`: Legacy rule-based classification (fallback)
- Keep related functionality in the same module
