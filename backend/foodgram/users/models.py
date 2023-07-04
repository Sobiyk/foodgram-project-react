from django.contrib.auth.models import AbstractUser
from django.db import models

from app.models import Recipe
from users.validators import UsernameValidator

USER = 'user'
ADMIN = 'admin'


class User(AbstractUser):
    """ Модель пользователя. """
    roles = (
        (USER, USER),
        (ADMIN, ADMIN),
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        validators=[UsernameValidator()],
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False,
        null=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False,
        null=False
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        unique=True,
        blank=False,
        null=False
    )
    role = models.CharField(
        'Статус пользователя',
        choices=roles,
        max_length=20,
        default=USER,
        blank=True
    )
    cart = models.ManyToManyField(Recipe, blank=True, related_name='user_cart')
    favorite_list = models.ManyToManyField(Recipe,
                                           blank=True,
                                           related_name='user_favorite')

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ['id']

    def __str__(self):
        return str(self.username)

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser

    @property
    def is_user(self):
        return self.role == USER
