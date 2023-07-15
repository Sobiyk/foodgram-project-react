from django.db.models import Q
from django_filters import rest_framework as filters

from app.models import Ingredient, Recipe, Tag


class RecipeFilter(filters.FilterSet):
    """Фильтр по полям объекта модели рецепта"""
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tag.objects.all(),
                                             conjoined=False)
    author = filters.CharFilter(field_name='author')
    is_favorited = filters.BooleanFilter(field_name='favorite_list',
                                         method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='cart',
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        value = bool(int(value))
        user_fav_list = self.request.user.favorite_list.all()
        if value:
            return queryset.filter(id__in=user_fav_list)
        return queryset.filter(~Q(id__in=user_fav_list))

    def filter_is_in_shopping_cart(self, queryset, name, value):
        value = bool(int(value))
        user_cart_list = self.request.user.cart.all()
        if value:
            return queryset.filter(id__in=user_cart_list)
        return queryset.filter(~Q(id__in=user_cart_list))


class IngredientFilter(filters.FilterSet):
    """Фильтр по полям объекта модели ингредиента"""
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']
