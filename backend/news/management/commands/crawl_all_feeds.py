# backend/news/management/commands/crawl_all_feeds.py
from django.core.management.base import BaseCommand
from news.models import Source
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os
from scraper.spiders.rss_generic import RssGenericSpider

class Command(BaseCommand):
    help = "Crawl all active feeds from Source model using Scrapy"

    def handle(self, *args, **options):
        # Tell Scrapy where to find settings
        os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "scraper.settings")

        sources = Source.objects.filter(active=True, rss_url__isnull=False)

        if not sources.exists():
            self.stdout.write(self.style.WARNING("No active sources with RSS URLs found."))
            return

        self.stdout.write(self.style.NOTICE(f"Found {sources.count()} sources to crawl."))

        process = CrawlerProcess(get_project_settings())

        for source in sources:
            self.stdout.write(self.style.NOTICE(f"Scheduling: {source.name}"))
            process.crawl(
                RssGenericSpider,
                feed=source.rss_url,
                source=source.name,
                homepage=source.homepage,
            )

        self.stdout.write(self.style.NOTICE("Starting Scrapy crawlers..."))
        process.start()
        self.stdout.write(self.style.SUCCESS("Finished crawling all feeds."))
