import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from agentic_memory import retrieve_relevant_memory, store_user_fact

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Mem0 Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Styling ---
st.markdown("""
    <style>
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 15px;
    }
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    .user-id-badge {
        padding: 2px 8px;
        border-radius: 10px;
        background-color: #f0f2f6;
        color: #31333F;
        font-size: 0.8rem;
        font-weight: 600;
    }
    /* Simple glassmorphism-ish effect for sidebar headers */
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        color: #6c757d;
        border-bottom: 1px solid #dee2e6;
        padding-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session():
    """Initialize necessary session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = None

def start_chat_app():
    initialize_session()
    
    # --- Sidebar ---
    with st.sidebar:
        st.title("🧠 Mem0 Dashboard")
        
        # User management section
        st.markdown('<div class="sidebar-header">Identity</div>', unsafe_allow_html=True)
        if st.session_state.user_id:
            st.success(f"Logged in as: **{st.session_state.user_id}**")
            if st.button("Switch User"):
                st.session_state.user_id = None
                st.session_state.messages = []
                st.rerun()
        else:
            user_input_name = st.text_input("Enter your name:", placeholder="e.g. Soban")
            if st.button("Connect"):
                if user_input_name:
                    st.session_state.user_id = user_input_name.strip()
                    st.rerun()
        
        # Memory View section
        if st.session_state.user_id:
            st.markdown('<div class="sidebar-header">Long-term Memories</div>', unsafe_allow_html=True)
            memories = retrieve_relevant_memory("general knowledge about user", st.session_state.user_id)
            if memories and memories != "None.":
                for memory in memories.split("\n"):
                    if memory.startswith("-"):
                        st.info(memory[2:])
            else:
                st.caption("No memories stored yet. Talk to me!")

    # --- Main Chat Interface ---
    st.title("Interactive Memory Chatbot")
    st.caption("A futuristic chatbot powered by Groq & Mem0")

    if not st.session_state.user_id:
        st.warning("Please enter your name in the sidebar to start chatting.")
        st.stop()

    # Display chat messages from history
    for msg in st.session_state.messages:
        avatar = "👤" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Chat Input
    if user_input := st.chat_input("Ask me anything..."):
        # Store user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # Process response
        with st.chat_message("assistant", avatar="🤖"):
            with st.status("🧠 Consulting long-term memory...", expanded=False) as status:
                known_facts = retrieve_relevant_memory(user_input, st.session_state.user_id)
                status.update(label="✨ Memory retrieved! Thinking...", state="running")
                
                # System prompt
                system_prompt = f"""
You are a helpful assistant with access to user memory.
Known facts about the user:
{known_facts if known_facts else "None."}

Instructions:
1. Use known facts if relevant to make the conversation personalized.
2. Be concise and helpful.
"""
                # Prepare messages for API
                api_messages = [{"role": "system", "content": system_prompt}]
                for m in st.session_state.messages:
                    api_messages.append({"role": m["role"], "content": m["content"]})

                # Groq Call
                client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                response = client.chat.completions.create(
                    model="moonshotai/kimi-k2-instruct",
                    messages=api_messages,
                    temperature=0.3
                )
                
                reply = response.choices[0].message.content
                status.update(label="✅ Response ready!", state="complete", expanded=False)

            # Display response
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
            # Save facts in background
            store_user_fact(user_input, st.session_state.user_id)
            
            # Rerun to update sidebar memories if a new one was added
            st.rerun()

if __name__ == "__main__":
    start_chat_app()
