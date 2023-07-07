from django.conf import settings
from django.db import models

from .validators import HexColorValidator, validate_not_zero


class Tag(models.Model):
    """ Модель тэга """
    name = models.CharField(max_length=200, blank=False,
                            unique=True, null=False)

    color = models.CharField(max_length=7, blank=False,
                             null=False, unique=True,
                             validators=[HexColorValidator()])

    slug = models.SlugField(max_length=200, blank=False,
                            null=False, unique=True)

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'тэги'
        ordering = ['id']

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """ Модель ингредиента """
    name = models.CharField(max_length=200, blank=False,
                            null=False)

    measurement_unit = models.CharField(max_length=200, blank=False,
                                        null=False)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        ordering = ['id']

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """ Модель рецепта """
    tags = models.ManyToManyField(Tag, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='recipes'
                               )
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         related_name='recipes'
                                         )
    name = models.CharField('Название', max_length=200, null=False,
                            blank=False
                            )
    image = models.ImageField('Изображение', upload_to='recipes/')
    text = models.TextField(max_length=500, blank=False, null=False)
    cooking_time = models.PositiveSmallIntegerField(
        blank=False,
        null=False,
        validators=[validate_not_zero]
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_ing')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='recipe_ing')
    amount = models.PositiveSmallIntegerField(blank=False,
                                              null=False,
                                              validators=[validate_not_zero])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]


class Subscription(models.Model):
    """ Модель подписки """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        ordering = ['id']
