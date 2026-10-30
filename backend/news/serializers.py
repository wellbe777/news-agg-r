from rest_framework import serializers
from .models import Source, Category, Article, UserInterest, UserArticleInteraction
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for displaying user data."""
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id", "username", "email"]

    
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "first_name", "last_name"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        # Create user using Django’s built-in user model
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def update(self, instance, validated_data):
        """Allow password change via update"""
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]

class SourceSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)  # inline categories

    class Meta:
        model = Source
        fields = ["id", "name", "homepage", "rss_url", "active", "categories"]

class ArticleSerializer(serializers.ModelSerializer):
    source = SourceSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    #api_url = serializers.HyperlinkedIdentityField(view_name="article-detail", lookup_field="pk")

    class Meta:
        model = Article
        fields = [
            "id", "title", "summary", "content", "url",  "image_url", "author", "published_at",
            "source", "categories"
        ]  # "api_url",


class UserInterestSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    sources = SourceSerializer(many=True, read_only=True)

    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        write_only=True,
        source="categories"
    )
    source_ids = serializers.PrimaryKeyRelatedField(
        queryset=Source.objects.all(),
        many=True,
        write_only=True,
        source="sources"
    )

    class Meta:
        model = UserInterest
        fields = ["categories", "sources", "category_ids", "source_ids"]


class UserArticleInteractionSerializer(serializers.ModelSerializer):
    article = ArticleSerializer(read_only=True)

    class Meta:
        model = UserArticleInteraction
        fields = ("id", "article", "viewed", "liked", "saved", "clicked_at")

# for testing 
class TestAddSerializer(serializers.Serializer):
    x = serializers.IntegerField()
    y = serializers.IntegerField()
