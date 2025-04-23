import speech_recognition as sr
import json
import requests
from fuzzywuzzy import fuzz
import os
from playsound import playsound

# Load your data
with open('test_data.json') as f:
    data = json.load(f)

# ElevenLabs API Config
ELEVENLABS_API_KEY = "sk_2eda98b5841acd9138ad36c4fd3631713cabc7d020042a73"
VOICE_ID = "TX3LPaxmHKxFdv7VOQHJ"

def speak(text):
    print(f"Bito: {text}")
    url = "https://api.elevenlabs.io/v1/text-to-speech/TX3LPaxmHKxFdv7VOQHJ"
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
        if response.status_code == 200:
            with open("output.mp3", "wb") as f:
                f.write(response.content)
            playsound("output.mp3")
            os.remove("output.mp3")
        else:
            print(f"ElevenLabs API Error: {response.status_code}")
            print(f"Response: {response.text}")
            # Fallback to printing text if TTS fails
            print("(Text-to-speech service unavailable)")
    except requests.exceptions.RequestException as e:
        print(f"Network Error: {str(e)}")
        print("(Text-to-speech service unavailable)")
    except Exception as e:
        print(f"TTS Error: {str(e)}")
        print("(Text-to-speech service unavailable)")

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening... Speak your query.")
        r.pause_threshold = 1.0
        r.adjust_for_ambient_noise(source)  # Adjusting to ambient noise
        r.energy_threshold = 3000  # You can try tweaking this value (lower = more sensitive to voice)
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=15)
            query = r.recognize_google(audio)
            print(f"You: {query}")
            return query.lower()
        except sr.UnknownValueError:
            speak("Sorry mate, I didn't catch that.")
            return ""
        except sr.WaitTimeoutError:
            speak("I didn't hear anything mate.")
            return ""
        except Exception as e: 
            print("Listen error:", str(e))
            return ""

def fuzzy_match(query, keywords):
    for keyword in keywords:
        if fuzz.token_sort_ratio(query, keyword) > 80:
            return True
    return False


def match_query(query, data):
    keywords_map = {
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

    for intent, keywords in keywords_map.items():
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
                if data["company"]["offerings"].get("career_opportunities", False):
                    return "Yes, our company offers internships and job opportunities."
                return "Currently, there are no openings for internships or jobs."
            elif intent == "social_media":
                for platform in ["LinkedIn", "Twitter", "Facebook", "Instagram"]:
                    if platform.lower() in query:
                        link = data["company"]["social_media"].get(platform)
                        return f"Here's our {platform}: {link}" if link else f"No {platform} profile found."
                return "We're on LinkedIn, Twitter, Facebook, and Instagram."
            elif intent == "email":
                email = data["company"].get("contact_email")
                return f"You can reach us at: {email}" if email else "Email not available."
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

def query_llm_with_openrouter(prompt):
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }
    payload = {
    "model": "openai/gpt-3.5-turbo",
    "messages": [
 {"role": "system", "content": """
You are Bito, a virtual assistant for Bitlogicx, a software company based in Lahore, Pakistan. You must only answer questions related to Bitlogicx.

Here is the company information you should use when responding:

📍 **Location**: A5 Commercial Block A, Architects Engineers Housing Society, Lahore, Pakistan  
🌐 **Website**: https://bitlogicx.com/  
📧 **Email**: contact@bitlogicx.com  
🧑‍💻 **Career Opportunities**: Available  
🔗 **Social Media**:  
- LinkedIn: https://www.linkedin.com/company/bitlogicx/  
- Facebook: Not available  
- Twitter: Not available  
- Instagram: Not available

🧠 **About Bitlogicx**:  
Bitlogicx is a dedicated team of professionals delivering exceptional software services and innovative solutions to drive business success.

🛠 **Services Offered**:  
- Software development  
- System integration  
- Business process automation  
- Consultation services  

🛒 **Products**:  
- Bitlogicx ERP  
- College/School Management System  
- Learning Management System  
- Online Tourism Platform  
- Inventory Management System  
- Restaurant POS  
- Point of Sale System  
- eCommerce Marketplace  
- HR and Payroll Management  

📦 **Industries Served**:  
Healthcare, Education, E-commerce, Finance, Manufacturing, Logistics, Real Estate, Travel & Tourism

⚙️ **Tech Stack**:  
- Frontend: React, Angular, Vue.js, Next.js, React Native  
- Backend: Node.js, Python, Java, PHP, .NET  
- Database: MySQL, PostgreSQL, MongoDB, SQL Server, Oracle  
- Cloud: AWS, Azure, Google Cloud, Digital Ocean  

📋 **Engagement Models**:  
- Time and Material: For evolving requirements  
- Fixed Price: For well-defined scope  
- Dedicated Team: Full-time focused resources

🧩 **Development Process**:  
Requirements Analysis → Design → Development → Testing → Deployment → Maintenance

❗️Your rules:
- You are ONLY allowed to answer questions related to Bitlogicx.
- DO NOT generate code, poems, jokes, or provide unrelated help (e.g., "how to make a Python game").
- If someone asks about something off-topic, respond politely with:
"I'm here to help only with questions about Bitlogicx. Let me know if you'd like to know more about our services or company!"

Stay friendly, helpful, and always stick to what you know about Bitlogicx.
"""},

        {"role": "user", "content": prompt}
    ]
}

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"LLM error: {response.status_code}"
    except Exception as e:
        return f"Error contacting LLM: {str(e)}"

# Start the bot
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
        speak("okay mate, let me check that for you...")
        reply = query_llm_with_openrouter(query)
        speak(reply)
