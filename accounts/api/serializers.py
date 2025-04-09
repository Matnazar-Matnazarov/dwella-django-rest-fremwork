from django.contrib.auth.models import User
from rest_framework import serializers
from accounts.models import CustomUser
from industry.models import IndustryUser


class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'password2')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            },
            'id': {'read_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Parollar bir xil emas."
            })
        if  CustomUser.objects.filter(username = attrs['username'],email=attrs['email']).first():
             raise serializers.ValidationError({
                "user or email": "uniqe"
            })
        return attrs

    def create(self, validated_data):
        # password2 ni olib tashlash
        validated_data.pop('password2', None)
        
        # Yangi foydalanuvchi yaratish
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.is_active = False
        # Parolni xavfsiz saqlash
        user.set_password(validated_data['password'])
        user.save()
        
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)  # Parolni yangilashda ham shifrlash
        return super().update(instance, validated_data)


class IndustryUserSerializer(serializers.ModelSerializer):
    industry_name = serializers.CharField(source="industry.name", read_only=True)

    class Meta:
        model = IndustryUser
        fields = ["industry_name", "price", "internship", "star"]


class MasterSerializer(serializers.ModelSerializer):
    industries = IndustryUserSerializer(
        source="industryuser_set", many=True, read_only=True
    )
    likes_count = serializers.IntegerField(source="count_likes", read_only=True)
    dislikes_count = serializers.IntegerField(source="count_dislikes", read_only=True)
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "full_name",
            "email",
            "phone_number",
            "picture",
            "industries",
            "likes_count",
            "dislikes_count",
            "is_online",
        ]
