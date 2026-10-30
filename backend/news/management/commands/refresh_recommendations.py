# backend/news/management/commands/refresh_recommendations.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from news.tasks import compute_recommendations_for_user

# Usage sync: python manage.py refresh_recommendations  or add (--async)

User = get_user_model()


class Command(BaseCommand):
    help = "Recompute and cache recommendations for all users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--async",
            action="store_true",
            help="Run tasks asynchronously via Celery instead of synchronously",
        )

    def handle(self, *args, **options):
        async_mode = options["async"]
        users = User.objects.all()
        total = users.count()

        self.stdout.write(self.style.NOTICE(f"Refreshing recommendations for {total} users..."))

        for user in users:
            if async_mode:
                compute_recommendations_for_user.delay(user.id)
            else:
                compute_recommendations_for_user(user.id)

        if async_mode:
            self.stdout.write(self.style.SUCCESS("Triggered async tasks for all users."))
        else:
            self.stdout.write(self.style.SUCCESS("Refreshed recommendations synchronously."))
