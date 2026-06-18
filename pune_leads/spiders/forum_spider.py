from scrapling.spiders import Response
from pune_leads.spiders.base_spider import BaseLeadSpider
from pune_leads.extractors.contact_extractor import extract_phones, extract_emails, extract_names
from pune_leads.extractors.property_extractor import extract_configuration, extract_locations, extract_budget
from pune_leads.extractors.intent_classifier import enrich_lead
from pune_leads.validators.lead_validator import validate_lead
from pune_leads.config import FORUM_URLS

_PROPERTY_KW = {"pune", "property", "bhk", "flat", "buy", "plot", "apartment", "real estate"}

# Reddit/Quora post selectors (rendered HTML)
_POST_SELECTORS = [
    "[data-testid='comment']",
    "shreddit-comment",
    ".Comment",
    ".answer",
    "div.entry p",
    ".node-body",
    "p.qtext_para",
]

class ForumLeadSpider(BaseLeadSpider):
    name = "forum_pune_leads"
    concurrent_requests = 2
    start_urls = FORUM_URLS

    async def parse(self, response: Response):
        # Follow thread/post links
        for link in response.css("a[href]::attr(href)").getall():
            if link.startswith("http") and self.is_relevant(link):
                yield response.follow(link, callback=self.parse_thread)
        # Also parse the search page itself for signal
        yield self.parse_page_as_lead(response)

    async def parse_thread(self, response: Response):
        text = response.text
        config = extract_configuration(text)
        locations = extract_locations(text)
        budget = extract_budget(text)

        # Try structured post selectors first
        posts = []
        for sel in _POST_SELECTORS:
            posts = response.css(sel)
            if posts:
                break

        targets = posts if posts else [None]  # fall back to full page

        for post in targets:
            post_text = " ".join(post.css("::text").getall()) if post else text
            if not any(kw in post_text.lower() for kw in _PROPERTY_KW):
                continue

            phones = extract_phones(post_text)
            emails = extract_emails(post_text)
            names = extract_names(post_text)
            c = extract_configuration(post_text) or config
            locs = extract_locations(post_text) or locations
            b = extract_budget(post_text) or budget

            # Yield even without contact info — forum discussions are intent signals
            lead = self.build_lead(
                response,
                name=names[0] if names else "",
                email=emails[0] if emails else "",
                phone=phones[0] if phones else "",
                configuration=c,
                location_interest=(locs or [""])[0],
                budget=b,
                inquiry_text=post_text[:500].strip(),
            )
            lead = enrich_lead(lead, post_text)
            lead = validate_lead(lead)

            # Only skip if no signal at all (no location, no config, no contact)
            has_signal = lead["email"] or lead["phone"] or lead["location_interest"] or lead["configuration"]
            if has_signal:
                yield lead

    def parse_page_as_lead(self, response: Response):
        """Extract page-level lead signal from search result pages."""
        text = response.text
        config = extract_configuration(text)
        locations = extract_locations(text)
        budget = extract_budget(text)
        phones = extract_phones(text)
        emails = extract_emails(text)

        if not (config or locations or phones or emails):
            return None

        lead = self.build_lead(
            response,
            email=emails[0] if emails else "",
            phone=phones[0] if phones else "",
            configuration=config,
            location_interest=(locations or [""])[0],
            budget=budget,
            inquiry_text=text[:300].strip(),
        )
        return validate_lead(enrich_lead(lead, text))
