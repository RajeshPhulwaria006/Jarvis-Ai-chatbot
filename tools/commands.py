from utils.speech import say
from assets import musics, WEBSITES

from langchain.agents import create_agent
from langchain.tools import tool
import webbrowser


@tool
def play_music(songName: str):
    """tool that take song name as parameter and execute the command if user want to play that song.
    constraints: give song name as parameter only, not any other such as 'play', 'jarvis' etc."""

    matched_song = next(
        (
            (name, url)
            for name, url in musics.items()
            if name.lower() == songName.lower().strip()
        ),
        None,
    )
    
    if matched_song:
        name, url = matched_song
        webbrowser.open(url)
        reply = f"Playing {name}."
    else:
        reply = (
            f"Sorry, I couldn't find {songName} in your playlist."
        )
        
    say(reply)
    return
    
@tool
def open_sites(siteName: str):
    """tool that take website name as parameter and execute the command if user want to open that website."""
    # Match website names case-insensitively.
    matched_site = next(
        (
            (name, url)
            for name, url in WEBSITES.items()
            if name.lower() == siteName.lower().strip()
        ),
        None,
    )

    if matched_site:
        name, url = matched_site
        webbrowser.open(url)
        reply = f"Opening {name}."
    else:
        reply = f"Sorry, {siteName} is not in your website list."

    say(reply)
    return
