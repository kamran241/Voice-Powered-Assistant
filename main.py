from speech_engine import speak, listen
from data_loader import load_data
from query_handler import match_query

# Load data once
data = load_data()

# Greet the user
speak("Hi! I'm Bito, your assistant. Ask me anything about our website.")

# Keep the assistant running
while True:
    query = listen()

    if "quit" in query or "exit" in query:
        speak("Goodbye mate!")
        break

    if query:
        if 'thank' in query or "thank you" in query:
            speak("You're welcome mate! Anything else you want to know about Our Company")
            continue

        response = match_query(query, data)
        speak(response)
