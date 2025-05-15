from django.db import models
from django.conf import settings
from recipes.models import Recipe


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shopping_cart_items',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_carts_of_users', 
        verbose_name='Рецепт в списке покупок'
    )

    class Meta:
        verbose_name = 'Корзина (рецепт)'
        verbose_name_plural = 'Корзины (рецепты)'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'], name='unique_user_recipe_shopping_cart')
        ]

    def __str__(self):
        return f'{self.user} has {self.recipe} in cart'


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_items',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by_users_relations',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранное (рецепт)'
        verbose_name_plural = 'Избранные (рецепты)'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'], name='unique_user_recipe_favorite')
        ]

    def __str__(self):
        return f'{self.user} favorited {self.recipe}'


class Subscription(models.Model):
    user = models.ForeignKey( 
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey( 
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Автор, на которого подписаны'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'], name='unique_user_author_subscription'),
            models.CheckConstraint(check=~models.Q(user=models.F('author')), name='prevent_self_subscription')
        ]

    def __str__(self):
        return f'{self.user} follows {self.author}'
