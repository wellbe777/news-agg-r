# backend/news/management/commands/crawl.py
import os
from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class Command(BaseCommand):
    help = "Run a Scrapy spider with optional -a args (e.g. -a feed=... -a source=...)"

    def add_arguments(self, parser):
        parser.add_argument("spider_name", type=str, help="Spider name")
        # Capture all unknown args like Scrapy's -a feed=...
        parser.add_argument(
            "scrapy_args",
            nargs="*",
            help="Additional arguments in the form key=value (like Scrapy -a)",
        )

    def handle(self, *args, **options):
        os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "scraper.settings")

        process = CrawlerProcess(get_project_settings())

        spider_name = options["spider_name"]
        scrapy_args = {}

        for arg in options["scrapy_args"]:
            if "=" in arg:
                key, val = arg.split("=", 1)
                scrapy_args[key] = val

        process.crawl(spider_name, **scrapy_args)
        process.start()
