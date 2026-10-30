# backend/news/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
import pgtrigger
from django.db.models.signals import pre_save
from django.dispatch import receiver

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    display_name = models.CharField(max_length=100, blank=True)

    class Meta:
        indexes = [models.Index(fields=["name"])]
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name or self.name


class Source(models.Model):
    name = models.CharField(max_length=128)
    homepage = models.URLField()
    rss_url = models.URLField(blank=True, null=True)
    active = models.BooleanField(default=True)
    categories = models.ManyToManyField("Category", related_name="sources", blank=True)

    class Meta:
        unique_together = ("name", "homepage")

    def __str__(self):
        return self.name


class Article(models.Model):
    source = models.ForeignKey(Source, on_delete=models.PROTECT)
    url = models.URLField(unique=True)
    title = models.CharField(max_length=512)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)
    author = models.CharField(max_length=256, blank=True)
    image_url = models.URLField(blank=True)
    published_at = models.DateTimeField(db_index=True)
    categories = models.ManyToManyField(Category, related_name="articles", blank=True)
    language = models.CharField(max_length=8, default="en")
    embeddings = models.BinaryField(null=True, blank=True)  # optional for recs
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True, editable=False)

    
    class Meta:
        indexes = [
            GinIndex(fields=["search_vector"]),  # FTS index Postgres
        ]
        #ordering = ["-published_at"]   # recent-first as default
        triggers = [
            pgtrigger.UpdateSearchVector(
                name="add_title_summary_content_to_vector",
                vector_field="search_vector",
                document_fields=["title", "summary", "content"],
            )
        ]

    def __str__(self):
        return self.title


class UserInterest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="interests")
    categories = models.ManyToManyField(Category, related_name="user_interests", blank=True)
    weight = models.FloatField(default=1.0)
    sources = models.ManyToManyField(Source, blank=True)

    def __str__(self):
        return f"{self.user.username} → {', '.join(c.name for c in self.categories.all()) or 'No categories'}"


class UserArticleInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="article_interactions")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="user_interactions")
    viewed = models.BooleanField(default=False)
    liked = models.BooleanField(default=False)
    saved = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "article")

    def __str__(self):
        flags = []
        if self.viewed:
            flags.append("viewed")
        if self.liked:
            flags.append("liked")
        if self.saved:
            flags.append("saved")
        return f"{self.user.username} → {self.article.title} ({', '.join(flags) or 'no action'})"
    

@receiver(pre_save, sender=Category)
def normalize_category_name(sender, instance, **kwargs):
    """
    Normalize category name before saving.
    Example:
      "   Sports " -> name="sports", display_name="Sports"
    """
    if instance.name:
        normalized = instance.name.strip().lower()
        instance.name = normalized
        if not instance.display_name:
            instance.display_name = normalized.title()

