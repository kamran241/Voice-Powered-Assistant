import speech_recognition as sr
import pyttsx3

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('volume', 1)

def speak(text):
    print(f"Bito: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, phrase_time_limit=10)
    try:
        query = r.recognize_google(audio)
        print(f"You: {query}")
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that. Can you repeat?")
        return ""
    except sr.RequestError:
        speak("There was a problem with the speech service.")
        return ""
# Start the assistant
speak("Hi! I'm Bito, your assistant. Ask me anything about our website.")