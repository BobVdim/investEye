# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . .

# Устанавливаем зависимости, если есть requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# Запускаем файл
CMD ["python", "main.py"]
