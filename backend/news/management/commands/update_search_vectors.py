from django.core.management.base import BaseCommand
from django.contrib.postgres.search import SearchVector
from news.models import Article

class Command(BaseCommand):
    help = "Rebuild search_vector field for all articles."

    def handle(self, *args, **kwargs):
        self.stdout.write("Updating search_vector for all articles...")

        Article.objects.update(
            search_vector=(
                SearchVector("title", weight="A") +
                SearchVector("summary", weight="B") +
                SearchVector("content", weight="C")
            )
        )

        self.stdout.write(self.style.SUCCESS("search_vector updated successfully."))
