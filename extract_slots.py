import spacy
from dateparser.search import search_dates
from datetime import datetime
import re



nlp = spacy.load("en_core_web_sm")

def extract_slots(text):
    doc = nlp(text)
    slots = {"name": None, "date": None, "time": None}

    # Extract name using spaCy
    for ent in doc.ents:
        if ent.label_ == "PERSON" and not slots["name"]:
            slots["name"] = ent.text

    # Set dateparser settings
    settings = {
        'PREFER_DATES_FROM': 'future',
        'RETURN_AS_TIMEZONE_AWARE': False
    }

    # Normalize periods in time expressions for consistency
    normalized_text = text.lower()
    normalized_text = normalized_text.replace("a.m.", "am").replace("p.m.", "pm")
    normalized_text = normalized_text.replace("a.m", "am").replace("p.m", "pm")

    # Try date parsing
    date_matches = search_dates(normalized_text, settings=settings)

    if date_matches:
        for original_text, parsed_dt in date_matches:
            cleaned = original_text.lower().strip()
            if cleaned in {"on", "at", "in", "by"} or len(cleaned) < 3:
                continue
            if cleaned.isalpha() and cleaned not in {"today", "tomorrow", "tonight"}:
                continue
            # Accept date only if clearly not today
            if not slots["date"] and parsed_dt.date() != datetime.today().date():
                slots["date"] = parsed_dt.strftime("%Y-%m-%d")
            # Accept time only if not midnight
            if not slots["time"] and parsed_dt.time() != datetime.min.time():
                slots["time"] = parsed_dt.strftime("%I:%M %p")

    # Fallback: custom regex if time is still not found
    if not slots["time"]:
        time_pattern = r"\b(1[0-2]|0?[1-9])(:[0-5][0-9])?\s?(am|pm)\b"
        match = re.search(time_pattern, normalized_text, re.IGNORECASE)
        if match:
            raw = match.group(0).replace(" ", "")
            try:
                parsed_time = datetime.strptime(raw, "%I%p")
            except ValueError:
                parsed_time = datetime.strptime(raw, "%I:%M%p")
            slots["time"] = parsed_time.strftime("%I:%M %p")

    return slots
