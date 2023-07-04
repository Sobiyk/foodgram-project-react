from django.contrib import admin

from .models import Ingredient, Recipe, Subscription, Tag


class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('author', 'name', 'tags')
    list_display = ('pk', 'name', 'author')


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name', 'measurement_unit')
    list_display = ('pk', 'name', 'measurement_unit')


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
