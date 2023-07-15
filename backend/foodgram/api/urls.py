from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet, RecipeViewSet, SubscriptionViewSet,
                    TagViewSet, UserViewSet)

app_name = 'api'

router = routers.DefaultRouter()

router.register(r'users/subscriptions', SubscriptionViewSet,
                basename='subscription')
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path(r'auth/', include('djoser.urls.authtoken')),
    path(r'', include(router.urls)),
]
