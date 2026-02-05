import json
import os
from typing import Literal

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from mem0 import MemoryClient
from pydantic import BaseModel, ValidationError

load_dotenv()


class MemoryDecision(BaseModel):
    save: Literal["yes", "no"]


MEMORY_CLASSIFIER_SYSTEM_PROMPT = """
You are a classifier for long-term memory in a chatbot.

Decide whether the user's message contains a stable, user-specific fact that
will be useful in future conversations. Save-worthy facts include:
- Identity or background (name, job, location, education)
- Long-term preferences (likes, dislikes, favorites)
- Long-term projects or goals
- Personal traits or recurring constraints

Do NOT save if the message is:
- A question or request
- A transient status update or one-off plan
- Generic conversation with no user-specific facts
- Sensitive data (passwords, secrets, medical, financial, legal)

Output JSON only, exactly in one of these forms:
{"save": "yes"}
{"save": "no"}
""".strip()


@st.cache_resource
def get_memory_client() -> MemoryClient:
    """Create and cache the Mem0 client."""
    return MemoryClient(api_key=os.getenv("MEM0_API_KEY"))


@st.cache_resource
def get_gemini_client() -> genai.Client:
    """Create and cache the Gemini client."""
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def _parse_memory_decision(raw_text: str) -> MemoryDecision:
    """Parse the model output into a validated MemoryDecision."""
    return MemoryDecision.model_validate_json(raw_text)


def is_fact_important(user_text: str) -> bool:
    """Return True if the user's message should be stored as long-term memory."""
    client = get_gemini_client()
    try:
        response = client.models.generate_content(
            model="gemma-3-27b",
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=MEMORY_CLASSIFIER_SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=MemoryDecision,
                temperature=0,
                max_output_tokens=20,
            ),
        )

        if getattr(response, "parsed", None) is not None:
            decision = response.parsed
        else:
            decision = _parse_memory_decision(response.text or "")

        return decision.save == "yes"
    except (ValidationError, json.JSONDecodeError) as e:
        st.warning(f"Memory classifier returned invalid JSON: {str(e)}")
        return False
    except Exception as e:
        st.warning(f"Memory classifier failed: {str(e)}")
        return False


def store_user_fact(user_text: str, user_id: str = "default_user") -> None:
    """Store a user fact in Mem0 if the classifier deems it important."""
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
