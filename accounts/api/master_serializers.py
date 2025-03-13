from rest_framework import serializers
from accounts.models import CustomUser
from industry.models import IndustryUser

class MasterSerializer(serializers.ModelSerializer):
    industry_data = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id", 
            "username", 
            "email", 
            "phone_number",
            "industry_data"
        ]

    def get_industry_data(self, obj):
        industry_users = obj.industryuser.all()
        industry_data = []
        
        for industry_user in industry_users:
            if industry_user and industry_user.industry:
                industry_data.append({
                    'name': industry_user.industry.name,
                    'price': industry_user.price,
                    'star': industry_user.star,
                    'internship': industry_user.internship
                })
        
        return industry_data