# Memory Chatbot - Project Context

## Project Overview

This is a Streamlit-based chatbot that uses Groq's MoonshotAI Kimi-K2-Instruct model and Mem0 for long-term memory. The bot remembers key facts about the user across conversations, providing contextual and personalized responses.

### Key Features
- **Long-term Memory**: Remembers user details like name, preferences, work, and personal facts across sessions using Mem0
- **AI-Powered Memory Classification**: Uses Groq's MoonshotAI Kimi-K2-Instruct to intelligently decide which user messages contain save-worthy facts
- **Rule-Based Memory Fallback**: Simple keyword-based memory classification as an alternative
- **MoonshotAI Kimi-K2-Instruct**: Powered by Groq's fast and efficient model for responses
- **Contextual Conversations**: Retrieves relevant past memories to personalize responses

### Architecture
The project consists of three main Python modules:

1. **app.py**: Main Streamlit application that handles the chat interface and orchestrates the conversation flow
2. **agentic_memory.py**: AI-powered memory classification using Groq's API for intelligent fact detection and storage
3. **memory.py**: Rule-based memory classification using keyword matching (legacy approach)

### Dependencies
The project relies on the following Python packages:
- python-dotenv: For environment variable management
- groq: For accessing Groq's AI models
- mem0ai: For memory storage and retrieval
- streamlit: For the web interface
- pydantic: For data validation

## Building and Running

### Prerequisites
- Python 3.7+
- API keys for Groq and Mem0

### Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your API keys:
   ```bash
   cp .env.example .env
   ```
   
   Required environment variables:
   - `GROQ_API_KEY`: Get from [Groq Cloud](https://console.groq.com/)
   - `MEM0_API_KEY`: Get from [Mem0](https://app.mem0.ai/)

### Running the Application
Run the app with:
```bash
streamlit run app.py
```

For development with auto-reload:
```bash
streamlit run app.py --server.runOnSave true
```

## Development Conventions

### Memory Classification Approaches
The bot uses one of two approaches to decide what to remember:

1. **AI-Powered** (`agentic_memory.py`): Uses Groq's MoonshotAI Kimi-K2-Instruct model to classify whether a message contains a stable, user-specific fact worth remembering. This handles complex cases and avoids storing sensitive information.

2. **Rule-Based** (`memory.py`): Uses keyword matching to identify important facts. Simpler and faster but less nuanced.

The main app (`app.py`) currently uses the AI-powered approach for better accuracy.

### How It Works
1. **User Input**: The user sends a message through the Streamlit chat interface
2. **Memory Retrieval**: Relevant past memories are retrieved from Mem0 based on the current message
3. **Contextual Response**: The MoonshotAI Kimi-K2-Instruct model generates a response using the retrieved memories as context
4. **Memory Storage**: After responding, the message is analyzed to determine if it contains a fact worth storing for future conversations

### Memory Decision Logic
The AI-powered memory classifier follows these rules:
- Save stable, user-specific facts that will be useful in future conversations:
  - Identity details (name, job, location, education)
  - Preferences (likes, dislikes, favorites)
  - Long-term projects or goals
  - Personal traits or recurring constraints
- Do not save:
  - Questions or requests
  - Temporary updates or one-off plans
  - Generic conversation without user-specific facts
  - Sensitive data (passwords, secrets, medical, financial, legal)

## Key Components

### agentic_memory.py
Contains the core memory functionality with:
- `MemoryDecision` Pydantic model for validating memory classification decisions
- `is_fact_important()` function that uses AI to determine if text contains important facts
- `store_user_fact()` function to store important facts in Mem0
- `retrieve_relevant_memory()` function to fetch relevant memories

### app.py
The main Streamlit application that:
- Manages chat history in session state
- Retrieves relevant memories before generating responses
- Formats system prompts with memory context
- Calls the Groq API for responses
- Stores user facts after each interaction

### memory.py
Legacy rule-based memory implementation that:
- Uses keyword triggers to identify important facts
- Provides fallback memory functionality
- Follows similar interface to agentic_memory.py for consistency