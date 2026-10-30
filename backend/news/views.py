# backend/news/views.py
from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import connection, models
from django.db.models import F, Prefetch, Q, Value, FloatField
from rest_framework.views import APIView
#from rest_framework.generics import ListAPIView
#from rest_framework.pagination import CursorPagination
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from .tasks import compute_recommendations_for_user, compute_recommendations_task, test_add
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.postgres.search import SearchQuery, SearchRank, TrigramSimilarity
from django.db.models.functions import Lower
from django.db.models.expressions import Func
from .management.commands.db_health import database_is_slow

from .models import Source, Article, Category, UserInterest, UserArticleInteraction
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    SourceSerializer,
    ArticleSerializer,
    CategorySerializer,
    UserInterestSerializer,
    UserArticleInteractionSerializer,
    TestAddSerializer,
)

class RegisterView(generics.CreateAPIView):
    """Register a new user and immediately issue JWT tokens."""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # ✅ Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        data = {
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": access,
        }
        return Response(data, status=status.HTTP_201_CREATED)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return current authenticated user info."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    pagination_class = None


class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Source.objects.prefetch_related("categories").all()
    serializer_class = SourceSerializer
    pagination_class = None

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "active": ["exact"],
        "categories__id": ["exact"],       # filter by category ID
        "categories__slug": ["exact"],     # filter by category slug
    }
    search_fields = ["name", "homepage"]
    ordering_fields = ["name"]


#class ArticleCursorPagination(CursorPagination):
#    ordering = '-created_at'
"""
class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ArticleSerializer
    #pagination_class = ArticleCursorPagination  # pagination override
    permission_classes = [AllowAny]
    """
    #Article API with:
    #- /articles/ (list + pagination)
    #- /articles/?search=AI (PostgreSQL FTS with rank + recency)
    #- /articles/?ordering=title or -published_at
"""
    ordering_fields = ("published_at", "title", "source__name")
    ordering = ("-published_at",)
    #queryset = (Article.objects.select_related("source").prefetch_related(Prefetch("categories", queryset=Category.objects.only("id", "name"))).order_by("-published_at"))
    queryset = (Article.objects.select_related("source").prefetch_related("categories").order_by("published_at"))

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    #filterset_fields = ["source", "categories__id"]  # re-validates source based on serializer fields <- causes error
    search_fields = ["title", "summary", "content"]

    def get_queryset(self):
        qs = super().get_queryset()
        request = self.request

        # --- User interest filtering ---
        user = request.user if request.user.is_authenticated else None
        category_param = request.query_params.get("category")
        source_param = request.query_params.get("source")
        print("inside ArticleViewSet...")

        # If user has interests AND did not manually choose filters:
        if user and not any([category_param, source_param, search_term]):
            interests = user.interests.prefetch_related("categories", "sources").first()

            if interests:
                selected_categories = list(interests.categories.values_list("name", flat=True))
                selected_sources = list(interests.sources.values_list("name", flat=True))
                print("inside ArticleViewSet interests...")
                # filter if user selected categories
                if selected_categories:
                    qs = qs.filter(categories__name__in=selected_categories)

                # filter if user selected sources
                if selected_sources:
                    qs = qs.filter(source__name__in=selected_sources)

        # --- Category filter ---
        if category_param:
            qs = qs.filter(categories__name__iexact=category_param)

        # --- Source filter ---
        if source_param:
            qs = qs.filter(source__name__iexact=source_param)

        # --- Keyword search ---
        search_term = request.query_params.get("search")
        if search_term:
            term = search_term.strip()

            # ---------------------------------------
            # 1. Prefix Full-Text Search (non-strict)
            # ---------------------------------------
            try:
                prefix_query = SearchQuery(f"{term}:*", search_type="raw")
                fts_rank = SearchRank(F("search_vector"), prefix_query)
            except Exception:
                prefix_query = None
                fts_rank = Value(0.0)

            # ---------------------------------------
            # 2. Trigram similarity (robust fuzzy match)
            # ---------------------------------------
            sim_title = Func(F("title"), Value(term), function="similarity", output_field=FloatField())
            sim_summary = Func(F("summary"), Value(term), function="similarity", output_field=FloatField())

            qs = qs.annotate(
                sim_title=sim_title,
                sim_summary=sim_summary,
                trigram_score=F("sim_title") * 1.6 + F("sim_summary"),
                total_rank=fts_rank + (F("sim_title") * 1.6) + F("sim_summary"),
            )

            # ---------------------------------------
            # 3. Adaptive threshold for short/typoed queries
            # ---------------------------------------
            if len(term) <= 3:
                trigram_threshold = 0.03
            elif len(term) <= 5:
                trigram_threshold = 0.06
            else:
                trigram_threshold = 0.12

            # ---------------------------------------
            # 4. OR-based matching (never strict)
            # ---------------------------------------
            filters = Q(
                trigram_score__gte=trigram_threshold
            ) | Q(
                title__icontains=term
            ) | Q(
                summary__icontains=term
            )

            if prefix_query:
                filters |= Q(search_vector=prefix_query)

            qs = qs.filter(filters).order_by("-total_rank", "-published_at")

            return qs  #.distinct()
"""

