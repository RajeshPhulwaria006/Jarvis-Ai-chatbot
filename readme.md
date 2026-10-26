# Jarvis AI Assistant

A personal AI assistant built with **Python, LangChain, Groq, SQLite, and text-to-speech**. Jarvis combines an LLM-powered conversational interface with practical Python automation, including news retrieval, website opening, music playback, and persistent conversation history.

The project is evolving from a command-based assistant into a more capable tool-using AI agent.

## Features

- **LLM-powered conversations:** Uses Groq-hosted language models through LangChain.
- **Tool calling:** Allows the agent to retrieve news through a dedicated tool.
- **News retrieval:** Fetches recent news articles using the WorldNewsAPI.
- **Website automation:** Opens supported websites using predefined mappings.
- **Music playback:** Opens songs from a predefined playlist.
- **Conversation history:** Stores user messages and assistant responses in SQLite.
- **Text-to-speech:** Uses `pyttsx3` to speak Jarvis's responses.
- **Command handling:** Supports explicit commands for exiting, opening websites, and playing songs.

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python |
| LLM provider | Groq |
| Agent framework | LangChain |
| News source | WorldNewsAPI |
| Database | SQLite |
| Text-to-speech | pyttsx3 |
| HTTP requests | Requests |
| Configuration | Environment variables with python-dotenv |

## Architecture

Jarvis uses a hybrid architecture: deterministic Python commands handle predictable actions, while the LangChain agent handles general conversation and tool-assisted requests.

```text
User
 |
 v
CLI Input
 |
 v
Command Router (processCommand)
 |
 +-- Exit command -------> Stop application
 |
 +-- Open website -------> Website allowlist -> Browser
 |
 +-- Play song ----------> Playlist mapping -> Browser
 |
 +-- Other requests
         |
         v
    Load conversation history
         |
         v
    LangChain Agent
         |
         +-- Groq language model
         |
         +-- News tool
         |      |
         |      v
         |   WorldNewsAPI
         |
         v
    Assistant response
         |
         +-- Save conversation to SQLite
         |
         v
    Text-to-speech output
```

**Important distinction:** Website opening and music playback currently use Python command routing. News retrieval is exposed to the LangChain agent as a tool. These actions are not yet unified under a single agent-controlled tool interface.

## Project Structure

```text
├── assets
│   ├── __init__.py
│   ├── playlist.py         # Song name-to-URL mappings
│   └── websites.py         # Website name-to-URL mappings
├── database
│   ├── __init__.py
│   └── build.py            # SQLite conversation-history operations
├── tools
│   ├── __init__.py
│   └── news.py             # WorldNewsAPI integration as an agent tool
├── utils
│   ├── __init__.py
│   └── speech.py           # Text-to-speech utility
├── .gitignore
├── config.py               # Environment variable configuration
├── main.py                 # Command router, agent setup, and main loop
├── readme.md
└── requirements.txt        # Python dependencies
```

The database file is created locally when the database functionality initializes. Exact runtime files may vary with the working directory.

## Getting Started

### 1. Prerequisites

- Python 3.10 or newer
- A Groq API key
- A WorldNewsAPI key for news retrieval
- Internet access
- A working audio output device if you want spoken responses

### 2. Clone the repository

```bash
git clone https://github.com/RajeshPhulwaria006/Jarvis-Ai-chatbot.git
cd Jarvis-Ai-chatbot
```

### 3. Create a virtual environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If text-to-speech dependencies fail to install, check the `pyttsx3` installation instructions for your operating system.

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
NEWS_API_KEY=your_worldnewsapi_key
```

Replace the placeholder values with your actual API keys.

- Get a Groq API key from [Groq Console](https://console.groq.com/).
- Get a news API key from [WorldNewsAPI](https://worldnewsapi.com/).

**Security:** Never commit `.env` or expose API keys in source code, screenshots, logs, or public repositories. Keep `.env` excluded through `.gitignore`.

### 6. Run Jarvis

```bash
python main.py
```

The current interface accepts typed commands in the terminal and speaks responses through text-to-speech.

## Usage

### General conversation

Enter a question or a conversational request:

```text
you : Explain how a Python decorator works.
you : Give me an overview of neural networks.
```

Jarvis passes general requests to the LangChain agent and returns the assistant's response.

### Fetch news

```text
you : Fetch today's technology news.
```

The agent can use the `get_news` tool to request news articles from WorldNewsAPI. The tool currently configures its request to use English-language articles and an India source-country filter.

News availability depends on the API, network connectivity, API limits, and the returned data. The application should not be assumed to have access to every news source.

### Open a website

```text
you : open github
you : open youtube
you : open google
```

Website commands are handled using the predefined mappings in `assets/websites.py`.

Only websites present in the mapping are supported by this command handler. Unknown names are not automatically searched for or opened.

### Play a song

```text
you : play [song name]
```

The song must match an entry in `assets/playlist.py`. Jarvis opens the mapped URL in the browser; playback behavior depends on the destination website.

### Exit

```text
you : exit
```

Other supported exit commands include `quit`, `goodbye`, and `stop jarvis`.

## How It Works

### 1. Command routing

`processCommand()` checks the user's input for explicit commands before sending other requests to the agent.

This makes predictable actions such as opening a website or selecting a song simple and controlled, without requiring an LLM to decide every operation.

### 2. LangChain agent

The application configures a Groq-backed chat model and creates an agent with the news tool.

Conceptually:

```python
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7,
)

