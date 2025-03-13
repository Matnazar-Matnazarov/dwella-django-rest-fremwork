# import requests
# import os
# import json
import os
import django
import pickle
import redis

# # Test image papkasini yaratish
# if not os.path.exists('test_image'):
#     os.makedirs('test_image')

# # API endpoint URL
# base_url = "http://127.0.0.1:8000"
# endpoint = f"{base_url}/announcements/api/announcement/"

# # Authentication token (Bearer token)
# headers = {
#     'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQxNzEzOTE0LCJpYXQiOjE3NDE2Mjc1MTQsImp0aSI6ImE2ODlhZmYwZGQ3YTQ2NGI5ZDhmNmQ5MTEwYzM3NzAxIiwidXNlcl9pZCI6MX0.RmyiFvvLZT9y7po16Dle_kLLInl8Lxi9thxfGbwPEVM'
# }

# # Announcement ma'lumotlari
# data = {
#     'title': 'Yangi e\'lon',
#     'description': 'E\'lon tafsilotlari',
#     'name': 'Test e\'lon',
#     'industry': json.dumps({'sector': 'IT', 'type': 'Software'}),
#     'address': 'Toshkent, Uzbekistan',
#     'location': f'POINT({69.2401} {41.2995})'  # WKT formatida
# }

# # Fayl handlerlarni saqlash uchun ro'yxat
# file_handlers = []

# try:
#     # Fayllarni ochish
#     file1 = open('test_image/image_1.png', 'rb')
#     file2 = open('test_image/image.png', 'rb')
#     file_handlers.extend([file1, file2])

#     # Rasmlarni yuborish
#     files = [
#         ('uploaded_images', file1),
#         ('uploaded_images', file2)
#     ]

#     # POST so'rovini yuborish
#     response = requests.post(
#         endpoint,
#         headers=headers,
#         data=data,
#         files=files
#     )

#     # Natijani tekshirish
#     if response.status_code == 201:  # 201 Created
#         print("E'lon muvaffaqiyatli yaratildi!")
#         print(response.json())
#     else:
#         print("Xatolik yuz berdi:", response.status_code)
#         print(response.json())

# except FileNotFoundError:
#     print("Xatolik: Test rasmlar topilmadi!")
#     print("Iltimos, test_image papkasiga image_1.png va image.png nomli rasmlarni joylang")

# finally:
#     # Ochilgan fayllarni yopish
#     for file_handler in file_handlers:
#         try:
#             file_handler.close()
#         except:
#             pass

# Django sozlamalarini sozlash
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Redisga ulanish
r = redis.Redis(host="localhost", port=6379, db=2)

# Kalitni olish (changed to an existing key)
key = "as:804c9c5455614cb809210063deb827af"
serialized_data = r.get(key)

# Ma'lumotlarni deserialized qilish
if serialized_data:
    data = pickle.loads(serialized_data)
    # Print only the relevant announcement details
    if hasattr(data, "_result_cache"):  # Check if it's a QuerySet
        # Use values_list to get all fields
        for announcement in data.values_list():
            print(announcement)  # Print all fields as a tuple
    else:
        print(data)  # Fallback for non-QuerySet data
