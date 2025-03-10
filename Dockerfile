FROM python:3.12-slim

# O'zgaruvchilarni o'rnatish
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Ishchi direktoriyani yaratish
WORKDIR /app

# System dependencies o'rnatish
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgis \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proyekt fayllarini ko'chirish
COPY . .

# Create necessary directories
RUN mkdir -p /app/static /app/media

# Permissions
RUN chown -R nobody:nogroup /app/static /app/media
USER nobody

# Gunicorn va Daphne uchun portlarni ochish
EXPOSE 8000 8001
