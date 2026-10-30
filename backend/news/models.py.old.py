# backend/news/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.title


class UserInterest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="interests")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="user_interests")
    weight = models.FloatField(default=1.0)

    class Meta:
        unique_together = ("user", "category")

    def __str__(self):
        return f"{self.user.username} → {self.category.name}"


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
