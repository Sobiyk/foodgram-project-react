from django.contrib.auth import get_user_model, hashers, password_validation
from rest_framework import serializers

from .fields import Base64ImageField
from .utils import add_ingredients
from app.models import Ingredient, Recipe, RecipeIngredient, Tag

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
        raise serializers.ValidationError(
            'Пароль не прошел валидацию'
        )

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


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSubSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        return obj.image.url


class IngredientInRecipeCreateSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('recipe', 'id', 'amount')


class IngredientRecSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecSerializer(read_only=True, many=True,
                                          source='recipe_ing')
    image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_image(self, obj):
        return obj.image.url

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


class RecipeSerializer(RecipeReadSerializer):
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeCreateSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def validate_ingredients(self, ingredients):
        unique_ing = []
        for ingredient in ingredients:
            if ingredient['id'] not in unique_ing:
                unique_ing.append(ingredient['id'])
            else:
                raise serializers.ValidationError(
                    'Нельзя добавлять ингредиент дважды'
                )
        if not unique_ing:
            raise serializers.ValidationError(
                'Нужно добавить хотя бы один ингредиент'
            )
        return ingredients

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        add_ingredients(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        super().update(recipe, validated_data)
        recipe.tags.clear()
        for tag in tags:
            recipe.tags.add(tag)
        recipe.recipe_ing.all().delete()
        add_ingredients(recipe, ingredients)
        return recipe


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
        raise serializers.ValidationError('Новый пароль не пошел валидацию')

    def validate_current_password(self, value):
        if hashers.check_password(value,
                                  self.context['request'].user.password):
            return value
        raise serializers.ValidationError('Неверный пароль')