class ArticleListView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all().select_related("source").prefetch_related("categories").order_by("-published_at")
    filter_backends = [filters.OrderingFilter]  #filters.SearchFilter,
    #search_fields = ["title", "summary", "categories__name", "source__name"]
    ordering = ["-published_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        request = self.request

        # -------------------------
        # Interests filtering
        # -------------------------
        use_interests = request.query_params.get("use_interests", "false").lower()

        if use_interests == "true" and request.user.is_authenticated:
            try:
                user_interest = (
                    request.user.interests.prefetch_related("categories", "sources").first()
                )

                if user_interest:
                    categories = user_interest.categories.all()
                    sources = user_interest.sources.all()

                    if categories.exists():
                        qs = qs.filter(categories__in=categories)

                    if sources.exists():
                        qs = qs.filter(source__in=sources)

            except Exception as e:
                print("Interest filter error:", e)

        # -------------------------
        # Category / Source
        # -------------------------
        category = request.query_params.get("category") or None
        source = request.query_params.get("source") or None

        if category:
            qs = qs.filter(categories__name__iexact=category)

        if source:
            qs = qs.filter(source__name__iexact=source)

        # -------------------------
        # Custom Search (FTS + Trigram)
        # -------------------------
        search_term = request.query_params.get("search")
        if search_term:
            term = search_term.strip()

            # FTS
            search_query = SearchQuery(term, config="english")

            qs = qs.annotate(
                fts_rank=SearchRank(F("search_vector"), search_query),
                trigram_title=Func(
                    F("title"),
                    Value(term),
                    function="similarity",
                    output_field=FloatField(),
                ),
                trigram_summary=Func(
                    F("summary"),
                    Value(term),
                    function="similarity",
                    output_field=FloatField(),
                ),
                trigram_score=F("trigram_title") * 1.6 + F("trigram_summary"),
            )

            # Adaptive trigram threshold
            if len(term) <= 3:
                trigram_threshold = 0.03
            elif len(term) <= 5:
                trigram_threshold = 0.06
            else:
                trigram_threshold = 0.12

            # Combine FTS + trigram + prefix match
            qs = qs.filter(
                Q(fts_rank__gt=0)
                | Q(trigram_score__gte=trigram_threshold)
                | Q(title__icontains=term)  # prefix or substring
                | Q(summary__icontains=term)
            ).order_by("-fts_rank", "-trigram_score", "-published_at")

            return qs.distinct()

        # Default ordering
        return qs.distinct().order_by(*self.ordering)


class ArticleDetailView(generics.RetrieveAPIView):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()


class NewsListView(generics.ListAPIView):
    queryset = Article.objects.all() #.order_by("-id")
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]


class UserInterestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Always ensure user has a UserInterest object
        interests, _ = UserInterest.objects.get_or_create(user=request.user)
        serializer = UserInterestSerializer(interests)
        return Response(serializer.data)

    def post(self, request):
        interests, _ = UserInterest.objects.get_or_create(user=request.user)
        serializer = UserInterestSerializer(interests, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserArticleInteractionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserArticleInteractionSerializer

    def get_queryset(self):
        return UserArticleInteraction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Recommendation API:
    - /recommendations/ → cached recommendations for the user
    - /recommendations/?search=AI → FTS with weighted rank on recommended IDs
    - /recommendations/?ordering=title -published_at, etc. → optional ordering
    """
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ("published_at", "title", "source__name")
    ordering = ("-published_at",)

    def get_queryset(self):
        user = self.request.user
        key = f"recommendations:{user.id}"
        fallback_key = f"fallback:{user.id}:recommendations"

        # ------------------------------------------------------
        # 1) Fast path → return cached recommendations
        # ------------------------------------------------------
        cached_ids = cache.get(key)

        if cached_ids:
            qs = Article.objects.filter(id__in=cached_ids)\
                .select_related("source")\
                .prefetch_related("categories")
            return qs

        # ------------------------------------------------------
        # 2) DB slow/unavailable → use fallback only
        # ------------------------------------------------------
        if database_is_slow():
            fallback_ids = cache.get(fallback_key)
            if fallback_ids:
                qs = Article.objects.filter(id__in=fallback_ids)\
                    .select_related("source")\
                    .prefetch_related("categories")
                return qs.order_by("-published_at")

            # No fallback? fail soft (empty recs)
            return Article.objects.none()

        # ------------------------------------------------------
        # 3) DB healthy → compute fresh recommendations
        # ------------------------------------------------------
        articles = compute_recommendations_for_user(user) or []
        fresh_ids = [a.id for a in articles]

        # store live cache + fallback copy
        cache.set(key, fresh_ids, 3600)
        cache.set(fallback_key, fresh_ids, 3600 * 24)

        # always return qs (never None)
        qs = Article.objects.filter(id__in=fresh_ids).select_related("source").prefetch_related("categories")

        # ------------------------------------------------------
        # 4) Full-text search inside recommended items
        # ------------------------------------------------------
        search_term = self.request.query_params.get("search")
        if search_term:
            search_query = SearchQuery(search_term)
            qs = (
                qs.annotate(
                    rank=SearchRank(
                        F("search_vector"), search_query,
                        weights=[0.3, 0.6, 1.0]
                    )
                )
                .filter(search_vector=search_query)
                .order_by("-rank", "-published_at")
            )
            return qs

        # ------------------------------------------------------
        # 5) Default ordering
        # ------------------------------------------------------
        return qs.order_by(*self.ordering)

    @action(detail=False, methods=["post"], url_path="refresh")
    def refresh(self, request):
        """Trigger async recomputation via Celery"""
        compute_recommendations_task.delay(request.user.id)
        return Response({"ok": True, "message": "Recomputing recommendations"})
    
    @action(detail=False, methods=["post"], url_path="refresh_all", permission_classes=[IsAdminUser])
    def refresh_all(self, request):
        """Admin-only: recompute recommendations for all users asynchronously."""
        from .tasks import compute_recommendations_for_all_users
        compute_recommendations_for_all_users.delay()
        return Response({"status": "global refresh started"}, status=status.HTTP_202_ACCEPTED)


class TestCeleryView(APIView):
    """
    Endpoint to queue a Celery test task.
    POST {"x": 2, "y": 3} → returns task_id
    GET /api/test-celery/?task_id=<uuid> → check status/result
    """

    def post(self, request):
        serializer = TestAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        x = serializer.validated_data["x"]
        y = serializer.validated_data["y"]

        task = test_add.delay(x, y)
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)

    def get(self, request):
        from celery.result import AsyncResult
        task_id = request.query_params.get("task_id")
        if not task_id:
            return Response({"error": "task_id required"}, status=status.HTTP_400_BAD_REQUEST)

        result = AsyncResult(task_id)
        data = {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.successful() else None,
        }
        return Response(data, status=status.HTTP_200_OK)
