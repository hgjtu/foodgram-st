from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Ingredient(models.Model):
    """Модель ингредиента"""
    # Единицы измерения
    GRAM = 'г'
    KILOGRAM = 'кг'
    LITER = 'л'
    MILLILITER = 'мл'
    PIECE = 'шт'
    TEASPOON = 'ч.л.'
    TABLESPOON = 'ст.л.'
    PINCH = 'щеп.'
    
    UNIT_CHOICES = [
        (GRAM, 'грамм'),
        (KILOGRAM, 'килограмм'),
        (LITER, 'литр'),
        (MILLILITER, 'миллилитр'),
        (PIECE, 'штука'),
        (TEASPOON, 'чайная ложка'),
        (TABLESPOON, 'столовая ложка'),
        (PINCH, 'щепотка'),
    ]
    
    name = models.CharField(
        'Название ингредиента',
        max_length=200,
        unique=True
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=10,
        choices=UNIT_CHOICES,
        default=GRAM
    )
    
    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
    
    def __str__(self):
        return f'{self.name}, {self.get_measurement_unit_display()}'