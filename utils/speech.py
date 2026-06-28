import pyttsx3

# function to make jarvis speak.
def say(text):
    engine = pyttsx3.init()     # initialization
    engine.say(text)
    print(f'jarvis: {text}')
    engine.runAndWait()