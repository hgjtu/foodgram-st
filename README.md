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
Для запуска с бд из бэкапа (для запуска чистого проекта очистить содержимое backups):
```bash
docker-compose -f docker-compose.prod.yml up --build
```

docker exec foodgram-st-backend-1 cp -r /app/media_ex/. /app/media/

Для создания бэкапа
```bash
docker exec foodgram-st-db-1 pg_dump -U postgres foodgram > backups/backup.sql
```

Учетные данные для уже созданных профилей
Логин: admin@example.com
Пароль: admin

Логин: mk@example.com
Пароль: 1q0o2w9i

Учетные данные для уже созданных профилей
Логин: km@example.com
Пароль: 1q0o2w9i

4. Для окончания работы
```bash
docker-compose -f docker-compose.prod.yml down
```

После запуска:
- Frontend будет доступен по адресу: http://localhost
- API документация будет доступна по адресу: http://localhost/api/docs/
- Административная панель Django: http://localhost/admin/
```

