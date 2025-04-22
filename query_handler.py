from fuzzywuzzy import fuzz   
    # Predefined keyword categories for matching
def fuzzy_match(query, keywords):
    return any(fuzz.partial_ratio(query, keyword) >= 80 for keyword in keywords)
    

def match_query(query, data):
  
    
    keywords_map = {
        "greeting": ["hello", "hi", "hey", "salam"],
        "company": ["who are you", "about", "what is bitlogicx", "name"],
        "location": ["location", "where", "address",'located'],
        "internship": ["internship", "job", "career", "opportunities", "jobs"],
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

    # Handle greeting
    if fuzzy_match(query, keywords_map["greeting"]):
        return data["response_templates"].get("greeting", "Hi there!")

    # Company introduction
    if fuzzy_match(query, keywords_map["company"]):
        return data["response_templates"].get("company_intro", "We are Bitlogicx.")

    # Location and contact info
    if fuzzy_match(query, keywords_map["location"]):
        return data["response_templates"]["contact"].format(
            contact_email=data["company"].get("contact_email", "info@example.com"),
            location=data["company"].get("location", "Location not found")
        )

    # Internships and job opportunities
    if fuzzy_match(query, keywords_map["internship"]):
        if data["company"]["offerings"].get("career_opportunities", False):
            return "Yes, Bitlogicx offers internships and career opportunities."
        return "Currently, there are no internship opportunities available."

    # Social media links
    if fuzzy_match(query, keywords_map["social_media"]):
        for platform in ["LinkedIn", "Twitter", "Facebook", "Instagram"]:
            if platform.lower() in query:
                link = data["company"]["social_media"].get(platform)
                if link:
                    return f"Here's our {platform}: {link}"
                return f"Sorry, we don't have a {platform} profile yet."
        return "We're on social media! You can ask about our LinkedIn, Twitter, Facebook, or Instagram profiles."

    # Email contact
    if fuzzy_match(query, keywords_map["email"]):
        email = data["company"].get("contact_email")
        if email:
            return f"You can reach us at: {email}"
        return "Sorry, our contact email is not available at the moment."

    # Services offered
    if fuzzy_match(query, keywords_map["service"]):
        services = data["services"].get("specific", [])
        return f"We offer services like: {', '.join(services)}."

    # Technologies used
    if fuzzy_match(query, keywords_map["tech"]):
        tech = data["custom_solutions"]["technologies"]
        return "We use the following technologies:\n" + "\n".join([
            f"{k.title()}: {', '.join(v)}" for k, v in tech.items()
        ])

    # Website info
    if fuzzy_match(query, keywords_map["website"]):
        return f"Our website is: {data['company'].get('website', 'https://bitlogicx.com')}"

    # Products
    if fuzzy_match(query, keywords_map["product"]):
        return "Our products include:\n" + "\n".join([
            f"{p['name']}: {p['description']}" for p in data["products"]
        ])

    # Specific product info
    for product in data["products"]:
        if fuzz.partial_ratio(query, product["name"].lower()) >= 85:
            return f"{product['name']}: {product['description']} (Use case: {product['use_case']})"

    # Industries served
    if fuzzy_match(query, keywords_map["industry"]):
        industries = data["custom_solutions"].get("industries_served", [])
        return f"We serve industries such as: {', '.join(industries)}."

    # Engagement models
    if fuzzy_match(query, keywords_map["engagement"]):
        models = data["custom_solutions"].get("engagement_models", [])
        return "We offer these engagement models:\n" + "\n".join([
            f"{m['name']}: {m['description']}" for m in models
        ])

    # Development process
    if fuzzy_match(query, keywords_map["development"]):
        steps = data["custom_solutions"].get("development_process", [])
        return "Our development process includes: " + " → ".join(steps)

    # Fallback if nothing matches
    return "I'm not sure how to answer that, mate. Try asking about our services, products, or technology stack."

# Start the assistant
# speak("Hi! I'm Bito, your assistant. Ask me anything about our website.")