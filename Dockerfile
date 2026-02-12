# 1. Берем легкий образ
FROM python:3.10-slim

# 2. Ставим системную библиотеку для FAISS (без нее будет ошибка)
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3. Сначала копируем только список библиотек
COPY requirements.txt .

# 4. Устанавливаем их (Koyeb сам их скачает при сборке)
RUN pip install --no-cache-dir -r requirements.txt

# 5. И только потом копируем остальной код
COPY . .

# 6. Запуск
CMD ["python", "main.py"]
