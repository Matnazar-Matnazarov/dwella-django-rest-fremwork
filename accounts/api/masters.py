from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from accounts.models import CustomUser, Role, Like
from accounts.api.master_serializers import MasterSerializer
from rest_framework.response import Response
from config.permissions import HasAPIKeyOrIsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Prefetch
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.db.models import OuterRef, Exists
from django.views.decorators.vary import vary_on_headers

class MasterAPIView(APIView):
    serializer_class = MasterSerializer
    throttle_classes = [UserRateThrottle]
    permission_classes = [HasAPIKeyOrIsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return CustomUser.objects.none()
        
        # Base queryset with prefetches
        queryset = (
            CustomUser.objects.filter(role=Role.MASTER)
            .prefetch_related(
                "industryuser",
                Prefetch(
                    "likes_received",
                    queryset=Like.objects.filter(is_like=True),
                    to_attr="likes",
                ),
                Prefetch(
                    "likes_received",
                    queryset=Like.objects.filter(is_like=False),
                    to_attr="dislikes",
                ),
            )
            .annotate(
                likes_count=Count(
                    "likes_received", filter=Q(likes_received__is_like=True)
                ),
                dislikes_count=Count(
                    "likes_received", filter=Q(likes_received__is_like=False)
                ),
            )
        )

        # Add is_like annotation only for authenticated users
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_like=Exists(
                    Like.objects.filter(
                        user=self.request.user,
                        master=OuterRef('pk'),
                        is_like=True
                    )
                )
            )
        
        return queryset.order_by("-id")

    def paginate_queryset(self, queryset):
        if not hasattr(self, "_paginator"):
            self._paginator = self.pagination_class()
        return self._paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        assert hasattr(self, "_paginator")
        return self._paginator.get_paginated_response(data)

    @method_decorator(cache_page(60 * 5, key_prefix="masters_list"))
    @method_decorator(vary_on_headers("Authorization", "X-API-KEY"))
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
