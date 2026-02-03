import streamlit as st
from mem0 import MemoryClient
from dotenv import load_dotenv
import re
import os

load_dotenv()

@st.cache_resource
def get_memory_client():
    return MemoryClient(
        api_key=os.getenv("MEM0_API_KEY")
    )


def is_fact_important(user_text):
    IMPORTANT_TRIGGERS = [
        "my name is", "i am", "i'm",
        "i like", "i love", "i hate", "i prefer",
        "i work as", "i am working on", "i'm working on", "i study",
        "i want", "i need", "i can", "i cannot", "i can't",
        "i have", "i own", "i live in", "i lived in",
        "i was born", "my job", "my hobby", "my favorite"
    ]

    text_lower = user_text.lower()
    for trigger in IMPORTANT_TRIGGERS:
        if re.search(r"\b" + re.escape(trigger) + r"\b", text_lower):
            return True

    return False


def store_user_fact(user_text, user_id="default_user"):
    if is_fact_important(user_text):
        client = get_memory_client()
        client.add(
            messages=[
            {
                "role": "user",
                "content": user_text
            }],
            user_id=user_id,
            version="v2"
        )

def retrieve_relevant_memory(user_text, user_id="default_user"):
    client = get_memory_client()
    search_results = client.search(
        query=user_text,
        filters={
            "AND": [
                {"user_id": user_id}
            ]
        },
        version="v2",
        limit=5
    )
    
    results = search_results.get("results") if search_results else []
    
    if not results:
        return "None."
        
    return "\n".join(f"- {r['memory']}" for r in results)