from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import dateformat, timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .mixins import ListRetrieveViewSet, ListViewSet
from .pagination import RecipePagination
from .permissions import IsOwnerOrAdmin, ReadOnly
from .serializers import (ChangePasswordSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeSerializer,
                          TagSerializer, UserSerializer, UserSignUpSerializer,
                          UserSubSerializer)
from .utils import add_to_list
from app.models import Ingredient, Recipe, RecipeIngredient, Subscription, Tag

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
        serializer = ChangePasswordSerializer(data=request.data,
                                              context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        exists = Subscription.objects.filter(user=user, author=author).exists()
        if request.method == 'POST':
            if request.user == author or exists:
                content = {'errors': 'Нельзя подписаться'}
                return Response(content,
                                status=status.HTTP_400_BAD_REQUEST)

            Subscription.objects.create(user=user, author=author)
            serializer = UserSubSerializer(author,
                                           context={'request': request})
            return Response(serializer.data)

        if exists:
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsOwnerOrAdmin | ReadOnly]
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action in ['create', 'shopping_cart', 'favorite']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'retrieve' or self.action == 'list':
            permission_classes = [AllowAny]
        elif self.action == 'destroy' or 'update':
            permission_classes = [IsOwnerOrAdmin]

        return [permission() for permission in permission_classes]

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        favorite = request.user.favorite_list.through
        return add_to_list(recipe, favorite, request)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        cart = request.user.cart.through
        return add_to_list(recipe, cart, request)

    @action(methods=['get'],
            detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        cart = request.user.cart.all()
        ingredients = RecipeIngredient.objects.select_related('recipe').filter(
            recipe_id__in=cart).values(
                'ingredient__name',
                'ingredient__measurement_unit').annotate(
                    sum_amount=Sum('amount'))
        text_content = ''
        for ing in ingredients:
            text_content += (f'{ing["ingredient__name"]}: '
                             f'{ing["sum_amount"]} '
                             f'{ing["ingredient__measurement_unit"]}\n')
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
    pagination_class = RecipePagination

    def get_queryset(self):
        queryset = self.request.user.follower.all()
        return User.objects.filter(
            id__in=queryset.values('author_id')
        )
