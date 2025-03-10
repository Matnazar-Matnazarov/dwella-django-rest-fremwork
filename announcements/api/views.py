from rest_framework import viewsets, status
from announcements.models import Announcement
from .serializers import AnnouncementSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Prefetch, Q

class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    queryset = Announcement.objects.none()
    
    def get_queryset(self):
        """
        Returns optimized queryset with prefetched related objects
        and filtered by the current user.
        """
        # Swagger schema generation paytida bo'sh queryset qaytarish
        if getattr(self, 'swagger_fake_view', False):
            return Announcement.objects.none()
            
        return (Announcement.objects
                .filter(client=self.request.user, is_deleted=False)
                .select_related('client')
                .prefetch_related('images', 'hit_count_generic'))
    
    def perform_create(self, serializer):
        serializer.save(client=self.request.user)
    
    def perform_update(self, serializer):
        if serializer.instance.client == self.request.user:
            serializer.save()
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    
    def perform_destroy(self, instance):
        """Soft delete implementation"""
        if instance.client == self.request.user:
            instance.is_deleted = True
            instance.save()
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
    @action(detail=False, methods=['get'])
    def my_announcements(self, request):
        """Endpoint to get only current user's announcements"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search announcements by title, name or description"""
        search_term = request.query_params.get('q', '')
        if not search_term:
            return Response({"error": "Search term is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        queryset = (Announcement.objects
                   .filter(
                       Q(is_deleted=False) &
                       (Q(title__icontains=search_term) | 
                        Q(name__icontains=search_term) | 
                        Q(description__icontains=search_term))
                   )
                   .select_related('client')
                   .prefetch_related('images', 'hit_count_generic'))
                   
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

