import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from agentic_memory import retrieve_relevant_memory, store_user_fact

load_dotenv()

def start_chat_app():
    """Initialize and run the memory-enabled chatbot interface."""
    st.title("Memory Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Type your message...")

    if user_input:
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        known_facts = retrieve_relevant_memory(user_input)

        # System prompt with user memory context
        system_prompt = f"""
You are a helpful assistant with access to user memory.

Known facts:
{known_facts if known_facts else "None."}

Instructions:
1. Use known facts if relevant.
2. Be concise and helpful.
3. Do not ask for known info.
"""

        # Call Groq API for response
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        chat_history = []
        for msg in st.session_state.messages[:-1]:
             chat_history.append({"role": msg["role"], "content": msg["content"]})

        chat_history.append({"role": "system", "content": system_prompt})

        response = client.chat.completions.create(
            model="moonshotai/kimi-k2-instruct",
            messages=chat_history,
            temperature=0.3
        )

        reply = response.choices[0].message.content

        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )

        store_user_fact(user_input)

        with st.chat_message("user"):
            st.write(user_input)
        with st.chat_message("assistant"):
            st.write(reply)

if __name__ == "__main__":
    start_chat_app()
