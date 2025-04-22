from rest_framework import serializers
from .models import Chat
from accounts.api.serializers import UserSerializer

class ChatSerializer(serializers.ModelSerializer):
    master_details = UserSerializer(source='master', read_only=True)
    client_details = UserSerializer(source='client', read_only=True)
    
    class Meta:
        model = Chat
        fields = [
            'id', 
            'connect_announcement', 
            'master', 'master_details',
            'client', 'client_details',
            'message', 
            'image', 
            'created_at'
        ]
        read_only_fields = ['created_at'] 