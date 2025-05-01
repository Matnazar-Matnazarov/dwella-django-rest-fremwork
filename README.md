# Dwella Building Jobs

Dwella - bu qurilish va ta'mirlash ishlari uchun ustalar va mijozlarni bog'lovchi zamonaviy platforma.

## 📋 Loyiha haqida

Dwella Building Jobs - bu mijozlar va professional quruvchilar/ustalar o'rtasidagi ishonchli bog'lanishni ta'minlovchi platforma. Bizning platforma orqali mijozlar o'zlariga kerakli ustalarni topishi, ustalar esa yangi ish loyihalarini olishi mumkin.

## ⭐️ Asosiy xususiyatlar

- 👨‍🔧 Malakali ustalarni topish va baholash
- 📝 Loyiha e'lonlarini joylash
- 💬 Real vaqtda xabar almashish
- 📱 Mobil qurilmalarga moslashgan interfeys
- ⭐️ Reyting va sharh tizimi
- 📍 Geolokatsiya xizmatlari
- 💰 Xavfsiz to'lov tizimi
- 📸 Loyiha rasmlari va hujjatlarini yuklash

## 🛠 Texnologiyalar

- Backend: Django REST Framework
- Mobile: React Native
- Ma'lumotlar bazasi: PostgreSQL
- Xabarlar: WebSocket
- Xarita: Google Maps API
- Autentifikatsiya: JWT

## 🚀 O'rnatish

```bash
# Repozitoriyani klonlash
git clone https://github.com/Matnazar-Matnazarov/Dwella.git

# Virtual muhitni yaratish va faollashtirish
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Loyiha ishga tushirish
python manage.py runserver
# 127.0.0.1:8000

# Redis serverini ishga tushirish
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Terminal 1
celery -A config worker -l info

# Terminal 2
celery -A config beat -l info

# Or
celery -A config.celery worker --beat --scheduler django --loglevel=info


## License

This project is dual-licensed under:

- [MIT License](./LICENSE-MIT)
- [Apache License 2.0](./LICENSE-APACHE)

