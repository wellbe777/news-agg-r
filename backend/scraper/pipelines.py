# backend/scraper/pipelines.py
import os
import django
from django.utils import timezone

from itemadapter import ItemAdapter

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newsagg.settings")  # adjust if your settings package is named differently
django.setup()

from news.models import Article, Source, Category


class DjangoWriterPipeline:
    """
    A Scrapy pipeline that saves scraped items into the Django ORM.
    """

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Get or create Source
        source, _ = Source.objects.get_or_create(
            name=adapter.get("source", spider.name),
            defaults={"homepage": adapter.get("homepage", "")},
        )

        # Get or create Article
        article, created = Article.objects.update_or_create(
            url=adapter.get["url"],
            defaults={
                "title": adapter.get("title", ""),
                "summary": adapter.get("summary", ""),
                "content": adapter.get("content", ""),
                "author": adapter.get("author", ""),
                "image_url": adapter.get("image_url", ""),
                "published_at": adapter.get("published_at", timezone.now()),
                "source": source,
            },
        )

        # Normalize and attach categories
        categories = adapter.get("categories", [])
        cleaned = []

        for cat_name in categories:
            # Normalize to lowercase, strip spaces
            normalized = cat_name.strip().lower()
            if not normalized:
                continue

            category, _ = Category.objects.get_or_create(name=normalized)
            
            # Optional: store a display-friendly version
            display_name = cat_name.strip().title()
            if category.display_name != display_name:
                category.display_name = display_name
                category.save(update_fields=["display_name"])

            cleaned.append(category)

        if cleaned:
            article.categories.set(cleaned)

        return item
