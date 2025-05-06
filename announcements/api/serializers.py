from rest_framework import serializers
from announcements.models import Announcement
from images.models import Image
from django.contrib.contenttypes.models import ContentType
from accounts.models import CustomUser

# django geo serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["id", "name"]


class AnnouncementSerializer(GeoFeatureModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    hit_count = serializers.SerializerMethodField()
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Announcement
        geo_field = "location"
        auto_bbox = True
        fields = [
            "id",
            "guid",
            "name",
            "title",
            "description",
            "address",
            "industry",
            "slug",
            "images",
            "hit_count",
            "created_at",
            "updated_at",
            "is_active",
            "uploaded_images",
            "location",
        ]
        read_only_fields = ["guid", "slug", "created_at", "updated_at"]

    def get_hit_count(self, obj):
        """Return the hit count for the announcement"""
        try:
            from hitcount.models import HitCount
            from django.contrib.contenttypes.models import ContentType
            
            ctype = ContentType.objects.get_for_model(Announcement)
            try:
                hitcount = HitCount.objects.get(content_type=ctype, object_pk=str(obj.pk))
                return hitcount.hits
            except HitCount.DoesNotExist:
                return 0
        except Exception as e:
            print(f"Error getting hit count: {e}")
            return 0

    def create(self, validated_data):
        """
        Create announcement with uploaded images
        """
        uploaded_images = validated_data.pop("uploaded_images", [])
        announcement = Announcement.objects.create(**validated_data)

        # Create image objects for each uploaded image
        if uploaded_images:
            content_type = ContentType.objects.get_for_model(Announcement)
            for image_file in uploaded_images:
                Image.objects.create(
                    name=image_file,
                    content_type=content_type,
                    object_id=announcement.id,
                )

        return announcement

    def update(self, instance, validated_data):
        """
        Update announcement with uploaded images
        """
        uploaded_images = validated_data.pop("uploaded_images", [])

        # Update the announcement instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Add new images if provided
        if uploaded_images:
            content_type = ContentType.objects.get_for_model(Announcement)
            for image_file in uploaded_images:
                Image.objects.create(
                    name=image_file, content_type=content_type, object_id=instance.id
                )

        return instance

    def to_representation(self, instance):
        """
        Override to ensure proper GeoJSON formatting
        """
        data = super().to_representation(instance)
        if instance.location:
            # GeoJSON format
            if "geometry" not in data:
                data["geometry"] = {
                    "type": "Point",
                    "coordinates": [
                        instance.location.x,  # longitude
                        instance.location.y,  # latitude
                    ],
                }
        return data
