from django.db.models import Q
from django_filters import rest_framework as filters

from app.models import Recipe


class RecipeFilter(filters.FilterSet):
    """Фильтр по полям объекта модели рецепта"""
    tags = filters.CharFilter(lookup_expr='slug')
    author = filters.CharFilter(lookup_expr='id')
    is_favorited = filters.BooleanFilter(field_name='favorite_list',
                                         method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='cart',
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited']

    def filter_is_favorited(self, queryset, name, value):
        value = bool(int(value))
        print(name)
        queryset1 = self.request.user.favorite_list.all()
        if value:
            return queryset.filter(id__in=queryset1)
        else:
            return queryset.filter(~Q(id__in=queryset1))

    def filter_is_in_shopping_cart(self, queryset, name, value):
        value = bool(int(value))
        queryset1 = self.request.user.cart.all()
        if value:
            return queryset.filter(id__in=queryset1)
        else:
            return queryset.filter(~Q(id__in=queryset1))
