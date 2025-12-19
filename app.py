import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


PERSONALITIES = {
    "Math Teacher": {
        "author": "Math Teacher",
        "system": (
            "You are a helpful, authoritative math teacher. Strictly answer only math-related questions. "
            "If the user's question is outside mathematics, politely respond: 'I can only answer math-related questions.'"
        ),
        "welcome": "Hello — I'm a math teacher. Ask me math questions (I only answer math).",
    },
    "Doctor": {
        "author": "Doctor",
        "system": (
            "You are a qualified medical doctor. Strictly answer only health and medical questions. "
            "Do not answer math questions — if the user's question is outside health/medicine (including math), "
            "respond: 'I can only answer health and medical questions.'"
        ),
        "welcome": "Hello — I'm a doctor. Ask about health or medical topics (I only answer medical queries).",
    },
    "Travel Guide": {
        "author": "Travel Guide",
        "system": (
            "You are an expert travel guide. Strictly provide travel advice, tips, and recommendations. "
            "Do not answer math questions — if the user's question is outside travel (including math), "
            "respond: 'I can only provide travel advice and tips.'"
        ),
        "welcome": "Hello — I'm a travel guide. Ask for travel tips, destinations, and itineraries (travel only).",
    },
    "Chef": {
        "author": "Chef",
        "system": (
            "You are a professional chef. Strictly answer only cooking and recipe questions. "
            "Do not answer math questions — if the user's question is outside cooking (including math), "
            "respond: 'I can only answer cooking and recipe questions.'"
        ),
        "welcome": "Hello — I'm a chef. Ask about recipes, techniques, and cooking tips (cooking only).",
    },
    "Tech Support": {
        "author": "Tech Support",
        "system": (
            "You are a knowledgeable technical support agent. Strictly answer only technical troubleshooting queries. "
            "Do not answer math questions — if the user's question is outside technical support (including math), "
            "respond: 'I can only answer technical troubleshooting questions.'"
        ),
        "welcome": "Hello — I'm tech support. Ask about troubleshooting and technical issues (tech support only).",
    },
}


def init_state():
    if "conversation_history" not in st.session_state:
        # default personality system message
        default_system = PERSONALITIES["Math Teacher"]["system"]
        st.session_state.conversation_history = [
            {"role": "system", "content": default_system}
        ]
    if "messages" not in st.session_state:
        # list of tuples: (role, author, content)
        st.session_state.messages = []
    if "welcome_shown" not in st.session_state:
        st.session_state.welcome_shown = False
    if "personality" not in st.session_state:
        st.session_state.personality = "Math Teacher"


def set_personality(personality_key: str):
    # update the system prompt to enforce personality scope
    persona = PERSONALITIES.get(personality_key)
    if not persona:
        return
    st.session_state.personality = personality_key
    # replace the first system message
    if (
        "conversation_history" in st.session_state
        and st.session_state.conversation_history
    ):
        st.session_state.conversation_history[0] = {
            "role": "system",
            "content": persona["system"],
        }
    else:
        st.session_state.conversation_history = [
            {"role": "system", "content": persona["system"]}
        ]
    # force re-show welcome for new personality
    st.session_state.welcome_shown = False


def render_messages():
    for role, author, content in st.session_state.messages:
        label = "You" if role == "user" else author
        with st.chat_message(role):
            st.markdown(f"**{label}**: {content}")


def stream_response():
    try:
        stream = client.chat.completions.create(
            messages=st.session_state.conversation_history,
            model="llama-3.3-70b-versatile",
            stream=True,
        )

        full_response = ""
        author = PERSONALITIES.get(st.session_state.personality, {}).get(
            "author", "Assistant"
        )
        with st.chat_message("assistant"):
            placeholder = st.empty()
            for chunk in stream:
                # Log the raw chunk so we can inspect its structure when debugging
                try:
                    print("STREAM CHUNK:", chunk)
                except Exception:
                    pass
                # Mirror the original chunk handling (try to read `content`)
                content = None
                try:
                    content = chunk.choices[0].delta.content
                except Exception:
                    pass

                if content is not None:
                    full_response += content
                    placeholder.markdown(f"**{author}**: {full_response}")

        st.session_state.conversation_history.append(
            {"role": "assistant", "content": full_response}
        )
        st.session_state.messages.append(("assistant", author, full_response))

    except Exception as e:
        st.error(f"An error occurred: {e}")


def main():
    st.set_page_config(page_title="Chatbot (Streamlit)", page_icon=":speech_balloon:")
    st.title("Chatbot (Streamlit)")

    init_state()

    # Personality selector in the sidebar
    with st.sidebar:
        st.header("Personality")
        options = list(PERSONALITIES.keys())
        # Use on_change to update system prompt when user switches personality
        selected = st.radio(
            "Choose personality:",
            options,
            index=options.index(st.session_state.personality),
            key="personality_radio",
        )
        if selected != st.session_state.personality:
            set_personality(selected)

    persona = PERSONALITIES.get(st.session_state.personality)
    # Page subtitle shows current persona
    st.subheader(f"Current personality: {st.session_state.personality}")

    # Show welcome message once (similar to Chainlit on_chat_start)
    if not st.session_state.welcome_shown:
        welcome = persona.get("welcome", "Hello — how can I help?")
        author = persona.get("author", "Assistant")
        st.session_state.messages.append(("assistant", author, welcome))
        st.session_state.welcome_shown = True

    render_messages()

    with st.form(key="input_form", clear_on_submit=True):
        user_input = st.text_input("Your question", key="user_input")
        submitted = st.form_submit_button("Send")

    if submitted and user_input:
        # preserve same conversation logic
        st.session_state.conversation_history.append(
            {"role": "user", "content": user_input}
        )
        st.session_state.messages.append(("user", "You", user_input))

        # Streaming and display
        stream_response()


if __name__ == "__main__":
    main()
