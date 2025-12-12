import google.generativeai as genai
import webbrowser
import pyttsx3
import playlist
import requests
import os
from dotenv import load_dotenv
import datetime

# Load .env file
load_dotenv()

# function to make jarvis speak.
def say(text):
    engine = pyttsx3.init()
    engine.say(text)
    print(f'jarvis: {text}')
    engine.runAndWait()
    
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

# function to make jarvis process the command
def AIprocess(command):
    # Replace with your Gemini API key
    API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=API_KEY)

    # Create a Gemini model instance
    model = genai.GenerativeModel("gemini-2.5-pro")  # free, fast version
    prompt = f"You are Jarvis, a kind-hearted virtual assistant like Alexa or ChatGPT. Your owner is Rajesh aka Raj. User says: {command}"
       
    response = model.generate_content(prompt)
    return response.text

# function to process tasks
def processCommand(c):
    if "open google" in c.lower():
        webbrowser.open('https://www.google.com/')
        say("opening google")
    
    elif "open youtube" in c.lower():
        webbrowser.open('https://www.youtube.com/')
        say("opening youtube")
        
    elif "open facebook" in c.lower():
        webbrowser.open('https://www.facebook.com/')
        say("opening facebook")
        
    elif "open instagram" in c.lower():
        webbrowser.open('https://www.instagram.com/')
        say("opening instagram")
        
    elif "open linkedin" in c.lower():
        webbrowser.open('https://www.linkedin.com/')
        say("opening linkedin")    
        
    elif "open chat gpt" in c.lower():
        webbrowser.open('https://chatgpt.com/')
        say("opening chat gpt")
    
    elif c.lower().startswith("play"):
        parts = c.lower().split(" ", 1)  # split only once at the first space
        if len(parts) > 1:  
            song = parts[1].strip()  # everything after "play"
            
            if song in playlist.musics:  
                link = playlist.musics[song]
                say("playing.")
                webbrowser.open(link)
            else:
                say(f"Song '{song}' not found in playlist.")
        else:
            say("Please tell me which song to play.")

        
    elif "say news" in c.lower():
        # Get News API key
        NEWS_API_KEY = os.getenv("NEWS_API_KEY")
        
        # Search for Indian news (English language)
        url = f"https://api.worldnewsapi.com/search-news?api-key={NEWS_API_KEY}&source-countries=in&language=en"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            say("In latest indian headlines:\n")
            for article in data.get("news", []):
                say(f"- {article.get('title')}")
                
        except requests.exceptions.RequestException as e:
            say("Error fetching news:", e)


    else:
        output = AIprocess(c)
        say(output)
                
if __name__ == '__main__':
    wishMe()
    while True:
        try:
            print("\nEnter your prompt here: ")
            command = input("you :")
            processCommand(command)
        except Exception as e:
            print("error: ", format(e))