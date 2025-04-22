import json

def load_data(filepath="company_data.json"):
    with open(filepath) as f:
        return json.load(f)
