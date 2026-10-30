# backend/scraper/spiders/verge.py
import scrapy
from datetime import datetime


class VergeSpider(scrapy.Spider):
    name = "verge"
    allowed_domains = ["theverge.com"]
    start_urls = ["https://www.theverge.com/"]

    def parse(self, response):
        # Grab links from homepage articles
        for article in response.css("a[data-analytics-link]"):
            url = article.attrib.get("href")
            if url and url.startswith("https://www.theverge.com/"):
                yield response.follow(url, callback=self.parse_article)

    def parse_article(self, response):
        title = response.css("h1::text").get() or ""
        summary = response.css("meta[name='description']::attr(content)").get() or ""
        author = response.css("a[data-analytics-link='byline']::text").get() or ""
        image = response.css("meta[property='og:image']::attr(content)").get() or ""

        # Verge articles usually have datetime in <time> tag
        published_str = response.css("time::attr(datetime)").get()
        try:
            published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
        except Exception:
            published_at = datetime.utcnow()

        # Categories/tags sometimes available
        categories = response.css("a[data-analytics-link='article label']::text").getall() or []

        content = " ".join(
            response.css("div.c-entry-content p::text, div.c-entry-content h2::text").getall()
        )

        yield {
            "url": response.url,
            "title": title.strip(),
            "summary": summary.strip(),
            "content": content.strip(),
            "author": author.strip(),
            "image_url": image,
            "published_at": published_at,
            "categories": [c.strip() for c in categories if c.strip()],
            "source": "The Verge",
            "homepage": "https://www.theverge.com",
        }
