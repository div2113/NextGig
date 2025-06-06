from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveUpdateAPIView,
)
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import ActivityLog
from rest_framework.exceptions import PermissionDenied

User = get_user_model()


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "size"
    max_page_size = 5


class ProfileRetriveView(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ProfileRetriveUpdateView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# Signup and List Users (list only if authenticated)
class UserListCreateApiView(ListCreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = (
        SearchFilter,
        OrderingFilter,
    )  # Enable ordering and search filtering
    search_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
    ]  # Fields for searching
    ordering_fields = ["username", "email", "date_joined"]  # Fields for ordering
    ordering = ["date_joined"]  # Default ordering by date_joined

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAdminUser()]


# Retrieve/Update/Delete specific user
class UserRetriveUpdateDestroyApiView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]  # Only admin can delete
        return [IsAuthenticated()]  # Others need to be authenticated

    def perform_update(self, serializer):
        # Lock `is_employer` from being updated unless the user is an admin
        if self.request.user.is_staff or self.get_object() == self.request.user:
            if "is_employer" in self.request.data and not self.request.user.is_staff:
                self.request.data.pop("is_employer", None)
            serializer.save()
        else:
            raise PermissionDenied("You can only update your own profile.")

    def update(self, request, *args, **kwargs):
        if self.get_object() != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You are not allowed to update another user's profile."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can delete users."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = self.get_object()
        username = user.username

        response = super().destroy(request, *args, **kwargs)

        ActivityLog.objects.create(
            user=request.user,
            action="User Deleted",
            details=f"Admin {request.user.username} permanently deleted user {username}.",
        )
        return response
