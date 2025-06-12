from rest_framework import viewsets,permissions,status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import NotificationSerializer
from .models import Notification
from rest_framework.permissions import BasePermission,IsAuthenticated

class IsJobSeeker(BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_anonymous and not request.user.is_employer


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class=NotificationSerializer
    permission_classes=[IsAuthenticated, IsJobSeeker]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=True,methods=['patch'],url_name="mark_read")
    def mark_as_read(self,request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read."}, status=status.HTTP_200_OK)
    