# backend/scraper/spiders/rss_generic.py

import scrapy
import feedparser
from datetime import datetime
from urllib.parse import urlparse
from asgiref.sync import sync_to_async
import re
from bs4 import BeautifulSoup
from news.models import Article, Source, Category


class RssGenericSpider(scrapy.Spider):
    """
    Generic RSS spider that can crawl any feed URL and save results to the Article model.

    Usage:
        python manage.py crawl_all_feeds
    """

    name = "rss_generic"

    def __init__(self, feed=None, source=None, homepage=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not feed:
            raise ValueError("You must provide a feed URL via feed=<url>")
        self.feed_url = feed
        self.source_name = source or urlparse(feed).netloc
        self.homepage = homepage or f"https://{urlparse(feed).netloc}"

    def start_requests(self):
        yield scrapy.Request(self.feed_url, callback=self.parse_feed)

    def extract_image_url(entry):
        # 1. media:content
        media_content = entry.get("media_content") or []
        if media_content:
            url = media_content[0].get("url")
            if url:
                return url

        # 2. media:thumbnail
        media_thumbnail = entry.get("media_thumbnail") or []
        if media_thumbnail:
            url = media_thumbnail[0].get("url")
            if url:
                return url

        # 3. enclosures / links
        for link in entry.get("links", []):
            if link.get("type", "").startswith("image/"):
                return link.get("href", "")

        # 4. image field
        image = entry.get("image")
        if isinstance(image, dict):
            return image.get("href") or image.get("url") or ""
        if isinstance(image, str):
            return image

        # 5. image inside summary/content HTML
        html_parts = []
        if entry.get("summary"):
            html_parts.append(entry.get("summary"))

        for content_item in entry.get("content", []):
            if isinstance(content_item, dict) and content_item.get("value"):
                html_parts.append(content_item["value"])

        for html in html_parts:
            soup = BeautifulSoup(html, "html.parser")
            img = soup.find("img")
            if img and img.get("src"):
                return img["src"]

        return ""

    async def parse_feed(self, response):
        parsed = feedparser.parse(response.body)

        for entry in parsed.entries:
            url = entry.get("link")
            title = entry.get("title", "").strip()
            summary = entry.get("summary", "").strip()
            published_at = None

            if "published_parsed" in entry and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6])
            elif "updated_parsed" in entry and entry.updated_parsed:
                published_at = datetime(*entry.updated_parsed[:6])
            else:
                published_at = datetime.utcnow()

            categories = [t["term"] for t in entry.get("tags", []) if "term" in t]
            image_url = ""
            #if "media_content" in entry and entry["media_content"]:
            #    image_url = entry["media_content"][0].get("url", "")
            image_url = self.extract_image_url(entry)

            self.logger.info(f"Categories for '{title[:60]}': {categories}")  # show if article has category

            data = {
                "url": url,
                "title": title,
                "summary": summary,
                "content": summary,  # RSS fallback
                "author": entry.get("author", ""),
                "image_url": image_url,
                "published_at": published_at,
                "source": self.source_name,
                "homepage": self.homepage,
                "categories": categories,
            }

            # Save to DB safely using sync_to_async
            await self.save_article(data)

    @sync_to_async
    def save_article(self, data: dict):
        """Safely create or update articles from async Scrapy context."""
        source_obj, _ = Source.objects.get_or_create(
            name=data["source"],
            defaults={"homepage": data["homepage"], "rss_url": self.feed_url},
        )

        article, _ = Article.objects.update_or_create(
            url=data["url"],
            defaults={
                "title": data["title"],
                "summary": data["summary"],
                "content": data["content"],
                "author": data["author"],
                "image_url": data["image_url"],
                "published_at": data["published_at"],
                "source": source_obj,
            },
        )
        # ✅ Save categories
        categories = data.get("categories", [])
        if categories:
            article.categories.clear()
            for cat_name in categories:
                cat_obj, _ = Category.objects.get_or_create(name=cat_name)
                article.categories.add(cat_obj)

        return article