agent = create_agent(
    model=llm,
    tools=[get_news],
    system_prompt=SYSTEM_PROMPT,
)
```

The configured model must be available to the Groq account being used. Model availability, API limits, and provider behavior can change.

When handling an agent request, the application invokes the agent with a message history. The agent can decide whether to call its registered news tool, depending on the request.

### 3. News tool

The news integration lives in `tools/news.py`.

Its responsibilities include:

- Requesting articles from WorldNewsAPI.
- Passing the configured API key and search parameters.
- Limiting the requested number of articles.
- Applying a request timeout.
- Handling common HTTP and connection errors.

The current implementation constrains the requested article count to a maximum of ten. Review the tool's return type and error formatting when extending it so that successful and unsuccessful calls have a consistent output format.

### 4. Conversation history

The database implementation in `database/build.py` uses SQLite to store messages with fields for the message ID, role, content, and timestamp.

The current design:

- Saves user and assistant messages.
- Loads a limited number of recent messages for subsequent requests.
- Reconstructs messages as LangChain human and AI messages.
- Provides a method to delete stored conversation history.

This is **basic persistent conversation history**, not semantic memory. It does not currently provide vector search, long-term fact extraction, multiple user profiles, or session-isolated conversations.

### 5. Text-to-speech

`utils/speech.py` uses `pyttsx3` to speak responses and print them in the terminal.

The current interface uses typed input. Microphone-based speech recognition is not implemented as part of the documented workflow.

## Configuration

| Setting | Purpose |
|---|---|
| `GROQ_API_KEY` | Authenticates requests to Groq |
| `NEWS_API_KEY` | Authenticates requests to WorldNewsAPI |
| Model name | Selects the configured Groq model |
| Temperature | Controls the model's response variability |
| History limit | Controls how many recent messages are loaded |

The API keys are expected to be configured locally. Keep configuration separate from application logic and avoid hardcoding secrets.

## Current Limitations

Jarvis is a learning and portfolio project, not a production-ready autonomous assistant.

- **Limited agent tools:** News retrieval is available to the agent, while website and music actions use deterministic command branches.
- **Basic memory:** SQLite stores conversation messages, but there is no semantic retrieval or user/session isolation.
- **No formal evaluation suite:** Agent behavior, tool selection, and regression cases need systematic tests.
- **Dependency consistency:** All imported LangChain packages must be listed in `requirements.txt` for reproducible installation.
- **Documentation maintenance:** Setup instructions and features should be kept synchronized with the actual code and selected model.
- **API dependence:** News requests require valid credentials, internet access, and available API quota.
- **Limited observability:** Structured tool traces, execution metrics, and detailed debugging reports are not yet established.
- **Command matching:** Website and song commands depend on predefined names and straightforward matching.
- **Memory clearing:** The current `clear memory` branch clears the database but does not return immediately. It can continue into normal agent processing and save new messages. This behavior should be fixed before treating memory clearing as reliable.

## Roadmap

The next improvements are prioritized around reliability rather than adding complexity for its own sake.

### Phase 1 — Reliability

- [ ] Synchronize `requirements.txt` with all imports.
- [ ] Fix the memory-clearing command so it returns immediately.
- [ ] Make the news tool's successful and error return types consistent.
- [ ] Refresh the README and verify setup from a clean environment.
- [ ] Add tests for command routing, history persistence, and API failures.

### Phase 2 — Unified Tool Interface

- [ ] Implement an `open_website` tool with an explicit website allowlist.
- [ ] Implement a `play_song` tool with playlist validation.
- [ ] Register supported actions with the agent where appropriate.
- [ ] Keep exit and destructive operations under explicit control.
- [ ] Add tests for unknown names and invalid tool arguments.

### Phase 3 — Evaluation and Observability

- [ ] Test whether the agent selects the correct tool for different requests.
- [ ] Record structured tool inputs, outputs, failures, and execution duration.
- [ ] Add regression tests for known failure cases.
- [ ] Track success rates and incorrect tool selections across a small evaluation dataset.

### Phase 4 — More Capable Assistant

- [ ] Add session-aware conversation history.
- [ ] Improve exception handling and retry behavior.
- [ ] Add confirmation before potentially consequential actions.
- [ ] Consider a stateful workflow or LangGraph only when multi-step tasks require it.
- [ ] Explore a graphical interface after the core agent is reliable.

## Testing

Automated tests and a formal agent evaluation suite are not yet established as part of the current project.

Before contributing major features, manually verify:

1. The application starts with valid environment variables.
2. General questions receive a response.
3. News requests call the tool when appropriate.
4. News API failures are handled gracefully.
5. Known websites and songs are matched correctly.
6. Unknown website and song names are handled safely.
7. Conversation history persists between application runs.
8. Clearing history actually leaves the database empty after the command finishes.

These checks should be converted into automated tests as the project develops.

## Contributing

Contributions and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make a focused change.
4. Run the relevant tests or manual checks.
5. Open a pull request describing the change and its behavior.

Keep API keys and other secrets out of commits. Prefer small, testable changes that improve reliability and maintainability.

## Project Goals

The long-term goal is to build a more reliable personal AI assistant that combines language-model reasoning with controlled tools, useful memory, observable execution, and practical automation.

The priority is to make existing capabilities **reliable, testable, and understandable** before introducing more complicated agent architectures.

## Author

**Rajesh Phulwaria**

- GitHub: [@RajeshPhulwaria006](https://github.com/RajeshPhulwaria006)
- Project repository: [Jarvis-Ai-chatbot](https://github.com/RajeshPhulwaria006/Jarvis-Ai-chatbot)

---

*Built as a hands-on project to learn Python automation, LLM integration, agent tool calling, and persistent conversation history.*
