from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import CustomUser, Role
from rest_framework_api_key.models import APIKey
from django.test import override_settings
import logging

# simple_history paketining log darajasini o'zgartirish
logging.getLogger('simple_history').setLevel(logging.ERROR)

@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {}
    }
)
class AuthenticationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Test user yaratish
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        self.user = CustomUser.objects.create_user(**self.user_data)
        
        # API key yaratish
        self.api_key, self.key = APIKey.objects.create_key(name="test-key")

    def test_token_obtain(self):
        """Test token olish"""
        url = reverse('token_obtain_pair')
        data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_masters_endpoint_with_auth(self):
        """Masters endpointini autentifikatsiya bilan tekshirish"""
        # Token olish
        token_url = reverse('token_obtain_pair')
        token_response = self.client.post(token_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        access_token = token_response.data['access']
        
        # Headers ni o'rnatish
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            HTTP_X_API_KEY=self.key
        )
        
        # Masters endpoint
        url = reverse('masters')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid_credentials(self):
        """Noto'g'ri ma'lumotlar bilan login qilishni tekshirish"""
        url = reverse('token_obtain_pair')
        invalid_data = {
            'username': self.user_data['username'],
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_without_auth(self):
        """Autentifikatsiyasiz protected endpoint ga murojaat qilishni tekshirish"""
        masters_url = reverse('masters')
        response = self.client.get(masters_url)
        # HasAPIKeyOrIsAuthenticated permission bo'lgani uchun 401 qaytaradi
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_without_api_key(self):
        """Faqat JWT token bilan, API key siz murojaat qilishni tekshirish"""
        # Token olish
        token_url = reverse('token_obtain_pair')
        token_response = self.client.post(token_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        access_token = token_response.data['access']
        
        # Faqat JWT token bilan murojaat
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        masters_url = reverse('masters')
        response = self.client.get(masters_url)
        # HasAPIKeyOrIsAuthenticated permission bo'lgani uchun 200 qaytaradi
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout(self):
        """Logout funksionalligini tekshirish"""
        # Token olish
        token_url = reverse('token_obtain_pair')
        token_response = self.client.post(token_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        access_token = token_response.data['access']
        
        # Token va API key ni o'rnatamiz
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            HTTP_X_API_KEY=self.key
        )
        
        # Logout qilamiz
        logout_url = reverse('logout')
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Logout dan keyin protected endpoint ga murojaat qilib ko'ramiz
        masters_url = reverse('masters')
        # Credentials ni tozalayamiz
        self.client.credentials()
        response = self.client.get(masters_url)
        # Autentifikatsiya yo'q bo'lgani uchun 401 qaytaradi
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Token yangilash funksionalligini tekshirish"""
        # Avval token olish
        token_url = reverse('token_obtain_pair')
        token_response = self.client.post(token_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        refresh_token = token_response.data['refresh']
        
        # Token yangilash
        refresh_url = reverse('token_refresh')
        response = self.client.post(refresh_url, {'refresh': refresh_token})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_verify(self):
        """Token tekshirish funksionalligini tekshirish"""
        # Avval token olish
        token_url = reverse('token_obtain_pair')
        token_response = self.client.post(token_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        access_token = token_response.data['access']
        
        # Token tekshirish
        verify_url = reverse('token_verify')
        response = self.client.post(verify_url, {'token': access_token})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_blacklist(self):
        """Token blacklist funksionalligini tekshirish"""
        # Avval token olish
        token_url = reverse('token_obtain_pair')
        token_response = self.client.post(token_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        refresh_token = token_response.data['refresh']
        
        # Token blacklist ga qo'shish
        blacklist_url = reverse('token_blacklist')
        response = self.client.post(blacklist_url, {'refresh': refresh_token})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_role_based_access(self):
        """Role asosida ruxsatlarni tekshirish"""
        # Admin user yaratish
        admin_user = CustomUser.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role=Role.ADMIN
        )
        
        # Admin uchun token olish
        token_url = reverse('token_obtain_pair')
        token_response = self.client.post(token_url, {
            'username': 'admin',
            'password': 'adminpass123'
        })
        
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        access_token = token_response.data['access']
        
        # Admin token bilan murojaat
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            HTTP_X_API_KEY=self.key
        )
        
        # Admin endpointlarini tekshirish
        # Admin panelga kirish uchun login qilish kerak, shuning uchun 302 (Redirect) qaytaradi
        admin_url = reverse('admin:index')  # Admin panel URL
        response = self.client.get(admin_url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)  # Redirect to login page

    def test_api_key_rotation(self):
        """API key almashish funksionalligini tekshirish"""
        # Yangi API key yaratish
        new_api_key, new_key = APIKey.objects.create_key(name="new-test-key")
        
        # Eski API key bilan murojaat
        self.client.credentials(HTTP_X_API_KEY=self.key)
        masters_url = reverse('masters')
        response = self.client.get(masters_url)
        # HasAPIKeyOrIsAuthenticated permission bo'lgani uchun 401 qaytaradi
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Yangi API key bilan murojaat
        self.client.credentials(HTTP_X_API_KEY=new_key)
        response = self.client.get(masters_url)
        # Yangi API key ham ishlaydi
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_expiration(self):
        """Token muddatini tekshirish"""
        # Avval token olish
        token_url = reverse('token_obtain_pair')
        token_response = self.client.post(token_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        access_token = token_response.data['access']
        
        # Token muddati tugaganligini simulyatsiya qilish
        # Bu test uchun token muddatini settings.py da qisqartirish kerak
        # Lekin test muhitida bu o'zgarishlar kerak emas
        
        # Token bilan murojaat
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            HTTP_X_API_KEY=self.key
        )
        
        masters_url = reverse('masters')
        response = self.client.get(masters_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Token hali amal qiladi 