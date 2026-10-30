from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Create or update the scraper service account"

    def handle(self, *args, **options):
        username = "scraper"
        password = "scraper-secret"  # use env var in prod

        user, created = User.objects.get_or_create(username=username)
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS("✅ Scraper user created"))
        else:
            self.stdout.write(self.style.WARNING("ℹ️ Scraper user already exists, password updated"))
