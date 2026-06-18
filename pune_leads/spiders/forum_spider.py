from scrapling.spiders import Response
from pune_leads.spiders.base_spider import BaseLeadSpider
from pune_leads.extractors.contact_extractor import extract_phones, extract_emails, extract_names
from pune_leads.extractors.property_extractor import extract_configuration, extract_locations, extract_budget
from pune_leads.extractors.intent_classifier import enrich_lead
from pune_leads.validators.lead_validator import validate_lead
from pune_leads.config import FORUM_URLS

_PROPERTY_KW = {"pune", "property", "bhk", "flat", "buy", "plot", "apartment"}

class ForumLeadSpider(BaseLeadSpider):
    name = "forum_pune_leads"
    concurrent_requests = 2
    start_urls = FORUM_URLS

    async def parse(self, response: Response):
        for link in response.css("a[href]::attr(href)").getall():
            if link.startswith("http") and self.is_relevant(link):
                yield response.follow(link, callback=self.parse_thread)

    async def parse_thread(self, response: Response):
        text = response.text
        config = extract_configuration(text)
        locations = extract_locations(text)
        budget = extract_budget(text)

        posts = response.css(".Comment, .answer, .post, [data-testid='comment'], .entry-content")
        targets = posts if posts else [None]

        for post in targets:
            post_text = " ".join(post.css("::text").getall()) if post else text
            if not any(kw in post_text.lower() for kw in _PROPERTY_KW):
                continue
            phones, emails = extract_phones(post_text), extract_emails(post_text)
            if not phones and not emails:
                continue
            lead = self.build_lead(
                response,
                name=(extract_names(post_text) or [""])[0],
                email=emails[0] if emails else "",
                phone=phones[0] if phones else "",
                configuration=config,
                location_interest=(locations or [""])[0],
                budget=budget,
                inquiry_text=post_text[:500],
            )
            yield validate_lead(enrich_lead(lead, post_text))
