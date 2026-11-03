# Jarvis AI Assistant 🤖

A personal AI assistant built with Python, LangChain, and Groq. Jarvis can answer questions, use tools, retrieve information, and interact through voice or text.

## Features

- AI conversations powered by Groq and LangChain.
- Tool calling for math, weather, news, and web search.
- Website opening and music playback.
- SQLite-based conversation history.
- Optional voice input with Whisper speech recognition.
- Natural text-to-speech using Edge TTS.
- Wake and sleep commands for voice interaction.

## Tech Stack

Python · LangChain · Groq · SQLite · Whisper · Edge TTS

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/RajeshPhulwaria006/Jarvis-Ai-chatbot.git
cd Jarvis-Ai-chatbot
```

### 2. Set up Python

```bash
python -m venv .venv
```

Activate the environment:

**Linux / macOS / WSL**
```bash
source .venv/bin/activate
```

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Create your `.env` file:

```bash
cp .env.example .env
```

On Windows PowerShell, use `Copy-Item .env.example .env`.

Add your API keys to `.env`:

```dotenv
GROQ_API_KEY=your_groq_api_key
NEWS_API_KEY=your_worldnewsapi_key
JARVIS_VOICE_MODE=false
```

Get your keys from [Groq Console](https://console.groq.com/) and [WorldNewsAPI](https://worldnewsapi.com/).

Never commit real API keys to GitHub.

### 4. Run Jarvis

```bash
python main.py
```

## How to Use

**Text mode:** Set `JARVIS_VOICE_MODE=false` in `.env` and type your commands in the terminal.

**Voice mode:** Set `JARVIS_VOICE_MODE=true` and speak when prompted. A working microphone and audio setup are required.

In voice mode, say “Wake up Jarvis” to activate the assistant. After handling a command, Jarvis returns to sleep until you wake it again.

Try asking Jarvis to:

- Explain a programming concept.
- Calculate a mathematical expression.
- Find recent news or search the web.
- Check the weather.
- Open a website or play a configured song.

## Project Structure

```text
├── assets/      # Website and music mappings
├── database/    # SQLite conversation history
├── tools/       # Math, news, weather, search, and commands
├── utils/       # Speech processing and system prompt
├── config.py    # Configuration
├── main.py      # Main application
└── requirements.txt
```

## Troubleshooting

- **Microphone errors:** Install PortAudio and verify that your audio device is available. Microphone access can require additional setup in WSL.
- **API errors:** Check your API keys, internet connection, and usage limits.
- **Speech errors:** Verify audio input/output and the required speech packages.

If voice mode is unavailable, use text mode instead.

## Future Improvements

Jarvis is an evolving personal project. Future improvements may include more reliable wake-word detection, better memory management, and additional tools.

## License
Copyright @ all rights reserved - Jarvis AI chatbot.

## Author

**Rajesh Phulwaria**

- GitHub: [@RajeshPhulwaria006](https://github.com/RajeshPhulwaria006)
- Project repository: [Jarvis-Ai-chatbot](https://github.com/RajeshPhulwaria006/Jarvis-Ai-chatbot)

---

*Built as a hands-on project to learn Python automation, LLM integration, agent tool calling, and persistent conversation history.*
