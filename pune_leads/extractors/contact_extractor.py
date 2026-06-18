import re

PHONE_RE = re.compile(r'\b(?:\+91[\s\-]?)?[6-9]\d{9}\b')
EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b')
NAME_CONTEXT_RE = re.compile(
    r'(?:name|contact|posted by|author|by|submitted by)[:\s]+([A-Z][a-z]+(?: [A-Z][a-z]+){1,2})',
    re.IGNORECASE,
)

def extract_phones(text: str) -> list:
    raw = PHONE_RE.findall(text)
    cleaned, seen = [], set()
    for p in raw:
        digits = re.sub(r'\D', '', p)
        if len(digits) == 10:
            normalized = f"+91{digits}"
        elif len(digits) == 12 and digits.startswith('91'):
            normalized = f"+{digits}"
        else:
            continue
        if normalized not in seen:
            seen.add(normalized)
            cleaned.append(normalized)
    return cleaned

def extract_emails(text: str) -> list:
    found = EMAIL_RE.findall(text)
    seen, result = set(), []
    for e in found:
        lower = e.lower()
        if lower not in seen:
            seen.add(lower)
            result.append(lower)
    return result

def extract_names(text: str) -> list:
    matches = NAME_CONTEXT_RE.findall(text)
    return list(dict.fromkeys(matches))
