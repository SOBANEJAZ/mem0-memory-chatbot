import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from agentic_memory import retrieve_relevant_memory, store_user_fact

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Mem0 | AI Memory Chat",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Styling (Premium Design) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Outfit:wght@400;600;700&display=swap');

    /* Global Styles */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #1a1a1a 0%, #0c0a09 100%);
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, .sidebar-header {
        font-family: 'Outfit', sans-serif !important;
    }

    /* Message Animation */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Glassmorphism Chat Bubble */
    .stChatMessage {
        animation: fadeInUp 0.4s ease-out forwards;
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px !important;
        padding: 1rem !important;
        margin-bottom: 0.8rem !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }
    
    /* Asymmetric border-radius for message roles */
    div[data-testimonial="true"] .stChatMessage[data-testid="stChatMessageAssistant"] {
        border-bottom-left-radius: 4px !important;
    }
    div[data-testimonial="true"] .stChatMessage[data-testid="stChatMessageUser"] {
        border-bottom-right-radius: 4px !important;
        background: rgba(255, 215, 0, 0.05) !important; /* Subtle gold tint for user */
    }

    /* Sidebar Styling */
    .stSidebar {
        background: rgba(12, 10, 9, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    .stSidebar [data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }

    .sidebar-header {
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        color: #eab308; /* yellow-500 */
        margin-top: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(234, 179, 8, 0.2);
    }

    /* Memory Cards */
    .memory-card {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        padding: 10px;
        border-left: 3px solid #eab308;
        margin-bottom: 8px;
        font-size: 0.9rem;
        color: #d1d5db;
        transition: all 0.2s ease;
    }
    .memory-card:hover {
        background: rgba(255, 255, 255, 0.05);
        transform: translateX(4px);
    }

    /* Buttons & Inputs */
    .stButton > button {
        border-radius: 10px !important;
        background: linear-gradient(135deg, #eab308 0%, #ca8a04 100%) !important;
        color: #000 !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(234, 179, 8, 0.4);
    }

    .stChatInputContainer {
        border-top: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Hide Streamlit components for a cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Status indicator styling */
    .stStatusWidget {
        background: transparent !important;
        border: none !important;
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
        st.markdown("<h1 style='text-align: center; color: #fff;'>🧠 MEM0</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 0.8rem;'>High-Fidelity Memory Lab</p>", unsafe_allow_html=True)
        
        # Identity Section
        st.markdown('<div class="sidebar-header">Identity</div>', unsafe_allow_html=True)
        if st.session_state.user_id:
            st.markdown(f"""
                <div style="background: rgba(234, 179, 8, 0.1); padding: 10px; border-radius: 10px; border: 1px solid rgba(234, 179, 8, 0.2); margin-top: 10px;">
                    <span style="color: #eab308; font-size: 0.8rem; font-weight: 600;">ACTIVE AGENT:</span><br>
                    <span style="color: #fff; font-size: 1.1rem; font-weight: 700;">{st.session_state.user_id}</span>
                </div>
            """, unsafe_allow_html=True)
            if st.button("DISCONNECT", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.messages = []
                st.rerun()
        else:
            user_input_name = st.text_input("NAME", placeholder="Enter codename...", key="id_input")
            if st.button("INITIALIZE SESSION", use_container_width=True):
                if user_input_name:
                    st.session_state.user_id = user_input_name.strip()
                    st.rerun()
        
        # Memory Section
        if st.session_state.user_id:
            st.markdown('<div class="sidebar-header">Cognitive Archive</div>', unsafe_allow_html=True)
            memories = retrieve_relevant_memory("general knowledge about user", st.session_state.user_id)
            if memories and memories != "None.":
                for memory in memories.split("\n"):
                    if memory.startswith("-"):
                        st.markdown(f'<div class="memory-card">{memory[2:]}</div>', unsafe_allow_html=True)
            else:
                st.caption("Archive empty. Patterns pending...")

    # --- Main Chat Interface ---
    if not st.session_state.user_id:
        st.markdown("""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh;">
                <h1 style="font-size: 3rem; margin-bottom: 1rem; background: linear-gradient(135deg, #fff 0%, #666 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Connect to Begin</h1>
                <p style="color: #888; text-align: center; max-width: 500px;">Please authenticate via the terminal panel on the left to initialize the neural connection.</p>
            </div>
        """, unsafe_allow_html=True)
        st.stop()

    st.markdown("<h2 style='font-weight: 700; margin-bottom: 0;'>Neural Interface</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666; margin-bottom: 2rem;'>Synchronized with Long-term Cognitive Archive</p>", unsafe_allow_html=True)

    # Display chat messages with custom avatars
    for msg in st.session_state.messages:
        avatar = "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=user&backgroundColor=b6e3f4" if msg["role"] == "user" else "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=bot&backgroundColor=ffd5dc"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Chat Input
    if user_input := st.chat_input("Inject message..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="https://api.dicebear.com/7.x/bottts-neutral/svg?seed=user&backgroundColor=b6e3f4"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="https://api.dicebear.com/7.x/bottts-neutral/svg?seed=bot&backgroundColor=ffd5dc"):
            with st.status("🔍 Accessing Cognitive Archive...", expanded=False) as status:
                known_facts = retrieve_relevant_memory(user_input, st.session_state.user_id)
                status.update(label="🧬 Processing neural pathways...", state="running")
                
                system_prompt = f"""
You are an advanced AI assistant with persistent user memory.
Current user identity: {st.session_state.user_id}
Retrieved cognitive facts:
{known_facts if known_facts else "None."}

Instructions:
1. Synthesize responses based on known cognitive facts to ensure continuity.
2. Maintain a professional, cutting-edge, yet helpful tone.
"""
                api_messages = [{"role": "system", "content": system_prompt}]
                for m in st.session_state.messages:
                    api_messages.append({"role": m["role"], "content": m["content"]})

                client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                response = client.chat.completions.create(
                    model="moonshotai/kimi-k2-instruct",
                    messages=api_messages,
                    temperature=0.3
                )
                
                reply = response.choices[0].message.content
                status.update(label="⚡ Response synthesized.", state="complete", expanded=False)

            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
            store_user_fact(user_input, st.session_state.user_id)
            st.rerun()

if __name__ == "__main__":
    start_chat_app()

