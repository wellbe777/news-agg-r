from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q, F, Case, When, Value, FloatField
from django.db.models.functions import Coalesce
from django.db.models.expressions import Func
from celery import shared_task
from django.contrib.auth import get_user_model
import logging
import time

from .models import Article, UserInterest, UserArticleInteraction

User = get_user_model()

def compute_recommendations_for_user(user, limit=20, cache_ttl=60*15):
    """
    Fast Python-based weighted scoring recommender.
    We fetch candidate articles, compute a score for each,
    sort in Python, and cache the top-N IDs.
    """

    interests, _ = UserInterest.objects.get_or_create(user=user)

    # --------------------------------------
    # 1. Collect candidate articles
    # --------------------------------------
    candidate_qs = Article.objects.all()

    # Explicit filters (widen candidate set, not reduce too strictly)
    if interests.categories.exists():
        candidate_qs = candidate_qs.filter(
            Q(categories__in=interests.categories.all())
            | Q(published_at__gte=timezone.now() - timedelta(days=7))
        )

    if interests.sources.exists():
        candidate_qs = candidate_qs.filter(
            Q(source__in=interests.sources.all())
            | Q(published_at__gte=timezone.now() - timedelta(days=7))
        )

    # If no explicit interests → recent articles only
    if not interests.categories.exists() and not interests.sources.exists():
        candidate_qs = Article.objects.filter(
            published_at__gte=timezone.now() - timedelta(days=7)
        )

    candidate_qs = candidate_qs.select_related("source").prefetch_related("categories")

    # --------------------------------------
    # 2. Implicit behavior
    # --------------------------------------
    interactions = UserArticleInteraction.objects.filter(user=user)

    liked_ids = set(interactions.filter(liked=True).values_list("article_id", flat=True))
    viewed_ids = set(interactions.filter(viewed=True).values_list("article_id", flat=True))

    liked_articles = Article.objects.filter(id__in=liked_ids)

    liked_cats = set(liked_articles.values_list("categories__id", flat=True))
    liked_sources = set(liked_articles.values_list("source_id", flat=True))

    user_cats = set(interests.categories.values_list("id", flat=True))
    user_sources = set(interests.sources.values_list("id", flat=True))

    now = timezone.now()

    # --------------------------------------
    # 3. Scoring function
    # --------------------------------------
    def score_article(article):
        score = 0.0

        article_cat_ids = set(article.categories.values_list("id", flat=True))
        article_source_id = article.source_id

        # Explicit Interest Match
        if article_cat_ids & user_cats:
            score += 1.0
        if article_source_id in user_sources:
            score += 1.0

        # Implicit Similarity to liked articles
        if article_cat_ids & liked_cats:
            score += 1.5
        if article_source_id in liked_sources:
            score += 1.5

        # Recency bonus (0 → 1)
        days_old = (now - article.published_at).days
        if days_old <= 30:
            score += max(0.0, 1 - days_old / 30)

        # Penalty if viewed before
        if article.id in viewed_ids:
            score -= 0.5

        return score

    # --------------------------------------
    # 4. Compute scores (fast, in Python)
    # --------------------------------------
    scored = []
    for article in candidate_qs:
        scored.append((score_article(article), article))

    # Sort by score DESC
    scored.sort(key=lambda x: x[0], reverse=True)

    # Take top-N articles
    top_articles = [a for _, a in scored[:limit]]

    # --------------------------------------
    # 5. Cache the result
    # --------------------------------------
    cache_key = f"user:{user.id}:recommendations"
    cache.set(cache_key, [a.id for a in top_articles], cache_ttl)

    return top_articles

# -------------------------------
# Celery Tasks
# -------------------------------

CACHE_TTL = 60 * 15  # 15 minutes
CACHE_KEY_FORMAT = "user:{user_id}:recommendations"


@shared_task
def compute_recommendations_task(user_id, limit=20):
    """
    Asynchronously recompute recommendations for a single user.
    Stores ordered list of article IDs under a consistent cache key.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

    articles = compute_recommendations_for_user(user, limit=limit)
    ids = [a.id for a in articles]

    cache_key = CACHE_KEY_FORMAT.format(user_id=user.id)
    cache.set(cache_key, ids, CACHE_TTL)

    return ids


@shared_task
def compute_recommendations_for_all_users(limit=20):
    """
    Recomputation for all users (admin-triggered or scheduled).
    """
    results = {}
    for user in User.objects.all():
        articles = compute_recommendations_for_user(user, limit=limit)
        ids = [a.id for a in articles]

        cache_key = CACHE_KEY_FORMAT.format(user_id=user.id)
        cache.set(cache_key, ids, CACHE_TTL)

        results[user.id] = len(ids)

    return results


logger = logging.getLogger(__name__)

@shared_task
def ping():
    """Debug task to test Celery setup."""
    logger.info("pong from Celery!")
    print("pong from Celery!")  # shows up in worker logs
    return "pong"


@shared_task
def test_add(x, y):
    """Simple test task that adds two numbers."""
    time.sleep(2)  # simulate some work
    return x + y
