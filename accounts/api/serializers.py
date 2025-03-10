from django.contrib.auth.models import User
from rest_framework import serializers
from accounts.models import CustomUser
from industry.models import IndustryUser

class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        """Meta class for the UserSerializer"""
        model = CustomUser
        fields = ['url', 'username', 'email', 'password', 'password2', 'is_staff', 'is_active', 'date_joined']
        read_only_fields = ['is_staff', 'is_active', 'date_joined']

    def validate(self, data):
        """Validation for password and password2"""
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Parollar bir xil emas")
        return data

    def create(self, validated_data):
        """Create a new user"""
        # password2 ni o'chiramiz chunki u modelda yo'q
        validated_data.pop('password2')
        password = validated_data.pop('password')
        
        # Foydalanuvchini yaratamiz
        user = CustomUser.objects.create(**validated_data)
        # Parolni xeshlaymiz
        user.set_password(password)
        user.save()
        
        return user

class IndustryUserSerializer(serializers.ModelSerializer):
    industry_name = serializers.CharField(source='industry.name', read_only=True)
    
    class Meta:
        model = IndustryUser
        fields = ['industry_name', 'price', 'internship', 'star']

class MasterSerializer(serializers.ModelSerializer):
    industries = IndustryUserSerializer(source='industryuser_set', many=True, read_only=True)
    likes_count = serializers.IntegerField(source='count_likes', read_only=True)
    dislikes_count = serializers.IntegerField(source='count_dislikes', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'full_name',
            'email',
            'phone_number',
            'picture',
            'industries',
            'likes_count',
            'dislikes_count',
            'is_online',
        ]

