from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


# Пользователь
class User(AbstractUser):
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Недопустимые символы в имени пользователя'
            )
        ]
    )
    email = models.EmailField(
        'Email',
        max_length=254,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=150
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150
    )
    password = models.CharField(
        'Пароль',
        max_length=150
    )
    is_subscribed = models.BooleanField(
        'Подписка на рассылку',
        default=False
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/avatars/',
        blank=True,
        null=True,
        default='userpic-icon.jpg'
    )
    shopping_cart = models.ManyToManyField(
        'recipes.Recipe',
        related_name='in_shopping_carts',
        verbose_name='Список покупок',
        blank=True
    )
    favorites = models.ManyToManyField(
        'recipes.Recipe',
        related_name='favorited_by',
        verbose_name='Избранное',
        blank=True
    )
    subscriptions = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='subscribers',
        verbose_name='Подписки',
        blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email'
            )
        ]

    def __str__(self):
        return self.username