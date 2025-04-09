from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import CustomUser, Role
from rest_framework_api_key.models import APIKey

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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
        # Credentials ni tozalaymiz
        self.client.credentials()
        response = self.client.get(masters_url)
        # Autentifikatsiya yo'q bo'lgani uchun 401 qaytaradi
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) 