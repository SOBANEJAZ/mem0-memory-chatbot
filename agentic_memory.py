import json
import os
from typing import Literal

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from mem0 import MemoryClient
from pydantic import BaseModel, ValidationError

load_dotenv()


class MemoryDecision(BaseModel):
    save: Literal["yes", "no"]


MEMORY_CLASSIFIER_SYSTEM_PROMPT = """
You classify user messages for long-term memory storage.

Save stable, user-specific facts that will be useful in future conversations:
- Identity details (name, job, location, education)
- Preferences (likes, dislikes, favorites)
- Long-term projects or goals
- Personal traits or recurring constraints

Do not save:
- Questions or requests
- Temporary updates or one-off plans
- Generic conversation without user-specific facts
- Sensitive data (passwords, secrets, medical, financial, legal)

Output JSON in one of these forms:
{"save": "yes"}
{"save": "no"}
""".strip()


@st.cache_resource
def get_memory_client() -> MemoryClient:
    """Initialize and cache the Mem0 client."""
    return MemoryClient(api_key=os.getenv("MEM0_API_KEY"))


@st.cache_resource
def get_groq_client() -> Groq:
    """Initialize and cache the Groq client."""
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def _parse_memory_decision(raw_text: str) -> MemoryDecision:
    """Validate and parse the model output into a MemoryDecision."""
    return MemoryDecision.model_validate_json(raw_text)


def is_fact_important(user_text: str) -> bool:
    """Check if the user's message contains important facts for long-term memory."""
    client = get_groq_client()
    try:
        response = client.chat.completions.create(
            model="moonshotai/kimi-k2-instruct",
            messages=[
                {
                    "role": "system",
                    "content": MEMORY_CLASSIFIER_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ],
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=20,
        )

        decision = _parse_memory_decision(response.choices[0].message.content or "")

        return decision.save == "yes"
    except (ValidationError, json.JSONDecodeError) as e:
        st.warning(f"Memory classifier returned invalid JSON: {str(e)}")
        return False
    except Exception as e:
        st.warning(f"Memory classifier failed: {str(e)}")
        return False


def store_user_fact(user_text: str, user_id: str = "default_user") -> None:
    """Store a user fact in Mem0 if the classifier determines it's important."""
    if not user_text:
        return

    if is_fact_important(user_text):
        client = get_memory_client()
        client.add(
            messages=[{"role": "user", "content": user_text}],
            user_id=user_id,
            version="v2",
        )


def retrieve_relevant_memory(user_text: str, user_id: str = "default_user") -> str:
    """Retrieve relevant memory for a user given the current message."""
    client = get_memory_client()
    search_results = client.search(
        query=user_text,
        filters={"AND": [{"user_id": user_id}]},
        version="v2",
        limit=5,
    )

    results = search_results.get("results") if search_results else []

    if not results:
        return "None."

    return "\n".join(f"- {r['memory']}" for r in results)
