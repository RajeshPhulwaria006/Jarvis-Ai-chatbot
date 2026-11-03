from utils.speech import say, listen
from tools import (
    get_news,
    get_weather, 
    math_calculator, 
    web_search,
    play_music,
    open_sites
)
from database.build import Database
from config import GROQ_API_KEY
from utils import SYSTEM_PROMPT

from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

import os
import webbrowser
import datetime

VOICE_MODE = os.getenv("JARVIS_VOICE_MODE", "false").lower() in {"1", "true", "yes", "on"}

# function to make jarvis wish/gather/
def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=4 and hour<12:
        say('good morning sir!')
        
    elif hour>=12 and hour<16:
        say('good afternoon sir!')
        
    else:
        say('good evening sir!')
    say('iam jarvis, how can i help you?')


# function to load and utilize history
def build_messages(user_message: str, db) -> list:
    """Build LangChain messages from stored chat history and current input."""

    history = db.load_history()
    messages = []

    for role, text in history:
        if role == "user":
            messages.append(HumanMessage(content=text))
        elif role in ("assistant", "model"):
            messages.append(AIMessage(content=text))

    messages.append(HumanMessage(content=user_message))
    return messages

# function to process command
def AIprocess(command: str) -> str:
    """Process a command using the Jarvis agent and conversation history."""
    try:
        messages = build_messages(command, db)

        # The agent handles tool selection and execution automatically.
        result = agent.invoke({"messages": messages})

        # Get the final assistant response.
        reply = result["messages"][-1].content

        if not isinstance(reply, str):
            reply = str(reply)

        reply = reply.strip()

        # Save only the user input and final response.
        db.save_message("user", command)
        db.save_message("assistant", reply)

        return reply

    except Exception as e:
        print(f"AI processing error: {e}")
        return "Sorry, I couldn't process your request. Please try again."

# function to handle commands to play or open external links
def processCommand(command: str):
    """Handle direct actions first, then delegate to the AI agent."""
    text = command.strip().lower()

    if not text: return

    # Exit commands
    if text in ("exit", "quit", "goodbye", "stop jarvis"):
        say("Goodbye, sir!")
        return "exit"

    # Clear conversation memory
    if "clear memory" in text.lower():
            db.clear_history()
            say("Memory cleared successfully.")
            return

    # # Open a website
    # if text.startswith("open "):
    #     site_name = text[5:].strip()

    #     # Match website names case-insensitively.
    #     matched_site = next(
    #         (
    #             (name, url)
    #             for name, url in WEBSITES.items()
    #             if name.lower() == site_name
    #         ),
    #         None,
    #     )

    #     if matched_site:
    #         name, url = matched_site
    #         webbrowser.open(url)
    #         reply = f"Opening {name}."
    #     else:
    #         reply = f"Sorry, {site_name} is not in your website list."

    #     say(reply)
    #     return

    # # Play a song
    # if text.startswith("play "):
    #     song_name = " ".join(text[5:].split())

    #     matched_song = next(
    #         (
    #             (name, url)
    #             for name, url in musics.items()
    #             if name.lower() == song_name
    #         ),
    #         None,
    #     )

    #     if matched_song:
    #         name, url = matched_song
    #         webbrowser.open(url)
    #         reply = f"Playing {name}."
    #     else:
    #         reply = (
    #             f"Sorry, I couldn't find {song_name} "
    #             "in your playlist."
    #         )
            
    #     say(reply)
    #     return

    # All other requests go to LangChain.
    reply = AIprocess(command)
    say(reply)

                
if __name__ == '__main__':

    db = Database()
    WAKE_PHRASES = {
        "wake up jarvis",
        "hey jarvis",
        "wake up",
    }

    SLEEP_PHRASES = {
        "go to sleep",
        "sleep jarvis",
        "stop listening",
        "you may sleep now"
    }

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.7,
    )

    agent = create_agent(
        model=llm,
        tools=[get_news, get_weather, math_calculator, web_search, play_music, open_sites],
        system_prompt=SystemMessage(content=SYSTEM_PROMPT),
    )
    
    wishMe()
    # voice assisted commands
    awake = False
    if VOICE_MODE:
        print("Jarvis is sleeping. Say 'Wake up Jarvis' to activate.")
    else:
        print("Typed mode enabled. Set JARVIS_VOICE_MODE=true for microphone input.")

    while True:
        try:
            if VOICE_MODE:
                command = listen().strip().lower()
                if not command:
                    continue

                if not awake:
                    if any(phrase in command for phrase in WAKE_PHRASES):
                        awake = True
                        say("I'm awake. How can I help?")
                    continue

                if any(phrase in command for phrase in SLEEP_PHRASES):
                    say("Going to sleep. Say wake up Jarvis when you need me.")
                    awake = False
                    continue

            else:
                command = input("You: ").strip()

            is_exit = processCommand(command)

            if is_exit == "exit":
                break

            if awake and VOICE_MODE:
                awake = False
                
        except KeyboardInterrupt:
            print("\nJarvis stopped.")
            break
        except Exception as exc:
            print(f"Jarvis runtime error: {exc}")