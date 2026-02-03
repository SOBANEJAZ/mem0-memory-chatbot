import streamlit as st
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from memory import retrieve_relevant_memory, store_user_fact

load_dotenv()

def start_chat_app():
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

        # Simplified System Prompt
        system_prompt = f"""
You are a helpful assistant with access to user memory.

Known facts:
{known_facts if known_facts else "None."}

Instructions:
1. Use known facts if relevant.
2. Be concise and helpful.
3. Do not ask for known info.
"""

        # Gemini Call
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        chat_history = []
        for msg in st.session_state.messages[:-1]: 
             chat_history.append({"role": "user" if msg["role"] == "user" else "model", "parts": [{"text": msg["content"]}]})

        chat = client.chats.create(
            model="gemini-2.5-flash", 
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3
            ),
            history=chat_history
        )
        
        response = chat.send_message(user_input)
        
        reply = response.text

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