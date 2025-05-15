from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


# Пользователь
class User(AbstractUser):
    username = models.CharField(
        "Логин",
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+\Z",
            )
        ],
    )
    email = models.EmailField("Email", max_length=254, unique=True)
    first_name = models.CharField("Имя", max_length=150)
    last_name = models.CharField("Фамилия", max_length=150)
    avatar = models.ImageField(
        "Аватар", upload_to="users/",
        blank=True, null=True, default="userpic-icon.jpg"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self):
        return self.username
