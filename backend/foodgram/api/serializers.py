import base64

from django.contrib.auth import get_user_model, password_validation
from django.core.files.base import ContentFile
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import serializers

from app.models import Ingredient, Recipe, RecipeIngredients, Tag

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_authenticated:
            request_user = self.context['request'].user
            return obj.following.filter(user=request_user).exists()
        return False


class UserSignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'id', 'password', 'username',
                  'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        if password_validation.validate_password(value) is None:
            return value

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        if self.context['request'].user.is_authenticated:
            return obj.user_favorite.filter(
                username=self.context['request'].user.username).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_authenticated:
            return obj.user_cart.filter(
                username=self.context['request'].user.username).exists()
        return False

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        tags = get_list_or_404(Tag, id__in=ret['tags'])
        serializer = TagSerializer(tags, many=True)
        ret['tags'] = serializer.data
        ingredients = get_list_or_404(Ingredient, id__in=ret['ingredients'])
        serializer_ing = IngredientSerializer(ingredients, many=True)
        for ing in serializer_ing.data:
            ing['amount'] = get_object_or_404(RecipeIngredients,
                                              recipe=instance,
                                              ingredient=ing['id']).amount
        ret['ingredients'] = serializer_ing.data
        return ret

    def to_internal_value(self, data):
        validated_data = super().to_internal_value(data)
        validated_data['ingredients'] = self.initial_data['ingredients']
        return validated_data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for ing in ingredients:
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, pk=ing['id']),
                amount=ing['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.tags.clear()
        for tag in tags:
            instance.tags.add(tag)
        instance.recipe_ing.all().delete()
        for ing in ingredients:
            RecipeIngredients.objects.create(
                recipe=instance,
                ingredient=get_object_or_404(Ingredient, pk=ing['id']),
                amount=ing['amount']
            )
        return instance


class RecipeSubSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    def get_recipes(self, obj):
        recipes = obj.recipes.filter()[:3]
        return RecipeSubSerializer(recipes, many=True).data


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(trim_whitespace=False)
    current_password = serializers.CharField(trim_whitespace=False)

    def validate(self, attrs):
        if attrs.get('new_password') == attrs.get('current_password'):
            raise serializers.ValidationError(
                'Новый пароль должен отличаться от текущего')
        return attrs

    def validate_new_password(self, value):
        if password_validation.validate_password(value) is None:
            return value
