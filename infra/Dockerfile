FROM nginx:1.25.4-alpine

# Удаляем дефолтную конфигурацию nginx
RUN rm /etc/nginx/conf.d/default.conf

# Копируем нашу конфигурацию
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Создаем директории для статических файлов
RUN mkdir -p /usr/share/nginx/html/static/ \
    && mkdir -p /usr/share/nginx/html/media/

# Устанавливаем права
RUN chown -R nginx:nginx /usr/share/nginx/html/ \
    && chmod -R 755 /usr/share/nginx/html/

# Открываем порт
EXPOSE 80

# Запускаем nginx
CMD ["nginx", "-g", "daemon off;"] 