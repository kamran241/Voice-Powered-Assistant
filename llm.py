import os
import json
import requests
import speech_recognition as sr
from fuzzywuzzy import fuzz
from playsound import playsound
import logging

# === Configuration ===
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_2eda98b5841acd9138ad36c4fd3631713cabc7d020042a73")
VOICE_ID = "TX3LPaxmHKxFdv7VOQHJ"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")

# === Logging Setup ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# === Load Data ===
with open('test_data.json') as f:
    data = json.load(f)

# === Speak Function (TTS) ===
def speak(text):
    print(f"Bito: {text}")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.7, "similarity_boost": 0.75}
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        with open("output.mp3", "wb") as f:
            f.write(response.content)
        playsound("output.mp3")
        os.remove("output.mp3")
    except Exception as e:
        logging.error(f"TTS Error: {e}")

# === Listen Function (STT) ===
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = 1.2
        r.energy_threshold = 3000
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=15)
            query = r.recognize_google(audio)
            print(f"You: {query}")
            return query.lower()
        except sr.UnknownValueError:
            speak("Sorry mate, I didn't catch that.")
        except sr.WaitTimeoutError:
            speak("I didn't hear anything mate.")
        except Exception as e:
            logging.error(f"STT Error: {e}")
    return ""

# === Fuzzy Intent Match ===
def fuzzy_match(query, keywords):
    return any(fuzz.token_sort_ratio(query, kw) > 80 for kw in keywords)

# === Intent Matching ===
def match_query(query, data):
    intents = {
        "greeting": ["hello", "hi", "hey", "salam"],
        "company": ["who are you", "about", "what is bitlogicx", "your company", "name"],
        "location": ["location", "where", "address"],
        "internship": ["internship", "job", "career", "opportunities", "jobs", "vacancy"],
        "product": ["product", "products", "what do you offer", "software", "erp"],
        "service": ["services", "solutions", "what do you do"],
        "tech": ["tech", "technology", "tools", "stack", "frameworks"],
        "website": ["website", "web address", "site"],
        "industry": ["industries", "clients", "served", "domain"],
        "engagement": ["engagement model", "pricing model", "time and material", "fixed price", "team"],
        "development": ["development process", "how you develop", "phases", "steps", "workflow"],
        "social_media": ["social media", "social", "media", "platforms", "profiles"],
        "email": ["email", "contact", "reach out", "contact us", "email address"]
    }

    for intent, keywords in intents.items():
        if fuzzy_match(query, keywords):
            if intent == "greeting":
                return data["response_templates"].get("greeting", "Hi there!")
            elif intent == "company":
                return data["response_templates"].get("company_intro", "We are Bitlogicx.")
            elif intent == "location":
                return data["response_templates"]["contact"].format(
                    contact_email=data["company"].get("contact_email", "info@example.com"),
                    location=data["company"].get("location", "Location not found")
                )
            elif intent == "internship":
                return "Yes, our company offers internships and job opportunities." \
                    if data["company"]["offerings"].get("career_opportunities", False) \
                    else "Currently, there are no openings for internships or jobs."
            elif intent == "social_media":
                for platform in ["LinkedIn", "Twitter", "Facebook", "Instagram"]:
                    if platform.lower() in query:
                        link = data["company"]["social_media"].get(platform)
                        return f"Here's our {platform}: {link}" if link else f"No {platform} profile found."
                return "We're on LinkedIn, Twitter, Facebook, and Instagram."
            elif intent == "email":
                return f"You can reach us at: {data['company'].get('contact_email', 'N/A')}"
            elif intent == "service":
                services = data["services"].get("specific", [])
                return f"We offer services like: {', '.join(services)}."
            elif intent == "tech":
                tech = data["custom_solutions"]["technologies"]
                return "We use the following technologies:\n" + "\n".join([f"{k.title()}: {', '.join(v)}" for k, v in tech.items()])
            elif intent == "website":
                return f"Our website is: {data['company'].get('website', 'https://bitlogicx.com')}"
            elif intent == "product":
                return "Our products include:\n" + "\n".join([f"{p['name']}: {p['description']}" for p in data["products"]])
            elif intent == "industry":
                industries = data["custom_solutions"].get("industries_served", [])
                return f"We serve industries such as: {', '.join(industries)}."
            elif intent == "engagement":
                models = data["custom_solutions"].get("engagement_models", [])
                return "Our engagement models include:\n" + "\n".join([f"{m['name']}: {m['description']}" for m in models])
            elif intent == "development":
                steps = data["custom_solutions"].get("development_process", [])
                return "Our development process includes: " + " → ".join(steps)

    for product in data["products"]:
        if fuzz.partial_ratio(query, product["name"].lower()) >= 85:
            return f"{product['name']}: {product['description']} (Use case: {product['use_case']})"

    return None

# === LLM Fallback (OpenRouter) ===
def query_llm_with_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": """
You are Bito, a virtual assistant for Bitlogicx. Only answer questions related to Bitlogicx. 
Refer only to the company's official details. Politely decline unrelated topics.
"""}, 
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"LLM Error: {e}"

# === Start Bot ===
if __name__ == "__main__":
    speak("Hi mate! I'm Bito from Bitlogicx. Ask me anything.")
    while True:
        query = listen()
        if not query:
            continue
        if "exit" in query or "quit" in query:
            speak("Goodbye mate!")
            break
        if "thank" in query:
            speak("You're welcome mate!")
            continue

        local_response = match_query(query, data)
        if local_response:
            speak(local_response)
        else:
            speak("Let me get the info for you...")
            reply = query_llm_with_openrouter(query)
            speak(reply)
