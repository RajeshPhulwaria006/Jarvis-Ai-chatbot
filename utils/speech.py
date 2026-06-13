import pyttsx3

# function to make jarvis speak.
engine = pyttsx3.init()     # initialization
def say(text):
    engine.say(text)
    print(f'jarvis: {text}')
    engine.runAndWait()