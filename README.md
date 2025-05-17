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

2. Создайте файл .env (пример .env.example) (POSTGRES_HOST=db, DEBUG=False)

3. Запустите проект:
```bash
docker-compose -f docker-compose.prod.yml up --build
```

4. Для окончания работы:
```bash
docker-compose -f docker-compose.prod.yml down
```

После запуска будут доступны ссылки:
- [Frontend](http://localhost)
- [API документация](http://localhost/api/docs/)
- [Административная панель](http://localhost/admin/)

### Локальное развертывание без Докера

1. Создайте файл .env (пример .env.example) (POSTGRES_HOST=localhost, DEBUG=True)

2. Cоздайте пустую базу данных PostgreSQL и внесите ее данные в .env

3. Перейти в backend/foodgramApi
```bash
cd backend/foodgramApi
```

4. Создать venv
```bash
python3 -m venv venv
```

5. Запустить vevn

Windows:
```bash
.\venv\Scripts\activate
```
Linux:
```bash
source venv/bin/activate
```

6. Установить зависимости
```bash
pip install -r requirements.txt
```

7. Применить миграции
```bash
python manage.py migrate
```

8. Создать суперюзера
```bash
python manage.py createsuperuser
```

9. Импортировать ингредиенты:
```bash
python manage.py load_ingredients ../data/ingredients.json
```

10. Собрать статику
```bash
python manage.py collectstatic --noinput
```

11. Запустить приложение
```bash
python manage.py runserver
```

После запуска будут доступны ссылки:
- [API](http://localhost:8000/api/)
- [Административная панель](http://localhost:8000/admin/)


## Автор
Калинина Марина Павловна, студент МИРЭА, группа ИКБО-02-22\
Почта для связи: kalinina.m.p@edu.mirea.ru

