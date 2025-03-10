from rest_framework import serializers
from announcements.models import Announcement
from images.models import Image
from django.contrib.contenttypes.models import ContentType
from accounts.models import CustomUser
# django geo serializers 


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'name', 'content_type', 'object_id']

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the CustomUser model"""
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'picture', 'role', 'is_active', 'is_staff', 'is_superuser']
        read_only_fields = ['is_active', 'is_staff', 'is_superuser']
        ref_name = "AnnouncementUserSerializer"

class AnnouncementSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    client = UserSerializer(read_only=True)
    hit_count = serializers.SerializerMethodField()
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'guid', 'name', 'title', 'description', 'client', 
            'location', 'address', 'industry', 'slug', 'images', 
            'hit_count', 'created_at', 'updated_at', 
            'is_active', 'uploaded_images'
        ]
        read_only_fields = ['guid', 'slug', 'created_at', 'updated_at', 'client']
    
    def get_hit_count(self, obj):
        """Return the hit count for the announcement"""
        try:
            return obj.hit_count_generic.count()
        except:
            return 0
    
    def create(self, validated_data):
        """
        Create announcement with uploaded images
        """
        uploaded_images = validated_data.pop('uploaded_images', [])
        announcement = Announcement.objects.create(**validated_data)
        
        # Create image objects for each uploaded image
        if uploaded_images:
            content_type = ContentType.objects.get_for_model(Announcement)
            for image_file in uploaded_images:
                Image.objects.create(
                    name=image_file,
                    content_type=content_type,
                    object_id=announcement.id
                )
        
        return announcement
    
    def update(self, instance, validated_data):
        """
        Update announcement with uploaded images
        """
        uploaded_images = validated_data.pop('uploaded_images', [])
        
        # Update the announcement instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Add new images if provided
        if uploaded_images:
            content_type = ContentType.objects.get_for_model(Announcement)
            for image_file in uploaded_images:
                Image.objects.create(
                    name=image_file,
                    content_type=content_type,
                    object_id=instance.id
                )
        
        return instance


