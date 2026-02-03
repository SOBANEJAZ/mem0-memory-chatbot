# Memory Chatbot

A Streamlit-based chatbot that uses Google's Gemini Flash 2.5 model and Mem0 for long-term memory. The bot remembers key facts about the user across conversations.

## Features

- **Long-term Memory**: Remembers user details like name, preferences, and work.
- **Gemini Flash 2.5**: Powered by Google's latest fast and efficient model.
- **Streamlit UI**: Simple and clean conversational interface.

## Setup

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your API keys:
   ```bash
   cp .env.example .env
   ```
   - `GEMINI_API_KEY`: Get from Google AI Studio.
   - `MEM0_API_KEY`: Get from Mem0.

## Usage

Run the app:
```bash
streamlit run app.py
```