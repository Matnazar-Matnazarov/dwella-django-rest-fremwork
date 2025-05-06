# Python rasmiysidan foydalanamiz
FROM python:3.11-slim

# Ishchi katalog yaratamiz
WORKDIR /app

# System dependencieslarni o'rnatamiz
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# Requirements faylini nusxalab olamiz
COPY requirements.txt .

# Python kutubxonalarni o'rnatamiz
RUN pip install --no-cache-dir -r requirements.txt

# Loyihani ichkariga nusxalash
COPY . .

# Port ochamiz (Django uchun default 8000)
EXPOSE 8000

# Entry point sifatida wait-for-redis va Django serverni ishlatamiz
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]
