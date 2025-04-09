from rest_framework import serializers
from accounts.models import CustomUser
from industry.models import IndustryUser, Industry


class IndustryUserSerializer(serializers.ModelSerializer):
    industry_name = serializers.CharField(source="industry.name", read_only=True)

    class Meta:
        model = IndustryUser
        fields = ["id", "industry", "industry_name", "price", "internship", "star"]


class MasterSerializer(serializers.ModelSerializer):
    industries = serializers.SerializerMethodField()
    full_name = serializers.CharField(source="get_full_name", read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    dislikes_count = serializers.IntegerField(read_only=True)
    is_like = serializers.BooleanField(read_only=True, default=None)
    
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "picture",
            "industries",
            "likes_count",
            "dislikes_count",
            "is_like",
        ]
    
    def get_industries(self, obj):
        # Use prefetched industries to avoid additional queries
        if hasattr(obj, 'prefetched_industries'):
            return IndustryUserSerializer(obj.prefetched_industries, many=True).data
        return IndustryUserSerializer(obj.industryuser.all(), many=True).data
