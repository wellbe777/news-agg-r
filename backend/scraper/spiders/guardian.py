# backend/scraper/spiders/guardian.py
import scrapy
from datetime import datetime


class GuardianSpider(scrapy.Spider):
    name = "guardian"
    allowed_domains = ["theguardian.com"]
    start_urls = ["https://www.theguardian.com/international"]

    def parse(self, response):
        # Select article links from homepage
        for article in response.css("a.u-faux-block-link__overlay"):
            url = article.attrib.get("href")
            if url and "/live/" not in url:  # skip live blogs
                yield response.follow(url, callback=self.parse_article)

    def parse_article(self, response):
        title = response.css("h1::text").get() or ""
        summary = response.css("meta[name='description']::attr(content)").get() or ""
        author = response.css("a[rel='author']::text").get() or ""
        image = response.css("meta[property='og:image']::attr(content)").get() or ""

        # Guardian sometimes stores date in <time> tag
        published_str = response.css("time::attr(datetime)").get()
        try:
            published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
        except Exception:
            published_at = datetime.utcnow()

        categories = response.css("a.submeta__link::text").getall() or []

        yield {
            "url": response.url,
            "title": title.strip(),
            "summary": summary.strip(),
            "content": " ".join(response.css("div.article-body-commercial-selector p::text").getall()),
            "author": author.strip(),
            "image_url": image,
            "published_at": published_at,
            "categories": [c.strip() for c in categories if c.strip()],
            "source": "The Guardian",
            "homepage": "https://www.theguardian.com",
        }
