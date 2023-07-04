from django.contrib.auth import get_user_model, hashers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import dateformat, timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .mixins import ListRetrieveViewSet, ListViewSet
from .permissions import IsOwnerOrAdmin, ReadOnly
from .serializers import (
    ChangePasswordSerializer, IngredientSerializer, RecipeSerializer,
    RecipeSubSerializer, TagSerializer, UserSerializer, UserSignUpSerializer,
    UserSubSerializer,
)
from app.models import Ingredient, Recipe, RecipeIngredients, Subscription, Tag

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter, )

    def get_permissions(self):
        permission_classes = []
        if self.action == 'create' or self.action == 'list':
            permission_classes = [AllowAny]
        elif self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        elif self.action == 'destroy':
            permission_classes = [IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserSignUpSerializer
        return UserSerializer

    @action(
            detail=False,
            methods=['post'],
            permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            input_data = serializer.validated_data
            cur_password = input_data.get('current_password')
            new_password = input_data.get('new_password')
            if hashers.check_password(cur_password, request.user.password):
                request.user.set_password(new_password)
                request.user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            content = {'current_password': 'Неверный пароль'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        user = self.request.user
        author = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            if (request.user == author or Subscription.objects.filter(
                user=user, author=author)):
                content = {'errors': 'Нельзя подписаться'}
                return Response(content,
                                status=status.HTTP_400_BAD_REQUEST)

            Subscription.objects.create(user=user, author=author)
            serializer = UserSubSerializer(author,
                                           context={'request': request})
            return Response(serializer.data)

        if Subscription.objects.filter(user=user, author=author):
            Subscription.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        content = {'errors': 'Вы не были подписаны на этого пользователя'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [ReadOnly]
    pagination_class = None


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [ReadOnly]
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsOwnerOrAdmin | ReadOnly]
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_permissions(self):
        permission_classes = []
        if self.action in ['create', 'shopping_cart', 'favorite']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'retrieve' or self.action == 'list':
            permission_classes = [AllowAny]
        elif self.action == 'destroy' or 'update':
            permission_classes = [IsOwnerOrAdmin]

        return [permission() for permission in permission_classes]

    def retrieve(self, request, *args, **kwargs):
        ret = super().retrieve(request, *args, **kwargs)
        for ing in ret.data['ingredients']:
            ing['amount'] = get_object_or_404(RecipeIngredients,
                                              recipe=self.get_object(),
                                              ingredient=ing['id']).amount
        return ret

    def list(self, request, *args, **kwargs):
        ret = super().list(request, *args, **kwargs)
        for recipe in ret.data['results']:
            for ing in recipe['ingredients']:
                ing['amount'] = get_object_or_404(RecipeIngredients,
                                                  recipe=recipe['id'],
                                                  ingredient=ing['id']).amount
        return ret

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        favorite = request.user.favorite_list.through
        if request.method == 'POST':
            if favorite.objects.filter(
                recipe_id=recipe.id,
                user_id=request.user.id
                ):
                content = {'errors': 'Вы уже добавили этот рецепт в избранное'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            favorite.objects.create(
                recipe_id=recipe.id,
                user_id=request.user.id
            )
            serializer = RecipeSubSerializer(recipe)
            return Response(serializer.data)
        try:
            favorite.objects.get(
                recipe_id=recipe.id,
                user_id=request.user.id
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            content = {'errors': 'Рецепт отсутствует в избранном'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        cart = request.user.cart.through
        if request.method == 'POST':
            if cart.objects.filter(
                recipe_id=recipe.id,
                user_id=request.user.id
                ):
                content = {'errors': 'Рецепт уже в списке покупок'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            cart.objects.create(
                recipe_id=recipe.id,
                user_id=request.user.id
            )
            serializer = RecipeSubSerializer(recipe)
            return Response(serializer.data)
        try:
            cart.objects.get(
                recipe_id=recipe.id,
                user_id=request.user.id
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            content = {'errors': 'Рецепт отсутствует в списке покупок'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'],
            detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        cart_content = request.user.cart.all()
        tmp_cart = {}
        for recipe in cart_content:
            for ingredient in recipe.ingredients.all():
                if ingredient.name not in tmp_cart:
                    tmp_obj = get_object_or_404(
                        RecipeIngredients,
                        recipe=recipe,
                        ingredient=ingredient)
                    tmp_cart[ingredient.name] = tmp_obj.amount
                else:
                    tmp_cart[ingredient.name] += tmp_obj.amount

        text_content = ''
        for key, value in tmp_cart.items():
            text_content += f'{key}: {value}\n'

        now = dateformat.format(timezone.now(), 'd-m-Y H-i')
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (f'attachment;'
                                           f'filename="{request.user.username}'
                                           f'_shopping_cart {now}.txt"')
        response.write(text_content)
        return response

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)


class SubscriptionViewSet(ListViewSet):
    serializer_class = UserSubSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.request.user.follower.all()
        user_queryset = User.objects.filter(
            id__in=queryset.values('author_id')
        )
        return user_queryset
