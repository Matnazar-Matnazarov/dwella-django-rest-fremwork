from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from accounts.models import CustomUser, Role
from accounts.api.master_serializers import MasterSerializer
from rest_framework.response import Response
from config.permissions import HasAPIKeyOrIsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

class MasterAPIView(APIView):
    serializer_class = MasterSerializer
    throttle_classes = [UserRateThrottle]
    permission_classes = [HasAPIKeyOrIsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return CustomUser.objects.filter(
            role=Role.MASTER
        ).prefetch_related(
            'industryuser'
        ).order_by("-id")

    def paginate_queryset(self, queryset):
        if not hasattr(self, '_paginator'):
            self._paginator = self.pagination_class()
        return self._paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        assert hasattr(self, '_paginator')
        return self._paginator.get_paginated_response(data)

    def get(self, request, pk=None):
        if pk is not None:
            master = get_object_or_404(self.get_queryset(), pk=pk)
            serializer = self.serializer_class(master)
            return Response(data=serializer.data)
        
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        return Response(data=[])