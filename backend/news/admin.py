# backend/news/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Article, Source, Category, UserInterest, UserArticleInteraction

User = get_user_model()


class ArticleInline(admin.TabularInline):
    model = Article
    extra = 0
    show_change_link = True


class UserInterestInline(admin.TabularInline):
    model = UserInterest
    extra = 0
    show_change_link = True


class UserArticleInteractionInline(admin.TabularInline):
    model = UserArticleInteraction
    extra = 0
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("name", "homepage", "rss_url", "active")
    search_fields = ("name", "homepage")
    list_filter = ("active", "categories")
    inlines = [ArticleInline]  # show articles under a source
    filter_horizontal = ("categories",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "published_at")
    search_fields = ("title", "summary", "content")
    list_filter = ("source", "published_at", "categories")
    filter_horizontal = ("categories",)
    inlines = [UserArticleInteractionInline]  # show interactions inside article


@admin.register(UserInterest)
class UserInterestAdmin(admin.ModelAdmin):
    list_display = ("user", "get_categories", "get_sources")

    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()]) or "—"
    get_categories.short_description = "Categories"

    def get_sources(self, obj):
        return ", ".join([s.name for s in obj.sources.all()]) or "—"
    get_sources.short_description = "Sources"


@admin.register(UserArticleInteraction)
class UserArticleInteractionAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "viewed", "liked", "saved", "clicked_at")
    list_filter = ("viewed", "liked", "saved")
    search_fields = ("user__username", "article__title")


# Attach UserInterest and Interactions to User model admin
class UserAdmin(admin.ModelAdmin):
    inlines = [UserInterestInline, UserArticleInteractionInline]
    list_display = ("username", "email", "is_staff", "is_superuser")


# Unregister default User admin and re-register with inlines
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, UserAdmin)
