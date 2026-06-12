from commands.assistant import AIprocess
from utils.speech import say
from commands.news import get_news
from assets.websites import WEBSITES

import assets.playlist as playlist
import webbrowser
import datetime

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

# function to process tasks
def processCommand(c):
    for name, url in WEBSITES.items():
        if f"open {name}" in c.lower():
            webbrowser.open(url)
            say(f"opening {name}")
            break
    
    if c.lower().startswith("play"):
        parts = c.lower().split(" ", 1)  # split only once at the first space
        if len(parts) > 1:  
            song = " ".join(parts[1].split())  # clear unwanted spaces
            
            if song in playlist.musics:  
                link = playlist.musics[song]
                say("playing.")
                webbrowser.open(link)
            else:
                say(f"Song '{song}' not found in playlist.")
        else:
            say("Please tell me which song to play.")

    elif "news" in c.lower():
        say("Here are today's top headlines.")

        for headline in get_news():
            say(headline)
        else:
            output = AIprocess(c)
            say(output)
                
if __name__ == '__main__':
    wishMe()
    print("Start you conversation: ")
    while True:
        try:
            command = input("you :")
            processCommand(command)
        except Exception as e:
            print("error: ", format(e))