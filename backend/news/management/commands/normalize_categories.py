from django.core.management.base import BaseCommand
from django.db import transaction
from news.models import Category, Article


class Command(BaseCommand):
    help = "Normalize and deduplicate Category names (case-insensitive, trimmed)."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Normalizing categories..."))

        categories = list(Category.objects.all())
        seen = {}
        merged = 0

        for category in categories:
            normalized = category.name.strip().lower()

            if not normalized:
                # Delete empty or invalid categories
                category.delete()
                continue

            if normalized in seen:
                # Merge duplicate: move article links to the canonical one
                canonical = seen[normalized]
                articles = Article.objects.filter(categories=category)
                for article in articles:
                    article.categories.add(canonical)
                category.delete()
                merged += 1
            else:
                # First occurrence of this normalized name
                category.name = normalized
                category.display_name = category.display_name or category.name.title()
                category.save(update_fields=["name", "display_name"])
                seen[normalized] = category

        self.stdout.write(
            self.style.SUCCESS(f"✅ Normalization complete — merged {merged} duplicates.")
        )
        self.stdout.write(
            self.style.SUCCESS(f"📦 Total categories remaining: {Category.objects.count()}")
        )
