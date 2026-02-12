# Используем самую легкую версию Python
FROM python:3.10-slim

# Устанавливаем рабочую папку
WORKDIR /app

# Копируем только файлы проекта
COPY . .

# Устанавливаем минимум библиотек без кэша (для экономии места)
RUN pip install --no-cache-dir aiogram huggingface_hub

# Запускаем скрипт
CMD ["python", "main.py"]
