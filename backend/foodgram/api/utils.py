from rest_framework import status
from rest_framework.response import Response

from api import serializers
from app.models import RecipeIngredient

def add_ingredients(recipe, ingredients):
    """ Метод для добавления ингредиентов в рецепт """
    RecipeIngredient.objects.bulk_create([
        RecipeIngredient(
            ingredient_id=item.get('id').id,
            recipe=recipe,
            amount=item['amount']) for item in ingredients 
    ])


def add_to_list(recipe, queryset, request):
    """ Добавляет или удаляет объект модели из списка ManyToMany """
    exists = queryset.objects.filter(recipe_id=recipe.id,
                                 user_id=request.user.id)
    if request.method == 'POST':
        if exists:
            content = {'errors': 'Рецепт уже в списке'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        queryset.objects.create(
            recipe_id=recipe.id,
            user_id=request.user.id
        )
        serializer = serializers.RecipeSubSerializer(recipe)
        return Response(serializer.data)
    if exists:
        queryset.objects.get(
            recipe_id=recipe.id,
            user_id=request.user.id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    content = {'errors': 'Рецепт отсутствует в списке'}
    return Response(content, status=status.HTTP_400_BAD_REQUEST)
