from scrapling.spiders import Spider, Request, Response

class MyQuotesSpider(Spider):
    name = "quotes_scraper"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 5

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }
        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0].attrib['href'])

if __name__ == "__main__":
    result = MyQuotesSpider(crawldir="./my_crawl_data").start()
    print(f"Scraped {len(result.items)} quotes")
    result.items.to_json("quotes.json")
    print("Saved to quotes.json")
