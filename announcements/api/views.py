from rest_framework import viewsets, status
from announcements.models import Announcement
from .serializers import AnnouncementSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from rest_framework_gis.filters import DistanceToPointFilter
from rest_framework.pagination import PageNumberPagination
from config.permissions import HasAPIKeyOrIsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [HasAPIKeyOrIsAuthenticated]
    distance_filter_field = "location"
    filter_backends = (DistanceToPointFilter,)
    pagination_class = PageNumberPagination
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    # Asosiy queryset
    queryset = Announcement.objects.filter(is_deleted=False).select_related("client")

    def get_queryset(self):
        # Swagger sxema yaratish so'rovi ekanligini tekshirish
        if getattr(self, 'swagger_fake_view', False):
            return Announcement.objects.none()

        # Asosiy queryset'ni olish
        queryset = super().get_queryset().select_related("client").prefetch_related("images")
        return queryset

    def perform_create(self, serializer):
        if self.request.user.role in ["CLIENT", "ADMIN", "SUPERADMIN", "MANAGER"]:
            serializer.save(client=self.request.user)
        else:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={"message": "You are not allowed to create an announcement"},
            )

    def perform_update(self, serializer):
        if serializer.instance.client == self.request.user:
            serializer.save()
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def perform_destroy(self, instance):
        if instance.client == self.request.user:
            instance.is_deleted = True
            instance.save()
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=["get"])
    def my_announcements(self, request):
        """Endpoint to get only current user's announcements"""
        queryset = self.get_queryset()
        if request.user.role in ["CLIENT", "ADMIN", "SUPERADMIN", "MANAGER"]:
            queryset = queryset.filter(client=request.user)
        else:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "You are not allowed to get announcements"},
            )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Search announcements by title, name or description"""
        search_term = request.query_params.get("q", "")
        if not search_term:
            return Response(
                {"error": "Search term is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        queryset = Announcement.objects.filter(
            Q(is_deleted=False)
            & (
                Q(title__icontains=search_term)
                | Q(name__icontains=search_term)
                | Q(description__icontains=search_term)
            )
        ).select_related("client").prefetch_related("images")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @method_decorator(
        cache_page(60 * 60, key_prefix="announcements_list")
    )  # 1 soat cache
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(
        cache_page(60 * 60, key_prefix="announcements_detail")
    )  # 1 soat cache
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
