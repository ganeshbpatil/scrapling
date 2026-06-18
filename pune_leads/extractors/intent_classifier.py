from pune_leads.config import INTENT_KEYWORDS, CONFIDENCE_SCORES

def classify_intent(text: str) -> str:
    text_lower = text.lower()
    scores = {
        intent: sum(1 for kw in keywords if kw in text_lower)
        for intent, keywords in INTENT_KEYWORDS.items()
    }
    scores = {k: v for k, v in scores.items() if v > 0}
    return max(scores, key=scores.get) if scores else "Researching"

def confidence_score(page_context: str) -> float:
    ctx = page_context.lower()
    if any(k in ctx for k in ["i want to buy", "interested in buying", "please call me", "call me back"]):
        return CONFIDENCE_SCORES["direct_inquiry"]
    if any(k in ctx for k in ["contact us", "send inquiry", "submit inquiry", "enquiry form"]):
        return CONFIDENCE_SCORES["contact_form"]
    if any(k in ctx for k in ["comment", "reply", "posted a comment"]):
        return CONFIDENCE_SCORES["property_comment"]
    if any(k in ctx for k in ["discussion", "thread", "topic"]):
        return CONFIDENCE_SCORES["property_discussion"]
    if any(k in ctx for k in ["forum", "community", "quora", "reddit"]):
        return CONFIDENCE_SCORES["forum_mention"]
    return CONFIDENCE_SCORES["general_interest"]

def enrich_lead(lead: dict, page_text: str) -> dict:
    lead["confidence_score"] = confidence_score(page_text)
    lead["intent"] = classify_intent(page_text)
    return lead
