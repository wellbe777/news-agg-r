# backend/news/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SourceViewSet, ArticleListView, ArticleDetailView, CategoryViewSet, NewsListView,
    UserInterestView, UserArticleInteractionViewSet, RecommendationViewSet, TestCeleryView, 
    RegisterView, CurrentUserView )  
# ArticleViewSet, UserInterestViewSet, RecommendationView, ArticleViewSet,

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"sources", SourceViewSet, basename="source")
#router.register(r"articles", ArticleViewSet, basename="article")
#router.register(r"user-interests", UserInterestViewSet, basename="userinterest")
router.register(r"interactions", UserArticleInteractionViewSet, basename="interaction")
router.register(r"recommendations", RecommendationViewSet, basename="recommendations")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterView.as_view(), name="register"),
    path("user/", CurrentUserView.as_view(), name="current-user"),
    path("articles/", ArticleListView.as_view(), name="articles"),
    path("articles/<int:pk>/", ArticleDetailView.as_view(), name="articles-detail"),
    #path("articles/search/", ArticleViewSet.as_view({"get": "list"}), name="article-search"),  # keep it as hidden alias
    
    path("news/", NewsListView.as_view(), name="news-list"),
    path("user/interests/", UserInterestView.as_view(), name="user-interests"),
    #path("recommendations/", RecommendationView.as_view(), name="recommendations"),
    path("test-celery/", TestCeleryView.as_view(), name="test-celery"),
]
