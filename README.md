# Foodgram Project

Foodgram - это сервис для публикации рецептов. Пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Технологии

- Python 3.9
- Django 3.2
- Django REST Framework
- PostgreSQL
- Docker
- Nginx
- React

## Установка и запуск проекта

### Запуск в Docker

1. Убедитесь, что у вас установлен Docker и Docker Compose.

2. Создайте файл .env (пример .env.example)

3. Запустите проект:
```bash
docker-compose -f docker-compose.prod.yml up --build
```
локально
создать пустую бд foodgram
localhost

импортировать ингредиенты
python manage.py load_ingredients ../data/ingredients.json



4. Для окончания работы:
```bash
docker-compose -f docker-compose.prod.yml down
```

После запуска:
- [Frontend](http://localhost)
- [API документация](http://localhost/api/docs/)
- [Административная панель](http://localhost/admin/)

## Автор
Калинина Марина Павловна, студент МИРЭА, группа ИКБО-02-22\
Почта для связи: kalinina.m.p@edu.mirea.ru

