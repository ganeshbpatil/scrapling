import re
from pune_leads.config import PUNE_MICRO_MARKETS, PROPERTY_CONFIGS

BHK_RE = re.compile(
    r'\b(\d)\s*[-]?\s*(?:bhk|bedroom|bed room|br)\b|'
    r'\b(one|two|three|four|five)\s*(?:bhk|bedroom|bed room)\b',
    re.IGNORECASE,
)
WORD_NUM = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5"}
BUDGET_RE = re.compile(
    r'(?:budget|price|cost|worth)[^\d]*?([\d.]+)\s*(?:cr(?:ore)?|lakh?|lac|l\b)',
    re.IGNORECASE,
)
BUDGET_PLAIN_RE = re.compile(r'\b([\d.]+)\s*(cr(?:ore)?|lakh?|lac)\b', re.IGNORECASE)

_MARKET_PATTERNS = {m: re.compile(r'\b' + re.escape(m) + r'\b', re.IGNORECASE) for m in PUNE_MICRO_MARKETS}
_CONFIG_PATTERNS = {c: re.compile(r'\b' + re.escape(c) + r'\b', re.IGNORECASE) for c in PROPERTY_CONFIGS}

def extract_configuration(text: str) -> str:
    for config, pat in _CONFIG_PATTERNS.items():
        if pat.search(text):
            return config
    m = BHK_RE.search(text)
    if m:
        digit = m.group(1) or WORD_NUM.get((m.group(2) or "").lower())
        if digit:
            return f"{digit} BHK"
    if re.search(r'\bvilla\b', text, re.IGNORECASE):
        return "Villa"
    if re.search(r'\bplot\b', text, re.IGNORECASE):
        return "Plot"
    if re.search(r'\bcommercial\b', text, re.IGNORECASE):
        return "Commercial"
    return ""

def extract_locations(text: str) -> list:
    return [market for market, pat in _MARKET_PATTERNS.items() if pat.search(text)]

def extract_budget(text: str) -> str:
    m = BUDGET_RE.search(text) or BUDGET_PLAIN_RE.search(text)
    if not m:
        return ""
    amount = float(m.group(1))
    unit = m.group(2).lower()
    return f"{amount} Cr" if unit.startswith("cr") else f"{amount} Lakh"
