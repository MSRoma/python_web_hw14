# Docker-команда FROM вказує базовий образ контейнера
# Наш базовий образ - це Linux з попередньо встановленим python-3.11
FROM python:3.11.6


# Встановимо робочу директорію всередині контейнера
RUN mkdir /fastapi_app

WORKDIR /fastapi_app

COPY requirements.txt .

# Встановимо залежності всередині контейнера
RUN pip install -r requirements.txt


# Скопіюємо інші файли в робочу директорію контейнера
COPY . .

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

