from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from accounts.models import CustomUser
from .serializers import MasterSerializer

class MastersView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        masters = CustomUser.objects.filter(role='MASTER').prefetch_related(
            'industryuser_set__industry',
            'likes_given',
            'likes_received'
        )
        serializer = MasterSerializer(masters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        return Response({"message": "Hello, world!"}, status=status.HTTP_200_OK)