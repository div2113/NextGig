from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from .serializers import EmployerProfileSerializer
from .models import EmployerProfile
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from user.models import ActivityLog
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError, PermissionDenied
from user.pagination import BasePagination
from rest_framework.exceptions import NotFound


class EmployerProfileCreateApiView(ListCreateAPIView):
    serializer_class = EmployerProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BasePagination

    def get_queryset(self):
        return EmployerProfile.objects.filter(is_deleted=False).order_by("id")

    def perform_create(self, serializer):
        user = self.request.user
        soft_deleted_profile = EmployerProfile.objects.filter(
            user=user, is_deleted=True
        ).first()

        if soft_deleted_profile:
            # If a soft-deleted profile exists, reuse it through the serializer
            serializer.instance = soft_deleted_profile
            soft_deleted_profile.is_deleted = False
            soft_deleted_profile.is_active = True
            serializer.save(user=user)

            ActivityLog.objects.create(
                user=user,
                action="Employer Profile Restored",
                details=f"{user.username} restored their soft-deleted employer profile.",
            )

        elif EmployerProfile.objects.filter(user=user, is_deleted=False).exists():
            raise ValidationError("You already have an employer profile.")
        else:
            serializer.save(user=user)
            ActivityLog.objects.create(
                user=user,
                action="Employer Profile Created",
                details=f"{user.username} created their employer profile.",
            )


class EmployerProfileDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = EmployerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_employer:
            return EmployerProfile.objects.filter(
                user=self.request.user, is_deleted=False
            )
        raise PermissionDenied("Jobseekers cannot access employer profiles.")

    def get_object(self):
        profile = EmployerProfile.objects.filter(
            user=self.request.user, is_deleted=False
        ).first()
        if not profile:
            raise NotFound("Employer profile not found.")
        return profile

    def perform_update(self, serializer):
        # Check that the employer can only update their own profile
        instance = self.get_object()
        if self.request.user != instance.user:
            raise PermissionDenied("You can only update your own profile.")

        serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action="Employer Profile Updated",
            details=f"Employer profile for {self.get_object().company_name} updated by {self.request.user.username}.",
        )

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.is_active = False
        instance.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action="Employer Profile Deleted",
            details=f"Employer profile for {instance.company_name} was deleted by {self.request.user.username}.",
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Employer profile deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class EmployerProfileAdminListView(ListAPIView):
    queryset = EmployerProfile.objects.all().order_by("id")
    serializer_class = EmployerProfileSerializer
    permission_classes = [IsAdminUser]
    pagination_class = PageNumberPagination
