from scrapling.spiders import Response
from pune_leads.spiders.base_spider import BaseLeadSpider
from pune_leads.extractors.contact_extractor import extract_phones, extract_emails, extract_names
from pune_leads.extractors.property_extractor import extract_configuration, extract_locations, extract_budget
from pune_leads.extractors.intent_classifier import enrich_lead
from pune_leads.validators.lead_validator import validate_lead
from pune_leads.config import START_URLS

class GoogleLeadSpider(BaseLeadSpider):
    name = "google_pune_leads"
    concurrent_requests = 5
    start_urls = START_URLS

    async def parse(self, response: Response):
        for link in response.css("a[href]::attr(href)").getall():
            if link.startswith("http") and "google.com" not in link and self.is_relevant(link):
                yield response.follow(link, callback=self.parse_result_page)
        next_page = response.css("a#pnnext::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    async def parse_result_page(self, response: Response):
        text = response.text
        phones = extract_phones(text)
        emails = extract_emails(text)
        if not phones and not emails:
            return
        names = extract_names(text)
        lead = self.build_lead(
            response,
            name=names[0] if names else "",
            email=emails[0] if emails else "",
            phone=phones[0] if phones else "",
            configuration=extract_configuration(text),
            location_interest=(extract_locations(text) or [""])[0],
            budget=extract_budget(text),
            inquiry_text=text[:500].strip(),
        )
        lead = enrich_lead(lead, text)
        lead = validate_lead(lead)
        yield lead
