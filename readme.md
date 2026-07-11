# 🤖 Jarvis AI Assistant

**A modular AI-powered virtual assistant built with Python, Google Gemini, and SQLite-powered persistent memory.**

Jarvis is an extensible desktop AI assistant capable of natural conversations, remembering previous conversations, web automation, media playback, and real-time news retrieval. The project is designed with scalability in mind, making it easy to integrate additional AI capabilities, APIs, desktop automation, and long-term AI memory.

---

## ✨ Features

### 🧠 AI Assistant

- Powered by **Google Gemini 3.5 Flash**
- Context-aware conversational responses
- Intelligent fallback when no predefined command matches
- Easily extensible for future AI tool/function calling

---

### 💾 Persistent Conversation Memory

Jarvis now remembers previous conversations using a **SQLite database**, enabling more natural and context-aware interactions across sessions.

Features:

- Stores every user and AI message locally
- Automatically loads recent conversation history
- Maintains conversational context between sessions
- Lightweight and offline-friendly using SQLite
- Easily extendable for long-term user preferences and semantic memory

Database location:

```text
database/memory.db
```

---

### 🌐 Website Launcher

Open your favorite websites with simple natural language commands.

Supported examples:

```text
open google
open youtube
open github
open linkedin
open instagram
open facebook
open chat gpt
```

New websites can be added by editing a single dictionary inside:

```text
assets/websites.py
```

---

### 🎵 Music Player

Play your favorite songs directly from your custom playlist.

Example:

```text
play skyfall
play afreen afreen
play chand sifarish
```

Adding a new song requires only a single entry inside:

```python
musics = {
    "song name": "youtube_link"
}
```

located in:

```text
assets/playlist.py
```

---

### 📰 Latest Indian News

Fetch the latest Indian headlines using a News API.

Example command:

```text
say news
```

Features:

- Latest Indian headlines
- Network error handling
- Configurable number of headlines

---

### 🔐 Secure API Management

Sensitive credentials are never stored in source code.

Environment variables are managed through:

```text
.env
```

Examples:

- Gemini API Key
- News API Key

---

## 📁 Project Structure

```text
Jarvis-AI/

├── assets/
│   ├── playlist.py
│   ├── websites.py
│   └── __init__.py
│
├── commands/
│   ├── assistant.py
│   ├── news.py
│   └── __init__.py
│
├── utils/
│   ├── speech.py
│   └── __init__.py
│
├── database/
│   ├── build.py
│   ├── memory.db
│   └── __init__.py
│
├── .env
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

---

## ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/RajeshPhulwaria006/Jarvis-AI-chatbot.git
```

Move into the project directory

```bash
cd Jarvis-AI-chatbot
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
GEMINI_API_KEY=your_api_key
NEWS_API_KEY=your_api_key
```

Run the assistant

```bash
python main.py
```

---

## 💻 Technologies Used

- Python
- Google Gemini API
- SQLite
- Requests
- pyttsx3
- python-dotenv
- Web Browser Automation

---

## 🧠 How Conversation Memory Works

1. Every user message is stored in a local SQLite database.
2. Every AI response is also saved.
3. Before generating a new response, Jarvis retrieves recent conversation history.
4. The previous messages are sent to Gemini along with the current prompt.
5. Gemini generates responses while maintaining conversational context.

This allows Jarvis to remember recent discussions even after restarting the application.

---

## 🤝 Contributing

Contributions, feature requests, and improvements are welcome.

Feel free to fork the repository and submit a pull request.

---

## 👨‍💻 Author

**Rajesh Phulwaria**

If you found this project useful, consider giving it a ⭐ on GitHub.