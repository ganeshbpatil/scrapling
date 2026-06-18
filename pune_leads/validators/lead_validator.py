import re
from difflib import get_close_matches
from pune_leads.config import PUNE_MICRO_MARKETS, PROPERTY_CONFIGS

PHONE_CLEAN_RE = re.compile(r'\D')
EMAIL_RE = re.compile(r'^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$')

def validate_phone(phone: str) -> str:
    digits = PHONE_CLEAN_RE.sub('', phone)
    if digits.startswith('91') and len(digits) == 12:
        digits = digits[2:]
    if len(digits) == 10 and digits[0] in '6789':
        return f"+91{digits}"
    return ""

def validate_email(email: str) -> str:
    email = email.strip().lower()
    return email if EMAIL_RE.match(email) else ""

def validate_location(location: str) -> str:
    if not location:
        return ""
    if location in PUNE_MICRO_MARKETS:
        return location
    matches = get_close_matches(location, PUNE_MICRO_MARKETS, n=1, cutoff=0.7)
    return matches[0] if matches else location

def validate_config(config: str) -> str:
    if config in PROPERTY_CONFIGS:
        return config
    matches = get_close_matches(config, PROPERTY_CONFIGS, n=1, cutoff=0.8)
    return matches[0] if matches else config

def validate_lead(lead: dict) -> dict:
    errors = []
    phone = validate_phone(lead.get("phone", ""))
    if not phone and lead.get("phone"):
        errors.append("invalid_phone")
    lead["phone"] = phone

    email = validate_email(lead.get("email", ""))
    if not email and lead.get("email"):
        errors.append("invalid_email")
    lead["email"] = email

    lead["location_interest"] = validate_location(lead.get("location_interest", ""))
    lead["configuration"] = validate_config(lead.get("configuration", ""))
    lead["validation_errors"] = errors
    return lead
