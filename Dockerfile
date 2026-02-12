# Используем официальный образ Python
FROM python:3.9

# Создаем рабочего пользователя (требование Hugging Face)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:${PATH}"

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY --chown=user . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем бота
CMD ["python", "main.py"]