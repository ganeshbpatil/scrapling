from scrapling.spiders import Response
from pune_leads.spiders.base_spider import BaseLeadSpider
from pune_leads.extractors.contact_extractor import extract_phones, extract_emails, extract_names
from pune_leads.extractors.property_extractor import extract_configuration, extract_locations, extract_budget
from pune_leads.extractors.intent_classifier import enrich_lead
from pune_leads.validators.lead_validator import validate_lead
from pune_leads.config import PORTAL_URLS

class PortalLeadSpider(BaseLeadSpider):
    name = "portal_pune_leads"
    concurrent_requests = 3
    start_urls = PORTAL_URLS

    async def parse(self, response: Response):
        for link in response.css("a[href]::attr(href)").getall():
            if self.is_relevant(link):
                yield response.follow(link, callback=self.parse_listing)

    async def parse_listing(self, response: Response):
        text = response.text
        config = extract_configuration(text)
        locations = extract_locations(text)
        budget = extract_budget(text)

        for comment in response.css(".comment, .review, .inquiry, .user-query, .discussion-post"):
            ct = " ".join(comment.css("::text").getall())
            c_phones, c_emails = extract_phones(ct), extract_emails(ct)
            if c_phones or c_emails:
                lead = self.build_lead(
                    response,
                    name=(extract_names(ct) or [""])[0],
                    email=c_emails[0] if c_emails else "",
                    phone=c_phones[0] if c_phones else "",
                    configuration=config,
                    location_interest=(locations or [""])[0],
                    budget=budget,
                    inquiry_text=ct[:500],
                )
                yield validate_lead(enrich_lead(lead, ct))

        phones, emails = extract_phones(text), extract_emails(text)
        if phones or emails:
            lead = self.build_lead(
                response,
                name=(extract_names(text) or [""])[0],
                email=emails[0] if emails else "",
                phone=phones[0] if phones else "",
                configuration=config,
                location_interest=(locations or [""])[0],
                budget=budget,
                inquiry_text=text[:500].strip(),
            )
            yield validate_lead(enrich_lead(lead, text))
