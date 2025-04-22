from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from ..models import Chat
from ..serializers import ChatSerializer
from connect_announcements.models import ConnectAnnouncement
from django.db.models import Q
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        connect_announcement_id = self.kwargs.get('connect_announcement_id')
        master_id = self.kwargs.get('master_id')
        client_id = self.kwargs.get('client_id')
        
        # Check if user is either the master or client
        user = self.request.user
        if str(user.id) != master_id and str(user.id) != client_id:
            context['error'] = "You don't have permission to access this chat"
        
        return context

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Check if this is a swagger schema generation request
        if getattr(self, 'swagger_fake_view', False):
            return Chat.objects.none()
        
        user = self.request.user
        return Chat.objects.filter(
            Q(master=user) | Q(client=user)
        ).order_by('created_at')
    
    @action(detail=False, methods=['get'])
    def get_chat_history(self, request):
        """Get chat history for a specific announcement between client and master"""
        connect_announcement_id = request.query_params.get('connect_announcement_id')
        master_id = request.query_params.get('master_id')
        client_id = request.query_params.get('client_id')
        
        if not all([connect_announcement_id, master_id, client_id]):
            return Response(
                {"error": "Missing required parameters"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is either the master or client
        user = request.user
        if str(user.id) != master_id and str(user.id) != client_id:
            return Response(
                {"error": "You don't have permission to access this chat"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get chat history
        chats = Chat.objects.filter(
            connect_announcement_id=connect_announcement_id,
            master_id=master_id,
            client_id=client_id
        ).order_by('created_at')
        
        serializer = self.get_serializer(chats, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def get_active_chats(self, request):
        """Get all active chats for the current user"""
        # Check if this is a swagger schema generation request
        if getattr(self, 'swagger_fake_view', False):
            return Response([])
            
        user = request.user
        
        # Get all connect announcements where the user is either master or client
        if user.role == 'MASTER':
            chats = Chat.objects.filter(master=user).values(
                'connect_announcement', 'client'
            ).distinct()
        else:
            chats = Chat.objects.filter(client=user).values(
                'connect_announcement', 'master'
            ).distinct()
        
        active_chats = []
        for chat in chats:
            connect_announcement = ConnectAnnouncement.objects.get(
                id=chat['connect_announcement']
            )
            
            # Get the most recent message
            if user.role == 'MASTER':
                recent_message = Chat.objects.filter(
                    connect_announcement=connect_announcement,
                    master=user,
                    client_id=chat['client']
                ).order_by('-created_at').first()
                
                client_id = chat['client']
                master_id = user.id
            else:
                recent_message = Chat.objects.filter(
                    connect_announcement=connect_announcement,
                    client=user,
                    master_id=chat['master']
                ).order_by('-created_at').first()
                
                client_id = user.id
                master_id = chat['master']
            
            active_chats.append({
                'connect_announcement_id': str(connect_announcement.id),
                'connect_announcement_title': connect_announcement.announcement.title if connect_announcement.announcement else "",
                'master_id': str(master_id),
                'client_id': str(client_id),
                'last_message': recent_message.message if recent_message else "",
                'last_message_time': recent_message.created_at if recent_message else None
            })
        
        return Response(active_chats) 